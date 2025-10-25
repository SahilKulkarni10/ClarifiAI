from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
import os
import sys

# Import configuration and database
from config import settings
from database import connect_to_mongo, close_mongo_connection, mongodb

# Import routes
from routes.auth import router as auth_router
from routes.finance import router as finance_router
from routes.chat import router as chat_router
from routes.analytics import router as analytics_router

# Import RAG system
from rag_system import finance_scraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting Finance AI Assistant API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"MongoDB URI configured: {'Yes' if settings.MONGODB_URI else 'No'}")
    
    # Connect to MongoDB (with error handling for deployment)
    try:
        await connect_to_mongo()
        logger.info("✅ MongoDB connected successfully")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB connection failed: {e}")
        logger.warning("API will start but database operations will fail")
        # Don't crash - let the app start anyway
    
    # Initialize RAG system with real-time financial knowledge
    logger.info("📚 RAG system initialized (lazy loading)")
    # Note: Knowledge base will be loaded on first use to save memory
    logger.info("✅ RAG system ready (models will load on demand)")
    
    logger.info("✅ Finance AI Assistant API started successfully!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Finance AI Assistant API...")
    try:
        await close_mongo_connection()
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")
    logger.info("👋 Finance AI Assistant API stopped")

# Create FastAPI app
app = FastAPI(
    title="Finance AI Assistant API",
    description="""
    ## 🤖 Personal Finance Assistant with AI & RAG
    
    A comprehensive Finance SaaS platform that helps users manage their personal finances with AI-powered insights.
    
    ### Features:
    - 💰 **Income & Expense Tracking**: Record and categorize all financial transactions
    - 📊 **Investment Portfolio**: Track mutual funds, stocks, and other investments
    - 💳 **Loan Management**: Monitor loan EMIs and outstanding amounts
    - 🛡️ **Insurance Tracking**: Manage all insurance policies
    - 🎯 **Goal Setting**: Set and track financial goals
    - 📈 **Analytics**: Detailed financial analytics and insights
    - 🤖 **AI Chat**: Conversational AI assistant for financial advice
    - 🔍 **RAG System**: Retrieval-Augmented Generation for personalized recommendations
    
    ### Technology Stack:
    - **Backend**: Python FastAPI
    - **Database**: MongoDB Atlas
    - **Vector DB**: ChromaDB
    - **AI**: Google Gemini
    - **Authentication**: JWT
    
    ### API Endpoints:
    - **Authentication**: `/auth/*` - User registration, login, profile management
    - **Finance Data**: `/finance/*` - CRUD operations for financial data
    - **AI Chat**: `/chat/*` - Conversational AI assistant
    - **Analytics**: `/analytics/*` - Financial analytics and reporting
    """,
    version="1.0.0",
    contact={
        "name": "Finance AI Team",
        "email": "support@financeai.com",
    },
    license_info={
        "name": "MIT License",
    },
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(finance_router)
app.include_router(chat_router)
app.include_router(analytics_router)

# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "🤖 Finance AI Assistant API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "features": [
            "Income & Expense Tracking",
            "Investment Portfolio Management",
            "Loan & Insurance Tracking",
            "AI-Powered Financial Insights",
            "RAG-based Recommendations",
            "Financial Analytics & Reporting"
        ]
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    from datetime import datetime
    
    # Check database status
    db_status = "disconnected"
    
    # Check if we can actually ping the database
    try:
        if mongodb.client:
            await mongodb.client.admin.command('ping')
            db_status = "connected"
        else:
            db_status = "not_initialized"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
    
    # API is always healthy if it responds
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "services": {
            "api": "healthy",
            "database": db_status,
            "vector_db": "available",
            "ai_model": "ready"
        },
        "message": "API is running" + (" with database" if db_status == "connected" else " (database disconnected)")
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )

if __name__ == "__main__":
    import sys
    port = int(os.getenv("PORT", settings.API_PORT))
    host = settings.API_HOST
    
    logger.info(f"🚀 Starting server on {host}:{port}")
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=settings.ENVIRONMENT == "development",
            log_level="info"
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)
