"""
Finance Routes
Handles all financial data CRUD operations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from app.core.database import get_database
from app.core.dependencies import get_current_user_id, get_current_user
from app.models.finance import (
    # Income models
    IncomeCreate, IncomeUpdate, IncomeResponse,
    # Expense models
    ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    # Investment models
    InvestmentCreate, InvestmentUpdate, InvestmentResponse,
    # Loan models
    LoanCreate, LoanUpdate, LoanResponse,
    # Insurance models
    InsuranceCreate, InsuranceUpdate, InsuranceResponse,
    # Goal models
    GoalCreate, GoalUpdate, GoalResponse,
    # Dashboard
    Dashboard
)
from app.services.finance_service import FinanceService

router = APIRouter(prefix="/finance", tags=["Finance"])


# =============================================================================
# INCOME ROUTES
# =============================================================================

@router.get("/income", response_model=List[IncomeResponse])
async def get_income(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all income entries for the current user."""
    service = FinanceService(db)
    return await service.get_income_list(user_id)


@router.post("/income", response_model=IncomeResponse, status_code=status.HTTP_201_CREATED)
async def create_income(
    data: IncomeCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new income entry."""
    service = FinanceService(db)
    return await service.create_income(user_id, data)


@router.get("/income/{income_id}", response_model=IncomeResponse)
async def get_income_by_id(
    income_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific income entry."""
    service = FinanceService(db)
    result = await service.get_income_by_id(user_id, income_id)
    if not result:
        raise HTTPException(status_code=404, detail="Income not found")
    return result


@router.put("/income/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: str,
    data: IncomeUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update an income entry."""
    service = FinanceService(db)
    result = await service.update_income(user_id, income_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Income not found")
    return result


@router.delete("/income/{income_id}")
async def delete_income(
    income_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete an income entry."""
    service = FinanceService(db)
    success = await service.delete_income(user_id, income_id)
    if not success:
        raise HTTPException(status_code=404, detail="Income not found")
    return {"message": "Income deleted successfully"}


# =============================================================================
# EXPENSE ROUTES
# =============================================================================

@router.get("/expenses", response_model=List[ExpenseResponse])
async def get_expenses(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all expense entries for the current user."""
    service = FinanceService(db)
    return await service.get_expense_list(user_id)


@router.post("/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: ExpenseCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new expense entry."""
    service = FinanceService(db)
    return await service.create_expense(user_id, data)


@router.get("/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense_by_id(
    expense_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific expense entry."""
    service = FinanceService(db)
    result = await service.get_expense_by_id(user_id, expense_id)
    if not result:
        raise HTTPException(status_code=404, detail="Expense not found")
    return result


@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    data: ExpenseUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update an expense entry."""
    service = FinanceService(db)
    result = await service.update_expense(user_id, expense_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Expense not found")
    return result


@router.delete("/expenses/{expense_id}")
async def delete_expense(
    expense_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete an expense entry."""
    service = FinanceService(db)
    success = await service.delete_expense(user_id, expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}


# =============================================================================
# INVESTMENT ROUTES
# =============================================================================

@router.get("/investments", response_model=List[InvestmentResponse])
async def get_investments(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all investment entries for the current user."""
    service = FinanceService(db)
    return await service.get_investment_list(user_id)


@router.post("/investments", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
async def create_investment(
    data: InvestmentCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new investment entry."""
    service = FinanceService(db)
    return await service.create_investment(user_id, data)


@router.get("/investments/{investment_id}", response_model=InvestmentResponse)
async def get_investment_by_id(
    investment_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific investment entry."""
    service = FinanceService(db)
    result = await service.get_investment_by_id(user_id, investment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Investment not found")
    return result


@router.put("/investments/{investment_id}", response_model=InvestmentResponse)
async def update_investment(
    investment_id: str,
    data: InvestmentUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update an investment entry."""
    service = FinanceService(db)
    result = await service.update_investment(user_id, investment_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Investment not found")
    return result


@router.delete("/investments/{investment_id}")
async def delete_investment(
    investment_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete an investment entry."""
    service = FinanceService(db)
    success = await service.delete_investment(user_id, investment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Investment not found")
    return {"message": "Investment deleted successfully"}


# =============================================================================
# LOAN ROUTES
# =============================================================================

@router.get("/loans", response_model=List[LoanResponse])
async def get_loans(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all loan entries for the current user."""
    service = FinanceService(db)
    return await service.get_loan_list(user_id)


@router.post("/loans", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(
    data: LoanCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new loan entry."""
    service = FinanceService(db)
    return await service.create_loan(user_id, data)


@router.get("/loans/{loan_id}", response_model=LoanResponse)
async def get_loan_by_id(
    loan_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific loan entry."""
    service = FinanceService(db)
    result = await service.get_loan_by_id(user_id, loan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Loan not found")
    return result


@router.put("/loans/{loan_id}", response_model=LoanResponse)
async def update_loan(
    loan_id: str,
    data: LoanUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a loan entry."""
    service = FinanceService(db)
    result = await service.update_loan(user_id, loan_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Loan not found")
    return result


@router.delete("/loans/{loan_id}")
async def delete_loan(
    loan_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a loan entry."""
    service = FinanceService(db)
    success = await service.delete_loan(user_id, loan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Loan not found")
    return {"message": "Loan deleted successfully"}


# =============================================================================
# INSURANCE ROUTES
# =============================================================================

@router.get("/insurance", response_model=List[InsuranceResponse])
async def get_insurance(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all insurance policies for the current user."""
    service = FinanceService(db)
    return await service.get_insurance_list(user_id)


@router.post("/insurance", response_model=InsuranceResponse, status_code=status.HTTP_201_CREATED)
async def create_insurance(
    data: InsuranceCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new insurance policy."""
    service = FinanceService(db)
    return await service.create_insurance(user_id, data)


@router.get("/insurance/{insurance_id}", response_model=InsuranceResponse)
async def get_insurance_by_id(
    insurance_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific insurance policy."""
    service = FinanceService(db)
    result = await service.get_insurance_by_id(user_id, insurance_id)
    if not result:
        raise HTTPException(status_code=404, detail="Insurance not found")
    return result


@router.put("/insurance/{insurance_id}", response_model=InsuranceResponse)
async def update_insurance(
    insurance_id: str,
    data: InsuranceUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update an insurance policy."""
    service = FinanceService(db)
    result = await service.update_insurance(user_id, insurance_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Insurance not found")
    return result


@router.delete("/insurance/{insurance_id}")
async def delete_insurance(
    insurance_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete an insurance policy."""
    service = FinanceService(db)
    success = await service.delete_insurance(user_id, insurance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Insurance not found")
    return {"message": "Insurance deleted successfully"}


# =============================================================================
# GOAL ROUTES
# =============================================================================

@router.get("/goals", response_model=List[GoalResponse])
async def get_goals(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all financial goals for the current user."""
    service = FinanceService(db)
    return await service.get_goal_list(user_id)


@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    data: GoalCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new financial goal."""
    service = FinanceService(db)
    return await service.create_goal(user_id, data)


@router.get("/goals/{goal_id}", response_model=GoalResponse)
async def get_goal_by_id(
    goal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific financial goal."""
    service = FinanceService(db)
    result = await service.get_goal_by_id(user_id, goal_id)
    if not result:
        raise HTTPException(status_code=404, detail="Goal not found")
    return result


@router.put("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    data: GoalUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a financial goal."""
    service = FinanceService(db)
    result = await service.update_goal(user_id, goal_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Goal not found")
    return result


@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a financial goal."""
    service = FinanceService(db)
    success = await service.delete_goal(user_id, goal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted successfully"}


# =============================================================================
# DASHBOARD
# =============================================================================

@router.get("/dashboard", response_model=Dashboard)
async def get_dashboard(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get dashboard data with aggregated financial summary.
    
    Returns:
    - Total income, expenses, investments, loans
    - Net worth calculation
    - Monthly summary
    - Counts of different financial entities
    """
    service = FinanceService(db)
    return await service.get_dashboard(user_id)
