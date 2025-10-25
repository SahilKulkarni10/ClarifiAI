from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from models import (
    IncomeCreate, Income, ExpenseCreate, Expense,
    InvestmentCreate, Investment, LoanCreate, Loan,
    InsuranceCreate, Insurance, BudgetCreate, Budget,
    GoalCreate, Goal
)
from auth import get_current_user
from database import get_database
from rag_system import vector_store
from utils import prepare_document_for_mongo, prepare_document_for_vector_store
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/finance", tags=["Finance Data"])

# Income Routes
@router.post("/income", response_model=dict)
async def add_income(
    income_data: IncomeCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add income record"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Create income document
        income_doc = {
            "user_id": user_id,
            **income_data.dict(),
            "created_at": datetime.utcnow()
        }
        
        # Prepare document for MongoDB (handle date and enum conversions)
        income_doc = prepare_document_for_mongo(income_doc)
        
        # Insert to database
        result = await db.income.insert_one(income_doc)
        
        # Add to vector store (prepare a separate document with simple types)
        vector_doc = prepare_document_for_vector_store(income_data.dict())
        vector_doc["user_id"] = user_id
        vector_doc["created_at"] = datetime.utcnow()
        await vector_store.add_user_data(user_id, "income", vector_doc)
        
        logger.info(f"Income added for user: {user_id}")
        
        return {
            "message": "Income added successfully",
            "id": str(result.inserted_id)
        }
        
    except Exception as e:
        logger.error(f"Error adding income: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/income", response_model=List[dict])
async def get_income(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(default=50, le=100),
    skip: int = Query(default=0, ge=0)
):
    """Get user income records"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        cursor = db.income.find(
            {"user_id": user_id}
        ).sort("date", -1).skip(skip).limit(limit)
        
        income_records = []
        async for record in cursor:
            record["_id"] = str(record["_id"])
            income_records.append(record)
        
        return income_records
        
    except Exception as e:
        logger.error(f"Error fetching income: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/income/{income_id}", response_model=dict)
async def update_income(
    income_id: str,
    income_data: IncomeCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update income record"""
    try:
        from bson import ObjectId
        db = get_database()
        user_id = current_user["sub"]
        
        # Check if income exists and belongs to user
        existing = await db.income.find_one({
            "_id": ObjectId(income_id),
            "user_id": user_id
        })
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Income not found"
            )
        
        # Update income document
        update_doc = {
            **income_data.dict(),
            "updated_at": datetime.utcnow()
        }
        update_doc = prepare_document_for_mongo(update_doc)
        
        await db.income.update_one(
            {"_id": ObjectId(income_id)},
            {"$set": update_doc}
        )
        
        logger.info(f"Income {income_id} updated for user: {user_id}")
        
        return {"message": "Income updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating income: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/income/{income_id}", response_model=dict)
