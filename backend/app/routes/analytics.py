"""
Analytics Routes
Handles financial analytics and reporting endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from app.core.database import get_database
from app.core.dependencies import get_current_user_id
from app.models.finance import FinancialSummary, ExpenseAnalytics, InvestmentAnalytics
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=FinancialSummary)
async def get_financial_summary(
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM format)"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get comprehensive financial summary.
    
    Returns:
    - Total income, expenses, investments, loans
    - Net worth calculation
    - Savings rate
    - Monthly cash flow
    
    Optionally filter by a specific month.
    """
    service = AnalyticsService(db)
    
    try:
        return await service.get_financial_summary(user_id, month)
    except Exception as e:
        logger.error(f"Summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate financial summary"
        )


@router.get("/expenses", response_model=ExpenseAnalytics)
async def get_expense_analytics(
    months: int = Query(6, ge=1, le=24, description="Number of months to analyze"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get expense analytics with category breakdown and trends.
    
    Returns:
    - Category-wise expense breakdown
    - Monthly expense trend
    - Top 10 expenses
    """
    service = AnalyticsService(db)
    
    try:
        return await service.get_expense_analytics(user_id, months)
    except Exception as e:
        logger.error(f"Expense analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate expense analytics"
        )


@router.get("/investments", response_model=InvestmentAnalytics)
async def get_investment_analytics(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get investment analytics with portfolio breakdown and performance.
    
    Returns:
    - Portfolio allocation by type
    - Total invested vs current value
    - Individual investment performance
    """
    service = AnalyticsService(db)
    
    try:
        return await service.get_investment_analytics(user_id)
    except Exception as e:
        logger.error(f"Investment analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate investment analytics"
        )


@router.get("/trends")
async def get_monthly_trends(
    months: int = Query(12, ge=1, le=36, description="Number of months to analyze"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get monthly income, expense, and savings trends.
    
    Returns:
    - Month-wise breakdown
    - Average monthly values
    """
    service = AnalyticsService(db)
    
    try:
        return await service.get_monthly_trends(user_id, months)
    except Exception as e:
        logger.error(f"Trends error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate trend analysis"
        )


@router.get("/reports")
async def get_financial_reports(
    report_type: str = Query("monthly", description="Type of report: monthly, quarterly, yearly"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Generate comprehensive financial report.
    
    Returns:
    - Complete financial summary
    - Expense breakdown
    - Investment summary
    - Trends
    - AI-generated insights
    """
    service = AnalyticsService(db)
    
    try:
        return await service.get_reports(user_id, report_type)
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate financial report"
        )
