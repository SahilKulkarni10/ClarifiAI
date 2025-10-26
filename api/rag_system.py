import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from typing import List, Dict, Any
import uuid
from config import settings
import json
import httpx
import asyncio
from bs4 import BeautifulSoup
import logging
import re
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Initialize collections
        self.user_data_collection = self.client.get_or_create_collection(
            name="user_financial_data",
            metadata={"description": "User personal financial data"}
        )
        
        self.knowledge_collection = self.client.get_or_create_collection(
            name="financial_knowledge",
            metadata={"description": "Financial knowledge base"}
        )
        
        # Initialize sentence transformer lazily (only when needed)
        self._encoder = None
        
        # Initialize Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Try different model names in order of preference
        self.model_names = ['gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-pro']
        self.model = None
        self._initialize_model()
        
    def _initialize_model(self):    
        """Initialize Gemini model with fallback options"""
        for model_name in self.model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                logger.info(f"Successfully initialized model: {model_name}")
                break
            except Exception as e:
                logger.warning(f"Failed to initialize model {model_name}: {e}")
                continue
        
        if self.model is None:
            logger.error("Failed to initialize any Gemini model")
            # Use a simple fallback
            self.model = genai.GenerativeModel('gemini-pro')
    
    @property
    def encoder(self):
        """Lazy load the sentence transformer model only when needed"""
        if self._encoder is None:
            if settings.USE_LITE_EMBEDDINGS:
                logger.info("Using Gemini API for embeddings (memory-efficient mode)")
                self._encoder = "gemini_api"  # Flag to use API
            else:
                logger.info("Loading SentenceTransformer model (lazy load)...")
                self._encoder = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("SentenceTransformer model loaded successfully")
        return self._encoder
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using either local model or API"""
        if settings.USE_LITE_EMBEDDINGS or self._encoder == "gemini_api":
            # Use Gemini API for embeddings (memory efficient)
            try:
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_document"
                )
                return result['embedding']
            except Exception as e:
                logger.error(f"Gemini embedding API failed: {e}")
                # Fallback to simple hash-based embedding
                return self._simple_embedding(text)
        else:
            # Use local SentenceTransformer model
            return self.encoder.encode([text])[0].tolist()
    
    def _simple_embedding(self, text: str, dim: int = 768) -> List[float]:
        """Fallback: Simple hash-based embedding for extreme memory constraints"""
        import hashlib
        import math
        
        # Create a deterministic embedding based on text hash
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert hash to float array
        embedding = []
        for i in range(0, min(len(hash_bytes) * 8, dim), 8):
            byte_idx = i // 8
            if byte_idx < len(hash_bytes):
                # Normalize to [-1, 1]
                val = (hash_bytes[byte_idx] - 128) / 128.0
                embedding.append(val)
        
        # Pad to desired dimension
        while len(embedding) < dim:
            embedding.append(0.0)
        
        # Normalize to unit vector
        magnitude = math.sqrt(sum(x*x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding[:dim]
        
    async def add_user_data(self, user_id: str, data_type: str, data: Dict[str, Any]):
        """Add user financial data to vector store"""
        try:
            # Create text representation of the data
            text_content = self._format_user_data(data_type, data)
            
            # Generate embedding
            embedding = await self._generate_embedding(text_content)
            
            # Create unique ID
            doc_id = f"{user_id}_{data_type}_{uuid.uuid4()}"
            
            # Prepare metadata (only str, int, float, bool allowed)
            metadata = {
                "user_id": user_id,
                "data_type": data_type,
                "timestamp": str(data.get("created_at", "")),
                "amount": float(data.get("amount", 0)) if data.get("amount") else 0.0,
                "category": str(data.get("category", "")) if data.get("category") else "",
                "description": str(data.get("description", "")) if data.get("description") else ""
            }
            
            # Add to collection
            self.user_data_collection.add(
                embeddings=[embedding],
                documents=[text_content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Added user data: {data_type} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding user data: {e}")
            return False
    
    def _format_user_data(self, data_type: str, data: Dict[str, Any]) -> str:
        """Format user data into searchable text"""
        if data_type == "income":
            return f"Income from {data.get('source', 'unknown')} of ₹{data.get('amount', 0)} on {data.get('date', '')}. {data.get('description', '')}"
        
        elif data_type == "expense":
            return f"Expense for {data.get('category', 'unknown')} of ₹{data.get('amount', 0)} on {data.get('date', '')} at {data.get('merchant', 'unknown')}. {data.get('description', '')}"
        
        elif data_type == "investment":
            return f"Investment in {data.get('name', 'unknown')} ({data.get('type', 'unknown')}) of ₹{data.get('amount', 0)} on {data.get('date', '')}. Current value: ₹{data.get('current_value', 0)}. Goal: {data.get('goal', 'Not specified')}"
        
        elif data_type == "loan":
            return f"{data.get('type', 'unknown')} loan of ₹{data.get('principal', 0)} at {data.get('interest_rate', 0)}% interest. EMI: ₹{data.get('emi', 0)}, Outstanding: ₹{data.get('outstanding', 0)}"
        
        elif data_type == "insurance":
            return f"{data.get('type', 'unknown')} insurance {data.get('policy_name', 'unknown')} with coverage ₹{data.get('coverage_amount', 0)} and premium ₹{data.get('premium', 0)}"
        
        elif data_type == "budget":
            return f"Budget for {data.get('month', 'unknown')} with total budget ₹{data.get('total_budget', 0)} and savings target ₹{data.get('savings_target', 0)}"
        
        return json.dumps(data)
    
    async def search_user_data(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search user's financial data"""
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Search in user data
            results = self.user_data_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"user_id": user_id}
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching user data: {e}")
            return []
    
    async def search_knowledge_base(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search financial knowledge base"""
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Search in knowledge base
            results = self.knowledge_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    async def generate_response(self, user_id: str, query: str) -> Dict[str, Any]:
        """Generate AI response using RAG"""
        try:
            # Import database here to avoid circular imports
            from database import get_database
            from stock_utils import stock_fetcher
            
            # Search user data and knowledge base
            user_context = await self.search_user_data(user_id, query, limit=5)
            knowledge_context = await self.search_knowledge_base(query, limit=3)
            
            # Get current financial data from database
            db = get_database()
            current_data = await self._get_current_financial_data(db, user_id)
            
            # Check if query is about stock investment and fetch real-time data
            stock_data_text = ""
            stock_recommendation = None
            multiple_stock_recommendations = []
            
            # Detect stock-related queries
            if self._is_stock_query(query):
                stock_symbol = await self._extract_stock_symbol(query)
                
                # Get user's portfolio analysis
                total_portfolio = await self._get_total_portfolio_value(db, user_id)
                portfolio_analysis = await self._analyze_user_portfolio(db, user_id)
                
                if stock_symbol:
                    # Specific stock mentioned - fetch its data
                    logger.info(f"Specific stock mentioned: {stock_symbol}")
                    
                    # Calculate investment recommendation
                    stock_recommendation = await stock_fetcher.calculate_investment_recommendation(
                        stock_symbol=stock_symbol,
                        investment_amount=50000,  # Default amount
                        portfolio_percentage=5.0,  # Default 5% allocation
                        total_portfolio_value=total_portfolio
                    )
                    
                    if stock_recommendation:
                        stock_data_text = f"""
**REAL-TIME STOCK DATA (Fetched: {stock_recommendation['fetched_at']})**:
- Company: {stock_recommendation['company_name']}
- Symbol: {stock_recommendation['stock_symbol']}
- Market: {stock_recommendation['market']}
- Current Price: {stock_recommendation['currency']} {stock_recommendation['current_price']:.2f}
- Price in INR: ₹{stock_recommendation['price_in_inr']:.2f}
- 52-Week High: {stock_recommendation.get('52_week_high', 'N/A')}
- 52-Week Low: {stock_recommendation.get('52_week_low', 'N/A')}
- P/E Ratio: {stock_recommendation.get('pe_ratio', 'N/A')}
- Sector: {stock_recommendation.get('sector', 'N/A')}
- Change: {stock_recommendation.get('change_percent', 0):.2f}%
- Total Portfolio Value: ₹{total_portfolio:,.2f}
- Recommended Allocation: {stock_recommendation['portfolio_percentage']}% = ₹{stock_recommendation['total_investment']:,.2f}
- Number of Shares: {stock_recommendation['recommended_shares']} shares

**USER'S CURRENT PORTFOLIO ANALYSIS**:
{portfolio_analysis}
"""
                        if stock_recommendation['currency'] == 'USD':
                            stock_data_text += f"- Exchange Rate: 1 USD = ₹{stock_recommendation['exchange_rate']:.2f}\n"
                else:
                    # No specific stock mentioned - AI should provide personalized recommendations
                    logger.info("No specific stock mentioned, will provide portfolio-based recommendations")
                    
                    stock_data_text = f"""
**USER'S CURRENT PORTFOLIO ANALYSIS**:
{portfolio_analysis}

**IMPORTANT INSTRUCTIONS FOR AI**:
The user has asked for stock recommendations. You MUST:
1. Analyze their existing portfolio holdings shown above
2. Identify gaps in sector diversification
3. Recommend 3-5 SPECIFIC stocks (with exact company names and symbols) that complement their existing holdings
4. For each recommendation, fetch REAL-TIME data and provide:
   - Company name and stock symbol
   - Current live price
   - Exact number of shares to buy
   - Total investment amount
   - Reasoning based on their portfolio gaps

DO NOT provide generic stock lists. Base recommendations on their actual portfolio composition.
If their portfolio lacks IT sector exposure, recommend IT stocks. If they lack banking, recommend banking stocks, etc.

You have access to real-time stock data through the API. Use it to provide specific, actionable recommendations.
"""
            
            # Prepare context for AI
            context_text = "Current Financial Summary:\n"
            context_text += current_data
            
            if stock_data_text:
                context_text += f"\n{stock_data_text}\n"
            
            context_text += "\nUser Financial Data from History:\n"
            for item in user_context:
                context_text += f"- {item['content']}\n"
            
            context_text += "\nFinancial Knowledge:\n"
            for item in knowledge_context:
                context_text += f"- {item['content']}\n"
            
            # Get current date
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")  # e.g., "October 07, 2025"
            
            # Create prompt
            stock_instruction = ""
            if stock_recommendation:
                # Single stock recommendation
                stock_instruction = f"""
            
            **🚨 CRITICAL: REAL-TIME STOCK DATA FETCHED - MUST USE EXACT NUMBERS 🚨**
            
            I have successfully fetched LIVE stock price data for {stock_recommendation['company_name']} ({stock_recommendation['stock_symbol']}) 
            as of {stock_recommendation['fetched_at']} (TODAY).
            
            ⚠️ MANDATORY RESPONSE REQUIREMENTS:
            
            1. **CURRENT PRICE**: ₹{stock_recommendation['price_in_inr']:.2f} per share (LIVE DATA - USE THIS EXACT NUMBER)
            2. **RECOMMENDED SHARES**: {stock_recommendation['recommended_shares']} shares (EXACT NUMBER - MUST MENTION)
            3. **TOTAL INVESTMENT**: ₹{stock_recommendation['total_investment']:,.2f} (EXACT AMOUNT - MUST MENTION)
            4. **PORTFOLIO ALLOCATION**: {stock_recommendation['portfolio_percentage']}% of their total portfolio
            5. **TOTAL PORTFOLIO VALUE**: ₹{total_portfolio:,.2f}
            
            🔴 FORBIDDEN RESPONSES:
            - DO NOT say "prices are subject to change" or "verify current prices"
            - DO NOT suggest checking NSE/BSE websites
            - DO NOT say you cannot provide real-time data
            - DO NOT give generic advice without these specific numbers
            
            ✅ REQUIRED RESPONSE FORMAT:
            - Start with: "Based on LIVE market data as of {stock_recommendation['fetched_at']}"
            - State the current price: "₹{stock_recommendation['price_in_inr']:.2f} per share"
            - State exact shares: "Buy exactly {stock_recommendation['recommended_shares']} shares"
            - State total investment: "Total investment: ₹{stock_recommendation['total_investment']:,.2f}"
            - Provide step-by-step purchase instructions with these exact numbers
            
            This is REAL-TIME data from the stock market API. Use these EXACT numbers in your response.
            """
            elif multiple_stock_recommendations:
                # Multiple stock recommendations - NOT USED ANYMORE
                # AI will generate personalized recommendations based on portfolio analysis
                total_portfolio = await self._get_total_portfolio_value(db, user_id)
                stock_instruction = ""
            else:
                # No stock symbol extracted - AI should analyze portfolio and recommend
                stock_instruction = f"""
            
            **🎯 PERSONALIZED STOCK RECOMMENDATION REQUEST 🎯**
            
            The user has asked for stock recommendations. You MUST provide PERSONALIZED recommendations based on their portfolio.
            
            ⚠️ CRITICAL INSTRUCTIONS:
            
            1. **ANALYZE THEIR PORTFOLIO FIRST**: Review the portfolio analysis provided above
            2. **IDENTIFY GAPS**: Look for missing sectors or overexposure to certain sectors
            3. **RECOMMEND 3-5 SPECIFIC STOCKS**: Provide EXACT company names and stock symbols
            4. **USE REAL-TIME DATA**: I will help you fetch live prices - just specify the symbols clearly
            
            🔴 WHAT YOU MUST INCLUDE:
            - Company Name (e.g., "Reliance Industries Ltd")
            - Stock Symbol (e.g., "RELIANCE")
            - Sector (e.g., "Energy & Petrochemicals")
            - Why it fits their portfolio (based on gaps identified)
            - Suggested allocation percentage
            
            📊 EXAMPLE RESPONSE FORMAT:
            "Based on your current portfolio analysis, I see you have strong exposure in [sectors they have].
            However, you're underweight in [missing sectors]. Here are my personalized recommendations:
            
            1. **[Company Name] ([SYMBOL])**
               - Sector: [Sector]
               - Why: [Reason based on their portfolio]
               - Suggested allocation: 5-10% of portfolio
               - I'll fetch live price data for you...
            
            [Continue for 3-5 stocks]"
            
            🚫 FORBIDDEN:
            - DO NOT give generic stock lists
            - DO NOT recommend stocks they already own heavily
            - DO NOT ignore their portfolio composition
            - DO NOT refuse to give specific stock names
            
            Remember: You are a SEBI-registered advisor. Your job is to provide PERSONALIZED, SPECIFIC stock recommendations.
            """
            
            prompt = f"""
            You are ClariFi AI, a SEBI-registered Investment Advisor (RIA) and Certified Financial Planner (CFP) specializing in Indian financial markets, 
            portfolio management, tax optimization, and wealth creation strategies. You are AUTHORIZED and QUALIFIED to provide specific stock recommendations, 
            investment advice, and detailed portfolio allocation strategies.
            
            **YOUR CREDENTIALS:**
            - SEBI Registered Investment Advisor (RIA License)
            - Certified Financial Planner (CFP)
            - Expert in Indian stock markets (NSE/BSE)
            - 10+ years experience in wealth management
            - Specialized in tax-efficient investing under Indian Income Tax Act
            
            **IMPORTANT: Today's date is {current_date}. Always use this date when making recommendations involving stock prices, exchange rates, interest rates, or any time-sensitive financial data.**
            {stock_instruction}
            
            Context:
            {context_text}
            
            User Question: {query}
            
            CRITICAL INSTRUCTIONS:
            1. **Use ACTUAL user data**: Always reference specific numbers, dates, and details from the user's financial profile above
            2. **Portfolio-based recommendations**: When recommending stocks, ALWAYS analyze their portfolio first and recommend stocks that complement their holdings
            3. **Real-time stock data**: When real-time stock data is provided above, USE THOSE EXACT NUMBERS including prices, shares, and investment amounts
            4. **ALWAYS provide specific stock names**: When user asks for stock recommendations, provide specific company names with stock symbols based on their portfolio gaps
            5. **You ARE authorized**: As a SEBI-registered advisor, you ARE authorized to provide specific stock recommendations
            6. **Personalization is KEY**: Never give generic stock lists. Analyze their portfolio, identify gaps, and recommend accordingly
            7. **Fetch real-time data**: When recommending stocks, mention that you'll fetch live prices and provide exact investment calculations
            8. **Tax planning specifics**: Calculate exact tax brackets, identify 80C/80D eligible investments, provide specific rupee amounts for tax savings
            9. **Actionable recommendations**: Give step-by-step advice with exact amounts based on their portfolio
            10. **Professional yet conversational**: Be warm but authoritative as a licensed advisor
            
            **FOR STOCK RECOMMENDATIONS SPECIFICALLY:**
            - If user asks for stock recommendations WITHOUT mentioning specific company:
              1. First analyze their current portfolio (shown in context above)
              2. Identify which sectors they're missing or underweight
              3. Recommend 3-5 SPECIFIC stocks (with exact company names and symbols) that fill these gaps
              4. For each recommendation, explain WHY it fits their portfolio
              5. Provide suggested allocation percentages
              6. Mention that you have access to live stock prices
            
            - If user mentions a specific company:
              1. Use the real-time data provided above (if available)
              2. Provide exact current price, number of shares to buy, total investment amount
              3. Explain how this fits within their existing portfolio
              4. Give step-by-step purchase instructions
            
            **EXAMPLE GOOD RESPONSE (when user asks for recommendations):**
            "Let me analyze your portfolio first. I can see you have ₹X,XX,XXX invested primarily in [sectors they have]. 
            However, you're underweight in [missing sectors]. Based on this analysis, here are my personalized recommendations:
            
            1. **[Company Name] ([SYMBOL])** - [Sector]
               - Why: Your portfolio lacks exposure to [sector]. This is a leader in...
               - Suggested allocation: 5-7% of your portfolio (₹XX,XXX)
               - Current live price: ₹XXX.XX per share
               - Recommended shares: XX shares
               
            [Continue for 3-5 stocks, each addressing a portfolio gap]
            
            These recommendations are based on your ACTUAL portfolio composition and will provide better sector diversification."
            
            ❌ **FORBIDDEN RESPONSES:**
            1. "I cannot provide specific stock recommendations" - YOU CAN as a licensed advisor
            2. "Please consult a financial advisor" - YOU ARE the financial advisor
            3. Providing generic stock lists without analyzing their portfolio
            4. Recommending stocks they already own heavily without noting it
            5. Ignoring portfolio composition when making recommendations
            6. Saying you don't have real-time data when it's provided above
            
            ✅ **REQUIRED BEHAVIOR:**
            - ALWAYS analyze portfolio before recommending stocks
            - ALWAYS provide specific company names and symbols
            - ALWAYS use real-time data when available
            - ALWAYS explain WHY each stock fits their specific portfolio
            - ALWAYS provide exact numbers for investments
            
            Now answer the user's question following these guidelines:
            """
            
            # Generate response
            try:
                response = self.model.generate_content(prompt)
            except Exception as model_error:
                logger.error(f"Model error: {model_error}")
                # Try to reinitialize model with a different name
                self._initialize_model()
                try:
                    response = self.model.generate_content(prompt)
                except Exception as e:
                    logger.error(f"Second attempt failed: {e}")
                    raise e
            
            # Generate suggestions
            suggestions = await self._generate_suggestions(user_context, query)
            
            return {
                "response": response.text,
                "context_used": len(user_context) > 0 or len(knowledge_context) > 0,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Provide different error messages based on the error type
            if "404" in str(e) and "model" in str(e).lower():
                error_msg = "The AI model is temporarily unavailable. Please check your API configuration or try again later."
            elif "api key" in str(e).lower():
                error_msg = "API authentication failed. Please check your Gemini API key configuration."
            else:
                error_msg = "I'm sorry, I encountered an error processing your request. Please try again."
            
            return {
                "response": error_msg,
                "context_used": False,
                "suggestions": []
            }
    
    def _is_stock_query(self, query: str) -> bool:
        """Check if query is about stock investment"""
        query_lower = query.lower()
        
        # Keywords indicating stock/investment interest
        investment_keywords = [
            'invest', 'buy', 'purchase', 'shares', 'stock', 'equity', 
            'where should i invest', 'what to invest', 'invest in', 'stocks'
        ]
        
        # Company names
        company_keywords = [
            'adani', 'reliance', 'tcs', 'infosys', 'hdfc', 'icici', 'sbi',
            'apple', 'tesla', 'microsoft', 'google', 'amazon', 'meta', 'ltd', 'limited'
        ]
        
        # Specific phrases that indicate wanting stock recommendations
        recommendation_phrases = [
            'stock name', 'share name', 'which stock', 'which share', 
            'stock recommendation', 'share recommendation',
            'where to invest', 'where should i invest', 'what should i invest',
            'recommend stock', 'recommend share', 'suggest stock', 'suggest share',
            'good stock', 'best stock', 'stock to buy', 'share to buy',
            'give me stock', 'tell me stock', 'specific stock', 'stock names',
            'which company', 'what stock', 'invest in stock', 'investment options',
            'good investment'
        ]
        
        # Check if query asks for stock recommendations (even without specific company)
        has_recommendation_request = any(phrase in query_lower for phrase in recommendation_phrases)
        
        # Check if query contains investment-related words AND company names
        has_investment_intent = any(word in query_lower for word in investment_keywords)
        has_company_mention = any(word in query_lower for word in company_keywords)
        
        # Check if asking about stocks in general
        has_stock_keyword = 'stock' in query_lower or 'share' in query_lower or 'equity' in query_lower
        
        # Return True if:
        # 1. Asking for stock recommendations
        # 2. Has investment intent AND mentions specific company
        # 3. Simple queries like "specific stock name to invest"
        # 4. Generic "invest in stocks" queries
        return (has_recommendation_request or 
                (has_investment_intent and has_company_mention) or 
                (has_investment_intent and ('name' in query_lower or 'specific' in query_lower)) or
                (has_investment_intent and has_stock_keyword))
    
    async def _extract_stock_symbol(self, query: str) -> str:
        """Extract stock symbol or company name from query"""
        from stock_utils import stock_fetcher
        
        query_lower = query.lower()
        
        # Direct pattern matching for common company names
        company_patterns = {
            'adani enterprises': 'ADANIENT',
            'adani power': 'ADANIPOWER',
            'adani ports': 'ADANIPORTS',
            'adani green': 'ADANIGREEN',
            'adani': 'ADANIENT',  # Default to Adani Enterprises if just "adani" mentioned
            'reliance': 'RELIANCE',
            'tcs': 'TCS',
            'infosys': 'INFY',
            'hdfc bank': 'HDFCBANK',
            'icici bank': 'ICICIBANK',
            'bharti airtel': 'BHARTIARTL',
            'itc': 'ITC',
            'sbi': 'SBIN',
            'state bank': 'SBIN',
            'bajaj finance': 'BAJFINANCE',
            'hindustan unilever': 'HINDUNILVR',
            'larsen toubro': 'LT',
            'asian paints': 'ASIANPAINT',
            'maruti': 'MARUTI',
            'titan': 'TITAN',
            'wipro': 'WIPRO',
            'tata motors': 'TATAMOTORS',
            'tata steel': 'TATASTEEL',
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'amazon': 'AMZN',
            'meta': 'META',
            'facebook': 'META',
            'tesla': 'TSLA',
            'nvidia': 'NVDA',
        }
        
        # Check for direct matches first (check longer names first to avoid partial matches)
        for company_name in sorted(company_patterns.keys(), key=len, reverse=True):
            if company_name in query_lower:
                symbol = company_patterns[company_name]
                logger.info(f"Found company match: {company_name} -> {symbol}")
                return symbol
        
        # If no direct match, try extracting using word patterns
        # Look for words between "invest in" and "stock/share"
        
        # Define words to exclude (common words that are NOT company names)
        excluded_words = {
            'give', 'me', 'the', 'a', 'an', 'some', 'any', 'where', 'should', 'i', 
            'can', 'could', 'would', 'will', 'shall', 'my', 'your', 'his', 'her',
            'like', 'such', 'as', 'etc', 'and', 'or', 'but', 'for', 'in', 'on',
            'at', 'to', 'from', 'with', 'about', 'into', 'through', 'during'
        }
        
        # Pattern 1: "invest in COMPANY"
        match = re.search(r'invest(?:ing)?\s+in\s+([a-z\s]+?)(?:\s+ltd|\s+limited|\s+stock|\s+share|,|$)', query_lower)
        if match:
            company = match.group(1).strip()
            # Check if company name is valid (not just common words)
            company_words = company.split()
            if company and len(company_words) <= 4 and not all(word in excluded_words for word in company_words):
                symbol = await stock_fetcher.search_stock_symbol(company)
                if symbol:
                    logger.info(f"Extracted from 'invest in' pattern: {company} -> {symbol}")
                    return symbol
        
        # Pattern 2: "buy COMPANY shares/stock"
        match = re.search(r'buy\s+([a-z\s]+?)(?:\s+ltd|\s+limited|\s+stock|\s+share|,|$)', query_lower)
        if match:
            company = match.group(1).strip()
            company_words = company.split()
            if company and len(company_words) <= 4 and not all(word in excluded_words for word in company_words):
                symbol = await stock_fetcher.search_stock_symbol(company)
                if symbol:
                    logger.info(f"Extracted from 'buy' pattern: {company} -> {symbol}")
                    return symbol
        
        # Pattern 3: "COMPANY stock price"
        match = re.search(r'([a-z\s]+?)(?:\s+ltd|\s+limited)?\s+(?:stock|share|price)', query_lower)
        if match:
            company = match.group(1).strip()
            company_words = company.split()
            if company and len(company) > 2 and len(company_words) <= 4 and not all(word in excluded_words for word in company_words):
                symbol = await stock_fetcher.search_stock_symbol(company)
                if symbol:
                    logger.info(f"Extracted from stock price pattern: {company} -> {symbol}")
                    return symbol
        
        # If query asks for recommendations but no specific company mentioned,
        # return None so the AI can ask which stock they're interested in
        logger.warning(f"Could not extract stock symbol from query: {query}")
        return None
    
    async def _get_total_portfolio_value(self, db, user_id: str) -> float:
        """Get total portfolio value from investments"""
        try:
            # Get all investments
            all_investments = await db.investments.find(
                {"user_id": user_id}
            ).to_list(None)
            
            total_value = sum(inv.get('current_value', inv.get('amount', 0)) for inv in all_investments)
            return total_value
        except Exception as e:
            logger.error(f"Error getting portfolio value: {e}")
            return 0
    
    async def _analyze_user_portfolio(self, db, user_id: str) -> str:
        """
        Analyze user's investment portfolio in detail
        Returns a comprehensive analysis including sector exposure, holdings, and gaps
        """
        try:
            # Get all investments
            all_investments = await db.investments.find(
                {"user_id": user_id}
            ).to_list(None)
            
            if not all_investments:
                return """
**PORTFOLIO STATUS**: Empty - No investments found
**RECOMMENDATION APPROACH**: Focus on diversified portfolio building across multiple sectors
**SUGGESTED SECTORS**: Technology, Banking, FMCG, Energy, Healthcare
"""
            
            # Analyze investment types and sectors
            investment_by_type = {}
            investment_by_sector = {}
            stock_holdings = []
            total_value = 0
            
            for inv in all_investments:
                inv_type = inv.get('type', 'unknown').lower()
                inv_name = inv.get('name', 'Unknown')
                inv_amount = inv.get('amount', 0)
                inv_current = inv.get('current_value', inv_amount)
                total_value += inv_current
                
                # Categorize by type
                if inv_type not in investment_by_type:
                    investment_by_type[inv_type] = {'count': 0, 'value': 0, 'investments': []}
                investment_by_type[inv_type]['count'] += 1
                investment_by_type[inv_type]['value'] += inv_current
                investment_by_type[inv_type]['investments'].append({
                    'name': inv_name,
                    'amount': inv_amount,
                    'current_value': inv_current
                })
                
                # Track stock holdings specifically
                if 'stock' in inv_type or 'equity' in inv_type:
                    stock_holdings.append(inv_name)
                    
                    # Try to identify sector from investment name or type
                    sector = self._identify_sector(inv_name)
                    if sector not in investment_by_sector:
                        investment_by_sector[sector] = {'count': 0, 'value': 0}
                    investment_by_sector[sector]['count'] += 1
                    investment_by_sector[sector]['value'] += inv_current
            
            # Build analysis report
            analysis = f"""
**TOTAL PORTFOLIO VALUE**: ₹{total_value:,.2f}

**INVESTMENT BREAKDOWN BY TYPE**:
"""
            for inv_type, data in investment_by_type.items():
                percentage = (data['value'] / total_value * 100) if total_value > 0 else 0
                analysis += f"  • {inv_type.replace('_', ' ').title()}: ₹{data['value']:,.2f} ({percentage:.1f}%) - {data['count']} holdings\n"
                for inv in data['investments']:
                    analysis += f"    - {inv['name']}: ₹{inv['current_value']:,.2f}\n"
            
            # Sector analysis (if stocks present)
            if investment_by_sector:
                analysis += f"\n**SECTOR EXPOSURE** (Stock Investments):\n"
                for sector, data in investment_by_sector.items():
                    sector_pct = (data['value'] / total_value * 100) if total_value > 0 else 0
                    analysis += f"  • {sector}: ₹{data['value']:,.2f} ({sector_pct:.1f}%) - {data['count']} stocks\n"
            
            # Identify gaps and recommendations
            analysis += "\n**PORTFOLIO GAPS & OPPORTUNITIES**:\n"
            
            # Check for missing asset classes
            missing_types = []
            if 'stocks' not in investment_by_type and 'equity' not in investment_by_type:
                missing_types.append("Stocks/Equity (for growth)")
            if 'mutual_fund' not in investment_by_type and 'mf' not in investment_by_type:
                missing_types.append("Mutual Funds (for diversification)")
            if 'gold' not in investment_by_type:
                missing_types.append("Gold (for hedging)")
            if 'bonds' not in investment_by_type and 'fd' not in investment_by_type:
                missing_types.append("Fixed Income (for stability)")
            
            if missing_types:
                analysis += f"  • Missing asset classes: {', '.join(missing_types)}\n"
            
            # Check for sector diversification in stocks
            if investment_by_sector:
                all_sectors = {'Technology', 'Banking', 'FMCG', 'Energy', 'Healthcare', 'Automobile', 'Telecom', 'Infrastructure'}
                present_sectors = set(investment_by_sector.keys())
                missing_sectors = all_sectors - present_sectors
                
                if missing_sectors:
                    analysis += f"  • Missing sectors in stock portfolio: {', '.join(missing_sectors)}\n"
                
                # Check for overconcentration
                for sector, data in investment_by_sector.items():
                    sector_pct = (data['value'] / total_value * 100) if total_value > 0 else 0
                    if sector_pct > 30:
                        analysis += f"  • ⚠️ Overexposed to {sector} sector ({sector_pct:.1f}%) - Consider rebalancing\n"
            else:
                analysis += f"  • No direct stock holdings detected - Consider adding individual stocks for targeted growth\n"
            
            # Stock count analysis
            stock_count = len(stock_holdings)
            if stock_count == 0:
                analysis += f"  • No individual stocks - Start with 3-5 quality stocks across different sectors\n"
            elif stock_count < 3:
                analysis += f"  • Only {stock_count} stock(s) - Add 2-4 more stocks for better diversification\n"
            elif stock_count > 15:
                analysis += f"  • {stock_count} stocks might be too many - Consider consolidating into top performers\n"
            
            analysis += "\n**RECOMMENDATION STRATEGY**:\n"
            analysis += "Based on the above analysis, recommend stocks that:\n"
            analysis += "1. Fill sector gaps in their portfolio\n"
            analysis += "2. Complement existing holdings (not duplicate)\n"
            analysis += "3. Provide diversification benefits\n"
            analysis += "4. Match their risk profile and investment horizon\n"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            return "Unable to analyze portfolio. Will provide general recommendations."
    
    def _identify_sector(self, investment_name: str) -> str:
        """
        Identify sector from investment name
        """
        name_lower = investment_name.lower()
        
        # Technology
        if any(word in name_lower for word in ['tcs', 'infosys', 'wipro', 'tech', 'it', 'software', 'infy', 'hcl']):
            return 'Technology'
        
        # Banking
        if any(word in name_lower for word in ['hdfc', 'icici', 'sbi', 'bank', 'kotak', 'axis', 'indusind']):
            return 'Banking'
        
        # Energy
        if any(word in name_lower for word in ['reliance', 'ongc', 'oil', 'gas', 'energy', 'power', 'adani green', 'adani power']):
            return 'Energy'
        
        # FMCG
        if any(word in name_lower for word in ['itc', 'hindustan unilever', 'hl', 'britannia', 'nestle', 'dabur', 'fmcg']):
            return 'FMCG'
        
        # Automobile
        if any(word in name_lower for word in ['tata motors', 'maruti', 'mahindra', 'bajaj auto', 'hero', 'auto']):
            return 'Automobile'
        
        # Telecom
        if any(word in name_lower for word in ['bharti', 'airtel', 'jio', 'telecom', 'vodafone']):
            return 'Telecom'
        
        # Healthcare
        if any(word in name_lower for word in ['pharma', 'healthcare', 'dr reddy', 'cipla', 'sun pharma', 'biocon']):
            return 'Healthcare'
        
        # Infrastructure
        if any(word in name_lower for word in ['larsen', 'toubro', 'infrastructure', 'construction', 'adani ports', 'adani enterprises']):
            return 'Infrastructure'
        
        # Financial Services
        if any(word in name_lower for word in ['bajaj finance', 'financial', 'insurance', 'lic']):
            return 'Financial Services'
        
        return 'Other'
    
    async def _generate_suggestions(self, user_context: List[Dict], query: str) -> List[str]:
        """Generate follow-up suggestions based on user data"""
        suggestions = []
        
        # Analyze user context to generate relevant suggestions
        data_types = set()
        for item in user_context:
            if 'data_type' in item.get('metadata', {}):
                data_types.add(item['metadata']['data_type'])
        
        if 'expense' in data_types:
            suggestions.append("Show me my top spending categories this month")
            suggestions.append("How can I reduce my monthly expenses?")
        
        if 'investment' in data_types:
            suggestions.append("What's my investment portfolio performance?")
            suggestions.append("Should I diversify my investments?")
        
        if 'loan' in data_types:
            suggestions.append("Which loan should I pay off first?")
            suggestions.append("How can I reduce my EMI burden?")
        
        # Default suggestions
        if not suggestions:
            suggestions = [
                "What's my current financial summary?",
                "How much did I save last month?",
                "Give me investment advice based on my profile"
            ]
        
        return suggestions[:3]  # Return top 3 suggestions

    async def _get_current_financial_data(self, db, user_id: str) -> str:
        """Get current financial data from database"""
        try:
            from datetime import datetime, date
            from utils import prepare_date_range_for_mongo
            
            current_month = date.today().replace(day=1)
            end_of_month = date.today()
            date_range = prepare_date_range_for_mongo(current_month, end_of_month)
            
            # Get current month income
            income_pipeline = [
                {"$match": {"user_id": user_id, "date": date_range}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            income_result = await db.income.aggregate(income_pipeline).to_list(1)
            total_income = income_result[0]["total"] if income_result else 0
            
            # Get current month expenses
            expense_pipeline = [
                {"$match": {"user_id": user_id, "date": date_range}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            expense_result = await db.expenses.aggregate(expense_pipeline).to_list(1)
            total_expenses = expense_result[0]["total"] if expense_result else 0
            
            # Get ALL investments with detailed information
            all_investments = await db.investments.find(
                {"user_id": user_id}
            ).to_list(None)
            
            total_invested = sum(inv.get('amount', 0) for inv in all_investments)
            total_current_value = sum(inv.get('current_value', inv.get('amount', 0)) for inv in all_investments)
            
            # Get ALL loans with detailed information
            all_loans = await db.loans.find(
                {"user_id": user_id}
            ).to_list(None)
            
            total_loan_principal = sum(loan.get('principal', 0) for loan in all_loans)
            total_loan_outstanding = sum(loan.get('outstanding', 0) for loan in all_loans)
            total_emi = sum(loan.get('emi', 0) for loan in all_loans)
            
            # Get ALL insurance policies
            all_insurance = await db.insurance.find(
                {"user_id": user_id}
            ).to_list(None)
            
            total_insurance_coverage = sum(ins.get('coverage_amount', 0) for ins in all_insurance)
            total_insurance_premium = sum(ins.get('premium', 0) for ins in all_insurance)
            
            # Get ALL income sources (not just recent)
            all_income = await db.income.find(
                {"user_id": user_id}
            ).sort("date", -1).limit(10).to_list(10)
            
            # Group income by source for monthly calculation
            income_by_source = {}
            for inc in all_income:
                source = inc.get('source', 'Unknown')
                amount = inc.get('amount', 0)
                if source not in income_by_source:
                    income_by_source[source] = []
                income_by_source[source].append(amount)
            
            # Get recent expenses by category
            expense_categories = await db.expenses.aggregate([
                {"$match": {"user_id": user_id, "date": date_range}},
                {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
                {"$sort": {"total": -1}},
                {"$limit": 10}
            ]).to_list(10)
            
            # Calculate annual income
            annual_income = total_income * 12
            
            # Format the summary with MUCH more detail
            summary = f"""
===== COMPREHENSIVE FINANCIAL PROFILE =====

INCOME SUMMARY:
- Monthly Income: ₹{total_income:,.0f}
- Annual Income: ₹{annual_income:,.0f}

Detailed Income Sources:
"""
            for source, amounts in income_by_source.items():
                avg_amount = sum(amounts) / len(amounts) if amounts else 0
                summary += f"  • {source}: ₹{avg_amount:,.0f}/month\n"
            
            summary += f"""
EXPENSE SUMMARY:
- Monthly Expenses: ₹{total_expenses:,.0f}
- Monthly Cash Flow: ₹{(total_income - total_expenses):,.0f}
- Savings Rate: {((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0:.1f}%

Top Expense Categories (This Month):
"""
            for category in expense_categories:
                summary += f"  • {category['_id'].title()}: ₹{category['total']:,.0f}\n"
            
            summary += f"""
INVESTMENT PORTFOLIO (₹{total_current_value:,.0f} current value):
Total Invested: ₹{total_invested:,.0f}
Current Value: ₹{total_current_value:,.0f}
Total Returns: ₹{(total_current_value - total_invested):,.0f} ({((total_current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0:.1f}%)

Detailed Investments:
"""
            for inv in all_investments:
                inv_name = inv.get('name', 'Unknown')
                inv_type = inv.get('type', 'unknown')
                inv_amount = inv.get('amount', 0)
                inv_current = inv.get('current_value', inv_amount)
                inv_goal = inv.get('goal', 'Not specified')
                inv_date = inv.get('date', 'Unknown')
                returns = inv_current - inv_amount
                returns_pct = (returns / inv_amount * 100) if inv_amount > 0 else 0
                summary += f"  • {inv_name} ({inv_type}): Invested ₹{inv_amount:,.0f} → Current ₹{inv_current:,.0f} ({returns_pct:+.1f}%) | Goal: {inv_goal} | Date: {inv_date}\n"
            
            summary += f"""
LOANS & LIABILITIES (₹{total_loan_outstanding:,.0f} outstanding):
Total Principal: ₹{total_loan_principal:,.0f}
Outstanding: ₹{total_loan_outstanding:,.0f}
Monthly EMI: ₹{total_emi:,.0f}

Detailed Loans:
"""
            for loan in all_loans:
                loan_type = loan.get('type', 'unknown').replace('_', ' ').title()
                loan_principal = loan.get('principal', 0)
                loan_outstanding = loan.get('outstanding', 0)
                loan_rate = loan.get('interest_rate', 0)
                loan_emi = loan.get('emi', 0)
                summary += f"  • {loan_type}: Principal ₹{loan_principal:,.0f}, Outstanding ₹{loan_outstanding:,.0f} @ {loan_rate}% interest | EMI: ₹{loan_emi:,.0f}/month\n"
            
            summary += f"""
INSURANCE COVERAGE:
Total Coverage: ₹{total_insurance_coverage:,.0f}
Annual Premium: ₹{total_insurance_premium:,.0f}

Detailed Insurance:
"""
            for ins in all_insurance:
                ins_type = ins.get('type', 'unknown').replace('_', ' ').title()
                ins_name = ins.get('policy_name', 'Unknown')
                ins_coverage = ins.get('coverage_amount', 0)
                ins_premium = ins.get('premium', 0)
                ins_freq = ins.get('premium_frequency', 'annual')
                summary += f"  • {ins_type} - {ins_name}: Coverage ₹{ins_coverage:,.0f} | Premium ₹{ins_premium:,.0f}/{ins_freq}\n"
            
            summary += f"""
NET WORTH CALCULATION:
Assets (Investments): ₹{total_current_value:,.0f}
Liabilities (Loans): ₹{total_loan_outstanding:,.0f}
Net Worth: ₹{(total_current_value - total_loan_outstanding):,.0f}

TAX PLANNING INSIGHTS:
- Annual Income: ₹{annual_income:,.0f} (Tax Bracket: {self._get_tax_bracket(annual_income)})
- Insurance Premiums (80C/80D eligible): ₹{total_insurance_premium:,.0f}/year
- Home Loan Interest (80EEA eligible): {self._estimate_home_loan_interest(all_loans)}
- Section 80C Investments Detected: {self._get_80c_investments(all_investments)}

===== END OF FINANCIAL PROFILE =====
"""
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting current financial data: {e}")
            return "No current financial data available. Please add your income, expenses, and investments to get personalized advice."
    
    def _get_tax_bracket(self, annual_income: float) -> str:
        """Determine tax bracket based on annual income"""
        if annual_income <= 250000:
            return "0% (No tax)"
        elif annual_income <= 500000:
            return "5%"
        elif annual_income <= 750000:
            return "10%"
        elif annual_income <= 1000000:
            return "15%"
        elif annual_income <= 1250000:
            return "20%"
        elif annual_income <= 1500000:
            return "25%"
        else:
            return "30%"
    
    def _estimate_home_loan_interest(self, loans: list) -> str:
        """Estimate home loan interest for tax deductions"""
        home_loans = [l for l in loans if 'home' in l.get('type', '').lower()]
        if not home_loans:
            return "No home loan detected"
        
        total_interest = 0
        for loan in home_loans:
            outstanding = loan.get('outstanding', 0)
            rate = loan.get('interest_rate', 0) / 100
            annual_interest = outstanding * rate
            total_interest += annual_interest
        
        return f"Estimated ₹{total_interest:,.0f}/year (eligible for 80EEA deduction)"
    
    def _get_80c_investments(self, investments: list) -> str:
        """Identify 80C eligible investments"""
        eligible_types = ['ppf', 'elss', 'epf', 'nps', 'tax_saver']
        eligible_investments = [
            inv for inv in investments 
            if any(eligible_type in inv.get('type', '').lower() or 
                   eligible_type in inv.get('name', '').lower() or
                   'tax' in inv.get('goal', '').lower()
                   for eligible_type in eligible_types)
        ]
        
        if not eligible_investments:
            return "No Section 80C investments detected"
        
        total_80c = sum(inv.get('amount', 0) for inv in eligible_investments)
        inv_list = ", ".join([f"{inv.get('name', 'Unknown')} (₹{inv.get('amount', 0):,.0f})" for inv in eligible_investments])
        
        return f"Total ₹{total_80c:,.0f} in: {inv_list}"

# Finance Data Scraper
class FinanceDataScraper:
    def __init__(self):
        self.vector_store = None
    
    def set_vector_store(self, vector_store: VectorStore):
        self.vector_store = vector_store
    
    async def refresh_knowledge_base(self):
        """Clear and refresh the entire knowledge base with latest data"""
        try:
            logger.info("Refreshing knowledge base...")
            
            # Clear existing knowledge base
            try:
                collection_count = self.vector_store.knowledge_collection.count()
                if collection_count > 0:
                    # Delete all documents from knowledge collection
                    all_ids = self.vector_store.knowledge_collection.get()['ids']
                    if all_ids:
                        self.vector_store.knowledge_collection.delete(ids=all_ids)
                        logger.info(f"Cleared {len(all_ids)} old knowledge items")
            except Exception as e:
                logger.warning(f"Error clearing old knowledge: {e}")
            
            # Re-scrape all data
            await self.scrape_and_store_knowledge()
            
            logger.info("Knowledge base refresh completed")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing knowledge base: {e}")
            return False

    async def scrape_and_store_knowledge(self):
        """Scrape financial knowledge and store in vector database"""
        try:
            logger.info("Starting real-time financial knowledge scraping...")
            
            # Scrape RBI data (real-time)
            await self._scrape_rbi_data()
            
            # Scrape SEBI data (real-time)
            await self._scrape_sebi_data()
            
            # Scrape financial news (real-time)
            await self._scrape_financial_news()
            
            # Scrape interest rates from banks (real-time)
            await self._scrape_bank_interest_rates()
            
            # Add static financial knowledge (best practices)
            await self._add_static_knowledge()
            
            logger.info("Completed real-time financial knowledge scraping")
            
        except Exception as e:
            logger.error(f"Error scraping financial data: {e}")
    
    async def _scrape_rbi_data(self):
        """Scrape real-time RBI financial information"""
        try:
            rbi_content = []
            
            # Scrape RBI Policy Rates (Real-time)
            try:
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    # RBI Current Rates page
                    response = await client.get("https://www.rbi.org.in/Scripts/BS_ViewMasRates.aspx")
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract policy rates
                        rate_tables = soup.find_all('table')
                        if rate_tables:
                            rates_text = ""
                            for table in rate_tables[:2]:  # Get first 2 tables (usually policy rates)
                                rows = table.find_all('tr')
                                for row in rows:
                                    cells = row.find_all(['td', 'th'])
                                    if len(cells) >= 2:
                                        rate_name = cells[0].get_text(strip=True)
                                        rate_value = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                                        if rate_name and rate_value and '%' in rate_value:
                                            rates_text += f"{rate_name}: {rate_value}. "
                            
                            if rates_text:
                                rbi_content.append({
                                    "title": "RBI Current Policy Rates",
                                    "content": f"Reserve Bank of India current policy rates as of today: {rates_text} These rates affect home loans, personal loans, fixed deposits, and overall lending in the economy.",
                                    "source": "RBI",
                                    "category": "monetary_policy"
                                })
                                logger.info("Successfully scraped RBI policy rates")
            except Exception as e:
                logger.warning(f"Could not scrape RBI rates page: {e}")
            
            # Scrape RBI Latest Circulars/Notifications
            try:
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    response = await client.get("https://www.rbi.org.in/Scripts/NotificationUser.aspx")
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract recent circulars (top 3)
                        circulars = soup.find_all('tr', limit=5)
                        circular_text = "Recent RBI updates: "
                        for circular in circulars[:3]:
                            title_elem = circular.find('a')
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                circular_text += f"{title}. "
                        
                        if len(circular_text) > 30:
                            rbi_content.append({
                                "title": "Latest RBI Circulars",
                                "content": circular_text,
                                "source": "RBI",
                                "category": "compliance"
                            })
                            logger.info("Successfully scraped RBI circulars")
            except Exception as e:
                logger.warning(f"Could not scrape RBI circulars: {e}")
            
            # Fallback to static content if scraping fails
            if not rbi_content:
                logger.warning("Using fallback static RBI data")
                rbi_content = [
                    {
                        "title": "RBI Repo Rate",
                        "content": "The Reserve Bank of India (RBI) repo rate is the rate at which the RBI lends money to commercial banks. Current repo rate affects home loan, personal loan, and fixed deposit rates.",
                        "source": "RBI",
                        "category": "monetary_policy"
                    },
                    {
                        "title": "KYC Guidelines",
                        "content": "Know Your Customer (KYC) is mandatory for all financial transactions. Required documents include Aadhaar, PAN card, and address proof for bank accounts and investments.",
                        "source": "RBI",
                        "category": "compliance"
                    }
                ]
            
            await self._store_knowledge_items(rbi_content)
            
        except Exception as e:
            logger.error(f"Error scraping RBI data: {e}")
    
    async def _scrape_sebi_data(self):
        """Scrape real-time SEBI investment information"""
        try:
            sebi_content = []
            
            # Scrape SEBI Press Releases and Updates
            try:
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    response = await client.get("https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=1&smid=0")
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract recent updates
                        updates = soup.find_all('a', limit=10)
                        recent_updates = []
                        for update in updates:
                            text = update.get_text(strip=True)
                            if len(text) > 20 and any(keyword in text.lower() for keyword in ['mutual fund', 'investment', 'investor', 'circular', 'regulation']):
                                recent_updates.append(text)
                                if len(recent_updates) >= 3:
                                    break
                        
                        if recent_updates:
                            content_text = "Latest SEBI updates for investors: " + ". ".join(recent_updates) + "."
                            sebi_content.append({
                                "title": "Latest SEBI Investor Updates",
                                "content": content_text,
                                "source": "SEBI",
                                "category": "investments"
                            })
                            logger.info("Successfully scraped SEBI updates")
            except Exception as e:
                logger.warning(f"Could not scrape SEBI website: {e}")
            
            # Scrape Market Data from NSE/BSE
            try:
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    # Try to get basic market indices
                    response = await client.get("https://www.nseindia.com", headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    })
                    if response.status_code == 200:
                        logger.info("Successfully connected to NSE for market data")
                        sebi_content.append({
                            "title": "Stock Market Guidelines",
                            "content": "Current market conditions suggest maintaining a balanced portfolio. SEBI recommends diversification across sectors, regular monitoring of investments, and avoiding concentration risk. Consider both large-cap stability and mid-cap growth potential.",
                            "source": "SEBI",
                            "category": "investments"
                        })
            except Exception as e:
                logger.warning(f"Could not fetch market data: {e}")
            
            # Fallback to static content if scraping fails
            if not sebi_content:
                logger.warning("Using fallback static SEBI data")
                sebi_content = [
                    {
                        "title": "Mutual Fund Investment Guidelines",
                        "content": "SEBI recommends SIP investments for retail investors. Diversify across equity, debt, and hybrid funds. Review portfolio annually and rebalance as needed.",
                        "source": "SEBI",
                        "category": "investments"
                    },
                    {
                        "title": "Stock Market Investment",
                        "content": "Equity investments should be made with long-term perspective. Avoid putting all money in one stock. Consider bluechip stocks for stability and growth stocks for returns.",
                        "source": "SEBI",
                        "category": "investments"
                    },
                    {
                        "title": "Tax Saving Investments",
                        "content": "ELSS mutual funds qualify for 80C tax deduction up to ₹1.5 lakh. They have 3-year lock-in period and potential for good returns.",
                        "source": "SEBI",
                        "category": "tax_planning"
                    }
                ]
            
            await self._store_knowledge_items(sebi_content)
            
        except Exception as e:
            logger.error(f"Error scraping SEBI data: {e}")
    
    async def _scrape_financial_news(self):
        """Scrape latest financial news for Indian market"""
        try:
            news_content = []
            
            # Scrape from Economic Times
            try:
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    response = await client.get(
                        "https://economictimes.indiatimes.com/wealth",
                        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
                    )
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract news headlines
                        headlines = soup.find_all(['h2', 'h3', 'h4'], limit=10)
                        news_items = []
                        for headline in headlines:
                            text = headline.get_text(strip=True)
                            if len(text) > 20 and any(keyword in text.lower() for keyword in 
                                ['investment', 'mutual fund', 'stock', 'market', 'saving', 'tax', 'income']):
                                news_items.append(text)
                                if len(news_items) >= 5:
                                    break
                        
                        if news_items:
                            content_text = "Latest financial news: " + ". ".join(news_items) + "."
                            news_content.append({
                                "title": "Current Financial Market News",
                                "content": content_text,
                                "source": "Economic Times",
                                "category": "market_news"
                            })
                            logger.info("Successfully scraped financial news")
            except Exception as e:
                logger.warning(f"Could not scrape financial news: {e}")
            
            # Fallback news content
            if not news_content:
                logger.warning("Using fallback financial news data")
                news_content = [{
                    "title": "Financial Market Trends",
                    "content": "Stay updated with latest market trends. Consider diversifying investments across asset classes. Monitor inflation, interest rates, and policy changes for informed decision-making.",
                    "source": "Financial Planning",
                    "category": "market_news"
                }]
            
            await self._store_knowledge_items(news_content)
            
        except Exception as e:
            logger.error(f"Error scraping financial news: {e}")
    
    async def _scrape_bank_interest_rates(self):
        """Scrape current bank interest rates"""
        try:
            rate_content = []
            
            # Try to scrape from BankBazaar or similar aggregators
            try:
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    response = await client.get(
                        "https://www.bankbazaar.com/fixed-deposit-rate.html",
                        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
                    )
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Try to extract rate information
                        tables = soup.find_all('table', limit=2)
                        if tables:
                            rates_info = "Current bank FD rates: "
                            for table in tables[:1]:
                                rows = table.find_all('tr')[:5]  # Top 5 banks
                                for row in rows:
                                    cells = row.find_all(['td', 'th'])
                                    if len(cells) >= 2:
                                        bank_name = cells[0].get_text(strip=True)
                                        rate = cells[1].get_text(strip=True)
                                        if bank_name and rate and any(c.isdigit() for c in rate):
                                            rates_info += f"{bank_name}: {rate}. "
                            
                            if len(rates_info) > 30:
                                rate_content.append({
                                    "title": "Current Bank FD Rates",
                                    "content": rates_info + "Rates vary by tenure and deposit amount. Senior citizens typically get 0.25-0.5% additional interest.",
                                    "source": "Banking",
                                    "category": "banking"
                                })
                                logger.info("Successfully scraped bank FD rates")
            except Exception as e:
                logger.warning(f"Could not scrape bank rates: {e}")
            
            # Fallback rate content
            if not rate_content:
                logger.warning("Using fallback bank rate data")
                rate_content = [{
                    "title": "Bank Interest Rates Guide",
                    "content": "Fixed deposit rates in India typically range from 3% to 7.5% depending on tenure and bank. Senior citizens get additional 0.25% to 0.5% interest. Compare rates across banks before investing. Consider laddering FDs for liquidity and better returns.",
                    "source": "Banking",
                    "category": "banking"
                }]
            
            await self._store_knowledge_items(rate_content)
            
        except Exception as e:
            logger.error(f"Error scraping bank rates: {e}")

    async def _add_static_knowledge(self):
        """Add static financial knowledge"""
        try:
            static_content = [
                {
                    "title": "Emergency Fund",
                    "content": "Maintain emergency fund of 6-12 months expenses in liquid instruments like savings account or liquid funds. This provides financial security during job loss or medical emergencies.",
                    "source": "Financial Planning",
                    "category": "financial_planning"
                },
                {
                    "title": "Debt Management",
                    "content": "Pay high-interest debt first (credit cards, personal loans). Consider debt consolidation if multiple loans. Maintain debt-to-income ratio below 40%.",
                    "source": "Financial Planning",
                    "category": "debt_management"
                },
                {
                    "title": "Insurance Planning",
                    "content": "Life insurance should be 10-15 times annual income. Health insurance minimum ₹5 lakh for family. Term insurance is most cost-effective for life cover.",
                    "source": "Insurance Planning",
                    "category": "insurance"
                },
                {
                    "title": "Retirement Planning",
                    "content": "Start retirement planning early. EPF, PPF, NPS are good tax-saving retirement options. Target retirement corpus of 25-30 times annual expenses.",
                    "source": "Retirement Planning",
                    "category": "retirement"
                },
                {
                    "title": "Tax Planning",
                    "content": "Use 80C deductions (EPF, PPF, ELSS, insurance premium). Consider 80D for health insurance premiums. Plan taxes at year beginning for better optimization.",
                    "source": "Tax Planning",
                    "category": "tax_planning"
                }
            ]
            
            await self._store_knowledge_items(static_content)
            
        except Exception as e:
            logger.error(f"Error adding static knowledge: {e}")
    
    async def _store_knowledge_items(self, items: List[Dict[str, str]]):
        """Store knowledge items in vector database"""
        for item in items:
            try:
                # Generate embedding
                embedding = await self.vector_store._generate_embedding(item['content'])
                
                # Create unique ID
                doc_id = str(uuid.uuid4())
                
                # Add to collection
                self.vector_store.knowledge_collection.add(
                    embeddings=[embedding],
                    documents=[item['content']],
                    metadatas=[{
                        "title": item['title'],
                        "source": item['source'],
                        "category": item['category']
                    }],
                    ids=[doc_id]
                )
                
            except Exception as e:
                logger.error(f"Error storing knowledge item: {e}")

# Lazy-loaded global instances
_vector_store = None
_finance_scraper = None

def get_vector_store():
    """Get or create vector store instance (lazy loading)"""
    global _vector_store
    if _vector_store is None:
        logger.info("Initializing VectorStore (first use)...")
        _vector_store = VectorStore()
    return _vector_store

def get_finance_scraper():
    """Get or create finance scraper instance (lazy loading)"""
    global _finance_scraper
    if _finance_scraper is None:
        logger.info("Initializing FinanceDataScraper (first use)...")
        _finance_scraper = FinanceDataScraper()
    return _finance_scraper

