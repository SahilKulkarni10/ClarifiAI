import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Sparkles, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle,
  Target,
  Lightbulb,
  ArrowRight,
  RefreshCw,
  Brain
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { useNavigate } from 'react-router-dom';

interface Insight {
  id: string;
  type: 'warning' | 'opportunity' | 'achievement' | 'recommendation' | 'tip';
  title: string;
  description: string;
  action?: {
    label: string;
    route?: string;
    onClick?: () => void;
  };
  priority: 'high' | 'medium' | 'low';
  category: 'spending' | 'saving' | 'investing' | 'goals' | 'general';
}

interface DashboardData {
  total_income: number;
  total_expenses: number;
  total_investments: number;
  total_loans: number;
  net_worth: number;
  monthly_summary: { income: number; expenses: number; savings: number };
  counts: { income: number; expenses: number; investments: number; loans: number; insurance: number; goals: number };
}

interface AIInsightsProps {
  dashboardData?: DashboardData;
  compact?: boolean;
}

export function AIInsights({ dashboardData, compact = false }: AIInsightsProps) {
  const navigate = useNavigate();
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    generateInsights();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dashboardData]);

  const generateInsights = () => {
    setLoading(true);
    const generatedInsights: Insight[] = [];

    if (!dashboardData) {
      setLoading(false);
      return;
    }

    // Spending Analysis
    if (dashboardData.monthly_summary.expenses > dashboardData.monthly_summary.income * 0.8) {
      generatedInsights.push({
        id: 'high-spending',
        type: 'warning',
        title: 'High Spending Alert',
        description: `You're spending ${((dashboardData.monthly_summary.expenses / dashboardData.monthly_summary.income) * 100).toFixed(0)}% of your income. Consider reducing discretionary expenses.`,
        action: {
          label: 'View Expenses',
          route: '/expenses'
        },
        priority: 'high',
        category: 'spending'
      });
    }

    // Savings Opportunity
    if (dashboardData.monthly_summary.savings < dashboardData.monthly_summary.income * 0.2) {
      generatedInsights.push({
        id: 'low-savings',
        type: 'opportunity',
        title: 'Increase Your Savings',
        description: 'You could save more! Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings.',
        action: {
          label: 'Set Savings Goal',
          route: '/goals'
        },
        priority: 'high',
        category: 'saving'
      });
    }

    // Investment Recommendation
    if (dashboardData.total_investments < dashboardData.net_worth * 0.3) {
      generatedInsights.push({
        id: 'low-investment',
        type: 'recommendation',
        title: 'Consider Investing More',
        description: 'Your investment portfolio is less than 30% of your net worth. Diversifying into investments could help grow your wealth.',
        action: {
          label: 'Explore Investments',
          route: '/investments'
        },
        priority: 'medium',
        category: 'investing'
      });
    }

    // Positive Insights
    if (dashboardData.monthly_summary.savings > 0) {
      const savingsRate = ((dashboardData.monthly_summary.savings / dashboardData.monthly_summary.income) * 100).toFixed(0);
      generatedInsights.push({
        id: 'good-savings',
        type: 'achievement',
        title: 'Great Savings Rate!',
        description: `You're saving ${savingsRate}% of your income. Keep up the excellent work!`,
        priority: 'low',
        category: 'saving'
      });
    }

    // Goal Reminder
    if (dashboardData.counts.goals > 0) {
      generatedInsights.push({
        id: 'goals-active',
        type: 'tip',
        title: 'Stay on Track',
        description: `You have ${dashboardData.counts.goals} active goal${dashboardData.counts.goals > 1 ? 's' : ''}. Regular contributions make a big difference!`,
        action: {
          label: 'View Goals',
          route: '/goals'
        },
        priority: 'medium',
        category: 'goals'
      });
    }

    // Smart Tips
    generatedInsights.push({
      id: 'smart-tip-1',
      type: 'tip',
      title: 'Track Daily Expenses',
      description: 'Small daily expenses add up! Track them to identify patterns and save more.',
      action: {
        label: 'Add Expense',
        route: '/expenses'
      },
      priority: 'low',
      category: 'general'
    });

    // Sort by priority
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    generatedInsights.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

    setInsights(generatedInsights);
    setLoading(false);
  };

  const getIconForType = (type: Insight['type']) => {
    switch (type) {
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case 'opportunity':
        return <TrendingUp className="h-5 w-5 text-blue-500" />;
      case 'achievement':
        return <Sparkles className="h-5 w-5 text-green-500" />;
      case 'recommendation':
        return <Lightbulb className="h-5 w-5 text-purple-500" />;
      case 'tip':
        return <Brain className="h-5 w-5 text-cyan-500" />;
    }
  };

  const getBadgeColorForPriority = (priority: Insight['priority']) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'low':
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400';
    }
  };

  const categories = [
    { value: 'all', label: 'All Insights' },
    { value: 'spending', label: 'Spending' },
    { value: 'saving', label: 'Saving' },
    { value: 'investing', label: 'Investing' },
    { value: 'goals', label: 'Goals' }
  ];

  const filteredInsights = selectedCategory === 'all' 
    ? insights 
    : insights.filter(i => i.category === selectedCategory);

  if (compact) {
    return (
      <Card className="border-purple-500/20 bg-gradient-to-br from-purple-500/5 to-blue-500/5 backdrop-blur-sm">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Brain className="h-5 w-5 text-purple-500" />
              AI Insights
            </CardTitle>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={generateInsights}
              disabled={loading}
            >
              <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-2">
          <AnimatePresence mode="popLayout">
            {filteredInsights.slice(0, 3).map((insight, index) => (
              <motion.div
                key={insight.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
                className="p-3 rounded-lg bg-card/50 border border-border/50 hover:border-purple-500/30 transition-colors"
              >
                <div className="flex gap-3">
                  <div className="mt-0.5">{getIconForType(insight.type)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h4 className="font-semibold text-sm">{insight.title}</h4>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {insight.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {filteredInsights.length > 3 && (
            <Button 
              variant="ghost" 
              size="sm" 
              className="w-full text-purple-500 hover:text-purple-600"
              onClick={() => navigate('/insights')}
            >
              View All Insights
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-6 w-6 text-purple-500" />
              AI-Powered Insights
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Personalized recommendations based on your financial behavior
            </p>
          </div>
          <Button 
            variant="outline" 
            size="sm"
            onClick={generateInsights}
            disabled={loading}
          >
            <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin")} />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Category Filter */}
        <div className="flex flex-wrap gap-2 mb-6">
          {categories.map((cat) => (
            <Button
              key={cat.value}
              variant={selectedCategory === cat.value ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(cat.value)}
            >
              {cat.label}
            </Button>
          ))}
        </div>

        {/* Insights Grid */}
        <div className="grid gap-4 md:grid-cols-2">
          <AnimatePresence mode="popLayout">
            {filteredInsights.map((insight, index) => (
              <motion.div
                key={insight.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className={cn(
                  "h-full hover:shadow-lg transition-shadow",
                  insight.priority === 'high' && "border-orange-500/30"
                )}>
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <div className="mt-1">{getIconForType(insight.type)}</div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <h4 className="font-semibold">{insight.title}</h4>
                          <Badge 
                            variant="secondary" 
                            className={getBadgeColorForPriority(insight.priority)}
                          >
                            {insight.priority}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">
                          {insight.description}
                        </p>
                        {insight.action && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 px-3 text-xs"
                            onClick={() => insight.action?.route && navigate(insight.action.route)}
                          >
                            {insight.action.label}
                            <ArrowRight className="ml-1 h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {filteredInsights.length === 0 && (
          <div className="text-center py-12">
            <Brain className="h-12 w-12 text-muted-foreground/50 mx-auto mb-4" />
            <p className="text-muted-foreground">No insights available for this category</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
