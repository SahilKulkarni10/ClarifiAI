import { useEffect, useState } from 'react';
import { AppLayout } from '@/components/layouts/AppLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  PieChart,
  Activity,
  CreditCard,
  ArrowUpRight,
  ArrowDownRight,
  Calendar
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { analyticsService, type FinancialSummary, type ExpenseAnalytics, type InvestmentAnalytics } from '@/services/analytics.service';

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [expenseAnalytics, setExpenseAnalytics] = useState<ExpenseAnalytics | null>(null);
  const [investmentAnalytics, setInvestmentAnalytics] = useState<InvestmentAnalytics | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const [summaryData, expenseData, investmentData] = await Promise.all([
          analyticsService.getFinancialSummary(),
          analyticsService.getExpenseAnalytics(6),
          analyticsService.getInvestmentAnalytics()
        ]);
        setSummary(summaryData);
        setExpenseAnalytics(expenseData);
        setInvestmentAnalytics(investmentData);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto"></div>
            <p className="text-muted-foreground">Loading analytics...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (!summary || !expenseAnalytics || !investmentAnalytics) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <Activity className="h-12 w-12 text-muted-foreground mx-auto" />
            <p className="text-muted-foreground">No analytics data available. Start adding your financial data!</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  // Transform expense analytics into category breakdown for display
  const categoryBreakdown = Object.entries(expenseAnalytics.category_breakdown).map(([name, amount]) => {
    const total = Object.values(expenseAnalytics.category_breakdown).reduce((sum, val) => sum + val, 0);
    const percentage = total > 0 ? (amount / total) * 100 : 0;
    const colorMap: { [key: string]: string } = {
      'housing': 'bg-blue-500',
      'food': 'bg-green-500',
      'transportation': 'bg-yellow-500',
      'entertainment': 'bg-purple-500',
      'shopping': 'bg-pink-500',
      'utilities': 'bg-orange-500',
      'healthcare': 'bg-red-500',
      'other': 'bg-gray-500'
    };
    return {
      name: name.charAt(0).toUpperCase() + name.slice(1),
      amount,
      percentage: Math.round(percentage),
      color: colorMap[name.toLowerCase()] || 'bg-gray-500'
    };
  }).sort((a, b) => b.amount - a.amount);

  const totalExpenses = Object.values(expenseAnalytics.category_breakdown).reduce((sum, val) => sum + val, 0);
  const topCategory = categoryBreakdown.length > 0 ? categoryBreakdown[0] : null;

  // Calculate average monthly expense from trends
  const avgMonthlyExpense = expenseAnalytics.monthly_trend.length > 0
    ? expenseAnalytics.monthly_trend.reduce((sum, item) => sum + item.amount, 0) / expenseAnalytics.monthly_trend.length
    : 0;

  // Calculate investment returns
  const investmentReturns = investmentAnalytics.total_invested > 0
    ? (investmentAnalytics.total_gain_loss / investmentAnalytics.total_invested) * 100
    : 0;

  // Calculate financial health score (simple algorithm)
  const calculateHealthScore = () => {
    let score = 50; // Base score
    
    // Savings rate contribution (max 30 points)
    if (summary.savings_rate > 30) score += 30;
    else if (summary.savings_rate > 20) score += 20;
    else if (summary.savings_rate > 10) score += 10;
    
    // Investment returns contribution (max 20 points)
    if (investmentReturns > 15) score += 20;
    else if (investmentReturns > 10) score += 15;
    else if (investmentReturns > 5) score += 10;
    
    return Math.min(score, 100);
  };

  const healthScore = calculateHealthScore();

  return (
    <AppLayout 
      title="Financial Analytics" 
      description="Detailed insights and trends about your finances"
    >
      {/* Key Insights */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        {/* Top Spending Category */}
        <Card className="border-border/40 bg-gradient-to-br from-blue-500/10 via-background to-background hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Top Spending</CardTitle>
            <PieChart className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {topCategory ? `${topCategory.name}` : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {topCategory ? `₹${topCategory.amount.toLocaleString('en-IN')} (${topCategory.percentage}%)` : 'No data'}
            </p>
          </CardContent>
        </Card>

        {/* Savings Rate */}
        <Card className="border-border/40 bg-gradient-to-br from-green-500/10 via-background to-background hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Savings Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {summary.savings_rate.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
              <ArrowUpRight className="h-3 w-3" />
              ₹{summary.monthly_cash_flow.toLocaleString('en-IN')} saved
            </p>
          </CardContent>
        </Card>

        {/* Average Monthly Expense */}
        <Card className="border-border/40 bg-gradient-to-br from-orange-500/10 via-background to-background hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg. Monthly Expense</CardTitle>
            <CreditCard className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              ₹{Math.round(avgMonthlyExpense).toLocaleString('en-IN')}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Last 6 months average
            </p>
          </CardContent>
        </Card>

        {/* Investment Returns */}
        <Card className="border-border/40 bg-gradient-to-br from-purple-500/10 via-background to-background hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Investment Returns</CardTitle>
            <TrendingUp className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className={cn("text-2xl font-bold", investmentReturns >= 0 ? "text-green-600" : "text-red-600")}>
              {investmentReturns >= 0 ? '+' : ''}{investmentReturns.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
              {investmentReturns >= 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
              ₹{Math.abs(investmentAnalytics.total_gain_loss).toLocaleString('en-IN')}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Spending by Category */}
      <Card className="mb-8 border-border/40">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl flex items-center gap-2">
                <PieChart className="h-6 w-6" />
                Spending by Category
              </CardTitle>
              <CardDescription className="mt-2">Breakdown of your expenses</CardDescription>
            </div>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">Total Expenses</div>
              <div className="text-2xl font-bold">₹{totalExpenses.toLocaleString('en-IN')}</div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {categoryBreakdown.length > 0 ? (
            <div className="space-y-4">
              {categoryBreakdown.map((category, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">{category.name}</span>
                    <span className="text-muted-foreground">
                      ₹{category.amount.toLocaleString('en-IN')} ({category.percentage}%)
                    </span>
                  </div>
                  <div className="relative h-3 bg-muted rounded-full overflow-hidden">
                    <div 
                      className={cn(category.color, "h-full transition-all")}
                      style={{ width: `${category.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">No expense data available</p>
          )}
        </CardContent>
      </Card>

      {/* Monthly Expense Trends */}
      <Card className="mb-8 border-border/40">
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <BarChart3 className="h-6 w-6" />
            Monthly Expense Trends
          </CardTitle>
          <CardDescription>Track your spending patterns over time</CardDescription>
        </CardHeader>
        <CardContent>
          {expenseAnalytics.monthly_trend.length > 0 ? (
            <div className="space-y-6">
              {expenseAnalytics.monthly_trend.map((month, index) => {
                const maxValue = Math.max(...expenseAnalytics.monthly_trend.map(m => m.amount));
                const percentage = maxValue > 0 ? (month.amount / maxValue) * 100 : 0;
                
                return (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-between text-sm font-medium">
                      <span className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        {new Date(month.month).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })}
                      </span>
                      <span className="text-muted-foreground">₹{month.amount.toLocaleString('en-IN')}</span>
                    </div>
                    <div className="relative h-8 bg-muted rounded-lg overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-blue-500 to-blue-400 flex items-center justify-end pr-3 text-white text-xs font-semibold transition-all"
                        style={{ width: `${percentage}%` }}
                      >
                        {percentage > 20 && `₹${month.amount.toLocaleString('en-IN')}`}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">No monthly trend data available</p>
          )}
        </CardContent>
      </Card>

      {/* Financial Health & Top Expenses */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Financial Health Score */}
        <Card className="border-border/40 bg-gradient-to-br from-green-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-green-600" />
              Financial Health Score
            </CardTitle>
            <CardDescription>Overall assessment of your financial wellness</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <div className="text-6xl font-bold text-green-600 mb-2">{healthScore}</div>
              <p className="text-sm text-muted-foreground">Out of 100</p>
            </div>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Savings Rate</span>
                  <span className="font-semibold">{summary.savings_rate.toFixed(1)}%</span>
                </div>
                <Progress value={Math.min(summary.savings_rate * 2, 100)} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Investment Growth</span>
                  <span className="font-semibold">{investmentReturns.toFixed(1)}%</span>
                </div>
                <Progress value={Math.min(Math.abs(investmentReturns) * 5, 100)} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Net Worth</span>
                  <span className={cn("font-semibold", summary.net_worth >= 0 ? "text-green-600" : "text-red-600")}>
                    ₹{Math.abs(summary.net_worth).toLocaleString('en-IN')}
                  </span>
                </div>
                <Progress value={summary.net_worth >= 0 ? 75 : 25} className="h-2" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Top Expenses */}
        <Card className="border-border/40">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-red-600" />
              Top Expenses
            </CardTitle>
            <CardDescription>Your largest spending transactions</CardDescription>
          </CardHeader>
          <CardContent>
            {expenseAnalytics.top_expenses.length > 0 ? (
              <div className="space-y-3">
                {expenseAnalytics.top_expenses.slice(0, 5).map((expense, index) => (
                  <div key={expense._id} className="flex items-center justify-between p-3 rounded-lg border border-border/40 hover:bg-accent/50 transition-colors">
                    <div className="flex-1">
                      <div className="font-medium text-sm">{expense.description || 'Expense'}</div>
                      <div className="text-xs text-muted-foreground">
                        {expense.category} • {new Date(expense.date).toLocaleDateString('en-IN')}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-red-600">₹{expense.amount.toLocaleString('en-IN')}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-8">No expense transactions</p>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
