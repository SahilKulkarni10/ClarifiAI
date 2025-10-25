from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from models import FinancialSummary, ExpenseAnalytics, InvestmentAnalytics
from auth import get_current_user
from database import get_database
from utils import prepare_date_range_for_mongo
from datetime import datetime, date, timedelta
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary", response_model=FinancialSummary)
async def get_financial_summary(
    current_user: dict = Depends(get_current_user),
    month: Optional[str] = Query(default=None, description="YYYY-MM format")
):
    """Get financial summary"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Set date range
        if month:
            start_date = datetime.strptime(f"{month}-01", "%Y-%m-%d").date()
            # Get last day of month
            if start_date.month == 12:
                end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
        else:
            # Current month
            today = date.today()
            start_date = date(today.year, today.month, 1)
            end_date = today
        
        # Calculate total income
        date_range = prepare_date_range_for_mongo(start_date, end_date)
        income_pipeline = [
            {"$match": {
                "user_id": user_id,
                "date": date_range
            }},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        income_result = await db.income.aggregate(income_pipeline).to_list(1)
        total_income = income_result[0]["total"] if income_result else 0
        
        # Calculate total expenses
        expense_pipeline = [
            {"$match": {
                "user_id": user_id,
                "date": date_range
            }},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        expense_result = await db.expenses.aggregate(expense_pipeline).to_list(1)
        total_expenses = expense_result[0]["total"] if expense_result else 0
        
        # Calculate total investments
        investment_pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        investment_result = await db.investments.aggregate(investment_pipeline).to_list(1)
        total_investments = investment_result[0]["total"] if investment_result else 0
        
        # Calculate total loan outstanding
        loan_pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total": {"$sum": "$outstanding"}}}
        ]
        loan_result = await db.loans.aggregate(loan_pipeline).to_list(1)
        total_loans = loan_result[0]["total"] if loan_result else 0
        
        # Calculate current investment values
        investment_cursor = db.investments.find({"user_id": user_id})
        current_investment_value = 0
        async for inv in investment_cursor:
            current_investment_value += inv.get("current_value", inv.get("amount", 0))
        
        # Calculate metrics
        net_worth = current_investment_value - total_loans
        monthly_cash_flow = total_income - total_expenses
        savings_rate = (monthly_cash_flow / total_income * 100) if total_income > 0 else 0
        
        return FinancialSummary(
            total_income=total_income,
            total_expenses=total_expenses,
            total_investments=total_investments,
            total_loans=total_loans,
            net_worth=net_worth,
            savings_rate=savings_rate,
            monthly_cash_flow=monthly_cash_flow
        )
        
    except Exception as e:
        logger.error(f"Error calculating financial summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/expenses", response_model=ExpenseAnalytics)
async def get_expense_analytics(
    current_user: dict = Depends(get_current_user),
    months: int = Query(default=6, le=12, description="Number of months to analyze")
):
    """Get expense analytics"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Calculate date range
        end_date = date.today()
        start_date = date(end_date.year, end_date.month - months + 1, 1) if end_date.month > months else date(end_date.year - 1, end_date.month - months + 13, 1)
        date_range = prepare_date_range_for_mongo(start_date, end_date)
        
        # Get category breakdown
        category_pipeline = [
            {"$match": {
                "user_id": user_id,
                "date": date_range
            }},
            {"$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"}
            }},
            {"$sort": {"total": -1}}
        ]
        category_result = await db.expenses.aggregate(category_pipeline).to_list(20)
        category_breakdown = {item["_id"]: item["total"] for item in category_result}
        
        # Get monthly trend
        monthly_pipeline = [
            {"$match": {
                "user_id": user_id,
                "date": date_range
            }},
            {"$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"}
                },
                "total": {"$sum": "$amount"}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        monthly_result = await db.expenses.aggregate(monthly_pipeline).to_list(12)
        monthly_trend = [
            {
                "month": f"{item['_id']['year']}-{item['_id']['month']:02d}",
                "amount": item["total"]
            }
            for item in monthly_result
        ]
        
        # Get top expenses
        top_expenses_pipeline = [
            {"$match": {
                "user_id": user_id,
                "date": date_range
            }},
            {"$sort": {"amount": -1}},
            {"$limit": 10},
            {"$project": {
                "amount": 1,
                "description": 1,
                "category": 1,
                "date": 1,
                "merchant": 1
            }}
        ]
        top_expenses_result = await db.expenses.aggregate(top_expenses_pipeline).to_list(10)
        top_expenses = []
        for expense in top_expenses_result:
            expense["_id"] = str(expense["_id"])
            top_expenses.append(expense)
        
        return ExpenseAnalytics(
            category_breakdown=category_breakdown,
            monthly_trend=monthly_trend,
            top_expenses=top_expenses
        )
        
    except Exception as e:
        logger.error(f"Error calculating expense analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/investments", response_model=InvestmentAnalytics)
