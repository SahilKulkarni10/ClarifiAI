import { useNavigate } from 'react-router-dom';
import { useRealtimeDashboard } from '@/hooks/useRealtimeDashboard';
import { type Dashboard } from '@/services/finance.service';
import { AppLayout } from '@/components/layouts/AppLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown,
  CreditCard, 
  ArrowUpRight, 
  ArrowDownRight, 
  Wallet, 
  Target, 
  Shield,
  PiggyBank,
  Activity,
  Plus,
  MessageSquare,
  BarChart3,
  RefreshCw
} from 'lucide-react';
import { cn } from '@/lib/utils';

const DEMO_DASHBOARD: Dashboard = {
  total_income: 0,
  total_expenses: 0,
  total_investments: 0,
  total_loans: 0,
  net_worth: 0,
  monthly_summary: { income: 0, expenses: 0, savings: 0 },
  counts: { income: 0, expenses: 0, investments: 0, loans: 0, insurance: 0, goals: 0 }
};

export default function DashboardPage() {
  const navigate = useNavigate();
  const { dashboard, loading, error, lastUpdated, refresh } = useRealtimeDashboard({
    refreshInterval: 30000, // Refresh every 30 seconds
    autoRefresh: true
  });

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto"></div>
            <p className="text-muted-foreground">Loading your financial dashboard...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  // Use dashboard data or fallback to demo data
  const dashboardData = dashboard || DEMO_DASHBOARD;
  const savingsRate = dashboardData.monthly_summary.income > 0 
    ? ((dashboardData.monthly_summary.savings / dashboardData.monthly_summary.income) * 100).toFixed(1) 
    : '0';

  const netWorthTrend = dashboardData.net_worth > 0;

  // Format last updated time
  const formatLastUpdated = (date: Date | null) => {
    if (!date) return 'Never';
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000); // seconds
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleTimeString();
  };

  return (
    <AppLayout 
      title="Financial Dashboard" 
      description="Your complete financial overview at a glance"
    >
      {/* Status Bar with Refresh */}
      <div className="mb-6 flex items-center justify-between p-4 rounded-lg border border-border/40 bg-card/50 backdrop-blur-sm">
        <div className="flex items-center gap-4">
          {error ? (
            <div className="flex items-center gap-2 text-yellow-600 dark:text-yellow-400">
              <Activity className="h-4 w-4" />
              <span className="text-sm">{error} - Showing available data</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
              <Activity className="h-4 w-4" />
              <span className="text-sm">Live data • Last updated: {formatLastUpdated(lastUpdated)}</span>
            </div>
          )}
        </div>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => refresh()}
          className="gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh Now
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <Card className="border-border/40 bg-gradient-to-br from-green-500/10 via-background to-background hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Income</CardTitle>
            <div className="p-2 rounded-lg bg-green-500/20">
              <TrendingUp className="h-4 w-4 text-green-600 dark:text-green-400" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground">₹{dashboardData.total_income.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
              <ArrowUpRight className="h-3 w-3" />
              {dashboardData.counts.income} transactions
            </p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-red-500/10 via-background to-background hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Expenses</CardTitle>
            <div className="p-2 rounded-lg bg-red-500/20">
              <TrendingDown className="h-4 w-4 text-red-600 dark:text-red-400" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground">₹{dashboardData.total_expenses.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
              <ArrowDownRight className="h-3 w-3" />
              {dashboardData.counts.expenses} transactions
            </p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-blue-500/10 via-background to-background hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Investments</CardTitle>
            <div className="p-2 rounded-lg bg-blue-500/20">
              <PiggyBank className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground">₹{dashboardData.total_investments.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              {dashboardData.counts.investments} holdings
            </p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-purple-500/10 via-background to-background hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Net Worth</CardTitle>
            <div className="p-2 rounded-lg bg-purple-500/20">
              <DollarSign className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            </div>
          </CardHeader>
          <CardContent>
            <div className={cn("text-3xl font-bold", netWorthTrend ? "text-green-600 dark:text-green-400" : "text-foreground")}>
              ₹{dashboardData.net_worth.toLocaleString('en-IN')}
            </div>
            <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
              {netWorthTrend ? <ArrowUpRight className="h-3 w-3 text-green-600" /> : <ArrowDownRight className="h-3 w-3" />}
              {netWorthTrend ? 'Positive' : 'Building'} wealth
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Monthly Summary */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <Card className="border-border/40 backdrop-blur-sm hover:shadow-lg transition-all">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              Monthly Income
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold mb-2">₹{dashboardData.monthly_summary.income.toLocaleString('en-IN')}</div>
            <Progress value={100} className="h-2 bg-green-100 dark:bg-green-900/20" />
          </CardContent>
        </Card>

        <Card className="border-border/40 backdrop-blur-sm hover:shadow-lg transition-all">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <CreditCard className="h-5 w-5 text-red-600" />
              Monthly Expenses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold mb-2">₹{dashboardData.monthly_summary.expenses.toLocaleString('en-IN')}</div>
            <Progress 
              value={dashboardData.monthly_summary.income > 0 ? (dashboardData.monthly_summary.expenses / dashboardData.monthly_summary.income) * 100 : 0} 
              className="h-2 bg-red-100 dark:bg-red-900/20" 
            />
          </CardContent>
        </Card>

        <Card className="border-border/40 backdrop-blur-sm hover:shadow-lg transition-all">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <PiggyBank className="h-5 w-5 text-blue-600" />
              Monthly Savings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold mb-2">₹{dashboardData.monthly_summary.savings.toLocaleString('en-IN')}</div>
            <div className="text-sm text-muted-foreground">Savings Rate: {savingsRate}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
        <Card 
          className="border-border/40 hover:border-primary/50 cursor-pointer transition-all group hover:shadow-lg"
          onClick={() => navigate('/investments')}
        >
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2 group-hover:text-primary transition-colors">
              <TrendingUp className="h-5 w-5" />
              Manage Investments
            </CardTitle>
            <CardDescription>View and track your portfolio</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" variant="outline">
              <Plus className="h-4 w-4 mr-2" />
              Add Investment
            </Button>
          </CardContent>
        </Card>

        <Card 
          className="border-border/40 hover:border-primary/50 cursor-pointer transition-all group hover:shadow-lg"
          onClick={() => navigate('/loans')}
        >
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2 group-hover:text-primary transition-colors">
              <Wallet className="h-5 w-5" />
              Track Loans
            </CardTitle>
            <CardDescription>Monitor EMI and outstanding</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-sm">
              <div className="flex justify-between mb-2">
                <span className="text-muted-foreground">Outstanding</span>
                <span className="font-semibold">₹{dashboardData.total_loans.toLocaleString('en-IN')}</span>
              </div>
              <Progress value={60} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card 
          className="border-border/40 hover:border-primary/50 cursor-pointer transition-all group hover:shadow-lg"
          onClick={() => navigate('/goals')}
        >
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2 group-hover:text-primary transition-colors">
              <Target className="h-5 w-5" />
              Financial Goals
            </CardTitle>
            <CardDescription>Set and achieve your targets</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" variant="outline">
              <Plus className="h-4 w-4 mr-2" />
              Create Goal
            </Button>
          </CardContent>
        </Card>

        <Card 
          className="border-border/40 hover:border-primary/50 cursor-pointer transition-all group hover:shadow-lg"
          onClick={() => navigate('/insurance')}
        >
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2 group-hover:text-primary transition-colors">
              <Shield className="h-5 w-5" />
              Insurance Policies
            </CardTitle>
            <CardDescription>Manage your coverage</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-muted-foreground">
              {dashboardData.counts.insurance} active policies
            </div>
          </CardContent>
        </Card>

        <Card 
          className="border-border/40 hover:border-primary/50 cursor-pointer transition-all group hover:shadow-lg"
          onClick={() => navigate('/chat')}
        >
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2 group-hover:text-primary transition-colors">
              <MessageSquare className="h-5 w-5" />
              AI Assistant
            </CardTitle>
            <CardDescription>Get personalized advice</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" variant="default">
              Start Chat
            </Button>
          </CardContent>
        </Card>

        <Card 
          className="border-border/40 hover:border-primary/50 cursor-pointer transition-all group hover:shadow-lg"
          onClick={() => navigate('/analytics')}
        >
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2 group-hover:text-primary transition-colors">
              <BarChart3 className="h-5 w-5" />
              Analytics
            </CardTitle>
            <CardDescription>View detailed reports</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" variant="outline">
              View Reports
            </Button>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
