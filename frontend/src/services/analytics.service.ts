/**
 * Analytics Service
 * Handles all analytics-related API calls
 */

import { apiClient } from '@/lib/api-client';

// Types for analytics data
export interface FinancialSummary {
  total_income: number;
  total_expenses: number;
  total_investments: number;
  total_loans: number;
  net_worth: number;
  savings_rate: number;
  monthly_cash_flow: number;
}

export interface CategoryBreakdown {
  [category: string]: number;
}

export interface MonthlyTrend {
  month: string;
  amount: number;
}

export interface TopExpense {
  _id: string;
  amount: number;
  description: string;
  category: string;
  date: string;
  merchant?: string;
}

export interface ExpenseAnalytics {
  category_breakdown: CategoryBreakdown;
  monthly_trend: MonthlyTrend[];
  top_expenses: TopExpense[];
}

export interface PortfolioBreakdown {
  [type: string]: number;
}

export interface PerformanceData {
  name: string;
  invested: number;
  current: number;
  gain_loss: number;
  gain_loss_percentage: number;
}

export interface InvestmentAnalytics {
  portfolio_breakdown: PortfolioBreakdown;
  total_invested: number;
  total_current: number;
  total_gain_loss: number;
  performance_data: PerformanceData[];
}

class AnalyticsService {
  // Financial summary
  async getFinancialSummary(month?: string): Promise<FinancialSummary> {
    const params = month ? `?month=${month}` : '';
    return apiClient.get<FinancialSummary>(`/analytics/summary${params}`);
  }

  // Expense analytics
  async getExpenseAnalytics(months: number = 6): Promise<ExpenseAnalytics> {
    return apiClient.get<ExpenseAnalytics>(`/analytics/expenses?months=${months}`);
  }

  // Investment analytics
  async getInvestmentAnalytics(): Promise<InvestmentAnalytics> {
    return apiClient.get<InvestmentAnalytics>('/analytics/investments');
  }
}

export const analyticsService = new AnalyticsService();
