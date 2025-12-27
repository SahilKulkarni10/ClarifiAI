"""
Finance Service
Handles all financial data CRUD operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from app.models.finance import (
    IncomeCreate, IncomeUpdate, IncomeResponse,
    ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    InvestmentCreate, InvestmentUpdate, InvestmentResponse,
    LoanCreate, LoanUpdate, LoanResponse,
    InsuranceCreate, InsuranceUpdate, InsuranceResponse,
    GoalCreate, GoalUpdate, GoalResponse,
    Dashboard, MonthlySummary, DashboardCounts
)


class FinanceService:
    """Service for financial data operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _doc_to_response(self, doc: dict, response_class, **extra_fields):
        """Convert MongoDB document to response model."""
        doc["id"] = str(doc.pop("_id"))
        if "user_id" in doc:
            doc["user_id"] = str(doc["user_id"])
        if "created_at" in doc and isinstance(doc["created_at"], datetime):
            doc["created_at"] = doc["created_at"].isoformat()
        doc.update(extra_fields)
        return response_class(**doc)
    
    async def _get_user_object_id(self, user_id: str) -> ObjectId:
        """Convert user_id string to ObjectId."""
        try:
            return ObjectId(user_id)
        except Exception:
            return user_id
    
    # =========================================================================
    # INCOME OPERATIONS
    # =========================================================================
    
    async def get_income_list(self, user_id: str) -> List[IncomeResponse]:
        """Get all income records for a user."""
        user_oid = await self._get_user_object_id(user_id)
        cursor = self.db.income.find({"user_id": user_oid}).sort("date", -1)
        
        results = []
        async for doc in cursor:
            results.append(self._doc_to_response(doc, IncomeResponse))
        
        return results
    
    async def get_income_by_id(self, user_id: str, income_id: str) -> Optional[IncomeResponse]:
        """Get a specific income record by ID."""
        user_oid = await self._get_user_object_id(user_id)
        doc = await self.db.income.find_one({
            "_id": ObjectId(income_id),
            "user_id": user_oid
        })
        if not doc:
            return None
        return self._doc_to_response(doc, IncomeResponse)
    
    async def create_income(
        self,
        user_id: str,
        data: IncomeCreate
    ) -> IncomeResponse:
        """Create a new income record."""
        user_oid = await self._get_user_object_id(user_id)
        
        doc = {
            "user_id": user_oid,
            "source": data.source,
            "amount": data.amount,
            "date": data.date,
            "category": data.category,
            "description": data.description,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.income.insert_one(doc)
        doc["_id"] = result.inserted_id
        
        logger.info(f"Income created for user {user_id}: {data.amount}")
        return self._doc_to_response(doc, IncomeResponse)
    
    async def update_income(
        self,
        user_id: str,
        income_id: str,
        data: IncomeUpdate
    ) -> IncomeResponse:
        """Update an existing income record."""
        user_oid = await self._get_user_object_id(user_id)
        
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.income.update_one(
            {"_id": ObjectId(income_id), "user_id": user_oid},
            {"$set": update_data}
        )
        
        doc = await self.db.income.find_one({"_id": ObjectId(income_id)})
        if not doc:
            raise ValueError("Income record not found")
        
        return self._doc_to_response(doc, IncomeResponse)
    
    async def delete_income(self, user_id: str, income_id: str) -> bool:
        """Delete an income record."""
        user_oid = await self._get_user_object_id(user_id)
        
        result = await self.db.income.delete_one({
            "_id": ObjectId(income_id),
            "user_id": user_oid
        })
        
        if result.deleted_count == 0:
            raise ValueError("Income record not found")
        
        logger.info(f"Income deleted: {income_id}")
        return True
    
    # =========================================================================
    # EXPENSE OPERATIONS
    # =========================================================================
    
    async def get_expense_list(self, user_id: str) -> List[ExpenseResponse]:
        """Get all expense records for a user."""
        user_oid = await self._get_user_object_id(user_id)
        cursor = self.db.expenses.find({"user_id": user_oid}).sort("date", -1)
        
        results = []
        async for doc in cursor:
            results.append(self._doc_to_response(doc, ExpenseResponse))
        
        return results
    
    async def get_expense_by_id(self, user_id: str, expense_id: str) -> Optional[ExpenseResponse]:
        """Get a specific expense record by ID."""
        user_oid = await self._get_user_object_id(user_id)
        doc = await self.db.expenses.find_one({
            "_id": ObjectId(expense_id),
            "user_id": user_oid
        })
        if not doc:
            return None
        return self._doc_to_response(doc, ExpenseResponse)
    
    async def create_expense(
        self,
        user_id: str,
        data: ExpenseCreate
    ) -> ExpenseResponse:
        """Create a new expense record."""
        user_oid = await self._get_user_object_id(user_id)
        
        doc = {
            "user_id": user_oid,
            "category": data.category,
            "amount": data.amount,
            "date": data.date,
            "description": data.description,
            "merchant": data.merchant,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.expenses.insert_one(doc)
        doc["_id"] = result.inserted_id
        
        logger.info(f"Expense created for user {user_id}: {data.amount}")
        return self._doc_to_response(doc, ExpenseResponse)
    
    async def update_expense(
        self,
        user_id: str,
        expense_id: str,
        data: ExpenseUpdate
    ) -> ExpenseResponse:
        """Update an existing expense record."""
        user_oid = await self._get_user_object_id(user_id)
        
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.expenses.update_one(
            {"_id": ObjectId(expense_id), "user_id": user_oid},
            {"$set": update_data}
        )
        
        doc = await self.db.expenses.find_one({"_id": ObjectId(expense_id)})
        if not doc:
            raise ValueError("Expense record not found")
        
        return self._doc_to_response(doc, ExpenseResponse)
    
    async def delete_expense(self, user_id: str, expense_id: str) -> bool:
        """Delete an expense record."""
        user_oid = await self._get_user_object_id(user_id)
        
        result = await self.db.expenses.delete_one({
            "_id": ObjectId(expense_id),
            "user_id": user_oid
        })
        
        if result.deleted_count == 0:
            raise ValueError("Expense record not found")
        
        logger.info(f"Expense deleted: {expense_id}")
        return True
    
    # =========================================================================
    # INVESTMENT OPERATIONS
    # =========================================================================
    
    async def get_investment_list(self, user_id: str) -> List[InvestmentResponse]:
        """Get all investment records for a user."""
        user_oid = await self._get_user_object_id(user_id)
        cursor = self.db.investments.find({"user_id": user_oid})
        
        results = []
        async for doc in cursor:
            # Calculate gain/loss if current_value is available
            gain_loss = None
            gain_loss_percentage = None
            
            if doc.get("current_value") is not None:
                gain_loss = doc["current_value"] - doc["amount"]
                if doc["amount"] > 0:
                    gain_loss_percentage = (gain_loss / doc["amount"]) * 100
            
            results.append(self._doc_to_response(
                doc, 
                InvestmentResponse,
                gain_loss=gain_loss,
                gain_loss_percentage=gain_loss_percentage
            ))
        
        return results
    
    async def get_investment_by_id(self, user_id: str, investment_id: str) -> Optional[InvestmentResponse]:
        """Get a specific investment record by ID."""
        user_oid = await self._get_user_object_id(user_id)
        doc = await self.db.investments.find_one({
            "_id": ObjectId(investment_id),
            "user_id": user_oid
        })
        if not doc:
            return None
        
        gain_loss = None
        gain_loss_percentage = None
        if doc.get("current_value") is not None:
            gain_loss = doc["current_value"] - doc["amount"]
            if doc["amount"] > 0:
                gain_loss_percentage = (gain_loss / doc["amount"]) * 100
        
        return self._doc_to_response(
            doc,
            InvestmentResponse,
            gain_loss=gain_loss,
            gain_loss_percentage=gain_loss_percentage
        )
    
    async def create_investment(
        self,
        user_id: str,
        data: InvestmentCreate
    ) -> InvestmentResponse:
        """Create a new investment record."""
        user_oid = await self._get_user_object_id(user_id)
        
        doc = {
            "user_id": user_oid,
            "type": data.type,
            "name": data.name,
            "amount": data.amount,
            "current_value": data.current_value or data.amount,
            "purchase_date": data.purchase_date,
            "units": data.units,
            "purchase_price": data.purchase_price,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.investments.insert_one(doc)
        doc["_id"] = result.inserted_id
        
        logger.info(f"Investment created for user {user_id}: {data.name}")
        
        # Calculate gain/loss
        gain_loss = doc["current_value"] - doc["amount"]
        gain_loss_percentage = (gain_loss / doc["amount"]) * 100 if doc["amount"] > 0 else 0
        
        return self._doc_to_response(
            doc,
            InvestmentResponse,
            gain_loss=gain_loss,
            gain_loss_percentage=gain_loss_percentage
        )
    
    async def update_investment(
        self,
        user_id: str,
        investment_id: str,
        data: InvestmentUpdate
    ) -> InvestmentResponse:
        """Update an existing investment record."""
        user_oid = await self._get_user_object_id(user_id)
        
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.investments.update_one(
            {"_id": ObjectId(investment_id), "user_id": user_oid},
            {"$set": update_data}
        )
        
        doc = await self.db.investments.find_one({"_id": ObjectId(investment_id)})
        if not doc:
            raise ValueError("Investment record not found")
        
        # Calculate gain/loss
        gain_loss = None
        gain_loss_percentage = None
        if doc.get("current_value") is not None:
            gain_loss = doc["current_value"] - doc["amount"]
            if doc["amount"] > 0:
                gain_loss_percentage = (gain_loss / doc["amount"]) * 100
        
        return self._doc_to_response(
            doc,
            InvestmentResponse,
            gain_loss=gain_loss,
            gain_loss_percentage=gain_loss_percentage
        )
    
    async def delete_investment(self, user_id: str, investment_id: str) -> bool:
        """Delete an investment record."""
        user_oid = await self._get_user_object_id(user_id)
        
        result = await self.db.investments.delete_one({
            "_id": ObjectId(investment_id),
            "user_id": user_oid
        })
        
        if result.deleted_count == 0:
            raise ValueError("Investment record not found")
        
        logger.info(f"Investment deleted: {investment_id}")
        return True
    
    # =========================================================================
    # LOAN OPERATIONS
    # =========================================================================
    
    async def get_loan_list(self, user_id: str) -> List[LoanResponse]:
        """Get all loan records for a user."""
        user_oid = await self._get_user_object_id(user_id)
        cursor = self.db.loans.find({"user_id": user_oid})
        
        results = []
        async for doc in cursor:
            # Calculate months remaining
            months_remaining = None
            total_interest = None
            
            try:
                from dateutil.parser import parse
                end_date = parse(doc.get("end_date", ""))
                today = datetime.now()
                if end_date > today:
                    months_remaining = (end_date.year - today.year) * 12 + (end_date.month - today.month)
                else:
                    months_remaining = 0
                
                # Calculate total interest (simple approximation)
                if months_remaining and doc.get("emi") and doc.get("outstanding"):
                    total_interest = (doc["emi"] * months_remaining) - doc["outstanding"]
            except Exception:
                pass
            
            results.append(self._doc_to_response(
                doc,
                LoanResponse,
                months_remaining=months_remaining,
                total_interest=total_interest
            ))
        
        return results
    
    async def create_loan(
        self,
        user_id: str,
        data: LoanCreate
    ) -> LoanResponse:
        """Create a new loan record."""
        user_oid = await self._get_user_object_id(user_id)
        
        doc = {
            "user_id": user_oid,
            "type": data.type,
            "principal": data.principal,
            "interest_rate": data.interest_rate,
            "emi": data.emi,
            "outstanding": data.outstanding,
            "start_date": data.start_date,
            "end_date": data.end_date,
            "lender": data.lender,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.loans.insert_one(doc)
        doc["_id"] = result.inserted_id
        
        logger.info(f"Loan created for user {user_id}: {data.type}")
        return self._doc_to_response(doc, LoanResponse)
    
    async def update_loan(
        self,
        user_id: str,
        loan_id: str,
        data: LoanUpdate
    ) -> LoanResponse:
        """Update an existing loan record."""
        user_oid = await self._get_user_object_id(user_id)
        
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.loans.update_one(
            {"_id": ObjectId(loan_id), "user_id": user_oid},
            {"$set": update_data}
        )
        
        doc = await self.db.loans.find_one({"_id": ObjectId(loan_id)})
        if not doc:
            raise ValueError("Loan record not found")
        
        return self._doc_to_response(doc, LoanResponse)
    
    async def delete_loan(self, user_id: str, loan_id: str) -> bool:
        """Delete a loan record."""
        user_oid = await self._get_user_object_id(user_id)
        
        result = await self.db.loans.delete_one({
            "_id": ObjectId(loan_id),
            "user_id": user_oid
        })
        
        if result.deleted_count == 0:
            raise ValueError("Loan record not found")
        
        logger.info(f"Loan deleted: {loan_id}")
        return True
    
    # =========================================================================
    # INSURANCE OPERATIONS
    # =========================================================================
    
    async def get_insurance_list(self, user_id: str) -> List[InsuranceResponse]:
        """Get all insurance records for a user."""
        user_oid = await self._get_user_object_id(user_id)
        cursor = self.db.insurance.find({"user_id": user_oid})
        
        results = []
        async for doc in cursor:
            # Calculate if active and days until renewal
            is_active = None
            days_until_renewal = None
            
            try:
                from dateutil.parser import parse
                end_date = parse(doc.get("end_date", ""))
                today = datetime.now()
                is_active = end_date > today
                if is_active:
                    days_until_renewal = (end_date - today).days
            except Exception:
                pass
            
            results.append(self._doc_to_response(
                doc,
                InsuranceResponse,
                is_active=is_active,
                days_until_renewal=days_until_renewal
            ))
        
        return results
    
    async def create_insurance(
        self,
        user_id: str,
        data: InsuranceCreate
    ) -> InsuranceResponse:
        """Create a new insurance record."""
        user_oid = await self._get_user_object_id(user_id)
        
        doc = {
            "user_id": user_oid,
            "type": data.type,
            "provider": data.provider,
            "premium": data.premium,
            "coverage": data.coverage,
            "start_date": data.start_date,
            "end_date": data.end_date,
            "policy_number": data.policy_number,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.insurance.insert_one(doc)
        doc["_id"] = result.inserted_id
        
        logger.info(f"Insurance created for user {user_id}: {data.type}")
        return self._doc_to_response(doc, InsuranceResponse)
    
    async def update_insurance(
        self,
        user_id: str,
        insurance_id: str,
        data: InsuranceUpdate
    ) -> InsuranceResponse:
        """Update an existing insurance record."""
        user_oid = await self._get_user_object_id(user_id)
        
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.insurance.update_one(
            {"_id": ObjectId(insurance_id), "user_id": user_oid},
            {"$set": update_data}
        )
        
        doc = await self.db.insurance.find_one({"_id": ObjectId(insurance_id)})
        if not doc:
            raise ValueError("Insurance record not found")
        
        return self._doc_to_response(doc, InsuranceResponse)
    
    async def delete_insurance(self, user_id: str, insurance_id: str) -> bool:
        """Delete an insurance record."""
        user_oid = await self._get_user_object_id(user_id)
        
        result = await self.db.insurance.delete_one({
            "_id": ObjectId(insurance_id),
            "user_id": user_oid
        })
        
        if result.deleted_count == 0:
            raise ValueError("Insurance record not found")
        
        logger.info(f"Insurance deleted: {insurance_id}")
        return True
    
    # =========================================================================
    # GOAL OPERATIONS
    # =========================================================================
    
    async def get_goal_list(self, user_id: str) -> List[GoalResponse]:
        """Get all goal records for a user."""
        user_oid = await self._get_user_object_id(user_id)
        cursor = self.db.goals.find({"user_id": user_oid})
        
        results = []
        async for doc in cursor:
            # Calculate progress percentage and monthly required
            progress_percentage = 0
            monthly_required = None
            
            if doc.get("target_amount", 0) > 0:
                progress_percentage = (doc.get("current_amount", 0) / doc["target_amount"]) * 100
            
            try:
                from dateutil.parser import parse
                target_date = parse(doc.get("target_date", ""))
                today = datetime.now()
                if target_date > today:
                    months_left = (target_date.year - today.year) * 12 + (target_date.month - today.month)
                    if months_left > 0:
                        remaining = doc.get("target_amount", 0) - doc.get("current_amount", 0)
                        monthly_required = remaining / months_left
            except Exception:
                pass
            
            results.append(self._doc_to_response(
                doc,
                GoalResponse,
                progress_percentage=round(progress_percentage, 1),
                monthly_required=round(monthly_required, 2) if monthly_required else None
            ))
        
        return results
    
    async def create_goal(
        self,
        user_id: str,
        data: GoalCreate
    ) -> GoalResponse:
        """Create a new goal record."""
        user_oid = await self._get_user_object_id(user_id)
        
        doc = {
            "user_id": user_oid,
            "name": data.name,
            "target_amount": data.target_amount,
            "current_amount": data.current_amount,
            "target_date": data.target_date,
            "priority": data.priority,
            "category": data.category,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.goals.insert_one(doc)
        doc["_id"] = result.inserted_id
        
        logger.info(f"Goal created for user {user_id}: {data.name}")
        
        # Calculate progress
        progress_percentage = 0
        if doc["target_amount"] > 0:
            progress_percentage = (doc["current_amount"] / doc["target_amount"]) * 100
        
        return self._doc_to_response(
            doc,
            GoalResponse,
            progress_percentage=round(progress_percentage, 1)
        )
    
    async def update_goal(
        self,
        user_id: str,
        goal_id: str,
        data: GoalUpdate
    ) -> GoalResponse:
        """Update an existing goal record."""
        user_oid = await self._get_user_object_id(user_id)
        
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.goals.update_one(
            {"_id": ObjectId(goal_id), "user_id": user_oid},
            {"$set": update_data}
        )
        
        doc = await self.db.goals.find_one({"_id": ObjectId(goal_id)})
        if not doc:
            raise ValueError("Goal record not found")
        
        # Calculate progress
        progress_percentage = 0
        if doc.get("target_amount", 0) > 0:
            progress_percentage = (doc.get("current_amount", 0) / doc["target_amount"]) * 100
        
        return self._doc_to_response(
            doc,
            GoalResponse,
            progress_percentage=round(progress_percentage, 1)
        )
    
    async def delete_goal(self, user_id: str, goal_id: str) -> bool:
        """Delete a goal record."""
        user_oid = await self._get_user_object_id(user_id)
        
        result = await self.db.goals.delete_one({
            "_id": ObjectId(goal_id),
            "user_id": user_oid
        })
        
        if result.deleted_count == 0:
            raise ValueError("Goal record not found")
        
        logger.info(f"Goal deleted: {goal_id}")
        return True
    
    # =========================================================================
    # DASHBOARD OPERATIONS
    # =========================================================================
    
    async def get_dashboard(self, user_id: str) -> Dashboard:
        """
        Get comprehensive dashboard data for a user.
        Aggregates all financial data into a single view.
        """
        user_oid = await self._get_user_object_id(user_id)
        
        # Get current month date range
        today = datetime.now()
        first_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Aggregate totals
        total_income = 0
        total_expenses = 0
        total_investments = 0
        total_loans = 0
        monthly_income = 0
        monthly_expenses = 0
        
        # Count records
        counts = DashboardCounts()
        
        # Calculate income totals
        income_cursor = self.db.income.find({"user_id": user_oid})
        async for doc in income_cursor:
            total_income += doc.get("amount", 0)
            counts.income += 1
            
            # Check if in current month
            try:
                from dateutil.parser import parse
                doc_date = parse(doc.get("date", ""))
                if doc_date >= first_of_month:
                    monthly_income += doc.get("amount", 0)
            except Exception:
                pass
        
        # Calculate expense totals
        expense_cursor = self.db.expenses.find({"user_id": user_oid})
        async for doc in expense_cursor:
            total_expenses += doc.get("amount", 0)
            counts.expenses += 1
            
            # Check if in current month
            try:
                from dateutil.parser import parse
                doc_date = parse(doc.get("date", ""))
                if doc_date >= first_of_month:
                    monthly_expenses += doc.get("amount", 0)
            except Exception:
                pass
        
        # Calculate investment totals
        investment_cursor = self.db.investments.find({"user_id": user_oid})
        async for doc in investment_cursor:
            total_investments += doc.get("current_value", doc.get("amount", 0))
            counts.investments += 1
        
        # Calculate loan totals
        loan_cursor = self.db.loans.find({"user_id": user_oid})
        async for doc in loan_cursor:
            total_loans += doc.get("outstanding", 0)
            counts.loans += 1
        
        # Count insurance and goals
        counts.insurance = await self.db.insurance.count_documents({"user_id": user_oid})
        counts.goals = await self.db.goals.count_documents({"user_id": user_oid})
        
        # Calculate net worth
        net_worth = total_income - total_expenses + total_investments - total_loans
        
        # Monthly summary
        monthly_summary = MonthlySummary(
            income=monthly_income,
            expenses=monthly_expenses,
            savings=monthly_income - monthly_expenses
        )
        
        return Dashboard(
            total_income=total_income,
            total_expenses=total_expenses,
            total_investments=total_investments,
            total_loans=total_loans,
            net_worth=net_worth,
            monthly_summary=monthly_summary,
            counts=counts
        )
