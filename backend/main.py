"""
ClariFi AI Backend
Main FastAPI Application

A RAG-powered financial advisory system that prioritizes
correctness, explainability, and safety.
"""

import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
import uvicorn

from app.core.config import settings
from app.core.database import database
from app.services.rag_engine import rag_engine
from app.services.llm_service import llm_service
from app.services.market_data import market_data

# Import routes
from app.routes import auth, finance, chat, analytics, market


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO"
)
logger.add(
    "logs/clarifi_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level="DEBUG"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    
    Startup:
    - Connect to MongoDB
    - Initialize RAG engine with ChromaDB
    - Initialize Gemini LLM
    
    Shutdown:
    - Close database connections
    - Cleanup resources
    """
    logger.info("Starting ClariFi AI Backend...")
    
    # Startup
    try:
        # Connect to MongoDB
        await database.connect()
        logger.info("MongoDB connection established")
        
        # Initialize RAG engine
        await rag_engine.initialize()
        logger.info("RAG engine initialized")
        
        # Initialize LLM service
        await llm_service.initialize()
        logger.info("LLM service initialized")
        
        logger.info("=" * 50)
        logger.info("ClariFi AI Backend is ready!")
        logger.info(f"API Docs: http://localhost:{settings.port}/docs")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down ClariFi AI Backend...")
    
    try:
        await database.disconnect()
        await market_data.close()
        logger.info("Resources cleaned up successfully")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Create FastAPI app
app = FastAPI(
    title="ClariFi AI API",
    description="""
    ## Financial Advisory AI Backend
    
    ClariFi AI is a RAG-powered financial advisory system that provides
    trustworthy, explainable, and safe financial guidance.
    
    ### Features
    
    - **Financial Data Management**: Track income, expenses, investments, loans, insurance, and goals
    - **AI-Powered Chat**: Get personalized financial advice using RAG and LLM
    - **Analytics**: Comprehensive financial analytics and insights
    - **Real-time Data**: Integration with market data APIs
    
    ### Architecture
    
    - All financial calculations are done by a deterministic rules engine
    - The LLM is used ONLY for explanation, never for calculations
    - RAG ensures responses are grounded in verified financial knowledge
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS Configuration - Must be added before routes
# Allow all origins in development for easier testing
origins = settings.cors_origins if settings.environment == "production" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with clear messages."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again later."
        }
    )


# Include routers
app.include_router(auth.router)
app.include_router(finance.router)
app.include_router(chat.router)
app.include_router(analytics.router)
app.include_router(market.router)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check."""
    return {
        "name": "ClariFi AI API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    health = {
        "status": "healthy",
        "services": {
            "database": "unknown",
            "rag_engine": "unknown",
            "llm_service": "unknown"
        }
    }
    
    # Check database
    try:
        if database._client:
            await database._client.admin.command('ping')
            health["services"]["database"] = "healthy"
        else:
            health["services"]["database"] = "not connected"
    except Exception as e:
        health["services"]["database"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    # Check RAG engine
    try:
        if rag_engine._initialized:
            health["services"]["rag_engine"] = "healthy"
        else:
            health["services"]["rag_engine"] = "not initialized"
    except:
        health["services"]["rag_engine"] = "unhealthy"
    
    # Check LLM service
    try:
        if llm_service._initialized:
            health["services"]["llm_service"] = "healthy" if llm_service.model else "limited (no API key)"
        else:
            health["services"]["llm_service"] = "not initialized"
    except:
        health["services"]["llm_service"] = "unhealthy"
    
    return health


# Run with uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
