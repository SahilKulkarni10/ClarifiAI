"""
Finance Models
Pydantic models for all financial data structures.
Aligned with frontend finance.service.ts types.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class ExpenseCategory(str, Enum):
    """Standard expense categories."""
    FOOD = "food"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    SHOPPING = "shopping"
    EDUCATION = "education"
    RENT = "rent"
    INSURANCE = "insurance"
    INVESTMENT = "investment"
    EMI = "emi"
    OTHER = "other"


class IncomeCategory(str, Enum):
    """Standard income categories."""
    SALARY = "salary"
    FREELANCE = "freelance"
    BUSINESS = "business"
    INVESTMENT = "investment"
    RENTAL = "rental"
    DIVIDEND = "dividend"
    INTEREST = "interest"
    BONUS = "bonus"
    OTHER = "other"


class InvestmentType(str, Enum):
    """Investment types."""
    STOCKS = "stocks"
    MUTUAL_FUNDS = "mutual_funds"
    FIXED_DEPOSIT = "fixed_deposit"
    PPF = "ppf"
    NPS = "nps"
    GOLD = "gold"
    REAL_ESTATE = "real_estate"
    BONDS = "bonds"
    CRYPTO = "crypto"
    OTHER = "other"


class LoanType(str, Enum):
    """Loan types."""
    HOME_LOAN = "home_loan"
    CAR_LOAN = "car_loan"
    PERSONAL_LOAN = "personal_loan"
    EDUCATION_LOAN = "education_loan"
    GOLD_LOAN = "gold_loan"
    CREDIT_CARD = "credit_card"
    OTHER = "other"


class InsuranceType(str, Enum):
    """Insurance types."""
    LIFE = "life"
    HEALTH = "health"
    TERM = "term"
    VEHICLE = "vehicle"
    HOME = "home"
    TRAVEL = "travel"
    OTHER = "other"


class GoalPriority(str, Enum):
    """Goal priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# =============================================================================
# INCOME MODELS
# =============================================================================

class IncomeBase(BaseModel):
    """Base income model."""
    source: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    date: str  # ISO date string
    category: str = Field(default="other")
    description: Optional[str] = Field(None, max_length=500)


class IncomeCreate(IncomeBase):
    """Model for creating income."""
    pass


class IncomeUpdate(BaseModel):
    """Model for updating income."""
    source: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)


class IncomeResponse(IncomeBase):
    """Model for income in API responses."""
    id: str
    user_id: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True


# =============================================================================
# EXPENSE MODELS
# =============================================================================

class ExpenseBase(BaseModel):
    """Base expense model."""
    category: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    date: str  # ISO date string
    description: Optional[str] = Field(None, max_length=500)
    merchant: Optional[str] = Field(None, max_length=100)


class ExpenseCreate(ExpenseBase):
    """Model for creating expense."""
    pass


class ExpenseUpdate(BaseModel):
    """Model for updating expense."""
    category: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    merchant: Optional[str] = Field(None, max_length=100)


class ExpenseResponse(ExpenseBase):
    """Model for expense in API responses."""
    id: str
    user_id: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True


# =============================================================================
# INVESTMENT MODELS
# =============================================================================

class InvestmentBase(BaseModel):
    """Base investment model."""
    type: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)  # Invested amount
    current_value: Optional[float] = None
    purchase_date: str  # ISO date string
    units: Optional[float] = None
    purchase_price: Optional[float] = None


class InvestmentCreate(InvestmentBase):
    """Model for creating investment."""
    pass


class InvestmentUpdate(BaseModel):
    """Model for updating investment."""
    type: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[float] = Field(None, gt=0)
    current_value: Optional[float] = None
    purchase_date: Optional[str] = None
    units: Optional[float] = None
    purchase_price: Optional[float] = None


class InvestmentResponse(InvestmentBase):
    """Model for investment in API responses."""
    id: str
    user_id: Optional[str] = None
    gain_loss: Optional[float] = None
    gain_loss_percentage: Optional[float] = None
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True


# =============================================================================
# LOAN MODELS
# =============================================================================

class LoanBase(BaseModel):
    """Base loan model."""
    type: str = Field(..., min_length=1)
    principal: float = Field(..., gt=0)
    interest_rate: float = Field(..., ge=0, le=100)
    emi: float = Field(..., gt=0)
    outstanding: float = Field(..., ge=0)
    start_date: str  # ISO date string
    end_date: str  # ISO date string
    lender: Optional[str] = Field(None, max_length=100)


