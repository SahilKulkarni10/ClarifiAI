"""
Chat Models
Pydantic models for AI chat functionality.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual chat message."""
    role: MessageRole
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat message request from user."""
    message: str = Field(..., min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    """Chat response from AI assistant."""
    response: str
    timestamp: str
    sources_used: Optional[List[str]] = None
    confidence: Optional[float] = None


class ChatHistory(BaseModel):
    """User's chat history."""
    messages: List[ChatMessage]


class ChatContext(BaseModel):
    """Context for RAG-enhanced chat."""
    user_query: str
    financial_context: Optional[dict] = None
    retrieved_documents: Optional[List[str]] = None
    user_profile: Optional[dict] = None


# =============================================================================
# RAG DOCUMENT MODELS
# =============================================================================

class FinancialDocumentCategory(str, Enum):
    """Categories for financial knowledge documents."""
    TAX = "tax"
    INSURANCE = "insurance"
    INVESTMENT = "investment"
    LOAN = "loan"
    SAVINGS = "savings"
    BUDGETING = "budgeting"
    RETIREMENT = "retirement"
    GENERAL = "general"


class FinancialDocument(BaseModel):
    """Financial knowledge document for RAG."""
    id: Optional[str] = None
    title: str
    content: str
    category: FinancialDocumentCategory
    source: str
    last_updated: str
    metadata: Optional[dict] = None


class DocumentChunk(BaseModel):
    """Chunked document for embedding."""
    chunk_id: str
    document_id: str
    content: str
    category: str
    metadata: Optional[dict] = None


class RAGSearchResult(BaseModel):
    """Search result from RAG retrieval."""
    content: str
    category: str
    source: str
    relevance_score: float


# =============================================================================
# RECOMMENDATION MODELS
# =============================================================================

class RecommendationType(str, Enum):
    """Types of financial recommendations."""
    INVESTMENT = "investment"
    SAVINGS = "savings"
    DEBT_MANAGEMENT = "debt_management"
    INSURANCE = "insurance"
    TAX_PLANNING = "tax_planning"
    GOAL_PLANNING = "goal_planning"
    BUDGET = "budget"
    GENERAL = "general"


class Recommendation(BaseModel):
    """Financial recommendation."""
    id: Optional[str] = None
    type: RecommendationType
    title: str
    summary: str
    detailed_explanation: str
    action_items: List[str]
    assumptions: List[str]
    data_sources: List[str]
    confidence_level: str  # high, medium, low
    created_at: Optional[str] = None


class RecommendationRequest(BaseModel):
    """Request for financial recommendation."""
    query: str
    context_type: Optional[RecommendationType] = None
    include_projections: bool = False


class RecommendationResponse(BaseModel):
    """Response containing recommendation."""
    recommendation: Recommendation
    related_suggestions: Optional[List[str]] = None
