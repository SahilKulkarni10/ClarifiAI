from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

# User Models
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=70, description="Password must be between 6-70 characters")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "secure123"
            }
        }

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    name: str
    email: str
    created_at: datetime
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Finance Data Models
class IncomeSource(str, Enum):
    SALARY = "salary"
    FREELANCE = "freelance"
    RENTAL = "rental"
    INVESTMENT = "investment"
    BUSINESS = "business"
    OTHER = "other"

class ExpenseCategory(str, Enum):
    FOOD = "food"
    RENT = "rent"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    OTHER = "other"

class InvestmentType(str, Enum):
    SIP = "sip"
    MUTUAL_FUND = "mutual_fund"
    STOCKS = "stocks"
    BONDS = "bonds"
    FD = "fd"
    PPF = "ppf"
    EPF = "epf"
    NPS = "nps"
    CRYPTO = "crypto"
    OTHER = "other"

class LoanType(str, Enum):
    HOME = "home"
    CAR = "car"
    PERSONAL = "personal"
    EDUCATION = "education"
    BUSINESS = "business"
    CREDIT_CARD = "credit_card"
    OTHER = "other"

class InsuranceType(str, Enum):
    LIFE = "life"
    HEALTH = "health"
    VEHICLE = "vehicle"
    HOME = "home"
    TRAVEL = "travel"
    OTHER = "other"

# Income Model
class IncomeCreate(BaseModel):
    source: IncomeSource
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    date: date
    frequency: str = Field(default="monthly")  # monthly, yearly, one-time

class Income(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    source: IncomeSource
    amount: float
    description: Optional[str]
    date: date
    frequency: str
    created_at: datetime

# Expense Model
class ExpenseCreate(BaseModel):
    category: ExpenseCategory
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    date: date
    merchant: Optional[str] = None

class Expense(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    category: ExpenseCategory
    amount: float
    description: Optional[str]
    date: date
    merchant: Optional[str]
    created_at: datetime

# Investment Model
class InvestmentCreate(BaseModel):
    type: InvestmentType
    name: str
    amount: float = Field(..., gt=0)
    date: date
    current_value: Optional[float] = None
    goal: Optional[str] = None
    maturity_date: Optional[date] = None

class Investment(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    type: InvestmentType
    name: str
    amount: float
    date: date
    current_value: Optional[float]
    goal: Optional[str]
    maturity_date: Optional[date]
    created_at: datetime

# Loan Model
class LoanCreate(BaseModel):
    type: LoanType
    principal: float = Field(..., gt=0)
    interest_rate: float = Field(..., gt=0, le=100)
    tenure_months: int = Field(..., gt=0)
    emi: float = Field(..., gt=0)
    outstanding: float = Field(..., ge=0)
    start_date: date
    bank_name: Optional[str] = None

class Loan(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    type: LoanType
    principal: float
    interest_rate: float
    tenure_months: int
    emi: float
    outstanding: float
    start_date: date
    bank_name: Optional[str]
    created_at: datetime

# Insurance Model
class InsuranceCreate(BaseModel):
    type: InsuranceType
    policy_name: str
    coverage_amount: float = Field(..., gt=0)
    premium: float = Field(..., gt=0)
    start_date: date
    renewal_date: date
    company_name: str

class Insurance(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    type: InsuranceType
    policy_name: str
    coverage_amount: float
    premium: float
    start_date: date
    renewal_date: date
    company_name: str
    created_at: datetime

# Budget Model
class BudgetCreate(BaseModel):
    month: str  # YYYY-MM format
    total_budget: float = Field(..., gt=0)
    category_budgets: Dict[str, float] = {}
    savings_target: Optional[float] = None

class Budget(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    month: str
    total_budget: float
    category_budgets: Dict[str, float]
    savings_target: Optional[float]
    created_at: datetime

# Goal Model
class GoalCreate(BaseModel):
    title: str
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0, ge=0)
    target_date: date
    description: Optional[str] = None

class Goal(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    title: str
    target_amount: float
    current_amount: float
    target_date: date
    description: Optional[str]
    created_at: datetime

# Chat Models
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    response: str
    context_used: bool = False
    suggestions: List[str] = []

# Analytics Models
class FinancialSummary(BaseModel):
    total_income: float
    total_expenses: float
    total_investments: float
    total_loans: float
    net_worth: float
    savings_rate: float
    monthly_cash_flow: float

class ExpenseAnalytics(BaseModel):
    category_breakdown: Dict[str, float]
    monthly_trend: List[Dict[str, Any]]
    top_expenses: List[Dict[str, Any]]

class InvestmentAnalytics(BaseModel):
    portfolio_breakdown: Dict[str, float]
    total_invested: float
    current_value: float
    returns: float
    returns_percentage: float