class LoanCreate(LoanBase):
    """Model for creating loan."""
    pass


class LoanUpdate(BaseModel):
    """Model for updating loan."""
    type: Optional[str] = None
    principal: Optional[float] = Field(None, gt=0)
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    emi: Optional[float] = Field(None, gt=0)
    outstanding: Optional[float] = Field(None, ge=0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    lender: Optional[str] = Field(None, max_length=100)


class LoanResponse(LoanBase):
    """Model for loan in API responses."""
    id: str
    user_id: Optional[str] = None
    months_remaining: Optional[int] = None
    total_interest: Optional[float] = None
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True


# =============================================================================
# INSURANCE MODELS
# =============================================================================

class InsuranceBase(BaseModel):
    """Base insurance model."""
    type: str = Field(..., min_length=1)
    provider: str = Field(..., min_length=1, max_length=100)
    premium: float = Field(..., gt=0)
    coverage: float = Field(..., gt=0)
    start_date: str  # ISO date string
    end_date: str  # ISO date string
    policy_number: Optional[str] = Field(None, max_length=50)


class InsuranceCreate(InsuranceBase):
    """Model for creating insurance."""
    pass


class InsuranceUpdate(BaseModel):
    """Model for updating insurance."""
    type: Optional[str] = None
    provider: Optional[str] = Field(None, min_length=1, max_length=100)
    premium: Optional[float] = Field(None, gt=0)
    coverage: Optional[float] = Field(None, gt=0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    policy_number: Optional[str] = Field(None, max_length=50)


class InsuranceResponse(InsuranceBase):
    """Model for insurance in API responses."""
    id: str
    user_id: Optional[str] = None
    is_active: Optional[bool] = None
    days_until_renewal: Optional[int] = None
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True


# =============================================================================
# GOAL MODELS
# =============================================================================

class GoalBase(BaseModel):
    """Base goal model."""
    name: str = Field(..., min_length=1, max_length=200)
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0, ge=0)
    target_date: str  # ISO date string
    priority: str = Field(default="medium")
    category: Optional[str] = None


class GoalCreate(GoalBase):
    """Model for creating goal."""
    pass


class GoalUpdate(BaseModel):
    """Model for updating goal."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    target_amount: Optional[float] = Field(None, gt=0)
    current_amount: Optional[float] = Field(None, ge=0)
    target_date: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None


class GoalResponse(GoalBase):
    """Model for goal in API responses."""
    id: str
    user_id: Optional[str] = None
    progress_percentage: Optional[float] = None
    monthly_required: Optional[float] = None
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True


# =============================================================================
# DASHBOARD MODELS
# =============================================================================

class MonthlySummary(BaseModel):
    """Monthly financial summary."""
    income: float = 0
    expenses: float = 0
    savings: float = 0


class DashboardCounts(BaseModel):
    """Count of financial records."""
    income: int = 0
    expenses: int = 0
    investments: int = 0
    loans: int = 0
    insurance: int = 0
    goals: int = 0


class Dashboard(BaseModel):
    """Complete dashboard data model."""
    total_income: float = 0
    total_expenses: float = 0
    total_investments: float = 0
    total_loans: float = 0
    net_worth: float = 0
    monthly_summary: MonthlySummary
    counts: DashboardCounts


# =============================================================================
# ANALYTICS MODELS
# =============================================================================

class CategoryBreakdown(BaseModel):
    """Category-wise breakdown of amounts."""
    category: str
    amount: float
    percentage: float


class MonthlyTrend(BaseModel):
    """Monthly trend data point."""
    month: str
    amount: float


class FinancialSummary(BaseModel):
    """Complete financial summary for analytics."""
    total_income: float = 0
    total_expenses: float = 0
    total_investments: float = 0
    total_loans: float = 0
    net_worth: float = 0
    savings_rate: float = 0
    monthly_cash_flow: float = 0


class ExpenseAnalytics(BaseModel):
    """Expense analytics data."""
    category_breakdown: dict  # {category: amount}
    monthly_trend: List[MonthlyTrend]
    top_expenses: List[ExpenseResponse]


class InvestmentPerformance(BaseModel):
    """Individual investment performance."""
    name: str
    invested: float
    current: float
    gain_loss: float
    gain_loss_percentage: float


class InvestmentAnalytics(BaseModel):
    """Investment analytics data."""
    portfolio_breakdown: dict  # {type: amount}
    total_invested: float
    total_current: float
    total_gain_loss: float
    performance_data: List[InvestmentPerformance]
