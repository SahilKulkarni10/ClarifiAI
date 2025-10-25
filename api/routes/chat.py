from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from models import ChatMessage, ChatResponse
from auth import get_current_user
from rag_system import vector_store, finance_scraper
from stock_utils import stock_fetcher
import logging
import json
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["AI Chat"])

@router.post("/message", response_model=ChatResponse)
async def chat_with_ai(
    chat_data: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Chat with AI assistant"""
    try:
        user_id = current_user["sub"]
        
        # Generate AI response using RAG
        response_data = await vector_store.generate_response(user_id, chat_data.message)
        
        logger.info(f"AI chat response generated for user: {user_id}")
        
        return ChatResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/message/stream")
async def chat_with_ai_stream(
    chat_data: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Stream AI chat response word by word"""
    async def generate_stream():
        try:
            user_id = current_user["sub"]
            
            # Generate AI response using RAG
            response_data = await vector_store.generate_response(user_id, chat_data.message)
            
            # Stream the response word by word
            words = response_data['response'].split()
            
            for i, word in enumerate(words):
                # Add space after word (except for last word)
                chunk = word + (' ' if i < len(words) - 1 else '')
                
                # Send word as JSON
                yield f"data: {json.dumps({'type': 'word', 'content': chunk})}\n\n"
                
                # Small delay to simulate typing (adjust speed here)
                await asyncio.sleep(0.10)  # 30ms per word
            
            # Send suggestions at the end if available
            if 'suggestions' in response_data and response_data['suggestions']:
                yield f"data: {json.dumps({'type': 'suggestions', 'content': response_data['suggestions']})}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming AI chat: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': 'Sorry, I encountered an error. Please try again.'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.post("/refresh-knowledge", response_model=dict)
async def refresh_knowledge_base(current_user: dict = Depends(get_current_user)):
    """Refresh knowledge base with latest real-time financial data"""
    try:
        logger.info(f"Knowledge base refresh triggered by user: {current_user['sub']}")
        
        # Refresh knowledge base with real-time data
        success = await finance_scraper.refresh_knowledge_base()
        
        if success:
            return {
                "status": "success",
                "message": "Knowledge base refreshed with latest financial data",
                "timestamp": "2025-10-06"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to refresh knowledge base"
            )
        
    except Exception as e:
        logger.error(f"Error refreshing knowledge base: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing knowledge base: {str(e)}"
        )

@router.get("/suggestions", response_model=dict)
async def get_chat_suggestions(current_user: dict = Depends(get_current_user)):
    """Get chat suggestions for user"""
    try:
        # Return default suggestions
        suggestions = [
            "What's my current financial summary?",
            "How much did I spend on food this month?",
            "Show me my investment portfolio performance",
            "Which loan should I pay off first?",
            "How can I improve my savings rate?",
            "What's my expense breakdown by category?",
            "Am I on track to meet my financial goals?",
            "Give me tax saving investment recommendations",
            "How much emergency fund do I need?",
            "Should I invest more in mutual funds or stocks?"
        ]
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Error getting chat suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/stock-price/{symbol}", response_model=dict)
async def get_stock_price(
    symbol: str,
    current_user: dict = Depends(get_current_user)
):
    """Get real-time stock price for a given symbol"""
    try:
        # Try Indian stock first
        stock_data = await stock_fetcher.get_indian_stock_price(symbol)
        
        # If not found, try US stock
        if not stock_data:
            stock_data = await stock_fetcher.get_us_stock_price(symbol)
        
        if not stock_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock data not found for symbol: {symbol}"
            )
        
        return {
            "status": "success",
            "data": stock_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock price: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/investment-recommendation", response_model=dict)
async def get_investment_recommendation(
    stock_symbol: str,
    investment_amount: float = 50000,
    portfolio_percentage: float = 5.0,
    current_user: dict = Depends(get_current_user)
):
    """Get investment recommendation with real-time stock price"""
    try:
        from database import get_database
        
        user_id = current_user["sub"]
        db = get_database()
        
        # Get total portfolio value
        all_investments = await db.investments.find(
            {"user_id": user_id}
        ).to_list(None)
        
        total_portfolio = sum(inv.get('current_value', inv.get('amount', 0)) for inv in all_investments)
        
        # Get investment recommendation
        recommendation = await stock_fetcher.calculate_investment_recommendation(
            stock_symbol=stock_symbol,
            investment_amount=investment_amount,
            portfolio_percentage=portfolio_percentage,
            total_portfolio_value=total_portfolio
        )
        
        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not fetch stock data for symbol: {stock_symbol}"
            )
        
        return {
            "status": "success",
            "recommendation": recommendation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating investment recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
