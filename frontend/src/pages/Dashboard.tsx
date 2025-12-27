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
import { motion } from 'framer-motion';
import CountUp from 'react-countup';
import { useAuth } from '@/hooks/useAuth';
import { useEffect, useState } from 'react';
import { OnboardingModal } from '@/components/OnboardingModal';
import { ExpensePieChart } from '@/components/charts/ExpensePieChart';
import { SavingsTrendChart } from '@/components/charts/SavingsTrendChart';
import { InvestmentPerformanceChart } from '@/components/charts/InvestmentPerformanceChart';
import { AIInsights } from '@/components/AIInsights';

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
  const { user } = useAuth();
  const { dashboard, loading, error, lastUpdated, refresh } = useRealtimeDashboard({
    refreshInterval: 30000, // Refresh every 30 seconds
    autoRefresh: true
  });
  
  // Get greeting based on time of day
  const [greeting, setGreeting] = useState('');
  
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good morning');
    else if (hour < 18) setGreeting('Good afternoon');
    else setGreeting('Good evening');
  }, []);

  const handleOnboardingComplete = (step?: number) => {
    // Navigate to specific page based on step
    if (step === 0) navigate('/income');
    else if (step === 1) navigate('/goals');
    else if (step === 2) navigate('/chat');
  };

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
      {/* Onboarding Modal */}
      <OnboardingModal onComplete={handleOnboardingComplete} />
      {/* Personalized Greeting */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-6"
      >
        <h1 className="text-3xl md:text-4xl font-bold mb-2">
          {greeting}, {user?.name?.split(' ')[0] || 'there'} 👋
        </h1>
        <p className="text-muted-foreground">
          Here's your financial overview for today
        </p>
      </motion.div>

      {/* Status Bar with Refresh */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="mb-6 flex items-center justify-between p-4 rounded-lg border border-border/40 bg-card/50 backdrop-blur-sm"
      >
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
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8"
      >
        <motion.div whileHover={{ scale: 1.02 }} transition={{ type: "spring", stiffness: 300 }}>
          <Card className="border-border/40 bg-gradient-to-br from-green-500/10 via-background to-background hover:shadow-lg transition-all h-full">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Income</CardTitle>
              <div className="p-2 rounded-lg bg-green-500/20">
                <TrendingUp className="h-4 w-4 text-green-600 dark:text-green-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">
                ₹<CountUp end={dashboardData.total_income} duration={2} separator="," />
              </div>
              <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                <ArrowUpRight className="h-3 w-3" />
                {dashboardData.counts.income} transactions
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} transition={{ type: "spring", stiffness: 300 }}>
          <Card className="border-border/40 bg-gradient-to-br from-red-500/10 via-background to-background hover:shadow-lg transition-all h-full">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Expenses</CardTitle>
              <div className="p-2 rounded-lg bg-red-500/20">
                <TrendingDown className="h-4 w-4 text-red-600 dark:text-red-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">
                ₹<CountUp end={dashboardData.total_expenses} duration={2} separator="," />
              </div>
              <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                <ArrowDownRight className="h-3 w-3" />
                {dashboardData.counts.expenses} transactions
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} transition={{ type: "spring", stiffness: 300 }}>
          <Card className="border-border/40 bg-gradient-to-br from-blue-500/10 via-background to-background hover:shadow-lg transition-all h-full">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Investments</CardTitle>
              <div className="p-2 rounded-lg bg-blue-500/20">
                <PiggyBank className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">
                ₹<CountUp end={dashboardData.total_investments} duration={2} separator="," />
              </div>
              <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                <TrendingUp className="h-3 w-3" />
                {dashboardData.counts.investments} holdings
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} transition={{ type: "spring", stiffness: 300 }}>
          <Card className="border-border/40 bg-gradient-to-br from-purple-500/10 via-background to-background hover:shadow-lg transition-all h-full">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Net Worth</CardTitle>
              <div className="p-2 rounded-lg bg-purple-500/20">
                <DollarSign className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className={cn("text-3xl font-bold", netWorthTrend ? "text-green-600 dark:text-green-400" : "text-foreground")}>
                ₹<CountUp end={dashboardData.net_worth} duration={2} separator="," />
              </div>
              <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                {netWorthTrend ? <ArrowUpRight className="h-3 w-3 text-green-600" /> : <ArrowDownRight className="h-3 w-3" />}
                {netWorthTrend ? 'Positive' : 'Building'} wealth
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

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

      {/* AI Insights - Compact View */}
      <div className="mb-8">
        <AIInsights dashboardData={dashboardData} compact={true} />
      </div>

      {/* Interactive Charts */}
      <div className="grid gap-6 lg:grid-cols-2 mb-8">
        <ExpensePieChart 
          data={[
            { category: 'housing', amount: dashboardData.monthly_summary.expenses * 0.3, color: '#3b82f6' },
            { category: 'food', amount: dashboardData.monthly_summary.expenses * 0.25, color: '#f59e0b' },
            { category: 'transport', amount: dashboardData.monthly_summary.expenses * 0.15, color: '#06b6d4' },
            { category: 'shopping', amount: dashboardData.monthly_summary.expenses * 0.15, color: '#ec4899' },
            { category: 'utilities', amount: dashboardData.monthly_summary.expenses * 0.1, color: '#eab308' },
            { category: 'other', amount: dashboardData.monthly_summary.expenses * 0.05, color: '#6b7280' },
          ]}
        />
        
        <SavingsTrendChart 
          data={[
            { month: 'Jan', income: 50000, expenses: 35000, savings: 15000 },
            { month: 'Feb', income: 52000, expenses: 36000, savings: 16000 },
            { month: 'Mar', income: 51000, expenses: 34000, savings: 17000 },
            { month: 'Apr', income: 53000, expenses: 37000, savings: 16000 },
            { month: 'May', income: 55000, expenses: 38000, savings: 17000 },
            { month: 'Jun', income: dashboardData.monthly_summary.income, expenses: dashboardData.monthly_summary.expenses, savings: dashboardData.monthly_summary.savings },
          ]}
        />
      </div>

      <div className="mb-8">
        <InvestmentPerformanceChart 
          data={[
            { name: 'Mutual Funds', invested: 100000, currentValue: 115000, returns: 15000 },
            { name: 'Stocks', invested: 50000, currentValue: 58000, returns: 8000 },
            { name: 'Gold', invested: 30000, currentValue: 32000, returns: 2000 },
            { name: 'FD', invested: 200000, currentValue: 212000, returns: 12000 },
          ]}
        />
      </div>

      {/* AI Insights Widget */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="mb-8"
      >
        <AIInsights dashboardData={dashboardData} compact={true} />
      </motion.div>

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
