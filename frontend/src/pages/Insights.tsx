import { AppLayout } from '@/components/layouts/AppLayout';
import { AIInsights } from '@/components/AIInsights';
import { SpendingInsights } from '@/components/SpendingInsights';
import { GoalRecommendations } from '@/components/GoalRecommendations';
import { useRealtimeDashboard } from '@/hooks/useRealtimeDashboard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card } from '@/components/ui/card';
import { Brain, TrendingDown, Target, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

export default function InsightsPage() {
  const { dashboard, loading } = useRealtimeDashboard({
    refreshInterval: 60000,
    autoRefresh: true
  });

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto"></div>
            <p className="text-muted-foreground">Loading insights...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout
      title="Financial Insights"
      description="AI-powered recommendations and analysis"
    >
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/20 to-blue-500/20">
            <Sparkles className="h-8 w-8 text-purple-500" />
          </div>
          <div>
            <h1 className="text-3xl md:text-4xl font-bold">Financial Insights</h1>
            <p className="text-muted-foreground mt-1">
              AI-powered analysis to help you make smarter financial decisions
            </p>
          </div>
        </div>
      </motion.div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:w-auto">
          <TabsTrigger value="overview" className="gap-2">
            <Brain className="h-4 w-4" />
            <span className="hidden sm:inline">Overview</span>
          </TabsTrigger>
          <TabsTrigger value="ai-insights" className="gap-2">
            <Sparkles className="h-4 w-4" />
            <span className="hidden sm:inline">AI Insights</span>
          </TabsTrigger>
          <TabsTrigger value="spending" className="gap-2">
            <TrendingDown className="h-4 w-4" />
            <span className="hidden sm:inline">Spending</span>
          </TabsTrigger>
          <TabsTrigger value="goals" className="gap-2">
            <Target className="h-4 w-4" />
            <span className="hidden sm:inline">Goals</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid gap-6 md:grid-cols-3"
          >
            <Card className="p-6 bg-gradient-to-br from-purple-500/10 to-blue-500/10 border-purple-500/20">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-purple-500/20">
                  <Brain className="h-6 w-6 text-purple-500" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">AI Recommendations</p>
                  <p className="text-2xl font-bold">6 Active</p>
                </div>
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-orange-500/10 to-red-500/10 border-orange-500/20">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-orange-500/20">
                  <TrendingDown className="h-6 w-6 text-orange-500" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Spending Alerts</p>
                  <p className="text-2xl font-bold">3 Areas</p>
                </div>
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/20">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-green-500/20">
                  <Target className="h-6 w-6 text-green-500" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Goal Progress</p>
                  <p className="text-2xl font-bold">On Track</p>
                </div>
              </div>
            </Card>
          </motion.div>

          <AIInsights dashboardData={dashboard} compact={false} />
        </TabsContent>

        <TabsContent value="ai-insights" className="space-y-6">
          <AIInsights dashboardData={dashboard} compact={false} />
        </TabsContent>

        <TabsContent value="spending" className="space-y-6">
          <SpendingInsights 
            expenses={[]} 
            monthlyBudget={dashboard?.monthly_summary.income || 50000}
          />
        </TabsContent>

        <TabsContent value="goals" className="space-y-6">
          <GoalRecommendations 
            monthlyIncome={dashboard?.monthly_summary.income || 75000}
            currentSavings={dashboard?.monthly_summary.savings || 15000}
          />
        </TabsContent>
      </Tabs>
    </AppLayout>
  );
}
