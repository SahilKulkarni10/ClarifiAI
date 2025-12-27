"""
Chat Service
Handles AI chat functionality with RAG integration.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from app.models.chat import (
    ChatMessage,
    ChatResponse,
    ChatHistory,
    MessageRole
)
from app.services.rag_engine import rag_engine
from app.services.llm_service import llm_service
from app.services.financial_rules import financial_rules
from app.services.finance_service import FinanceService
from app.services.market_data import market_data


class ChatService:
    """Service for AI chat operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.finance_service = FinanceService(db)
    
    async def send_message(
        self,
        user_id: str,
        message: str
    ) -> ChatResponse:
        """
        Process a user message and generate AI response.
        
        This method:
        1. Saves the user message
        2. Retrieves relevant context from RAG
        3. Gets user's financial data for context
        4. Performs any necessary calculations
        5. Generates LLM response with all context
        6. Saves and returns the response
        """
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # Initialize RAG and LLM if needed
            await rag_engine.initialize()
            await llm_service.initialize()
            
            # Save user message to history
            await self._save_message(user_id, MessageRole.USER, message, timestamp)
            
            # Detect query intent and get relevant RAG context
            query_intent = self._detect_query_intent(message)
            
            # Get user's financial context (with stock recommendations if needed)
            include_stocks = query_intent.get("requires_stock_recommendations", False)
            financial_data = await self._get_user_financial_context(
                user_id, 
                include_stock_recommendations=include_stocks,
                user_query=message if include_stocks else None
            )
            
            rag_context = await rag_engine.get_context_for_query(
                message,
                categories=query_intent.get("categories")
            )
            
            # Perform any calculations if needed
            calculated_results = await self._perform_calculations(
                message,
                query_intent,
                financial_data
            )
            
            # Generate LLM response
            response_text = await llm_service.generate_response(
                user_query=message,
                rag_context=rag_context if rag_context else None,
                financial_data=financial_data,
                calculated_results=calculated_results
            )
            
            response_timestamp = datetime.utcnow().isoformat()
            
            # Save assistant response to history
            await self._save_message(
                user_id,
                MessageRole.ASSISTANT,
                response_text,
                response_timestamp
            )
            
            # Determine sources used
            sources_used = []
            if rag_context:
                sources_used.append("Financial Knowledge Base")
            if financial_data:
                sources_used.append("Your Financial Data")
            if calculated_results:
                sources_used.append("Financial Calculations")
            
            return ChatResponse(
                response=response_text,
                timestamp=response_timestamp,
                sources_used=sources_used if sources_used else None
            )
            
        except Exception as e:
            logger.error(f"Chat error for user {user_id}: {e}")
            error_response = (
                "I apologize, but I encountered an error processing your request. "
                "Please try again or rephrase your question."
            )
            return ChatResponse(
                response=error_response,
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def get_history(self, user_id: str) -> ChatHistory:
        """Get chat history for a user."""
        try:
            user_oid = ObjectId(user_id)
        except:
            user_oid = user_id
        
        cursor = self.db.chat_history.find(
            {"user_id": user_oid}
        ).sort("timestamp", 1)
        
        messages = []
        async for doc in cursor:
            messages.append(ChatMessage(
                role=doc.get("role", "assistant"),
                content=doc.get("content", ""),
                timestamp=doc.get("timestamp", "")
            ))
        
        return ChatHistory(messages=messages)
    
    async def clear_history(self, user_id: str) -> bool:
        """Clear chat history for a user."""
        try:
            user_oid = ObjectId(user_id)
        except:
            user_oid = user_id
        
        result = await self.db.chat_history.delete_many({"user_id": user_oid})
        logger.info(f"Cleared {result.deleted_count} messages for user {user_id}")
        return True
    
    async def _save_message(
        self,
        user_id: str,
        role: MessageRole,
        content: str,
        timestamp: str
    ) -> None:
        """Save a message to chat history."""
        try:
            user_oid = ObjectId(user_id)
        except:
            user_oid = user_id
        
        await self.db.chat_history.insert_one({
            "user_id": user_oid,
            "role": role.value,
            "content": content,
            "timestamp": timestamp,
            "created_at": datetime.utcnow()
        })
    
    async def _get_user_financial_context(
        self,
        user_id: str,
        include_stock_recommendations: bool = False,
        user_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get summarized financial context for the user."""
        try:
            dashboard = await self.finance_service.get_dashboard(user_id)
            
            # Helper to safely format numbers
            def fmt(val):
                try:
                    return f"₹{float(val):,.0f}"
                except (ValueError, TypeError):
                    return f"₹{val}" if val else "₹0"
            
            # Build context dictionary
            context = {
                "total_income": fmt(dashboard.total_income),
                "total_expenses": fmt(dashboard.total_expenses),
                "total_investments": fmt(dashboard.total_investments),
                "total_loans": fmt(dashboard.total_loans),
                "net_worth": fmt(dashboard.net_worth),
                "monthly_income": fmt(dashboard.monthly_summary.income),
                "monthly_expenses": fmt(dashboard.monthly_summary.expenses),
                "monthly_savings": fmt(dashboard.monthly_summary.savings)
            }
            
            # Calculate savings rate (safely convert to float)
            try:
                monthly_income = float(dashboard.monthly_summary.income or 0)
                monthly_savings = float(dashboard.monthly_summary.savings or 0)
            except (ValueError, TypeError):
                monthly_income = 0
                monthly_savings = 0
            
            if monthly_income > 0:
                savings_rate = (monthly_savings / monthly_income) * 100
                context["savings_rate"] = f"{savings_rate:.1f}%"
            
            # Add stock recommendations if requested
            if include_stock_recommendations:
                # Determine risk profile based on savings rate
                savings_pct = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
                if savings_pct >= 40:
                    risk_profile = "aggressive"
                elif savings_pct >= 20:
                    risk_profile = "moderate"
                else:
                    risk_profile = "conservative"
                
                # Safely convert portfolio values to float
                try:
                    total_inv = float(dashboard.total_investments or 0)
                except (ValueError, TypeError):
                    total_inv = 0
                
                portfolio = {
                    "total_investments": total_inv,
                    "monthly_savings": monthly_savings
                }
                
                # Fetch real-time stock recommendations
                stock_recommendations = await market_data.get_stock_recommendations(
                    portfolio=portfolio,
                    risk_profile=risk_profile,
                    query=user_query
                )
                context["stock_recommendations"] = stock_recommendations
                context["risk_profile"] = risk_profile
            
            return context
            
        except Exception as e:
            logger.warning(f"Could not get financial context for user {user_id}: {e}")
            return {}
    
    def _detect_query_intent(self, message: str) -> Dict[str, Any]:
        """
        Detect the intent of the user's query to optimize RAG retrieval.
        Returns categories and keywords for better context retrieval.
        """
        message_lower = message.lower()
        
        intent = {
            "categories": [],
            "keywords": [],
            "requires_calculation": False,
            "calculation_type": None
        }
        
        # Investment-related keywords
        investment_keywords = [
            "invest", "mutual fund", "sip", "portfolio",
            "equity", "debt fund", "returns", "cagr"
        ]
        if any(kw in message_lower for kw in investment_keywords):
            intent["categories"].append("investment")
            intent["keywords"].extend(["investment", "returns", "portfolio"])
        
        # Stock-specific keywords
        stock_keywords = [
            "stock", "share", "nifty", "sensex", "equity", "trading",
            "buy stock", "which stock", "best stock", "recommend stock",
            "stock recommendation", "invest in stock"
        ]
        if any(kw in message_lower for kw in stock_keywords):
            intent["categories"].append("stock")
            intent["keywords"].extend(["stock", "equity", "shares"])
            intent["requires_stock_recommendations"] = True
        
        # Loan-related keywords
        loan_keywords = [
            "loan", "emi", "mortgage", "debt", "borrow", "interest rate",
            "repayment", "prepayment", "principal"
        ]
        if any(kw in message_lower for kw in loan_keywords):
            intent["categories"].append("loan")
            intent["keywords"].extend(["loan", "emi", "debt"])
            
            # Check if EMI calculation needed
            if "calculate" in message_lower or "how much" in message_lower:
                intent["requires_calculation"] = True
                intent["calculation_type"] = "emi"
        
        # Tax-related keywords
        tax_keywords = [
            "tax", "80c", "80d", "deduction", "elss", "ppf",
            "nps", "tax saving", "income tax"
        ]
        if any(kw in message_lower for kw in tax_keywords):
            intent["categories"].append("tax")
            intent["keywords"].extend(["tax", "deduction", "saving"])
        
        # Insurance-related keywords
        insurance_keywords = [
            "insurance", "policy", "premium", "coverage", "term",
            "health insurance", "life insurance"
        ]
        if any(kw in message_lower for kw in insurance_keywords):
            intent["categories"].append("insurance")
            intent["keywords"].extend(["insurance", "coverage"])
        
        # Savings-related keywords
        savings_keywords = [
            "save", "saving", "emergency fund", "budget", "expense"
        ]
        if any(kw in message_lower for kw in savings_keywords):
            intent["categories"].append("savings")
            intent["categories"].append("budgeting")
            intent["keywords"].extend(["savings", "budget"])
        
        # Retirement-related keywords
        retirement_keywords = [
            "retire", "retirement", "pension", "nps", "epf"
        ]
        if any(kw in message_lower for kw in retirement_keywords):
            intent["categories"].append("retirement")
            intent["keywords"].extend(["retirement", "pension"])
        
        # Goal-related keywords
        goal_keywords = [
            "goal", "target", "plan", "achieve", "save for"
        ]
        if any(kw in message_lower for kw in goal_keywords):
            intent["requires_calculation"] = True
            intent["calculation_type"] = "goal"
        
        # SIP calculation
        if "sip" in message_lower and ("calculate" in message_lower or "return" in message_lower):
            intent["requires_calculation"] = True
            intent["calculation_type"] = "sip"
        
        return intent
    
    async def _perform_calculations(
        self,
        message: str,
        query_intent: Dict[str, Any],
        financial_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Perform any necessary financial calculations based on query intent.
        """
        if not query_intent.get("requires_calculation"):
            return None
        
        calc_type = query_intent.get("calculation_type")
        results = {}
        
        try:
            if calc_type == "emi":
                # Try to extract loan parameters from message
                params = self._extract_loan_params(message)
                if params:
                    emi_result = financial_rules.calculate_emi(
                        principal=params.get("principal", 0),
                        annual_rate=params.get("rate", 10),
                        tenure_months=params.get("tenure", 12)
                    )
                    results = {
                        "calculation_type": "EMI Calculation",
                        **emi_result
                    }
            
            elif calc_type == "sip":
                # Try to extract SIP parameters
                params = self._extract_sip_params(message)
                if params:
                    sip_result = financial_rules.calculate_sip_returns(
                        monthly_investment=params.get("monthly", 5000),
                        annual_rate=params.get("rate", 12),
                        years=params.get("years", 10)
                    )
                    results = {
                        "calculation_type": "SIP Returns Projection",
                        **sip_result
                    }
            
            elif calc_type == "goal":
                # Calculate goal feasibility
                params = self._extract_goal_params(message)
                if params:
                    goal_result = financial_rules.calculate_goal_feasibility(
                        target_amount=params.get("target", 1000000),
                        current_savings=params.get("current", 0),
                        monthly_contribution=params.get("monthly", 10000),
                        years_remaining=params.get("years", 5)
                    )
                    results = {
                        "calculation_type": "Goal Feasibility Analysis",
                        **goal_result
                    }
        
        except Exception as e:
            logger.warning(f"Calculation error: {e}")
        
        return results if results else None
    
    def _extract_loan_params(self, message: str) -> Optional[Dict[str, float]]:
        """Extract loan parameters from message text."""
        import re
        
        params = {}
        
        # Extract principal amount
        principal_patterns = [
            r'(?:loan|borrow|principal).*?(?:rs\.?|₹|inr)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|l)?',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|l)?\s*(?:loan|rs|₹)',
        ]
        for pattern in principal_patterns:
            match = re.search(pattern, message.lower())
            if match:
                amount = float(match.group(1).replace(',', ''))
                if 'lakh' in message.lower() or 'lac' in message.lower():
                    amount *= 100000
                params['principal'] = amount
                break
        
        # Extract interest rate
        rate_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:%|percent|per\s*cent)',
            r'(?:rate|interest).*?(\d+(?:\.\d+)?)',
        ]
        for pattern in rate_patterns:
            match = re.search(pattern, message.lower())
            if match:
                params['rate'] = float(match.group(1))
                break
        
        # Extract tenure
        tenure_patterns = [
            r'(\d+)\s*(?:year|yr)',
            r'(\d+)\s*(?:month)',
        ]
        for pattern in tenure_patterns:
            match = re.search(pattern, message.lower())
            if match:
                tenure = int(match.group(1))
                if 'year' in message.lower() or 'yr' in message.lower():
                    tenure *= 12
                params['tenure'] = tenure
                break
        
        return params if params else None
    
    def _extract_sip_params(self, message: str) -> Optional[Dict[str, float]]:
        """Extract SIP parameters from message text."""
        import re
        
        params = {}
        
        # Extract monthly amount
        amount_patterns = [
            r'(?:sip|invest|monthly).*?(?:rs\.?|₹|inr)?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:per\s*month|monthly|pm)',
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, message.lower())
            if match:
                params['monthly'] = float(match.group(1).replace(',', ''))
                break
        
        # Extract expected return rate
        rate_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:%|percent)\s*(?:return|growth)',
            r'(?:return|expect).*?(\d+(?:\.\d+)?)\s*%',
        ]
        for pattern in rate_patterns:
            match = re.search(pattern, message.lower())
            if match:
                params['rate'] = float(match.group(1))
                break
        
        # Extract years
        year_pattern = r'(\d+)\s*(?:year|yr)'
        match = re.search(year_pattern, message.lower())
        if match:
            params['years'] = int(match.group(1))
        
        return params if params else None
    
    def _extract_goal_params(self, message: str) -> Optional[Dict[str, float]]:
        """Extract goal planning parameters from message text."""
        import re
        
        params = {}
        
        # Extract target amount
        target_patterns = [
            r'(?:target|goal|need|want).*?(?:rs\.?|₹|inr)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|l|cr|crore)?',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|l|cr|crore)',
        ]
        for pattern in target_patterns:
            match = re.search(pattern, message.lower())
            if match:
                amount = float(match.group(1).replace(',', ''))
                if 'lakh' in message.lower() or 'lac' in message.lower():
                    amount *= 100000
                elif 'cr' in message.lower() or 'crore' in message.lower():
                    amount *= 10000000
                params['target'] = amount
                break
        
        # Extract years
        year_pattern = r'(\d+)\s*(?:year|yr)'
        match = re.search(year_pattern, message.lower())
        if match:
            params['years'] = int(match.group(1))
        
        return params if params else None
