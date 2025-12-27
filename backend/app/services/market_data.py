"""
Market Data Service
Fetches real-time market data from free APIs.
All external data is fetched here, cached, and used for calculations.
The LLM never fetches external data directly.
"""

from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from cachetools import TTLCache
import httpx
import asyncio
from loguru import logger

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("yfinance not available. Stock features will be limited.")

from app.core.config import settings


class MarketDataService:
    """
    Service for fetching real-time market data from free APIs.
    
    Data Sources:
    - mfapi.in: Indian mutual fund NAV data (free, no API key required)
    - Public APIs for market indices
    """
    
    def __init__(self):
        # Cache with TTL (time-to-live) in seconds
        self.cache = TTLCache(maxsize=1000, ttl=settings.cache_ttl_seconds)
        self.http_client = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self.http_client is None or self.http_client.is_closed:
            self.http_client = httpx.AsyncClient(timeout=30.0)
        return self.http_client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self.http_client and not self.http_client.is_closed:
            await self.http_client.aclose()
    
    # =========================================================================
    # MUTUAL FUND DATA (mfapi.in - Free, No API Key)
    # =========================================================================
    
    async def get_mutual_fund_nav(self, scheme_code: str) -> Optional[Dict[str, Any]]:
        """
        Get current NAV for a mutual fund scheme.
        
        Args:
            scheme_code: AMFI scheme code (e.g., "119551" for HDFC Mid-Cap)
            
        Returns:
            Dictionary with NAV data or None if not found
        """
        cache_key = f"mf_nav_{scheme_code}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            client = await self._get_client()
            response = await client.get(
                f"https://api.mfapi.in/mf/{scheme_code}"
            )
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    "scheme_code": scheme_code,
                    "scheme_name": data.get("meta", {}).get("scheme_name", "Unknown"),
                    "fund_house": data.get("meta", {}).get("fund_house", "Unknown"),
                    "scheme_type": data.get("meta", {}).get("scheme_type", "Unknown"),
                    "current_nav": None,
                    "nav_date": None,
                    "fetched_at": datetime.utcnow().isoformat()
                }
                
                # Get latest NAV
                nav_data = data.get("data", [])
                if nav_data:
                    latest = nav_data[0]
                    result["current_nav"] = float(latest.get("nav", 0))
                    result["nav_date"] = latest.get("date", "")
                
                # Cache the result
                self.cache[cache_key] = result
                
                logger.debug(f"Fetched NAV for scheme {scheme_code}: {result['current_nav']}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to fetch MF NAV for {scheme_code}: {e}")
        
        return None
    
    async def get_mutual_fund_historical(
        self,
        scheme_code: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get historical NAV data for a mutual fund.
        
        Args:
            scheme_code: AMFI scheme code
            days: Number of days of history
            
        Returns:
            List of historical NAV data points
        """
        cache_key = f"mf_hist_{scheme_code}_{days}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            client = await self._get_client()
            response = await client.get(
                f"https://api.mfapi.in/mf/{scheme_code}"
            )
            
            if response.status_code == 200:
                data = response.json()
                nav_data = data.get("data", [])[:days]
                
                result = [
                    {
                        "date": item.get("date", ""),
                        "nav": float(item.get("nav", 0))
                    }
                    for item in nav_data
                ]
                
                self.cache[cache_key] = result
                return result
                
        except Exception as e:
            logger.error(f"Failed to fetch MF history for {scheme_code}: {e}")
        
        return []
    
    async def search_mutual_funds(self, query: str) -> List[Dict[str, str]]:
        """
        Search for mutual funds by name.
        
        Note: mfapi.in doesn't have a search endpoint, so we use the full list
        and filter client-side. This is cached aggressively.
        """
        cache_key = "mf_all_schemes"
        
        if cache_key not in self.cache:
            try:
                client = await self._get_client()
                response = await client.get("https://api.mfapi.in/mf")
                
                if response.status_code == 200:
                    self.cache[cache_key] = response.json()
                else:
                    return []
                    
            except Exception as e:
                logger.error(f"Failed to fetch MF list: {e}")
                return []
        
        all_schemes = self.cache.get(cache_key, [])
        query_lower = query.lower()
        
        # Filter and return matching schemes
        matches = [
            {"scheme_code": str(s.get("schemeCode", "")), 
             "scheme_name": s.get("schemeName", "")}
            for s in all_schemes
            if query_lower in s.get("schemeName", "").lower()
        ][:20]  # Limit to 20 results
        
        return matches
    
    async def calculate_mf_returns(
        self,
        scheme_code: str,
        investment_date: str,
        units: float
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate returns for a mutual fund investment.
        
        Args:
            scheme_code: AMFI scheme code
            investment_date: Date of investment (YYYY-MM-DD)
            units: Number of units purchased
            
        Returns:
            Dictionary with investment returns
        """
        # Get current NAV
        current_data = await self.get_mutual_fund_nav(scheme_code)
        if not current_data or not current_data.get("current_nav"):
            return None
        
        # Get historical data to find investment date NAV
        historical = await self.get_mutual_fund_historical(scheme_code, 365)
        
        # Find NAV on or near investment date
        investment_nav = None
        for item in historical:
            if item.get("date", "") <= investment_date:
                investment_nav = item.get("nav")
                break
        
        if not investment_nav:
            # If we can't find historical NAV, use current as estimate
            investment_nav = current_data["current_nav"]
        
        # Calculate returns
        current_nav = current_data["current_nav"]
        invested_value = units * investment_nav
        current_value = units * current_nav
        absolute_return = current_value - invested_value
        percentage_return = ((absolute_return / invested_value) * 100) if invested_value > 0 else 0
        
        return {
            "scheme_name": current_data.get("scheme_name", ""),
            "scheme_code": scheme_code,
            "units": units,
            "investment_nav": investment_nav,
            "current_nav": current_nav,
            "invested_value": round(invested_value, 2),
            "current_value": round(current_value, 2),
            "absolute_return": round(absolute_return, 2),
            "percentage_return": round(percentage_return, 2),
            "nav_date": current_data.get("nav_date", "")
        }
    
    # =========================================================================
    # INTEREST RATES (Cached/Static Data)
    # =========================================================================
    
    def get_current_interest_rates(self) -> Dict[str, float]:
        """
        Get current benchmark interest rates.
        These are periodically updated from official sources.
        
        Note: In production, these would be fetched from RBI or other official sources.
        """
        # These rates should be updated periodically from official sources
        return {
            "repo_rate": 6.50,
            "reverse_repo_rate": 3.35,
            "bank_rate": 6.75,
            "crr": 4.50,
            "slr": 18.00,
            "ppf_rate": 7.10,
            "epf_rate": 8.15,
            "sukanya_samriddhi_rate": 8.00,
            "nsc_rate": 7.70,
            "senior_citizen_savings_rate": 8.20,
            "fd_avg_rate": 7.00,
            "home_loan_avg_rate": 8.50,
            "personal_loan_avg_rate": 12.00,
            "education_loan_avg_rate": 10.00,
            "last_updated": "2024-01-01"
        }
    
    # =========================================================================
    # TAX RATES (Static Data)
    # =========================================================================
    
    def get_tax_slabs_new_regime(self) -> List[Dict[str, Any]]:
        """Get tax slabs under new regime (FY 2024-25)."""
        return [
            {"min": 0, "max": 300000, "rate": 0},
            {"min": 300001, "max": 600000, "rate": 5},
            {"min": 600001, "max": 900000, "rate": 10},
            {"min": 900001, "max": 1200000, "rate": 15},
            {"min": 1200001, "max": 1500000, "rate": 20},
            {"min": 1500001, "max": float('inf'), "rate": 30},
        ]
    
    def get_tax_slabs_old_regime(self) -> List[Dict[str, Any]]:
        """Get tax slabs under old regime (FY 2024-25)."""
        return [
            {"min": 0, "max": 250000, "rate": 0},
            {"min": 250001, "max": 500000, "rate": 5},
            {"min": 500001, "max": 1000000, "rate": 20},
            {"min": 1000001, "max": float('inf'), "rate": 30},
        ]
    
    def get_section_80c_limits(self) -> Dict[str, int]:
        """Get Section 80C deduction limits."""
        return {
            "section_80c": 150000,
            "section_80ccd_1b": 50000,  # Additional NPS
            "section_80d_self": 25000,  # Health insurance
            "section_80d_parents": 25000,  # Parents (50000 if senior)
            "section_80d_parents_senior": 50000,
            "section_24_home_loan": 200000,  # Home loan interest
        }

    # =========================================================================
    # REAL-TIME STOCK DATA (Yahoo Finance - Free, No API Key)
    # =========================================================================
    
    async def get_stock_price(self, symbol: str, exchange: str = "NS") -> Optional[Dict[str, Any]]:
        """
        Get real-time stock price and basic info.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE", "TCS")
            exchange: Exchange suffix - "NS" for NSE, "BO" for BSE
            
        Returns:
            Dictionary with stock data or None if not found
        """
        if not YFINANCE_AVAILABLE:
            logger.warning("yfinance not available for stock data")
            return None
        
        cache_key = f"stock_{symbol}_{exchange}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            ticker_symbol = f"{symbol}.{exchange}"
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            if not info or info.get("regularMarketPrice") is None:
                # Try BSE if NSE fails
                if exchange == "NS":
                    logger.debug(f"{symbol}.NS failed, trying .BO...")
                    await asyncio.sleep(0.5)  # Small delay
                    return await self.get_stock_price(symbol, "BO")
                # Return None if both fail - we don't want hardcoded data
                logger.warning(f"Could not fetch real-time data for {symbol}")
                return None
            
            # Handle None values gracefully
            current_price = info.get("regularMarketPrice") or info.get("currentPrice") or 0
            prev_close = info.get("previousClose") or current_price
            
            result = {
                "symbol": symbol,
                "name": info.get("longName") or info.get("shortName") or symbol,
                "exchange": exchange,
                "current_price": current_price,
                "previous_close": prev_close,
                "open": info.get("open") or current_price,
                "day_high": info.get("dayHigh") or current_price,
                "day_low": info.get("dayLow") or current_price,
                "volume": info.get("volume") or 0,
                "market_cap": info.get("marketCap") or 0,
                "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
                "pb_ratio": info.get("priceToBook"),
                "dividend_yield": (info.get("dividendYield") or 0) * 100,
                "52_week_high": info.get("fiftyTwoWeekHigh") or current_price,
                "52_week_low": info.get("fiftyTwoWeekLow") or current_price,
                "sector": info.get("sector") or "Unknown",
                "industry": info.get("industry") or "Unknown",
                "change_percent": round(
                    ((current_price - prev_close) / prev_close) * 100, 2
                ) if prev_close else 0,
                "fetched_at": datetime.utcnow().isoformat()
            }
            
            self.cache[cache_key] = result
            logger.info(f"✓ Real-time data: {symbol} = ₹{result['current_price']:.2f} (P/E: {result.get('pe_ratio', 'N/A')})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch real-time stock data for {symbol}: {e}")
            # Try BSE if we were trying NSE
            if exchange == "NS":
                await asyncio.sleep(0.5)
                return await self.get_stock_price(symbol, "BO")
            return None  # Don't return hardcoded fallback data
    
    def _get_fallback_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Return fallback static data for major stocks when API fails."""
        fallback_stocks = {
            "RELIANCE": {"name": "Reliance Industries", "sector": "Energy", "pe_ratio": 25.5, "price": 2950},
            "TCS": {"name": "Tata Consultancy Services", "sector": "IT", "pe_ratio": 28.2, "price": 4180},
            "HDFCBANK": {"name": "HDFC Bank", "sector": "Banking", "pe_ratio": 19.8, "price": 1720},
            "INFY": {"name": "Infosys", "sector": "IT", "pe_ratio": 24.5, "price": 1850},
            "ICICIBANK": {"name": "ICICI Bank", "sector": "Banking", "pe_ratio": 18.5, "price": 1280},
            "HINDUNILVR": {"name": "Hindustan Unilever", "sector": "FMCG", "pe_ratio": 55.2, "price": 2450},
            "ITC": {"name": "ITC Limited", "sector": "FMCG", "pe_ratio": 26.1, "price": 465},
            "SBIN": {"name": "State Bank of India", "sector": "Banking", "pe_ratio": 10.5, "price": 820},
            "BHARTIARTL": {"name": "Bharti Airtel", "sector": "Telecom", "pe_ratio": 45.2, "price": 1580},
            "KOTAKBANK": {"name": "Kotak Mahindra Bank", "sector": "Banking", "pe_ratio": 20.1, "price": 1780},
            "PERSISTENT": {"name": "Persistent Systems", "sector": "IT", "pe_ratio": 35.8, "price": 5200},
            "POLYCAB": {"name": "Polycab India", "sector": "Manufacturing", "pe_ratio": 42.5, "price": 6800},
            "TRENT": {"name": "Trent Limited", "sector": "Retail", "pe_ratio": 85.2, "price": 6500},
            "DIXON": {"name": "Dixon Technologies", "sector": "Electronics", "pe_ratio": 95.5, "price": 15500},
            "COALINDIA": {"name": "Coal India", "sector": "Mining", "pe_ratio": 7.5, "price": 420, "dividend_yield": 5.2},
            "POWERGRID": {"name": "Power Grid Corp", "sector": "Utilities", "pe_ratio": 12.8, "price": 320, "dividend_yield": 4.8},
            "ZOMATO": {"name": "Zomato", "sector": "Food Tech", "pe_ratio": 350, "price": 280},
        }
        
        if symbol in fallback_stocks:
            data = fallback_stocks[symbol]
            return {
                "symbol": symbol,
                "name": data["name"],
                "exchange": "NS",
                "current_price": data["price"],
                "pe_ratio": data["pe_ratio"],
                "sector": data["sector"],
                "dividend_yield": data.get("dividend_yield", 0),
                "change_percent": 0,
                "recommendation_reason": "Blue-chip stock with strong fundamentals",
                "fetched_at": datetime.utcnow().isoformat(),
                "is_fallback": True
            }
        return None
    
    async def get_multiple_stocks(self, symbols: List[str], exchange: str = "NS") -> List[Dict[str, Any]]:
        """
        Get real-time data for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            exchange: Exchange suffix
            
        Returns:
            List of stock data dictionaries
        """
        results = []
        for symbol in symbols:
            data = await self.get_stock_price(symbol, exchange)
            if data:
                results.append(data)
        return results
    
    async def get_stock_recommendations(
        self,
        portfolio: Dict[str, Any],
        risk_profile: str = "moderate",
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get real-time stock recommendations based on user's portfolio and risk profile.
        
        Args:
            portfolio: User's current portfolio data
            risk_profile: "conservative", "moderate", or "aggressive"
            query: Optional specific stock query from user
            
        Returns:
            Investment recommendations with real-time data
        """
        # Stock universe by category - these are NSE symbols
        stock_categories = {
            "large_cap": ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK"],
            "mid_cap": ["PERSISTENT", "POLYCAB", "TRENT", "DIXON", "PIIND", "COFORGE", "MPHASIS", "ASTRAL", "PHOENIXLTD"],
            "dividend": ["COALINDIA", "POWERGRID", "ONGC", "VEDL", "IOC", "BPCL", "NTPC", "RECLTD"],
            "growth": ["ZOMATO", "PAYTM", "NYKAA", "DELHIVERY", "POLICYBZR"],
            "banking": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", "INDUSINDBK"],
            "it": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTIM", "PERSISTENT", "COFORGE"],
            "pharma": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "APOLLOHOSP"],
            "auto": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "HEROMOTOCO"],
            "fmcg": ["HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR", "MARICO"],
        }
        
        recommendations = {
            "analysis": {},
            "recommended_stocks": [],
            "market_overview": {},
            "allocation_suggestion": {},
            "rationale": "",
            "fetched_at": datetime.utcnow().isoformat()
        }
        
        # If user asked about specific stocks or sectors
        if query:
            query_lower = query.lower()
            target_symbols = []
            
            # Check if query mentions specific sectors
            for sector, symbols in stock_categories.items():
                if sector in query_lower:
                    target_symbols.extend(symbols[:5])
                    break
            
            # Check if query mentions specific stock
            for sector, symbols in stock_categories.items():
                for sym in symbols:
                    if sym.lower() in query_lower:
                        target_symbols.append(sym)
            
            # If no specific match, use default based on risk
            if not target_symbols:
                if "dividend" in query_lower or "income" in query_lower:
                    target_symbols = stock_categories["dividend"][:5]
                elif "growth" in query_lower or "aggressive" in query_lower:
                    target_symbols = stock_categories["growth"][:3] + stock_categories["mid_cap"][:3]
                elif "safe" in query_lower or "conservative" in query_lower:
                    target_symbols = stock_categories["large_cap"][:5]
        else:
            # Default selection based on risk profile
            if risk_profile == "conservative":
                target_symbols = stock_categories["large_cap"][:4] + stock_categories["dividend"][:3]
                recommendations["allocation_suggestion"] = {
                    "large_cap": 50, "mid_cap": 10, "debt_funds": 30, "gold": 10
                }
                recommendations["rationale"] = "Focus on stability with blue-chip stocks and dividend income"
            elif risk_profile == "aggressive":
                target_symbols = stock_categories["mid_cap"][:4] + stock_categories["growth"][:3] + stock_categories["large_cap"][:2]
                recommendations["allocation_suggestion"] = {
                    "large_cap": 30, "mid_cap": 40, "small_cap": 20, "gold": 10
                }
                recommendations["rationale"] = "Growth-focused with higher mid/small cap exposure"
            else:  # moderate
                target_symbols = stock_categories["large_cap"][:4] + stock_categories["mid_cap"][:3]
                recommendations["allocation_suggestion"] = {
                    "large_cap": 40, "mid_cap": 25, "debt_funds": 25, "gold": 10
                }
                recommendations["rationale"] = "Balanced approach with mix of stability and growth"
        
        # Fetch real-time data for selected stocks
        stock_data = []
        failed_symbols = []
        for i, symbol in enumerate(target_symbols[:15]):  # Try more symbols to get at least 5-7 with real data
            data = await self.get_stock_price(symbol)
            if data and not data.get("is_fallback"):  # Skip fallback/cached data
                # Add recommendation reason based on metrics
                recommendation_reason = self._generate_stock_recommendation(data)
                data["recommendation_reason"] = recommendation_reason
                stock_data.append(data)
                if len(stock_data) >= 7:  # Got enough real-time stocks
                    break
            else:
                failed_symbols.append(symbol)
            
            # Small delay to avoid rate limiting
            if i < len(target_symbols) - 1:
                await asyncio.sleep(0.3)
        
        # Log failures
        if failed_symbols:
            logger.warning(f"Failed to fetch data for: {', '.join(failed_symbols)}")
        
        # Check if we got real-time data
        if not stock_data:
            logger.error("No real-time stock data available. Using fallback recommendations.")
            # Provide fallback generic recommendations
            recommendations["recommended_stocks"] = []
            recommendations["fallback_advice"] = self._get_generic_investment_advice(risk_profile)
            recommendations["error"] = "Unable to fetch real-time stock data at the moment. Here's general guidance based on your risk profile."
            return recommendations
        
        # Sort by a simple scoring mechanism
        for stock in stock_data:
            score = 0
            # Positive change is good
            if stock.get("change_percent", 0) > 0:
                score += 1
            # Reasonable P/E is good (between 10 and 30)
            pe = stock.get("pe_ratio")
            if pe and 10 <= pe <= 30:
                score += 2
            elif pe and pe < 10:
                score += 1  # Could be value trap or genuinely undervalued
            # Good dividend yield
            if stock.get("dividend_yield", 0) > 2:
                score += 1
            stock["score"] = score
        
        stock_data.sort(key=lambda x: x.get("score", 0), reverse=True)
        recommendations["recommended_stocks"] = stock_data
        logger.info(f"Fetched {len(stock_data)} real-time stock recommendations")
        
        # Add Nifty 50 overview
        nifty_data = await self.get_stock_price("NIFTY50", "NS")
        if not nifty_data:
            # Try alternative symbol
            nifty_data = await self._get_index_data("^NSEI")
        recommendations["market_overview"]["nifty50"] = nifty_data
        
        # SIP recommendations based on monthly savings
        monthly_savings = portfolio.get("monthly_savings", 0)
        if monthly_savings > 0:
            recommendations["sip_suggestion"] = {
                "amount": monthly_savings * 0.6,
                "frequency": "monthly",
                "recommended_allocation": [
                    {"type": "Nifty 50 Index Fund", "percentage": 40},
                    {"type": "Flexi Cap Fund", "percentage": 30},
                    {"type": "Mid Cap Fund", "percentage": 20},
                    {"type": "Debt Fund", "percentage": 10},
                ]
            }
        
        return recommendations
    
    def _generate_stock_recommendation(self, stock_data: Dict[str, Any]) -> str:
        """Generate a recommendation reason based on stock metrics."""
        reasons = []
        
        pe = stock_data.get("pe_ratio")
        if pe:
            try:
                pe_val = float(pe)
                if pe_val < 15:
                    reasons.append("undervalued (low P/E)")
                elif pe_val < 25:
                    reasons.append("fairly valued")
                elif pe_val > 50:
                    reasons.append("high growth expectations")
            except (ValueError, TypeError):
                pass
        
        div_yield = stock_data.get("dividend_yield", 0)
        try:
            div_val = float(div_yield) if div_yield else 0
            if div_val > 3:
                reasons.append(f"high dividend yield ({div_val:.1f}%)")
            elif div_val > 1.5:
                reasons.append(f"decent dividend ({div_val:.1f}%)")
        except (ValueError, TypeError):
            pass
        
        change = stock_data.get("change_percent", 0)
        try:
            change_val = float(change) if change else 0
            if change_val > 2:
                reasons.append("strong momentum today")
            elif change_val < -2:
                reasons.append("dip buying opportunity")
        except (ValueError, TypeError):
            pass
        
        # 52-week position
        high_52 = stock_data.get("52_week_high", 0)
        low_52 = stock_data.get("52_week_low", 0)
        current = stock_data.get("current_price", 0)
        
        if high_52 and low_52 and current:
            range_52 = high_52 - low_52
            if range_52 > 0:
                position = (current - low_52) / range_52
                if position > 0.9:
                    reasons.append("near 52-week high")
                elif position < 0.3:
                    reasons.append("near 52-week low - potential value")
        
        if not reasons:
            reasons.append(f"{stock_data.get('sector', 'Market')} sector play")
        
        return ", ".join(reasons[:3])
    
    def _get_generic_investment_advice(self, risk_profile: str) -> str:
        """Generate generic investment advice when real-time data unavailable."""
        advice_map = {
            "conservative": (
                "For a conservative approach, consider:\n"
                "• Large-cap stocks from banking (HDFC Bank, ICICI Bank) and IT sectors (TCS, Infosys)\n"
                "• Blue-chip companies with consistent dividends\n"
                "• Index funds tracking Nifty 50\n"
                "• 60% equity, 30% debt funds, 10% gold\n"
                "Start with SIP for rupee cost averaging."
            ),
            "moderate": (
                "For a balanced portfolio, consider:\n"
                "• Mix of large-cap (50%) and mid-cap (30%) stocks\n"
                "• Sectors: Banking, IT, FMCG, Pharma\n"
                "• Nifty 50 and Nifty Next 50 index funds\n"
                "• 70% equity, 20% debt, 10% gold\n"
                "Use SIP for systematic investing."
            ),
            "aggressive": (
                "For growth-focused investing, consider:\n"
                "• Mid-cap and small-cap stocks (higher risk, higher returns)\n"
                "• Growth sectors: Technology, EV, Renewable Energy\n"
                "• Flexi-cap and multi-cap funds\n"
                "• 80% equity, 10% debt, 10% alternatives\n"
                "Monitor quarterly and rebalance annually."
            )
        }
        return advice_map.get(risk_profile, advice_map["moderate"])
    
    async def _get_index_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get index data (Nifty, Sensex)."""
        if not YFINANCE_AVAILABLE:
            return None
        
        cache_key = f"index_{symbol}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            result = {
                "symbol": symbol,
                "name": info.get("shortName", symbol),
                "current_value": info.get("regularMarketPrice", 0),
                "previous_close": info.get("previousClose", 0),
                "change_percent": round(
                    ((info.get("regularMarketPrice", 0) - info.get("previousClose", 1)) / 
                     info.get("previousClose", 1)) * 100, 2
                ) if info.get("previousClose") else 0,
                "fetched_at": datetime.utcnow().isoformat()
            }
            
            self.cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Failed to fetch index data for {symbol}: {e}")
            return None
    
    async def search_stocks(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for stocks by name or symbol.
        
        Args:
            query: Search query (company name or symbol)
            
        Returns:
            List of matching stocks with real-time data
        """
        # Common Indian stocks for quick search
        common_stocks = {
            "reliance": "RELIANCE", "tcs": "TCS", "infosys": "INFY", "infy": "INFY",
            "hdfc": "HDFCBANK", "icici": "ICICIBANK", "sbi": "SBIN", "state bank": "SBIN",
            "itc": "ITC", "airtel": "BHARTIARTL", "bharti": "BHARTIARTL",
            "wipro": "WIPRO", "hcl": "HCLTECH", "tech mahindra": "TECHM",
            "maruti": "MARUTI", "tata motors": "TATAMOTORS", "bajaj": "BAJAJ-AUTO",
            "kotak": "KOTAKBANK", "axis": "AXISBANK", "indusind": "INDUSINDBK",
            "sun pharma": "SUNPHARMA", "dr reddy": "DRREDDY", "cipla": "CIPLA",
            "asian paints": "ASIANPAINT", "titan": "TITAN", "hindustan unilever": "HINDUNILVR",
            "hul": "HINDUNILVR", "nestle": "NESTLEIND", "britannia": "BRITANNIA",
            "zomato": "ZOMATO", "paytm": "PAYTM", "nykaa": "NYKAA",
            "adani": "ADANIENT", "adani ports": "ADANIPORTS", "adani green": "ADANIGREEN",
            "l&t": "LT", "larsen": "LT", "ultratech": "ULTRACEMCO",
            "power grid": "POWERGRID", "ntpc": "NTPC", "coal india": "COALINDIA",
            "ongc": "ONGC", "ioc": "IOC", "bpcl": "BPCL",
        }
        
        query_lower = query.lower()
        matched_symbols = []
        
        # Find matching stocks
        for key, symbol in common_stocks.items():
            if query_lower in key or query_lower in symbol.lower():
                if symbol not in matched_symbols:
                    matched_symbols.append(symbol)
        
        # Fetch real-time data for matches
        results = []
        for symbol in matched_symbols[:5]:
            data = await self.get_stock_price(symbol)
            if data:
                results.append(data)
        
        return results
    
    def get_nifty50_stocks(self) -> List[str]:
        """Get list of Nifty 50 stock symbols."""
        return [
            "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "HINDUNILVR",
            "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK",
            "ASIANPAINT", "MARUTI", "TITAN", "SUNPHARMA", "ULTRACEMCO",
            "WIPRO", "BAJFINANCE", "HCLTECH", "TECHM", "NESTLEIND",
            "TATAMOTORS", "M&M", "NTPC", "POWERGRID", "ONGC", "COALINDIA",
            "JSWSTEEL", "TATASTEEL", "ADANIENT", "ADANIPORTS", "BAJAJ-AUTO",
            "DRREDDY", "CIPLA", "DIVISLAB", "APOLLOHOSP", "EICHERMOT",
            "HEROMOTOCO", "BRITANNIA", "DABUR", "GRASIM", "HINDALCO",
            "INDUSINDBK", "BPCL", "IOC", "TATACONSUM", "BAJAJFINSV", "SBILIFE"
        ]


# Global instance
market_data = MarketDataService()
