"""
Financial Rules Engine
Deterministic financial calculations and rules-based logic.
All financial calculations must happen here, NOT in the LLM.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from loguru import logger
import math


class FinancialRulesEngine:
    """
    Rule-based financial logic engine.
    Performs all financial calculations deterministically.
    LLM is only used to explain these calculations.
    """
    
    # ==========================================================================
    # INCOME & EXPENSE ANALYSIS
    # ==========================================================================
    
    @staticmethod
    def calculate_savings_rate(
        total_income: float,
        total_expenses: float
    ) -> float:
        """
        Calculate savings rate as percentage of income.
        
        Returns:
            Savings rate as percentage (0-100)
        """
        if total_income <= 0:
            return 0.0
        
        savings = total_income - total_expenses
        return round((savings / total_income) * 100, 2)
    
    @staticmethod
    def categorize_expense_health(
        expenses_by_category: Dict[str, float],
        total_income: float
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze expense categories and provide health assessment.
        
        Returns:
            Dictionary with category analysis and recommendations
        """
        # Recommended maximum percentages by category (of income)
        recommended_limits = {
            "rent": 30,
            "food": 15,
            "transport": 10,
            "utilities": 10,
            "entertainment": 10,
            "shopping": 10,
            "healthcare": 5,
            "education": 10,
            "emi": 40,  # All EMIs combined
            "other": 10
        }
        
        results = {}
        total_expenses = sum(expenses_by_category.values())
        
        for category, amount in expenses_by_category.items():
            category_lower = category.lower()
            limit = recommended_limits.get(category_lower, 10)
            
            if total_income > 0:
                percentage = (amount / total_income) * 100
            else:
                percentage = 0
            
            # Determine health status
            if percentage <= limit * 0.8:
                status = "healthy"
                message = f"{category} spending is well within limits"
            elif percentage <= limit:
                status = "moderate"
                message = f"{category} spending is approaching the recommended limit"
            else:
                status = "overspending"
                message = f"{category} spending exceeds the recommended {limit}% of income"
            
            results[category] = {
                "amount": amount,
                "percentage_of_income": round(percentage, 1),
                "recommended_limit": limit,
                "status": status,
                "message": message
            }
        
        return results
    
    @staticmethod
    def calculate_monthly_cash_flow(
        monthly_income: float,
        monthly_expenses: float,
        emi_total: float = 0
    ) -> Dict[str, float]:
        """
        Calculate monthly cash flow metrics.
        """
        total_outflow = monthly_expenses + emi_total
        net_cash_flow = monthly_income - total_outflow
        
        return {
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "emi_obligations": emi_total,
            "total_outflow": total_outflow,
            "net_cash_flow": net_cash_flow,
            "disposable_income": max(0, net_cash_flow)
        }
    
    # ==========================================================================
    # INVESTMENT CALCULATIONS
    # ==========================================================================
    
    @staticmethod
    def calculate_compound_interest(
        principal: float,
        annual_rate: float,
        years: int,
        compounds_per_year: int = 12
    ) -> Dict[str, float]:
        """
        Calculate compound interest returns.
        
        Args:
            principal: Initial investment amount
            annual_rate: Annual interest rate (as percentage, e.g., 12 for 12%)
            years: Investment duration in years
            compounds_per_year: Compounding frequency (12 for monthly)
            
        Returns:
            Dictionary with final amount, total interest, and growth rate
        """
        rate = annual_rate / 100
        n = compounds_per_year
        t = years
        
        final_amount = principal * (1 + rate/n) ** (n*t)
        total_interest = final_amount - principal
        total_growth_rate = ((final_amount / principal) - 1) * 100
        
        return {
            "principal": principal,
            "final_amount": round(final_amount, 2),
            "total_interest": round(total_interest, 2),
            "total_growth_rate": round(total_growth_rate, 2),
            "cagr": annual_rate
        }
    
    @staticmethod
    def calculate_sip_returns(
        monthly_investment: float,
        annual_rate: float,
        years: int
    ) -> Dict[str, float]:
        """
        Calculate SIP investment returns.
        Uses the standard SIP formula.
        
        Returns:
            Dictionary with total invested, final value, and returns
        """
        rate = annual_rate / 100
        monthly_rate = rate / 12
        months = years * 12
        
        # SIP Future Value formula
        if monthly_rate > 0:
            future_value = monthly_investment * (
                ((1 + monthly_rate) ** months - 1) / monthly_rate
            ) * (1 + monthly_rate)
        else:
            future_value = monthly_investment * months
        
        total_invested = monthly_investment * months
        total_returns = future_value - total_invested
        
        return {
            "monthly_investment": monthly_investment,
            "total_invested": round(total_invested, 2),
            "future_value": round(future_value, 2),
            "total_returns": round(total_returns, 2),
            "absolute_return_percentage": round((total_returns / total_invested) * 100, 2) if total_invested > 0 else 0,
            "assumed_annual_rate": annual_rate,
            "duration_years": years
        }
    
    @staticmethod
    def calculate_portfolio_allocation_score(
        equity_percentage: float,
        debt_percentage: float,
        gold_percentage: float,
        age: int
    ) -> Dict[str, Any]:
        """
        Evaluate if portfolio allocation is appropriate for age.
        Rule of thumb: Equity allocation = 100 - Age
        """
        recommended_equity = max(20, min(80, 100 - age))
        recommended_debt = 100 - recommended_equity - 10  # 10% for gold
        recommended_gold = 10
        
        # Calculate deviation
        equity_deviation = equity_percentage - recommended_equity
        
        if abs(equity_deviation) <= 10:
            status = "balanced"
            message = "Portfolio allocation is appropriate for your age"
        elif equity_deviation > 10:
            status = "aggressive"
            message = f"Portfolio is more aggressive than typical for age {age}"
        else:
            status = "conservative"
            message = f"Portfolio is more conservative than typical for age {age}"
        
        return {
            "current_allocation": {
                "equity": equity_percentage,
                "debt": debt_percentage,
                "gold": gold_percentage
            },
            "recommended_allocation": {
                "equity": recommended_equity,
                "debt": recommended_debt,
                "gold": recommended_gold
            },
            "status": status,
            "message": message,
            "equity_deviation": round(equity_deviation, 1)
        }
    
    # ==========================================================================
    # LOAN CALCULATIONS
    # ==========================================================================
    
    @staticmethod
    def calculate_emi(
        principal: float,
        annual_rate: float,
        tenure_months: int
    ) -> Dict[str, float]:
        """
        Calculate EMI using standard formula.
        EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
        """
        if annual_rate == 0:
            emi = principal / tenure_months
            total_interest = 0
        else:
            monthly_rate = annual_rate / (12 * 100)
            emi = principal * monthly_rate * (1 + monthly_rate)**tenure_months
            emi = emi / ((1 + monthly_rate)**tenure_months - 1)
            total_interest = (emi * tenure_months) - principal
        
        return {
            "emi": round(emi, 2),
            "principal": principal,
            "total_interest": round(total_interest, 2),
            "total_payment": round(emi * tenure_months, 2),
            "tenure_months": tenure_months,
            "annual_rate": annual_rate
        }
    
    @staticmethod
    def analyze_loan_affordability(
        monthly_income: float,
        existing_emis: float,
        proposed_emi: float
    ) -> Dict[str, Any]:
        """
        Analyze if a new loan is affordable.
        Rule: Total EMIs should not exceed 50% of income.
        """
        total_emi = existing_emis + proposed_emi
        emi_to_income_ratio = (total_emi / monthly_income) * 100 if monthly_income > 0 else 100
        
        if emi_to_income_ratio <= 40:
            status = "affordable"
            message = "This loan is affordable and within safe limits"
        elif emi_to_income_ratio <= 50:
            status = "manageable"
            message = "This loan is manageable but leaves little room for savings"
        else:
            status = "risky"
            message = "This loan may strain your finances. Consider reducing the loan amount or tenure"
        
        return {
            "monthly_income": monthly_income,
            "existing_emis": existing_emis,
            "proposed_emi": proposed_emi,
            "total_emi": total_emi,
            "emi_to_income_ratio": round(emi_to_income_ratio, 1),
            "safe_limit": 50,
            "status": status,
            "message": message,
            "max_recommended_emi": round(monthly_income * 0.5 - existing_emis, 2)
        }
    
    @staticmethod
    def calculate_loan_prepayment_benefit(
        outstanding: float,
        emi: float,
        annual_rate: float,
        prepayment_amount: float,
        remaining_months: int
    ) -> Dict[str, Any]:
        """
        Calculate benefit of loan prepayment.
        """
        monthly_rate = annual_rate / (12 * 100)
        
        # Interest saved calculation (approximation)
        # Interest that would have been paid on prepayment amount
        interest_saved = prepayment_amount * monthly_rate * (remaining_months / 2)
        
        # New outstanding after prepayment
        new_outstanding = outstanding - prepayment_amount
        
        # New tenure with same EMI
        if monthly_rate > 0 and emi > new_outstanding * monthly_rate:
            new_tenure = math.log(emi / (emi - new_outstanding * monthly_rate)) / math.log(1 + monthly_rate)
            new_tenure = int(new_tenure)
        else:
            new_tenure = remaining_months
        
        months_reduced = remaining_months - new_tenure
        
        return {
            "prepayment_amount": prepayment_amount,
            "interest_saved": round(interest_saved, 2),
            "new_outstanding": round(new_outstanding, 2),
            "original_remaining_months": remaining_months,
            "new_remaining_months": new_tenure,
            "months_reduced": months_reduced,
            "recommendation": "Prepayment is beneficial" if interest_saved > 0 else "Consider other investment options"
        }
    
    # ==========================================================================
    # GOAL PLANNING
    # ==========================================================================
    
    @staticmethod
    def calculate_goal_feasibility(
        target_amount: float,
        current_savings: float,
        monthly_contribution: float,
        years_remaining: float,
        expected_return: float = 10
    ) -> Dict[str, Any]:
        """
        Assess if a financial goal is achievable.
        """
        months = int(years_remaining * 12)
        
        if months <= 0:
            return {
                "is_feasible": current_savings >= target_amount,
                "message": "Target date has passed or is imminent",
                "shortfall": max(0, target_amount - current_savings)
            }
        
        # Calculate future value of current savings + monthly SIP
        monthly_rate = expected_return / (12 * 100)
        
        # Future value of current savings
        fv_current = current_savings * (1 + monthly_rate) ** months
        
        # Future value of SIP
        if monthly_rate > 0:
            fv_sip = monthly_contribution * (
                ((1 + monthly_rate) ** months - 1) / monthly_rate
            ) * (1 + monthly_rate)
        else:
            fv_sip = monthly_contribution * months
        
        total_future_value = fv_current + fv_sip
        shortfall = target_amount - total_future_value
        
        is_feasible = total_future_value >= target_amount
        
        # Calculate required monthly contribution if not feasible
        if not is_feasible and monthly_rate > 0:
            required_fv = target_amount - fv_current
            required_monthly = required_fv * monthly_rate / (
                ((1 + monthly_rate) ** months - 1) * (1 + monthly_rate)
            )
            required_monthly = max(0, required_monthly)
        else:
            required_monthly = monthly_contribution
        
        return {
            "is_feasible": is_feasible,
            "target_amount": target_amount,
            "projected_amount": round(total_future_value, 2),
            "shortfall": round(max(0, shortfall), 2),
            "current_monthly_contribution": monthly_contribution,
            "required_monthly_contribution": round(required_monthly, 2),
            "additional_monthly_needed": round(max(0, required_monthly - monthly_contribution), 2),
            "years_remaining": years_remaining,
            "assumed_return": expected_return,
            "message": "Goal is achievable with current plan" if is_feasible else f"Need to increase monthly contribution by ₹{round(max(0, required_monthly - monthly_contribution), 2)}"
        }
    
    @staticmethod
    def prioritize_goals(
        goals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prioritize financial goals based on urgency and importance.
        """
        priority_weights = {
            "high": 3,
            "medium": 2,
            "low": 1
        }
        
        scored_goals = []
        today = datetime.now()
        
        for goal in goals:
            try:
                target_date = parse_date(goal.get("target_date", ""))
                days_remaining = (target_date - today).days
                months_remaining = max(1, days_remaining / 30)
            except:
                months_remaining = 120  # Default 10 years
            
            # Calculate urgency score (higher for nearer goals)
            urgency = 100 / months_remaining if months_remaining > 0 else 100
            
            # Get priority weight
            priority = goal.get("priority", "medium").lower()
            priority_weight = priority_weights.get(priority, 2)
            
            # Calculate completion percentage
            current = goal.get("current_amount", 0)
            target = goal.get("target_amount", 1)
            completion = (current / target) * 100 if target > 0 else 0
            
            # Composite score
            score = (urgency * priority_weight * 10) - completion
            
            scored_goals.append({
                **goal,
                "urgency_score": round(urgency, 2),
                "priority_weight": priority_weight,
                "completion_percentage": round(completion, 1),
                "composite_score": round(score, 2),
                "months_remaining": round(months_remaining, 0)
            })
        
        # Sort by composite score (higher first)
        scored_goals.sort(key=lambda x: x["composite_score"], reverse=True)
        
        return scored_goals
    
    # ==========================================================================
    # INSURANCE ANALYSIS
    # ==========================================================================
    
    @staticmethod
    def calculate_life_insurance_need(
        annual_income: float,
        outstanding_loans: float,
        existing_savings: float,
        num_dependents: int,
        years_until_youngest_independent: int = 18
    ) -> Dict[str, Any]:
        """
        Calculate recommended life insurance coverage.
        Uses Human Life Value approach with adjustments.
        """
        # Basic calculation: Income replacement for dependents
        income_replacement = annual_income * years_until_youngest_independent * 0.7
        
        # Add outstanding liabilities
        total_need = income_replacement + outstanding_loans
        
        # Subtract existing savings/investments
        net_need = total_need - existing_savings
        
        # Minimum recommendation
        minimum_cover = max(net_need, annual_income * 10)
        
        return {
            "annual_income": annual_income,
            "income_replacement_years": years_until_youngest_independent,
            "calculated_need": round(net_need, 2),
            "recommended_cover": round(minimum_cover, 2),
            "outstanding_loans": outstanding_loans,
            "existing_savings": existing_savings,
            "num_dependents": num_dependents,
            "formula_used": "Human Life Value (modified)",
            "assumptions": [
                "70% of income needed for dependents",
                f"Income replacement for {years_until_youngest_independent} years",
                "Existing savings can offset insurance need"
            ]
        }
    
    @staticmethod
    def calculate_health_insurance_need(
        age: int,
        family_members: int,
        city_tier: int = 1  # 1 = metro, 2 = tier 2, 3 = tier 3
    ) -> Dict[str, Any]:
        """
        Calculate recommended health insurance coverage.
        """
        # Base coverage by city tier
        base_coverage = {
            1: 1000000,  # ₹10 lakh for metros
            2: 750000,   # ₹7.5 lakh for tier 2
            3: 500000    # ₹5 lakh for tier 3
        }
        
        base = base_coverage.get(city_tier, 750000)
        
        # Adjust for family size
        family_multiplier = 1 + (family_members - 1) * 0.2
        
        # Adjust for age
        if age > 50:
            age_multiplier = 1.5
        elif age > 40:
            age_multiplier = 1.2
        else:
            age_multiplier = 1.0
        
        recommended = base * family_multiplier * age_multiplier
        
        return {
            "recommended_coverage": round(recommended, -4),  # Round to nearest 10k
            "base_coverage": base,
            "family_members": family_members,
            "city_tier": city_tier,
            "age_group": "senior" if age > 50 else "adult" if age > 40 else "young adult",
            "recommendations": [
                "Consider a family floater plan",
                "Add super top-up for cost-effective higher coverage",
                "Check for no-claim bonus features",
                "Ensure coverage for pre-existing conditions after waiting period"
            ]
        }
    
    # ==========================================================================
    # NET WORTH & FINANCIAL HEALTH
    # ==========================================================================
    
    @staticmethod
    def calculate_net_worth(
        assets: Dict[str, float],
        liabilities: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate net worth from assets and liabilities.
        """
        total_assets = sum(assets.values())
        total_liabilities = sum(liabilities.values())
        net_worth = total_assets - total_liabilities
        
        return {
            "total_assets": round(total_assets, 2),
            "total_liabilities": round(total_liabilities, 2),
            "net_worth": round(net_worth, 2),
            "asset_breakdown": assets,
            "liability_breakdown": liabilities,
            "debt_to_asset_ratio": round((total_liabilities / total_assets) * 100, 1) if total_assets > 0 else 0
        }
    
    @staticmethod
    def calculate_financial_health_score(
        savings_rate: float,
        emergency_fund_months: float,
        debt_to_income_ratio: float,
        investment_rate: float,
        insurance_coverage: bool
    ) -> Dict[str, Any]:
        """
        Calculate overall financial health score (0-100).
        """
        scores = {}
        
        # Savings rate score (max 20)
        if savings_rate >= 30:
            scores["savings"] = 20
        elif savings_rate >= 20:
            scores["savings"] = 15
        elif savings_rate >= 10:
            scores["savings"] = 10
        else:
            scores["savings"] = 5
        
        # Emergency fund score (max 20)
        if emergency_fund_months >= 6:
            scores["emergency_fund"] = 20
        elif emergency_fund_months >= 3:
            scores["emergency_fund"] = 15
        elif emergency_fund_months >= 1:
            scores["emergency_fund"] = 10
        else:
            scores["emergency_fund"] = 5
        
        # Debt management score (max 20)
        if debt_to_income_ratio <= 20:
            scores["debt"] = 20
        elif debt_to_income_ratio <= 40:
            scores["debt"] = 15
        elif debt_to_income_ratio <= 60:
            scores["debt"] = 10
        else:
            scores["debt"] = 5
        
        # Investment score (max 20)
        if investment_rate >= 20:
            scores["investment"] = 20
        elif investment_rate >= 10:
            scores["investment"] = 15
        elif investment_rate >= 5:
            scores["investment"] = 10
        else:
            scores["investment"] = 5
        
        # Insurance score (max 20)
        scores["insurance"] = 20 if insurance_coverage else 5
        
        total_score = sum(scores.values())
        
        # Determine health status
        if total_score >= 80:
            status = "excellent"
            message = "Your financial health is excellent! Keep it up."
        elif total_score >= 60:
            status = "good"
            message = "Your financial health is good. Some areas can be improved."
        elif total_score >= 40:
            status = "fair"
            message = "Your financial health needs attention. Focus on weak areas."
        else:
            status = "poor"
            message = "Your financial health needs significant improvement."
        
        return {
            "total_score": total_score,
            "max_score": 100,
            "status": status,
            "message": message,
            "breakdown": scores,
            "areas_for_improvement": [
                area for area, score in scores.items() if score < 15
            ]
        }


# Global instance
financial_rules = FinancialRulesEngine()