async def get_investment_analytics(current_user: dict = Depends(get_current_user)):
    """Get investment analytics"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Get portfolio breakdown by type
        portfolio_pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$type",
                "total_invested": {"$sum": "$amount"},
                "current_value": {"$sum": {"$ifNull": ["$current_value", "$amount"]}}
            }}
        ]
        portfolio_result = await db.investments.aggregate(portfolio_pipeline).to_list(20)
        
        portfolio_breakdown = {}
        total_invested = 0
        current_value = 0
        
        for item in portfolio_result:
            portfolio_breakdown[item["_id"]] = item["current_value"]
            total_invested += item["total_invested"]
            current_value += item["current_value"]
        
        # Calculate returns
        returns = current_value - total_invested
        returns_percentage = (returns / total_invested * 100) if total_invested > 0 else 0
        
        return InvestmentAnalytics(
            portfolio_breakdown=portfolio_breakdown,
            total_invested=total_invested,
            current_value=current_value,
            returns=returns,
            returns_percentage=returns_percentage
        )
        
    except Exception as e:
        logger.error(f"Error calculating investment analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/spending-trends", response_model=dict)
async def get_spending_trends(
    current_user: dict = Depends(get_current_user),
    months: int = Query(default=12, le=24)
):
    """Get detailed spending trends"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Calculate date range
        end_date = date.today()
        start_date = date(end_date.year - 1, end_date.month, 1) if months >= 12 else date(end_date.year, end_date.month - months + 1, 1)
        
        # Convert to datetime for MongoDB queries
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get spending by category and month
        pipeline = [
            {"$match": {
                "user_id": user_id,
                "date": {"$gte": start_datetime, "$lte": end_datetime}
            }},
            {"$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"},
                    "category": "$category"
                },
                "amount": {"$sum": "$amount"}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        result = await db.expenses.aggregate(pipeline).to_list(1000)
        
        # Organize data
        trends = defaultdict(list)
        for item in result:
            month_key = f"{item['_id']['year']}-{item['_id']['month']:02d}"
            category = item['_id']['category']
            trends[category].append({
                "month": month_key,
                "amount": item["amount"]
            })
        
        return {"trends": dict(trends)}
        
    except Exception as e:
        logger.error(f"Error calculating spending trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/goal-progress", response_model=dict)
