import { useState, useEffect, useCallback } from 'react';
import { financeService, type Dashboard } from '@/services/finance.service';

interface UseRealtimeDashboardOptions {
  refreshInterval?: number; // in milliseconds
  autoRefresh?: boolean;
}

export function useRealtimeDashboard(options: UseRealtimeDashboardOptions = {}) {
  const { refreshInterval = 30000, autoRefresh = true } = options; // Default 30 seconds
  
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch all data in parallel for real-time accuracy
      const [
        incomeData,
        expenseData,
        investmentData,
        loanData,
        insuranceData,
        goalData
      ] = await Promise.all([
        financeService.getIncome().catch(() => []),
        financeService.getExpenses().catch(() => []),
        financeService.getInvestments().catch(() => []),
        financeService.getLoans().catch(() => []),
        financeService.getInsurance().catch(() => []),
        financeService.getGoals().catch(() => [])
      ]);

      // Calculate totals from actual data
      let totalIncome = 0;
      for (const item of incomeData) {
        totalIncome += item.amount;
      }

      let totalExpenses = 0;
      for (const item of expenseData) {
        totalExpenses += item.amount;
      }

      let totalInvestments = 0;
      for (const item of investmentData) {
        totalInvestments += item.current_value || item.amount;
      }

      let totalLoans = 0;
      for (const item of loanData) {
        totalLoans += item.outstanding;
      }

      // Calculate current month data
      const now = new Date();
      const currentMonth = now.getMonth();
      const currentYear = now.getFullYear();

      const monthlyIncome = incomeData
        .filter(item => {
          const date = new Date(item.date);
          return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
        })
        .reduce((sum, item) => sum + item.amount, 0);

      const monthlyExpenses = expenseData
        .filter(item => {
          const date = new Date(item.date);
          return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
        })
        .reduce((sum, item) => sum + item.amount, 0);

      const monthlySavings = monthlyIncome - monthlyExpenses;

      // Calculate net worth (assets - liabilities)
      const netWorth = totalInvestments - totalLoans;

      const dashboardData: Dashboard = {
        total_income: totalIncome,
        total_expenses: totalExpenses,
        total_investments: totalInvestments,
        total_loans: totalLoans,
        net_worth: netWorth,
        monthly_summary: {
          income: monthlyIncome,
          expenses: monthlyExpenses,
          savings: monthlySavings
        },
        counts: {
          income: incomeData.length,
          expenses: expenseData.length,
          investments: investmentData.length,
          loans: loanData.length,
          insurance: insuranceData.length,
          goals: goalData.length
        }
      };

      setDashboard(dashboardData);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const intervalId = setInterval(() => {
      fetchDashboard();
    }, refreshInterval);

    return () => clearInterval(intervalId);
  }, [autoRefresh, refreshInterval, fetchDashboard]);

  const refresh = useCallback(() => {
    return fetchDashboard();
  }, [fetchDashboard]);

  return {
    dashboard,
    loading,
    error,
    lastUpdated,
    refresh
  };
}
