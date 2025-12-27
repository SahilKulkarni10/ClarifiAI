"""
Chat Routes
Handles AI chat functionality with RAG integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from app.core.database import get_database
from app.core.dependencies import get_current_user_id
from app.models.chat import ChatRequest, ChatResponse, ChatHistory
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Send a message and get AI response.
    
    The AI response is generated using:
    1. RAG (Retrieval-Augmented Generation) from financial knowledge base
    2. User's financial data for context
    3. Pre-calculated results from financial rules engine
    4. Gemini LLM for natural language response
    
    The LLM never makes calculations - all financial calculations
    are done by the deterministic rules engine.
    """
    service = ChatService(db)
    
    try:
        response = await service.send_message(
            user_id=user_id,
            message=request.message
        )
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


@router.get("/history", response_model=ChatHistory)
async def get_chat_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get chat history for the current user.
    
    Returns all messages in chronological order.
    """
    service = ChatService(db)
    
    try:
        return await service.get_history(user_id)
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch history"
        )


@router.delete("/clear")
async def clear_chat_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Clear all chat history for the current user.
    
    This cannot be undone.
    """
    service = ChatService(db)
    
    try:
        await service.clear_history(user_id)
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        logger.error(f"History clear error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear history"
        )
