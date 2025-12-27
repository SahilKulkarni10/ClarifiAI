"""
Multi-LLM Service
Integration with Ollama (primary) and Google Gemini (fallback).
The LLM is used ONLY for explanation and communication, NOT for financial calculations.
"""

from typing import Optional, Dict, Any, List
from loguru import logger
from enum import Enum
import httpx

# Check if Ollama server is available (we'll use httpx instead of ollama library)
OLLAMA_AVAILABLE = True  # Will be verified during initialization

# Gemini client
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not available. LLM features will be limited.")

from app.core.config import settings


class LLMProvider(str, Enum):
    """Available LLM providers."""
    OLLAMA = "ollama"
    GEMINI = "gemini"
    FALLBACK = "fallback"


class QueryComplexity(str, Enum):
    """Query complexity classification for model selection."""
    FAST = "fast"  # Use phi3:mini
    DETAILED = "detailed"  # Use llama3.1:8b


class MultiLLMService:
    """
    Service for interacting with multiple LLM providers.
    
    Priority: Ollama (phi3:mini/llama3.1:8b) → Gemini → Fallback
    
    Important: The LLM is used ONLY for:
    - Explaining financial concepts
    - Providing context to pre-calculated results
    - Generating user-friendly responses
    
    All financial calculations are done in financial_rules.py
    """
    
    def __init__(self):
        self.ollama_base_url = getattr(settings, 'ollama_base_url', 'http://localhost:11434')
        self.gemini_model = None
        self.active_provider: LLMProvider = LLMProvider.FALLBACK
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize LLM providers in priority order: Ollama → Gemini → Fallback."""
        if self._initialized:
            return
        
        global OLLAMA_AVAILABLE
        
        # Try Ollama first (primary) - use httpx to check connection
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_base_url}/api/tags")
                if response.status_code == 200:
                    self.active_provider = LLMProvider.OLLAMA
                    logger.info(f"✓ Ollama initialized: {settings.ollama_fast_model} (fast), {settings.ollama_detailed_model} (detailed)")
                    self._initialized = True
                    return
        except Exception as e:
            OLLAMA_AVAILABLE = False
            logger.warning(f"Ollama connection failed: {e}. Trying Gemini...")
        
        # Fall back to Gemini
        if GEMINI_AVAILABLE and settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                
                generation_config = {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 4096,
                }
                
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
                ]
                
                self.gemini_model = genai.GenerativeModel(
                    model_name=settings.gemini_model,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                
                self.active_provider = LLMProvider.GEMINI
                logger.info(f"✓ Gemini initialized: {settings.gemini_model} (fallback)")
                self._initialized = True
                return
                
            except Exception as e:
                logger.error(f"Gemini initialization failed: {e}")
        
        # Use fallback mode
        self.active_provider = LLMProvider.FALLBACK
        logger.warning("⚠ Using fallback responses (no LLM provider available)")
        self._initialized = True
    
    def _classify_query_complexity(self, user_query: str) -> QueryComplexity:
        """
        Classify query complexity to select appropriate Ollama model.
        
        FAST (phi3:mini): Quick lookups, simple lists, calculations
        DETAILED (llama3.1:8b): Deep analysis, explanations, planning
        """
        query_lower = user_query.lower()
        
        # Keywords for detailed analysis
        detailed_keywords = [
            "explain", "why", "how", "analyze", "compare", "strategy",
            "plan", "detail", "comprehensive", "breakdown", "advice",
            "tax planning", "retirement", "portfolio", "diversify"
        ]
        
        # Keywords for fast responses
        fast_keywords = [
            "list", "show", "what are", "recommend stocks", "top stocks",
            "emi", "calculate", "price", "current", "quick"
        ]
        
        # Check for detailed keywords
        if any(keyword in query_lower for keyword in detailed_keywords):
            return QueryComplexity.DETAILED
        
        # Check for fast keywords
        if any(keyword in query_lower for keyword in fast_keywords):
            return QueryComplexity.FAST
        
        # Default to fast for concise responses
        return QueryComplexity.FAST
    
    def _build_system_prompt(self) -> str:
        """Build a concise system prompt for the financial advisor persona."""
        return """You are ClariFi AI, a helpful financial assistant for Indian investors.