async def get_goal_progress(current_user: dict = Depends(get_current_user)):
    """Get financial goal progress"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Get all goals
        cursor = db.goals.find({"user_id": user_id}).sort("target_date", 1)
        
        goals_progress = []
        async for goal in cursor:
            progress_percentage = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
            
            # Calculate days remaining
            today = date.today()
            target_date = goal["target_date"]
            if isinstance(target_date, datetime):
                target_date = target_date.date()
            days_remaining = (target_date - today).days
            
            # Calculate required monthly savings
            months_remaining = max(1, days_remaining / 30)
            remaining_amount = goal["target_amount"] - goal["current_amount"]
            required_monthly_savings = remaining_amount / months_remaining if months_remaining > 0 else 0
            
            goals_progress.append({
                "id": str(goal["_id"]),
                "title": goal.get("title", goal.get("name", "Untitled Goal")),
                "target_amount": goal["target_amount"],
                "current_amount": goal["current_amount"],
                "progress_percentage": progress_percentage,
                "days_remaining": days_remaining,
                "required_monthly_savings": required_monthly_savings,
                "target_date": goal["target_date"],
                "on_track": progress_percentage >= (100 - (days_remaining / max(1, (target_date - goal.get("created_at", datetime.utcnow()).date()).days) * 100)) if days_remaining > 0 else True
            })
        
        return {"goals": goals_progress}
        
    except Exception as e:
        logger.error(f"Error calculating goal progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/income", response_model=dict)
async def get_income_analytics(
    current_user: dict = Depends(get_current_user),
    months: int = Query(default=6, le=12)
):
    """Get income analytics"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Calculate date range
        end_date = date.today()
        start_date = date(end_date.year, end_date.month - months + 1, 1) if end_date.month > months else date(end_date.year - 1, end_date.month - months + 13, 1)
        
        # Convert to datetime for MongoDB queries
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get source breakdown
        source_pipeline = [
            {"$match": {
                "user_id": user_id,
                "date": {"$gte": start_datetime, "$lte": end_datetime}
            }},
            {"$group": {
                "_id": "$source",
                "total": {"$sum": "$amount"}
            }},
            {"$sort": {"total": -1}}
        ]
        source_result = await db.income.aggregate(source_pipeline).to_list(20)
        source_breakdown = {item["_id"]: item["total"] for item in source_result}
        
        # Get monthly trend
        monthly_pipeline = [
            {"$match": {
                "user_id": user_id,
                "date": {"$gte": start_datetime, "$lte": end_datetime}
            }},
            {"$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"}
                },
                "total": {"$sum": "$amount"}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        monthly_result = await db.income.aggregate(monthly_pipeline).to_list(12)
        monthly_trend = [
            {
                "month": f"{item['_id']['month']:02d}/{item['_id']['year']}",
                "year": item['_id']['year'],
                "month_num": item['_id']['month'],
                "amount": item["total"]
            }
            for item in monthly_result
        ]
        
        return {
            "source_breakdown": source_breakdown,
            "monthly_trend": monthly_trend
        }
        
    except Exception as e:
        logger.error(f"Error calculating income analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/monthly-comparison", response_model=dict)
async def get_monthly_comparison(
    current_user: dict = Depends(get_current_user),
    months: int = Query(default=6, le=12)
):
    """Get monthly income vs expense comparison"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Calculate date range
        end_date = date.today()
        start_date = date(end_date.year, end_date.month - months + 1, 1) if end_date.month > months else date(end_date.year - 1, end_date.month - months + 13, 1)
        
        # Convert to datetime for MongoDB queries
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get monthly income
        income_pipeline = [
            {"$match": {
                "user_id": user_id,
                "date": {"$gte": start_datetime, "$lte": end_datetime}
            }},
            {"$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"}
                },
                "total": {"$sum": "$amount"}
            }}
        ]
        income_result = await db.income.aggregate(income_pipeline).to_list(12)
        income_by_month = {f"{item['_id']['year']}-{item['_id']['month']:02d}": item["total"] for item in income_result}
        
        # Get monthly expenses
        expense_pipeline = [
            {"$match": {
                "user_id": user_id,
                "date": {"$gte": start_datetime, "$lte": end_datetime}
            }},
            {"$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"}
                },
                "total": {"$sum": "$amount"}
            }}
        ]
        expense_result = await db.expenses.aggregate(expense_pipeline).to_list(12)
        expense_by_month = {f"{item['_id']['year']}-{item['_id']['month']:02d}": item["total"] for item in expense_result}
        
        # Create comparison data
        comparison_data = []
        current_date = start_date
        while current_date <= end_date:
            month_key = f"{current_date.year}-{current_date.month:02d}"
            income = income_by_month.get(month_key, 0)
            expenses = expense_by_month.get(month_key, 0)
            
            comparison_data.append({
                "month": current_date.month,
                "year": current_date.year,
                "month_name": current_date.strftime("%b %Y"),
                "income": income,
                "expenses": expenses,
                "savings": income - expenses,
                "savings_rate": (income - expenses) / income * 100 if income > 0 else 0
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return {"data": comparison_data}
        
    except Exception as e:
        logger.error(f"Error calculating monthly comparison: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
