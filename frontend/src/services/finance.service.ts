/**
 * Finance Service
 * Handles all finance-related API calls
 */

import { apiClient } from '@/lib/api-client';
import { API_ENDPOINTS } from '@/lib/api-config';

// Types for finance data
export interface Income {
  id?: string;
  source: string;
  amount: number;
  date: string;
  category: string;
  description?: string;
}

export interface Expense {
  id?: string;
  category: string;
  amount: number;
  date: string;
  description?: string;
}

export interface Investment {
  id?: string;
  type: string;
  name: string;
  amount: number;
  current_value?: number;
  purchase_date: string;
}

export interface Loan {
  id?: string;
  type: string;
  principal: number;
  interest_rate: number;
  emi: number;
  outstanding: number;
  start_date: string;
  end_date: string;
}

export interface Insurance {
  id?: string;
  type: string;
  provider: string;
  premium: number;
  coverage: number;
  start_date: string;
  end_date: string;
}

export interface Goal {
  id?: string;
  name: string;
  target_amount: number;
  current_amount: number;
  target_date: string;
  priority: string;
}

export interface Dashboard {
  total_income: number;
  total_expenses: number;
  total_investments: number;
  total_loans: number;
  net_worth: number;
  monthly_summary: {
    income: number;
    expenses: number;
    savings: number;
  };
  counts: {
    income: number;
    expenses: number;
    investments: number;
    loans: number;
    insurance: number;
    goals: number;
  };
}

class FinanceService {
  // Income methods
  async getIncome(): Promise<Income[]> {
    return apiClient.get<Income[]>(API_ENDPOINTS.finance.income);
  }

  async createIncome(data: Income): Promise<Income> {
    return apiClient.post<Income>(API_ENDPOINTS.finance.income, data);
  }

  async updateIncome(id: string, data: Income): Promise<Income> {
    return apiClient.put<Income>(`${API_ENDPOINTS.finance.income}/${id}`, data);
  }

  async deleteIncome(id: string): Promise<void> {
    return apiClient.delete<void>(`${API_ENDPOINTS.finance.income}/${id}`);
  }

  // Expense methods
  async getExpenses(): Promise<Expense[]> {
    return apiClient.get<Expense[]>(API_ENDPOINTS.finance.expense);
  }

  async createExpense(data: Expense): Promise<Expense> {
    return apiClient.post<Expense>(API_ENDPOINTS.finance.expense, data);
  }

  async updateExpense(id: string, data: Expense): Promise<Expense> {
    return apiClient.put<Expense>(`${API_ENDPOINTS.finance.expense}/${id}`, data);
  }

  async deleteExpense(id: string): Promise<void> {
    return apiClient.delete<void>(`${API_ENDPOINTS.finance.expense}/${id}`);
  }

  // Investment methods
  async getInvestments(): Promise<Investment[]> {
    return apiClient.get<Investment[]>(API_ENDPOINTS.finance.investment);
  }

  async createInvestment(data: Investment): Promise<Investment> {
    return apiClient.post<Investment>(API_ENDPOINTS.finance.investment, data);
  }

  async updateInvestment(id: string, data: Investment): Promise<Investment> {
    return apiClient.put<Investment>(`${API_ENDPOINTS.finance.investment}/${id}`, data);
  }

  async deleteInvestment(id: string): Promise<void> {
    return apiClient.delete<void>(`${API_ENDPOINTS.finance.investment}/${id}`);
  }

  // Loan methods
  async getLoans(): Promise<Loan[]> {
    return apiClient.get<Loan[]>(API_ENDPOINTS.finance.loan);
  }

  async createLoan(data: Loan): Promise<Loan> {
    return apiClient.post<Loan>(API_ENDPOINTS.finance.loan, data);
  }

  async updateLoan(id: string, data: Loan): Promise<Loan> {
    return apiClient.put<Loan>(`${API_ENDPOINTS.finance.loan}/${id}`, data);
  }

  async deleteLoan(id: string): Promise<void> {
    return apiClient.delete<void>(`${API_ENDPOINTS.finance.loan}/${id}`);
  }

  // Insurance methods
  async getInsurance(): Promise<Insurance[]> {
    return apiClient.get<Insurance[]>(API_ENDPOINTS.finance.insurance);
  }

  async createInsurance(data: Insurance): Promise<Insurance> {
    return apiClient.post<Insurance>(API_ENDPOINTS.finance.insurance, data);
  }

  async updateInsurance(id: string, data: Insurance): Promise<Insurance> {
    return apiClient.put<Insurance>(`${API_ENDPOINTS.finance.insurance}/${id}`, data);
  }

  async deleteInsurance(id: string): Promise<void> {
    return apiClient.delete<void>(`${API_ENDPOINTS.finance.insurance}/${id}`);
  }

  // Goal methods
  async getGoals(): Promise<Goal[]> {
    return apiClient.get<Goal[]>(API_ENDPOINTS.finance.goal);
  }

  async createGoal(data: Goal): Promise<Goal> {
    return apiClient.post<Goal>(API_ENDPOINTS.finance.goal, data);
  }

  async updateGoal(id: string, data: Goal): Promise<Goal> {
    return apiClient.put<Goal>(`${API_ENDPOINTS.finance.goal}/${id}`, data);
  }

  async deleteGoal(id: string): Promise<void> {
    return apiClient.delete<void>(`${API_ENDPOINTS.finance.goal}/${id}`);
  }

  // Dashboard
  async getDashboard(): Promise<Dashboard> {
    return apiClient.get<Dashboard>(API_ENDPOINTS.finance.dashboard);
  }
}

export const financeService = new FinanceService();