IMPORTANT RULES:
✓ When specific STOCKS are provided with prices/P/E ratios, ALWAYS recommend those exact stocks
✓ Use stock symbols (e.g., RELIANCE, TCS) with current prices
✓ Complete your response fully - don't cut off mid-sentence
✓ Be clear, concise, and actionable
✓ Use ₹ for Indian currency
✓ Use bullet points for lists

FOR STOCK QUESTIONS:
- Recommend the SPECIFIC stocks provided in the data
- Include: Symbol, Name, Price, P/E ratio, Sector
- Explain WHY each stock is recommended
- Suggest portfolio allocation percentages
- Mention SIP amounts if provided
- DON'T give generic mutual fund advice when stocks are requested

FOR OTHER FINANCIAL QUESTIONS:
- Tax: Mention sections (80C, 80D, 24)
- Loans/EMI: Show calculations
- Investments: Match risk profile
- Savings: Practical targets

Always be friendly and end with actionable advice."""
    
    def _build_context_prompt(
        self,
        user_query: str,
        rag_context: Optional[str] = None,
        financial_data: Optional[Dict[str, Any]] = None,
        calculated_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build a concise prompt with essential context only."""
        
        # Helper to safely format numbers
        def safe_fmt(val):
            try:
                num = float(str(val).replace('₹', '').replace(',', ''))
                return f"₹{num:,.0f}"
            except (ValueError, TypeError):
                return str(val) if val else "N/A"
        
        prompt_parts = []
        query_lower = user_query.lower()
        
        # Check if this is a stock query
        is_stock_query = any(kw in query_lower for kw in ["stock", "share", "invest", "buy", "recommend"])
        
        # Add brief context if available (only if NOT a stock query)
        if rag_context and not is_stock_query:
            # Trim RAG context to 300 chars for speed
            trimmed_rag = rag_context[:300] + "..." if len(rag_context) > 300 else rag_context
            prompt_parts.append(f"Context: {trimmed_rag}\n")
        
        # Add essential financial data only
        if financial_data:
            # Risk profile is important for stocks
            if financial_data.get("risk_profile") and is_stock_query:
                prompt_parts.append(f"User's risk profile: {financial_data['risk_profile']}")
            
            # Income if available
            if financial_data.get("monthly_income"):
                prompt_parts.append(f"Monthly income: {financial_data['monthly_income']}")
            
            # Stock recommendations (OPTIMIZED FORMAT)
            if "stock_recommendations" in financial_data and is_stock_query:
                stock_recs = financial_data["stock_recommendations"]
                if stock_recs.get("recommended_stocks"):
                    prompt_parts.append("\n📊 REAL-TIME STOCK RECOMMENDATIONS (use these exact stocks):\n")
                    for i, stock in enumerate(stock_recs["recommended_stocks"][:5], 1):
                        symbol = stock.get("symbol", "")
                        name = stock.get("name", "")
                        price = stock.get("current_price", 0)
                        pe = stock.get("pe_ratio")
                        change = stock.get("change_percent", 0)
                        sector = stock.get("sector", "")
                        reason = stock.get("recommendation_reason", "")
                        
                        # Format concisely
                        try:
                            price_str = f"₹{float(price):,.0f}" if price else "N/A"
                        except (ValueError, TypeError):
                            price_str = str(price) if price else "N/A"
                        try:
                            pe_str = f"{float(pe):.1f}" if pe else "N/A"
                        except (ValueError, TypeError):
                            pe_str = "N/A"
                        try:
                            change_str = f"{float(change):+.1f}%" if change else "0.0%"
                        except (ValueError, TypeError):
                            change_str = "0.0%"
                        
                        prompt_parts.append(
                            f"{i}. {symbol} ({name})\n"
                            f"   Price: {price_str} ({change_str} today)\n"
                            f"   P/E: {pe_str} | Sector: {sector}\n"
                            f"   Why: {reason}\n"
                        )
                    
                    # Add allocation if available
                    if stock_recs.get("allocation_suggestion"):
                        alloc = stock_recs["allocation_suggestion"]
                        alloc_str = ", ".join([f"{v}% {k.replace('_', ' ')}" for k, v in alloc.items()])
                        prompt_parts.append(f"\nSuggested Portfolio: {alloc_str}")
                    
                    # Add SIP suggestion
                    if stock_recs.get("sip_suggestion"):
                        sip = stock_recs["sip_suggestion"]
                        sip_amount = safe_fmt(sip.get('amount', 0))
                        prompt_parts.append(f"\nSIP Recommendation: {sip_amount}/month for systematic investing")
        
        # Add pre-calculated results if available
        if calculated_results:
            prompt_parts.append("\nCalculations:")
            for key, value in list(calculated_results.items())[:5]:  # Limit to 5 items
                prompt_parts.append(f"• {key}: {value}")
        
        # Add user query with clear instructions
        prompt_parts.append(f"\n\nQuestion: {user_query}")
        
        if is_stock_query:
            prompt_parts.append("\n⚠️ IMPORTANT: Recommend the SPECIFIC stocks listed above (with symbols, prices, P/E). Don't give generic mutual fund advice.")
        
        prompt_parts.append("\nProvide a complete, helpful answer:")
        
        return "\n".join(prompt_parts)
    
    async def generate_response(
        self,
        user_query: str,
        rag_context: Optional[str] = None,
        financial_data: Optional[Dict[str, Any]] = None,
        calculated_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response to a user query using the best available LLM.
        
        Args:
            user_query: The user's question
            rag_context: Retrieved context from knowledge base
            financial_data: User's financial data for context
            calculated_results: Pre-calculated results from financial rules engine
            
        Returns:
            Generated response string
        """
        await self.initialize()
        
        # Build the complete prompt
        prompt = self._build_context_prompt(
            user_query,
            rag_context,
            financial_data,
            calculated_results
        )
        
        # Try providers in order: Ollama → Gemini → Fallback
        if self.active_provider == LLMProvider.OLLAMA or OLLAMA_AVAILABLE:
            response = await self._generate_ollama_response(prompt, user_query)
            if response:
                return response
            # If Ollama fails, try Gemini if available
            if GEMINI_AVAILABLE and settings.gemini_api_key:
                logger.warning("Ollama failed, trying Gemini...")
            else:
                logger.warning("Ollama failed, no Gemini configured, using fallback...")
                return self._generate_fallback_response(user_query, rag_context, financial_data, calculated_results)
        
        if (self.active_provider == LLMProvider.GEMINI or GEMINI_AVAILABLE) and settings.gemini_api_key:
            response = await self._generate_gemini_response(prompt)
            if response:
                return response
            # If Gemini fails, use fallback
            logger.warning("Gemini failed, using fallback...")
        
        # Fallback response
        return self._generate_fallback_response(
            user_query, rag_context, financial_data, calculated_results
        )
    
    async def _generate_ollama_response(self, prompt: str, user_query: str) -> Optional[str]:
        """Generate response using Ollama models via HTTP API with proper timeout."""
        if not OLLAMA_AVAILABLE:
            return None
        
        try:
            # Select model based on query complexity
            complexity = self._classify_query_complexity(user_query)
            model = (
                settings.ollama_detailed_model if complexity == QueryComplexity.DETAILED
                else settings.ollama_fast_model
            )
            
            logger.info(f"Using Ollama model: {model} ({complexity.value})")
            
            # Truncate prompt if too long (phi3:mini has 4k context)
            # More aggressive truncation for faster responses
            max_prompt_chars = 1200 if complexity == QueryComplexity.FAST else 3000
            if len(prompt) > max_prompt_chars:
                # Keep important parts, trim middle
                lines = prompt.split('\n')
                # Keep first 10 lines (system + stock data) and last 4 lines (question)
                header = '\n'.join(lines[:10])
                footer = '\n'.join(lines[-4:])
                prompt = header + "\n\n[Additional context trimmed]\n\n" + footer
                logger.info(f"Prompt trimmed to {len(prompt)} chars for faster response")
            
            # Timeout: 90s for fast, 120s for detailed
            timeout = 90.0 if complexity == QueryComplexity.FAST else 120.0
            
            # Use httpx for proper async timeout handling
            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=5.0)) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": f"You are ClariFi AI, a helpful financial advisor for Indian investors. Be concise.\n\n{prompt}",
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "num_predict": 500 if complexity == QueryComplexity.FAST else 800,  # Increased for complete responses
                            "num_ctx": 2048,
                            "num_thread": 8,  # Increased threads for faster generation
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("response", "").strip()
                    
                    if response_text:
                        logger.info(f"Ollama response: {len(response_text)} chars")
                        return response_text
            
            return None
            
        except httpx.TimeoutException:
            logger.error(f"Ollama timeout after {timeout}s - model may be overloaded. Consider using smaller model or increasing timeout.")
            return None
        except httpx.ConnectError as e:
            logger.error(f"Ollama connection error: {e}. Check if Ollama is running.")
            return None
        except Exception as e:
            logger.error(f"Ollama generation error: {type(e).__name__}: {e}")
            return None

    async def _generate_gemini_response(self, prompt: str) -> Optional[str]:
        """Generate response using Gemini."""
        if not self.gemini_model:
            return None
        
        try:
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                response_text = response.text.strip()
                
                # Validate response completeness
                if self._is_response_complete(response_text):
                    return response_text
                else:
                    logger.warning("Gemini response appears incomplete")
                    return None
            
            return None
            
        except Exception as e:
            # Check if it's a quota/rate limit error
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str or "rate limit" in error_str:
                logger.error(f"Gemini quota exceeded: {e}")
                logger.warning("Gemini API quota exhausted. Using fallback. Please check your billing/usage at https://ai.dev/usage")
            else:
                logger.error(f"Gemini generation error: {e}")
            return None
    
    def _is_response_complete(self, response_text: str) -> bool:
        """Check if response appears complete (not truncated)."""
        if not response_text:
            return False
        
        # Check for incomplete endings
        incomplete_endings = (',', 'with', 'and', 'the', 'a', 'for', 'to', 'of', 'in', 'is', 'are', 'that', 'which', ':', '-')
        last_word = response_text.rstrip().split()[-1].lower() if response_text.split() else ""
        
        if last_word in incomplete_endings or response_text.endswith((',', ':')):
            return False
        
        return True
    
    def _generate_fallback_response(
        self,
        user_query: str,
        rag_context: Optional[str] = None,
        financial_data: Optional[Dict[str, Any]] = None,
        calculated_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a complete response when all LLMs fail."""
        
        # Helper to safely format numbers
        def fmt_num(val, default=0):
            try:
                return float(val) if val is not None else default
            except (ValueError, TypeError):
                return default
        
        response_parts = []
        query_lower = user_query.lower() if user_query else ""
        
        # Check if this is a stock query and we have stock recommendations
        if financial_data and "stock_recommendations" in financial_data:
            stock_recs = financial_data["stock_recommendations"]
            risk_profile = financial_data.get("risk_profile", "moderate")
            
            response_parts.append(f"Based on your {risk_profile} risk profile, here are stocks to consider:\n")
            
            if stock_recs.get("recommended_stocks"):
                for stock in stock_recs["recommended_stocks"][:5]:
                    symbol = stock.get("symbol", "")
                    name = stock.get("name", "")
                    price = fmt_num(stock.get("current_price", 0))
                    pe = stock.get("pe_ratio")
                    pe_str = f"{fmt_num(pe):.0f}" if pe else "N/A"
                    reason = stock.get("recommendation_reason", "Strong fundamentals")
                    
                    response_parts.append(f"• {symbol} ({name}) - ₹{price:,.0f}, P/E: {pe_str}, {reason}")
            
            if stock_recs.get("allocation_suggestion"):
                alloc = stock_recs["allocation_suggestion"]
                alloc_str = ", ".join([f"{v}% {k.replace('_', ' ')}" for k, v in alloc.items()])
                response_parts.append(f"\nSuggested Allocation: {alloc_str}")
            
            if stock_recs.get("sip_suggestion"):
                sip = stock_recs["sip_suggestion"]
                sip_amount = fmt_num(sip.get('amount', 0))
                response_parts.append(f"\nAlso consider: SIP of ₹{sip_amount:,.0f}/month for systematic investing.")
            
            return "\n".join(response_parts)
        
        # Handle calculated results (EMI, tax, goals, etc.)
        if calculated_results:
            if "emi" in query_lower or "loan" in query_lower:
                response_parts.append("Here's your loan calculation:\n")
            elif "tax" in query_lower:
                response_parts.append("Here's your tax analysis:\n")
            elif "goal" in query_lower or "save" in query_lower:
                response_parts.append("Here's your goal planning:\n")
            else:
                response_parts.append("Based on my calculations:\n")
            
            for key, value in calculated_results.items():
                formatted_key = key.replace('_', ' ').title()
                try:
                    num_val = float(value)
                    if num_val > 1000:
                        response_parts.append(f"• {formatted_key}: ₹{num_val:,.0f}")
                    else:
                        response_parts.append(f"• {formatted_key}: {value}")
                except (ValueError, TypeError):
                    response_parts.append(f"• {formatted_key}: {value}")
            
            return "\n".join(response_parts)
        
        # Handle financial context based response
        if financial_data:
            response_parts.append("Based on your financial profile:\n")
            
            # Show key metrics
            for key in ["monthly_income", "monthly_expenses", "monthly_savings", "savings_rate", "net_worth"]:
                if key in financial_data:
                    formatted_key = key.replace('_', ' ').title()
                    response_parts.append(f"• {formatted_key}: {financial_data[key]}")
            
            # Add general advice based on query type
            if "save" in query_lower or "budget" in query_lower:
                response_parts.append("\nTip: Aim to save at least 20-30% of your monthly income.")
            elif "invest" in query_lower:
                response_parts.append("\nTip: Diversify across equity, debt, and gold based on your risk profile.")
            elif "retire" in query_lower:
                response_parts.append("\nTip: Start early with NPS and PPF for tax-efficient retirement savings.")
            
            return "\n".join(response_parts)
        
        # Use RAG context if available
        if rag_context:
            response_parts.append("Here's what I found:\n")
            sentences = rag_context.split('.')[:4]
            response_parts.append('. '.join(sentences) + '.')
            return "\n".join(response_parts)
        
        # Generic fallback
        return "I can help you with financial questions about investments, taxes, loans, savings, and more. Could you please provide more details about what you'd like to know?"
    
    async def generate_recommendation(
        self,
        recommendation_type: str,
        user_data: Dict[str, Any],
        calculated_results: Dict[str, Any],
        rag_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured financial recommendation.
        
        Returns:
            Dictionary with recommendation details
        """
        await self.initialize()
        
        prompt = f"""Based on the following information, generate a structured financial recommendation:

RECOMMENDATION TYPE: {recommendation_type}

USER DATA:
{self._format_dict(user_data)}

CALCULATED RESULTS (use these exact numbers):
{self._format_dict(calculated_results)}

RELEVANT KNOWLEDGE:
{rag_context or 'No additional context available'}

Please provide a response in the following format:
1. SUMMARY: A one-sentence summary of the recommendation
2. EXPLANATION: Detailed explanation (2-3 paragraphs)
3. ACTION ITEMS: List of specific actions the user should take
4. ASSUMPTIONS: List any assumptions made
5. CAVEATS: Any limitations or warnings

Remember: Use only the provided calculated results. Do not invent new numbers."""

        try:
            # Try Ollama first (use detailed model for recommendations)
            if self.active_provider == LLMProvider.OLLAMA:
                try:
                    response = ollama.chat(
                        model=settings.ollama_detailed_model,
                        messages=[{'role': 'user', 'content': prompt}],
                        options={'temperature': 0.7, 'num_predict': 1024}
                    )
                    if response and 'message' in response:
                        generated_text = response['message']['content']
                    else:
                        generated_text = ""
                except Exception as e:
                    logger.error(f"Ollama recommendation error: {e}")
                    generated_text = ""
            
            # Try Gemini if Ollama failed
            elif self.gemini_model:
                try:
                    response = self.gemini_model.generate_content(prompt)
                    generated_text = response.text if response and response.text else ""
                except Exception as e:
                    logger.error(f"Gemini recommendation error: {e}")
                    generated_text = ""
            else:
                generated_text = ""
            
            # Parse the response into structured format
            return self._parse_recommendation_response(
                generated_text,
                recommendation_type,
                calculated_results
            )
            
        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            return {
                "summary": f"Based on the analysis, here are recommendations for {recommendation_type}",
                "explanation": "Please review the calculated results for details.",
                "action_items": ["Review the provided calculations", "Consider consulting a financial advisor"],
                "assumptions": list(calculated_results.get("assumptions", [])),
                "data_sources": ["User-provided financial data"],
                "calculated_results": calculated_results
            }
    
    def _format_dict(self, d: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary for prompt."""
        lines = []
        prefix = "  " * indent
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._format_dict(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}: {', '.join(str(v) for v in value)}")
            else:
                lines.append(f"{prefix}{key}: {value}")
        return '\n'.join(lines)
    
    def _parse_recommendation_response(
        self,
        response_text: str,
        recommendation_type: str,
        calculated_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse LLM response into structured recommendation."""
        # Default structure
        result = {
            "type": recommendation_type,
            "summary": "",
            "explanation": "",
            "action_items": [],
            "assumptions": [],
            "caveats": [],
            "calculated_results": calculated_results
        }
        
        if not response_text:
            return result
        
        # Simple parsing logic
        current_section = None
        sections = {
            "SUMMARY": "summary",
            "EXPLANATION": "explanation",
            "ACTION ITEMS": "action_items",
            "ASSUMPTIONS": "assumptions",
            "CAVEATS": "caveats"
        }
        
        lines = response_text.split('\n')
        buffer = []
        
        for line in lines:
            line_upper = line.upper().strip()
            
            # Check if this is a section header
            matched_section = None
            for header, field in sections.items():
                if header in line_upper:
                    matched_section = field
                    break
            
            if matched_section:
                # Save previous section
                if current_section and buffer:
                    content = '\n'.join(buffer).strip()
                    if current_section in ["action_items", "assumptions", "caveats"]:
                        # Parse as list
                        items = [
                            item.lstrip('•-*123456789. ')
                            for item in content.split('\n')
                            if item.strip()
                        ]
                        result[current_section] = items
                    else:
                        result[current_section] = content
                
                current_section = matched_section
                buffer = []
            else:
                buffer.append(line)
        
        # Save last section
        if current_section and buffer:
            content = '\n'.join(buffer).strip()
            if current_section in ["action_items", "assumptions", "caveats"]:
                items = [
                    item.lstrip('•-*123456789. ')
                    for item in content.split('\n')
                    if item.strip()
                ]
                result[current_section] = items
            else:
                result[current_section] = content
        
        # Fallback if no sections found
        if not result["summary"] and not result["explanation"]:
            result["explanation"] = response_text
            result["summary"] = response_text[:200] + "..." if len(response_text) > 200 else response_text
        
        return result


# Global instance
llm_service = MultiLLMService()
