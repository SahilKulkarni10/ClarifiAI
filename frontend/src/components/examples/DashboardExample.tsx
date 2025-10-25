/**
 * Example Dashboard Component
 * Demonstrates how to use the finance service to fetch and display data
 */

import { useEffect, useState } from 'react';
import { financeService, type Dashboard } from '@/services/finance.service';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export const DashboardExample = () => {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        const data = await financeService.getDashboard();
        setDashboard(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (loading) {
    return <div>Loading dashboard...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  if (!dashboard) {
    return <div>No data available</div>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Income</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            ₹{dashboard.total_income.toLocaleString()}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Expenses</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            ₹{dashboard.total_expenses.toLocaleString()}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Investments</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            ₹{dashboard.total_investments.toLocaleString()}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Net Worth</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            ₹{dashboard.net_worth.toLocaleString()}
          </div>
        </CardContent>
      </Card>

      <Card className="col-span-full">
        <CardHeader>
          <CardTitle>Monthly Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <p className="text-sm text-muted-foreground">Income</p>
              <p className="text-xl font-bold">
                ₹{dashboard.monthly_summary.income.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Expenses</p>
              <p className="text-xl font-bold">
                ₹{dashboard.monthly_summary.expenses.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Savings</p>
              <p className="text-xl font-bold text-green-600">
                ₹{dashboard.monthly_summary.savings.toLocaleString()}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
