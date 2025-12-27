"""
Analytics Service
Handles financial analytics and reporting.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta

from app.models.finance import (
    FinancialSummary,
    ExpenseAnalytics,
    InvestmentAnalytics,
    MonthlyTrend,
    InvestmentPerformance,
    ExpenseResponse
)
from app.services.financial_rules import financial_rules


class AnalyticsService:
    """Service for financial analytics operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def _get_user_object_id(self, user_id: str) -> ObjectId:
        """Convert user_id string to ObjectId."""
        try:
            return ObjectId(user_id)
        except:
            return user_id
    
    async def get_financial_summary(
        self,
        user_id: str,
        month: Optional[str] = None
    ) -> FinancialSummary:
        """
        Get comprehensive financial summary.
        
        Args:
            user_id: User's ID
            month: Optional month filter (YYYY-MM format)
        """
        user_oid = await self._get_user_object_id(user_id)
        
        # Initialize totals
        total_income = 0
        total_expenses = 0
        total_investments = 0
        total_loans = 0
        monthly_income = 0
        monthly_expenses = 0
        
        # Get date range for filtering
        if month:
            try:
                filter_date = parse_date(month + "-01")
                start_date = filter_date.replace(day=1)
                end_date = (start_date + relativedelta(months=1))
            except:
                start_date = None
                end_date = None
        else:
            # Current month
            today = datetime.now()
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + relativedelta(months=1)
        
        # Aggregate income
        async for doc in self.db.income.find({"user_id": user_oid}):
            amount = doc.get("amount", 0)
            total_income += amount
            
            # Check if in date range
            try:
                doc_date = parse_date(doc.get("date", ""))
                if start_date and end_date and start_date <= doc_date < end_date:
                    monthly_income += amount
            except:
                pass
        
        # Aggregate expenses
        async for doc in self.db.expenses.find({"user_id": user_oid}):
            amount = doc.get("amount", 0)
            total_expenses += amount
            
            # Check if in date range
            try:
                doc_date = parse_date(doc.get("date", ""))
                if start_date and end_date and start_date <= doc_date < end_date:
                    monthly_expenses += amount
            except:
                pass
        
        # Aggregate investments (current value)
        async for doc in self.db.investments.find({"user_id": user_oid}):
            total_investments += doc.get("current_value", doc.get("amount", 0))
        
        # Aggregate loan outstanding
        async for doc in self.db.loans.find({"user_id": user_oid}):
            total_loans += doc.get("outstanding", 0)
        
        # Calculate derived metrics
        net_worth = total_investments - total_loans + (total_income - total_expenses)
        savings_rate = financial_rules.calculate_savings_rate(monthly_income, monthly_expenses)
        monthly_cash_flow = monthly_income - monthly_expenses
        
        return FinancialSummary(
            total_income=total_income,
            total_expenses=total_expenses,
            total_investments=total_investments,
            total_loans=total_loans,
            net_worth=net_worth,
            savings_rate=savings_rate,
            monthly_cash_flow=monthly_cash_flow
        )
    
    async def get_expense_analytics(
        self,
        user_id: str,
        months: int = 6
    ) -> ExpenseAnalytics:
        """
        Get expense analytics with category breakdown and trends.
        
        Args:
            user_id: User's ID
            months: Number of months to analyze
        """
        user_oid = await self._get_user_object_id(user_id)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)
        
        # Initialize data structures
        category_totals = defaultdict(float)
        monthly_totals = defaultdict(float)
        all_expenses = []
        
        # Fetch and process expenses
        async for doc in self.db.expenses.find({"user_id": user_oid}):
            amount = doc.get("amount", 0)
            category = doc.get("category", "other")
            date_str = doc.get("date", "")
            
            # Add to category breakdown
            category_totals[category] += amount
            
            # Try to parse date for trend analysis
            try:
                doc_date = parse_date(date_str)
                
                # Only include in trend if within range
                if start_date <= doc_date <= end_date:
                    month_key = doc_date.strftime("%Y-%m")
                    monthly_totals[month_key] += amount
                
                # Add to all expenses for top expenses
                all_expenses.append({
                    "_id": str(doc["_id"]),
                    "amount": amount,
                    "description": doc.get("description", ""),
                    "category": category,
                    "date": date_str,
                    "merchant": doc.get("merchant")
                })
            except:
                pass
        
        # Build monthly trend (sorted by month)
        monthly_trend = []
        for month_key in sorted(monthly_totals.keys()):
            monthly_trend.append(MonthlyTrend(
                month=month_key,
                amount=monthly_totals[month_key]
            ))
        
        # Get top 10 expenses
        all_expenses.sort(key=lambda x: x["amount"], reverse=True)
        top_expenses = [
            ExpenseResponse(
                id=exp["_id"],
                amount=exp["amount"],
                description=exp["description"],
                category=exp["category"],
                date=exp["date"],
                merchant=exp.get("merchant")
            )
            for exp in all_expenses[:10]
        ]
        
        return ExpenseAnalytics(
            category_breakdown=dict(category_totals),
            monthly_trend=monthly_trend,
            top_expenses=top_expenses
        )
    
    async def get_investment_analytics(
        self,
        user_id: str
    ) -> InvestmentAnalytics:
        """
        Get investment analytics with portfolio breakdown and performance.
        """
        user_oid = await self._get_user_object_id(user_id)
        
        # Initialize data structures
        type_totals = defaultdict(float)
        total_invested = 0
        total_current = 0
        performance_data = []
        
        # Fetch and process investments
        async for doc in self.db.investments.find({"user_id": user_oid}):
            invested = doc.get("amount", 0)
            current = doc.get("current_value", invested)
            inv_type = doc.get("type", "other")
            name = doc.get("name", "Unknown")
            
            # Update totals
            total_invested += invested
            total_current += current
            type_totals[inv_type] += current
            
            # Calculate performance
            gain_loss = current - invested
            gain_loss_percentage = ((gain_loss / invested) * 100) if invested > 0 else 0
            
            performance_data.append(InvestmentPerformance(
                name=name,
                invested=invested,
                current=current,
                gain_loss=round(gain_loss, 2),
                gain_loss_percentage=round(gain_loss_percentage, 2)
            ))
        
        # Sort performance data by gain/loss percentage
        performance_data.sort(key=lambda x: x.gain_loss_percentage, reverse=True)
        
        total_gain_loss = total_current - total_invested
        
        return InvestmentAnalytics(
            portfolio_breakdown=dict(type_totals),
            total_invested=total_invested,
            total_current=total_current,
            total_gain_loss=round(total_gain_loss, 2),
            performance_data=performance_data
        )
    
    async def get_monthly_trends(
        self,
        user_id: str,
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Get monthly income, expense, and savings trends.
        """
        user_oid = await self._get_user_object_id(user_id)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)
        
        # Initialize monthly data
        monthly_data = defaultdict(lambda: {"income": 0, "expenses": 0})
        
        # Process income
        async for doc in self.db.income.find({"user_id": user_oid}):
            try:
                doc_date = parse_date(doc.get("date", ""))
                if start_date <= doc_date <= end_date:
                    month_key = doc_date.strftime("%Y-%m")
                    monthly_data[month_key]["income"] += doc.get("amount", 0)
            except:
                pass
        
        # Process expenses
        async for doc in self.db.expenses.find({"user_id": user_oid}):
            try:
                doc_date = parse_date(doc.get("date", ""))
                if start_date <= doc_date <= end_date:
                    month_key = doc_date.strftime("%Y-%m")
                    monthly_data[month_key]["expenses"] += doc.get("amount", 0)
            except:
                pass
        
        # Build response
        trends = []
        for month_key in sorted(monthly_data.keys()):
            data = monthly_data[month_key]
            trends.append({
                "month": month_key,
                "income": data["income"],
                "expenses": data["expenses"],
                "savings": data["income"] - data["expenses"]
            })
        
        return {
            "trends": trends,
            "summary": {
                "avg_monthly_income": sum(t["income"] for t in trends) / len(trends) if trends else 0,
                "avg_monthly_expenses": sum(t["expenses"] for t in trends) / len(trends) if trends else 0,
                "avg_monthly_savings": sum(t["savings"] for t in trends) / len(trends) if trends else 0,
            }
        }
    
    async def get_reports(
        self,
        user_id: str,
        report_type: str = "monthly"
    ) -> Dict[str, Any]:
        """
        Generate financial reports.
        
        Args:
            user_id: User's ID
            report_type: Type of report (monthly, quarterly, yearly)
        """
        # Get all analytics data
        summary = await self.get_financial_summary(user_id)
        expense_analytics = await self.get_expense_analytics(user_id)
        investment_analytics = await self.get_investment_analytics(user_id)
        trends = await self.get_monthly_trends(user_id)
        
        return {
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "financial_summary": {
                "total_income": summary.total_income,
                "total_expenses": summary.total_expenses,
                "total_investments": summary.total_investments,
                "total_loans": summary.total_loans,
                "net_worth": summary.net_worth,
                "savings_rate": summary.savings_rate,
                "monthly_cash_flow": summary.monthly_cash_flow
            },
            "expense_breakdown": expense_analytics.category_breakdown,
            "investment_summary": {
                "total_invested": investment_analytics.total_invested,
                "total_current_value": investment_analytics.total_current,
                "total_gain_loss": investment_analytics.total_gain_loss,
                "portfolio_allocation": investment_analytics.portfolio_breakdown
            },
            "trends": trends["trends"],
            "insights": await self._generate_insights(
                summary, expense_analytics, investment_analytics
            )
        }
    
    async def _generate_insights(
        self,
        summary: FinancialSummary,
        expenses: ExpenseAnalytics,
        investments: InvestmentAnalytics
    ) -> List[str]:
        """Generate automated financial insights."""
        insights = []
        
        # Savings rate insight
        if summary.savings_rate >= 30:
            insights.append(f"Excellent! Your savings rate of {summary.savings_rate:.1f}% is above the recommended 30%.")
        elif summary.savings_rate >= 20:
            insights.append(f"Good progress! Your savings rate is {summary.savings_rate:.1f}%. Consider increasing it to 30%.")
        elif summary.savings_rate >= 10:
            insights.append(f"Your savings rate of {summary.savings_rate:.1f}% could be improved. Aim for at least 20%.")
        else:
            insights.append(f"Warning: Your savings rate is {summary.savings_rate:.1f}%. Consider reviewing your expenses to save more.")
        
        # Expense insight
        if expenses.category_breakdown:
            highest_category = max(expenses.category_breakdown.items(), key=lambda x: x[1])
            insights.append(f"Your highest expense category is '{highest_category[0]}' at ₹{highest_category[1]:,.0f}.")
        
        # Investment insight
        if investments.total_invested > 0:
            roi = (investments.total_gain_loss / investments.total_invested) * 100
            if roi >= 0:
                insights.append(f"Your investments have grown by {roi:.1f}% overall.")
            else:
                insights.append(f"Your investments are down by {abs(roi):.1f}%. Consider reviewing your portfolio.")
        
        # Net worth insight
        if summary.net_worth > 0:
            insights.append(f"Your net worth is ₹{summary.net_worth:,.0f}. Keep building it!")
        elif summary.net_worth < 0:
            insights.append(f"Your net worth is negative at ₹{summary.net_worth:,.0f}. Focus on debt reduction.")
        
        return insights
