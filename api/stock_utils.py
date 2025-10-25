import yfinance as yf
import httpx
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class StockDataFetcher:
    """Fetch real-time stock prices from NSE/BSE and international markets"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
        
    async def get_indian_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get Indian stock price from NSE
        
        Args:
            symbol: Stock symbol (e.g., 'ADANIENT' for Adani Enterprises)
        
        Returns:
            Dictionary with price data or None if not found
        """
        try:
            # Add .NS suffix for NSE stocks
            nse_symbol = f"{symbol}.NS"
            
            # Check cache first
            cache_key = f"indian_{symbol}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if (datetime.now() - timestamp).seconds < self.cache_duration:
                    logger.info(f"Returning cached data for {symbol}")
                    return cached_data
            
            # Fetch using yfinance in a thread to avoid blocking
            stock_data = await asyncio.to_thread(self._fetch_yfinance_data, nse_symbol)
            
            if stock_data:
                # Cache the result
                self.cache[cache_key] = (stock_data, datetime.now())
                return stock_data
            
            # Try BSE if NSE fails
            bse_symbol = f"{symbol}.BO"
            stock_data = await asyncio.to_thread(self._fetch_yfinance_data, bse_symbol)
            
            if stock_data:
                self.cache[cache_key] = (stock_data, datetime.now())
                return stock_data
            
            logger.warning(f"Could not fetch stock data for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Indian stock price for {symbol}: {e}")
            return None
    
    def _fetch_yfinance_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Synchronous function to fetch data from yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if not current_price:
                return None
            
            return {
                'symbol': symbol,
                'current_price': float(current_price),
                'currency': info.get('currency', 'INR'),
                'open': float(info.get('open', 0)) if info.get('open') else None,
                'high': float(info.get('dayHigh', 0)) if info.get('dayHigh') else None,
                'low': float(info.get('dayLow', 0)) if info.get('dayLow') else None,
                'previous_close': float(info.get('previousClose', 0)) if info.get('previousClose') else None,
                'change': float(info.get('regularMarketChange', 0)) if info.get('regularMarketChange') else None,
                'change_percent': float(info.get('regularMarketChangePercent', 0)) if info.get('regularMarketChangePercent') else None,
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE'),
                '52_week_high': float(info.get('fiftyTwoWeekHigh', 0)) if info.get('fiftyTwoWeekHigh') else None,
                '52_week_low': float(info.get('fiftyTwoWeekLow', 0)) if info.get('fiftyTwoWeekLow') else None,
                'company_name': info.get('longName', info.get('shortName', '')),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error in _fetch_yfinance_data for {symbol}: {e}")
            return None
    
    async def get_us_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get US stock price
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL' for Apple)
        
        Returns:
            Dictionary with price data or None if not found
        """
        try:
            # Check cache first
            cache_key = f"us_{symbol}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if (datetime.now() - timestamp).seconds < self.cache_duration:
                    logger.info(f"Returning cached data for {symbol}")
                    return cached_data
            
            # Fetch using yfinance in a thread to avoid blocking
            stock_data = await asyncio.to_thread(self._fetch_yfinance_data, symbol)
            
            if stock_data:
                # Cache the result
                self.cache[cache_key] = (stock_data, datetime.now())
                return stock_data
            
            logger.warning(f"Could not fetch US stock data for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching US stock price for {symbol}: {e}")
            return None
    
    async def get_currency_rate(self, from_currency: str = "USD", to_currency: str = "INR") -> Optional[float]:
        """
        Get currency exchange rate
        
        Args:
            from_currency: Source currency code (default: USD)
            to_currency: Target currency code (default: INR)
        
        Returns:
            Exchange rate or None if not found
        """
        try:
            # Check cache first
            cache_key = f"currency_{from_currency}_{to_currency}"
            if cache_key in self.cache:
                cached_rate, timestamp = self.cache[cache_key]
                if (datetime.now() - timestamp).seconds < self.cache_duration:
                    logger.info(f"Returning cached currency rate for {from_currency}/{to_currency}")
                    return cached_rate
            
            # Use yfinance to get forex data
            forex_symbol = f"{from_currency}{to_currency}=X"
            forex_data = await asyncio.to_thread(self._fetch_yfinance_data, forex_symbol)
            
            if forex_data and forex_data.get('current_price'):
                rate = forex_data['current_price']
                self.cache[cache_key] = (rate, datetime.now())
                return rate
            
            logger.warning(f"Could not fetch currency rate for {from_currency}/{to_currency}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching currency rate: {e}")
            return None
    
    async def search_stock_symbol(self, query: str) -> Optional[str]:
        """
        Search for stock symbol by company name
        
        Args:
            query: Company name or partial name
        
        Returns:
            Best matching symbol or None
        """
        # Common stock mappings for Indian companies
        indian_stock_map = {
            'adani enterprises': 'ADANIENT',
            'adani power': 'ADANIPOWER',
            'adani ports': 'ADANIPORTS',
            'adani green': 'ADANIGREEN',
            'reliance': 'RELIANCE',
            'tcs': 'TCS',
            'infosys': 'INFY',
            'hdfc bank': 'HDFCBANK',
            'icici bank': 'ICICIBANK',
            'bharti airtel': 'BHARTIARTL',
            'itc': 'ITC',
            'sbi': 'SBIN',
            'bajaj finance': 'BAJFINANCE',
            'hindustan unilever': 'HINDUNILVR',
            'larsen toubro': 'LT',
            'asian paints': 'ASIANPAINT',
            'maruti suzuki': 'MARUTI',
            'titan': 'TITAN',
            'wipro': 'WIPRO',
            'tata motors': 'TATAMOTORS',
            'tata steel': 'TATASTEEL',
            'tata power': 'TATAPOWER',
        }
        
        # Common US stock mappings
        us_stock_map = {
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'amazon': 'AMZN',
            'meta': 'META',
            'facebook': 'META',
            'tesla': 'TSLA',
            'nvidia': 'NVDA',
            'netflix': 'NFLX',
        }
        
        query_lower = query.lower().strip()
        
        # Check Indian stocks first
        for name, symbol in indian_stock_map.items():
            if name in query_lower or query_lower in name:
                return symbol
        
        # Check US stocks
        for name, symbol in us_stock_map.items():
            if name in query_lower or query_lower in name:
                return symbol
        
        # If exact match not found, return the query as-is (might be a valid symbol)
        return query.upper()
    
    async def calculate_investment_recommendation(
        self, 
        stock_symbol: str,
        investment_amount: float,
        portfolio_percentage: float = 5.0,
        total_portfolio_value: float = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate investment recommendation with current stock price
        
        Args:
            stock_symbol: Stock symbol
            investment_amount: Amount to invest (INR)
            portfolio_percentage: Target portfolio percentage
            total_portfolio_value: Total portfolio value
        
        Returns:
            Dictionary with investment recommendation
        """
        try:
            # Try to fetch as Indian stock first
            stock_data = await self.get_indian_stock_price(stock_symbol)
            is_indian = True
            
            # If not found, try US stock
            if not stock_data:
                stock_data = await self.get_us_stock_price(stock_symbol)
                is_indian = False
            
            if not stock_data:
                logger.warning(f"Could not fetch stock data for {stock_symbol}")
                return None
            
            current_price = stock_data['current_price']
            currency = stock_data.get('currency', 'INR')
            
            # Convert to INR if needed
            price_in_inr = current_price
            if currency == 'USD':
                exchange_rate = await self.get_currency_rate('USD', 'INR')
                if exchange_rate:
                    price_in_inr = current_price * exchange_rate
                else:
                    # Fallback exchange rate
                    price_in_inr = current_price * 83.5
            
            # Calculate recommended investment amount if portfolio value is provided
            if total_portfolio_value > 0:
                recommended_amount = (portfolio_percentage / 100) * total_portfolio_value
            else:
                recommended_amount = investment_amount
            
            # Calculate number of shares
            num_shares = int(recommended_amount / price_in_inr)
            total_investment = num_shares * price_in_inr
            
            recommendation = {
                'stock_symbol': stock_symbol,
                'company_name': stock_data.get('company_name', stock_symbol),
                'current_price': current_price,
                'currency': currency,
                'price_in_inr': round(price_in_inr, 2),
                'exchange_rate': await self.get_currency_rate('USD', 'INR') if currency == 'USD' else 1.0,
                'recommended_shares': num_shares,
                'total_investment': round(total_investment, 2),
                'portfolio_percentage': portfolio_percentage,
                'market': 'NSE/BSE' if is_indian else 'US Market',
                'change_percent': stock_data.get('change_percent', 0),
                'pe_ratio': stock_data.get('pe_ratio'),
                '52_week_high': stock_data.get('52_week_high'),
                '52_week_low': stock_data.get('52_week_low'),
                'sector': stock_data.get('sector', ''),
                'fetched_at': stock_data.get('fetched_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            }
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error calculating investment recommendation: {e}")
            return None
    
    async def get_sector_based_recommendations(
        self, 
        missing_sectors: List[str],
        total_portfolio_value: float,
        num_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get stock recommendations based on missing sectors in portfolio
        
        Args:
            missing_sectors: List of sectors that are missing or underweight
            total_portfolio_value: Total portfolio value for allocation
            num_recommendations: Number of stocks to recommend
            
        Returns:
            List of stock recommendations with real-time data
        """
        try:
            # Comprehensive sector-to-stock mapping
            sector_stocks = {
                'Technology': ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM'],
                'Banking': ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK'],
                'FMCG': ['HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'DABUR'],
                'Energy': ['RELIANCE', 'ONGC', 'BPCL', 'COALINDIA', 'NTPC'],
                'Healthcare': ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'AUROPHARMA', 'DIVISLAB'],
                'Automobile': ['TATAMOTORS', 'MARUTI', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO'],
                'Telecom': ['BHARTIARTL', 'IDEA'],
                'Infrastructure': ['LT', 'ADANIENT', 'ADANIPORTS', 'ULTRACEMCO'],
                'Financial Services': ['BAJFINANCE', 'BAJAJFINSV', 'SBILIFE', 'HDFCLIFE'],
                'Metals': ['TATASTEEL', 'HINDALCO', 'JINDALSTEL', 'VEDL']
            }
            
            recommendations = []
            stocks_to_fetch = []
            
            # Select stocks from missing sectors
            for sector in missing_sectors:
                if sector in sector_stocks:
                    # Pick top stock from each missing sector
                    stocks_to_fetch.append({
                        'symbol': sector_stocks[sector][0],
                        'sector': sector
                    })
            
            # If we need more recommendations, add diversified picks
            if len(stocks_to_fetch) < num_recommendations:
                popular_picks = [
                    {'symbol': 'RELIANCE', 'sector': 'Energy'},
                    {'symbol': 'TCS', 'sector': 'Technology'},
                    {'symbol': 'HDFCBANK', 'sector': 'Banking'},
                    {'symbol': 'INFY', 'sector': 'Technology'},
                    {'symbol': 'HINDUNILVR', 'sector': 'FMCG'},
                ]
                
                for pick in popular_picks:
                    if len(stocks_to_fetch) >= num_recommendations:
                        break
                    if not any(s['symbol'] == pick['symbol'] for s in stocks_to_fetch):
                        stocks_to_fetch.append(pick)
            
            # Fetch real-time data for each stock
            for stock_info in stocks_to_fetch[:num_recommendations]:
                try:
                    recommendation = await self.calculate_investment_recommendation(
                        stock_symbol=stock_info['symbol'],
                        investment_amount=50000,
                        portfolio_percentage=5.0,
                        total_portfolio_value=total_portfolio_value
                    )
                    
                    if recommendation:
                        recommendation['recommended_sector'] = stock_info['sector']
                        recommendations.append(recommendation)
                        
                except Exception as e:
                    logger.warning(f"Could not fetch data for {stock_info['symbol']}: {e}")
                    continue
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting sector-based recommendations: {e}")
            return []

# Global instance
stock_fetcher = StockDataFetcher()