async def delete_income(
    income_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete income record"""
    try:
        from bson import ObjectId
        db = get_database()
        user_id = current_user["sub"]
        
        # Check if income exists and belongs to user
        existing = await db.income.find_one({
            "_id": ObjectId(income_id),
            "user_id": user_id
        })
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Income not found"
            )
        
        await db.income.delete_one({"_id": ObjectId(income_id)})
        
        logger.info(f"Income {income_id} deleted for user: {user_id}")
        
        return {"message": "Income deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting income: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Expense Routes
@router.post("/expenses", response_model=dict)
async def add_expense(
    expense_data: ExpenseCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add expense record"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Create expense document
        expense_doc = {
            "user_id": user_id,
            **expense_data.dict(),
            "created_at": datetime.utcnow()
        }
        
        # Prepare document for MongoDB (handle date and enum conversions)
        expense_doc = prepare_document_for_mongo(expense_doc)
        
        # Insert to database
        result = await db.expenses.insert_one(expense_doc)
        
        # Add to vector store (prepare a separate document with simple types)
        vector_doc = prepare_document_for_vector_store(expense_data.dict())
        vector_doc["user_id"] = user_id
        vector_doc["created_at"] = datetime.utcnow()
        await vector_store.add_user_data(user_id, "expense", vector_doc)
        
        logger.info(f"Expense added for user: {user_id}")
        
        return {
            "message": "Expense added successfully",
            "id": str(result.inserted_id)
        }
        
    except Exception as e:
        logger.error(f"Error adding expense: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/expenses", response_model=List[dict])
async def get_expenses(
    current_user: dict = Depends(get_current_user),
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=100),
    skip: int = Query(default=0, ge=0)
):
    """Get user expense records"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Build query
        query = {"user_id": user_id}
        if category:
            query["category"] = category
        
        cursor = db.expenses.find(query).sort("date", -1).skip(skip).limit(limit)
        
        expense_records = []
        async for record in cursor:
            record["_id"] = str(record["_id"])
            expense_records.append(record)
        
        return expense_records
        
    except Exception as e:
        logger.error(f"Error fetching expenses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/expenses/{expense_id}", response_model=dict)
async def update_expense(
    expense_id: str,
    expense_data: ExpenseCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update expense record"""
    try:
        from bson import ObjectId
        db = get_database()
        user_id = current_user["sub"]
        
        # Check if expense exists and belongs to user
        existing = await db.expenses.find_one({
            "_id": ObjectId(expense_id),
            "user_id": user_id
        })
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        # Update expense document
        update_doc = {
            **expense_data.dict(),
            "updated_at": datetime.utcnow()
        }
        update_doc = prepare_document_for_mongo(update_doc)
        
        await db.expenses.update_one(
            {"_id": ObjectId(expense_id)},
            {"$set": update_doc}
        )
        
        logger.info(f"Expense {expense_id} updated for user: {user_id}")
        
        return {"message": "Expense updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating expense: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/expenses/{expense_id}", response_model=dict)
async def delete_expense(
    expense_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete expense record"""
    try:
        from bson import ObjectId
        db = get_database()
        user_id = current_user["sub"]
        
        # Check if expense exists and belongs to user
        existing = await db.expenses.find_one({
            "_id": ObjectId(expense_id),
            "user_id": user_id
        })
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        await db.expenses.delete_one({"_id": ObjectId(expense_id)})
        
        logger.info(f"Expense {expense_id} deleted for user: {user_id}")
        
        return {"message": "Expense deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting expense: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Investment Routes
@router.post("/investments", response_model=dict)
async def add_investment(
    investment_data: InvestmentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add investment record"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Create investment document
        investment_doc = {
            "user_id": user_id,
            **investment_data.dict(),
            "created_at": datetime.utcnow()
        }
        
        # Prepare document for MongoDB (handle date and enum conversions)
        investment_doc = prepare_document_for_mongo(investment_doc)
        
        # Insert to database
        result = await db.investments.insert_one(investment_doc)
        
        # Add to vector store (prepare a separate document with simple types)
        vector_doc = prepare_document_for_vector_store(investment_data.dict())
        vector_doc["user_id"] = user_id
        vector_doc["created_at"] = datetime.utcnow()
        await vector_store.add_user_data(user_id, "investment", vector_doc)
        
        logger.info(f"Investment added for user: {user_id}")
        
        return {
            "message": "Investment added successfully",
            "id": str(result.inserted_id)
        }
        
    except Exception as e:
        logger.error(f"Error adding investment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/investments", response_model=List[dict])
async def get_investments(
    current_user: dict = Depends(get_current_user),
    investment_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=100),
    skip: int = Query(default=0, ge=0)
):
    """Get user investment records"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Build query
        query = {"user_id": user_id}
        if investment_type:
            query["type"] = investment_type
        
        cursor = db.investments.find(query).sort("date", -1).skip(skip).limit(limit)
        
        investment_records = []
        async for record in cursor:
            record["_id"] = str(record["_id"])
            investment_records.append(record)
        
        return investment_records
        
    except Exception as e:
        logger.error(f"Error fetching investments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/investments/{investment_id}", response_model=dict)
async def update_investment(
    investment_id: str,
    investment_data: InvestmentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update investment record"""
    try:
        from bson import ObjectId
        db = get_database()
        user_id = current_user["sub"]
        
        # Check if investment exists and belongs to user
        existing = await db.investments.find_one({
            "_id": ObjectId(investment_id),
            "user_id": user_id
        })
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investment not found"
            )
        
        # Update investment document
        update_doc = {
            **investment_data.dict(),
            "updated_at": datetime.utcnow()
        }
        update_doc = prepare_document_for_mongo(update_doc)
        
        await db.investments.update_one(
            {"_id": ObjectId(investment_id)},
            {"$set": update_doc}
        )
        
        logger.info(f"Investment {investment_id} updated for user: {user_id}")
        
        return {"message": "Investment updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating investment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/investments/{investment_id}", response_model=dict)
async def delete_investment(
    investment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete investment record"""
    try:
        from bson import ObjectId
        db = get_database()
        user_id = current_user["sub"]
        
        # Check if investment exists and belongs to user
        existing = await db.investments.find_one({
            "_id": ObjectId(investment_id),
            "user_id": user_id
        })
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investment not found"
            )
        
        await db.investments.delete_one({"_id": ObjectId(investment_id)})
        
        logger.info(f"Investment {investment_id} deleted for user: {user_id}")
        
        return {"message": "Investment deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting investment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Loan Routes
@router.post("/loans", response_model=dict)
async def add_loan(
    loan_data: LoanCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add loan record"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Create loan document
        loan_doc = {
            "user_id": user_id,
            **loan_data.dict(),
            "created_at": datetime.utcnow()
        }
        
        # Prepare document for MongoDB (handle date and enum conversions)
        loan_doc = prepare_document_for_mongo(loan_doc)
        
        # Insert to database
        result = await db.loans.insert_one(loan_doc)
        
        # Add to vector store (prepare a separate document with simple types)
        vector_doc = prepare_document_for_vector_store(loan_data.dict())
        vector_doc["user_id"] = user_id
        vector_doc["created_at"] = datetime.utcnow()
        await vector_store.add_user_data(user_id, "loan", vector_doc)
        
        logger.info(f"Loan added for user: {user_id}")
        
        return {
            "message": "Loan added successfully",
            "id": str(result.inserted_id)
        }
        
    except Exception as e:
        logger.error(f"Error adding loan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/loans", response_model=List[dict])
async def get_loans(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(default=50, le=100),
    skip: int = Query(default=0, ge=0)
):
    """Get user loan records"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        cursor = db.loans.find(
            {"user_id": user_id}
        ).sort("start_date", -1).skip(skip).limit(limit)
        
        loan_records = []
        async for record in cursor:
            record["_id"] = str(record["_id"])
            loan_records.append(record)
        
        return loan_records
        
    except Exception as e:
        logger.error(f"Error fetching loans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/loans/{loan_id}", response_model=dict)
async def update_loan(
    loan_id: str,
    loan_data: LoanCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update loan record"""
    try:
        from bson import ObjectId
        db = get_database()
        user_id = current_user["sub"]
        
        # Check if loan exists and belongs to user
        existing = await db.loans.find_one({
            "_id": ObjectId(loan_id),
            "user_id": user_id
        })
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan not found"
            )
        
        # Update loan document
        update_doc = {
            **loan_data.dict(),
            "updated_at": datetime.utcnow()
        }
        update_doc = prepare_document_for_mongo(update_doc)
        
        await db.loans.update_one(
            {"_id": ObjectId(loan_id)},
            {"$set": update_doc}
        )
        
        logger.info(f"Loan {loan_id} updated for user: {user_id}")
        
        return {"message": "Loan updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating loan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/loans/{loan_id}", response_model=dict)
async def delete_loan(
    loan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete loan record"""
    try:
        from bson import ObjectId
        db = get_database()
        user_id = current_user["sub"]
        
        # Check if loan exists and belongs to user
        existing = await db.loans.find_one({
            "_id": ObjectId(loan_id),
            "user_id": user_id
        })
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan not found"
            )
        
        await db.loans.delete_one({"_id": ObjectId(loan_id)})
        
        logger.info(f"Loan {loan_id} deleted for user: {user_id}")
        
        return {"message": "Loan deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting loan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Insurance Routes
@router.post("/insurance", response_model=dict)
async def add_insurance(
    insurance_data: InsuranceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add insurance record"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Create insurance document
        insurance_doc = {
            "user_id": user_id,
            **insurance_data.dict(),
            "created_at": datetime.utcnow()
        }
        
        # Prepare document for MongoDB (handle date and enum conversions)
        insurance_doc = prepare_document_for_mongo(insurance_doc)
        
        # Insert to database
        result = await db.insurance.insert_one(insurance_doc)
        
        # Add to vector store (prepare a separate document with simple types)
        vector_doc = prepare_document_for_vector_store(insurance_data.dict())
        vector_doc["user_id"] = user_id
        vector_doc["created_at"] = datetime.utcnow()
        await vector_store.add_user_data(user_id, "insurance", vector_doc)
        
        logger.info(f"Insurance added for user: {user_id}")
        
        return {
            "message": "Insurance added successfully",
            "id": str(result.inserted_id)
        }
        
    except Exception as e:
        logger.error(f"Error adding insurance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/insurance", response_model=List[dict])
async def get_insurance(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(default=50, le=100),
    skip: int = Query(default=0, ge=0)
):
    """Get user insurance records"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        cursor = db.insurance.find(
            {"user_id": user_id}
        ).sort("start_date", -1).skip(skip).limit(limit)
        
        insurance_records = []
        async for record in cursor:
            record["_id"] = str(record["_id"])
            insurance_records.append(record)
        
        return insurance_records
        
    except Exception as e:
        logger.error(f"Error fetching insurance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Budget Routes
@router.post("/budgets", response_model=dict)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create budget"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Check if budget already exists for the month
        existing_budget = await db.budgets.find_one({
            "user_id": user_id,
            "month": budget_data.month
        })
        
        if existing_budget:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Budget already exists for this month"
            )
        
        # Create budget document
        budget_doc = {
            "user_id": user_id,
            **budget_data.dict(),
            "created_at": datetime.utcnow()
        }
        
        # Prepare document for MongoDB (handle date and enum conversions)
        budget_doc = prepare_document_for_mongo(budget_doc)
        
        # Insert to database
        result = await db.budgets.insert_one(budget_doc)
        
        # Add to vector store (prepare a separate document with simple types)
        vector_doc = prepare_document_for_vector_store(budget_data.dict())
        vector_doc["user_id"] = user_id
        vector_doc["created_at"] = datetime.utcnow()
        await vector_store.add_user_data(user_id, "budget", vector_doc)
        
        logger.info(f"Budget created for user: {user_id}")
        
        return {
            "message": "Budget created successfully",
            "id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating budget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/budgets", response_model=List[dict])
async def get_budgets(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(default=12, le=24),
    skip: int = Query(default=0, ge=0)
):
    """Get user budgets"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        cursor = db.budgets.find(
            {"user_id": user_id}
        ).sort("month", -1).skip(skip).limit(limit)
        
        budget_records = []
        async for record in cursor:
            record["_id"] = str(record["_id"])
            budget_records.append(record)
        
        return budget_records
        
    except Exception as e:
        logger.error(f"Error fetching budgets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Goal Routes
@router.post("/goals", response_model=dict)
async def create_goal(
    goal_data: GoalCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create financial goal"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Create goal document
        goal_doc = {
            "user_id": user_id,
            **goal_data.dict(),
            "created_at": datetime.utcnow()
        }
        
        # Prepare document for MongoDB (handle date and enum conversions)
        goal_doc = prepare_document_for_mongo(goal_doc)
        
        # Insert to database
        result = await db.goals.insert_one(goal_doc)
        
        # Add to vector store (prepare a separate document with simple types)
        vector_doc = prepare_document_for_vector_store(goal_data.dict())
        vector_doc["user_id"] = user_id
        vector_doc["created_at"] = datetime.utcnow()
        await vector_store.add_user_data(user_id, "goal", vector_doc)
        
        logger.info(f"Goal created for user: {user_id}")
        
        return {
            "message": "Goal created successfully",
            "id": str(result.inserted_id)
        }
        
    except Exception as e:
        logger.error(f"Error creating goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/goals", response_model=List[dict])
async def get_goals(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(default=20, le=50),
    skip: int = Query(default=0, ge=0)
):
    """Get user goals"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        cursor = db.goals.find(
            {"user_id": user_id}
        ).sort("target_date", 1).skip(skip).limit(limit)
        
        goal_records = []
        async for record in cursor:
            record["_id"] = str(record["_id"])
            # Calculate progress percentage
            if record["target_amount"] > 0:
                record["progress_percentage"] = (record["current_amount"] / record["target_amount"]) * 100
            else:
                record["progress_percentage"] = 0
            goal_records.append(record)
        
        return goal_records
        
    except Exception as e:
        logger.error(f"Error fetching goals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Dashboard Route
@router.get("/dashboard", response_model=dict)
async def get_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get user financial dashboard summary"""
    try:
        db = get_database()
        user_id = current_user["sub"]
        
        # Calculate total income
        total_income = 0
        async for record in db.income.find({"user_id": user_id}):
            total_income += record.get("amount", 0)
        
        # Calculate total expenses
        total_expenses = 0
        async for record in db.expense.find({"user_id": user_id}):
            total_expenses += record.get("amount", 0)
        
        # Calculate total investments
        total_investments = 0
        async for record in db.investment.find({"user_id": user_id}):
            total_investments += record.get("current_value", record.get("amount", 0))
        
        # Calculate total loans
        total_loans = 0
        async for record in db.loan.find({"user_id": user_id}):
            total_loans += record.get("outstanding", 0)
        
        # Calculate monthly summary (current month)
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        first_day_of_month = datetime(now.year, now.month, 1)
        
        monthly_income = 0
        async for record in db.income.find({
            "user_id": user_id,
            "date": {"$gte": first_day_of_month}
        }):
            monthly_income += record.get("amount", 0)
        
        monthly_expenses = 0
        async for record in db.expense.find({
            "user_id": user_id,
            "date": {"$gte": first_day_of_month}
        }):
            monthly_expenses += record.get("amount", 0)
        
        # Calculate net worth
        net_worth = total_income - total_expenses + total_investments - total_loans
        
        # Get recent transactions count
        income_count = await db.income.count_documents({"user_id": user_id})
        expense_count = await db.expense.count_documents({"user_id": user_id})
        investment_count = await db.investment.count_documents({"user_id": user_id})
        loan_count = await db.loan.count_documents({"user_id": user_id})
        insurance_count = await db.insurance.count_documents({"user_id": user_id})
        goal_count = await db.goals.count_documents({"user_id": user_id})
        
        logger.info(f"Dashboard data fetched for user: {user_id}")
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "total_investments": total_investments,
            "total_loans": total_loans,
            "net_worth": net_worth,
            "monthly_summary": {
                "income": monthly_income,
                "expenses": monthly_expenses,
                "savings": monthly_income - monthly_expenses
            },
            "counts": {
                "income": income_count,
                "expenses": expense_count,
                "investments": investment_count,
                "loans": loan_count,
                "insurance": insurance_count,
                "goals": goal_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
