import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  TrendingDown,
  AlertCircle,
  Calendar,
  PieChart,
  BarChart3,
  Target,
  ShoppingBag,
  Coffee,
  Home,
  Car,
  Utensils
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface SpendingPattern {
  category: string;
  amount: number;
  percentage: number;
  trend: 'up' | 'down' | 'stable';
  trendPercentage: number;
  prediction: number;
  recommendation?: string;
}

interface Expense {
  id: string;
  amount: number;
  category: string;
  date: string;
}

interface SpendingInsightsProps {
  expenses?: Expense[];
  monthlyBudget?: number;
}

const categoryIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  'Food & Dining': Utensils,
  'Shopping': ShoppingBag,
  'Housing': Home,
  'Transportation': Car,
  'Entertainment': Coffee,
  'default': PieChart
};

export function SpendingInsights({ expenses = [], monthlyBudget = 50000 }: SpendingInsightsProps) {
  const [patterns, setPatterns] = useState<SpendingPattern[]>([]);
  const [totalSpending, setTotalSpending] = useState(0);
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('month');

  useEffect(() => {
    analyzeSpendingPatterns();
  }, [expenses, selectedPeriod]);

  const analyzeSpendingPatterns = () => {
    // Mock data for demonstration - in production, this would use real expense data
    const mockPatterns: SpendingPattern[] = [
      {
        category: 'Food & Dining',
        amount: 12500,
        percentage: 35,
        trend: 'up',
        trendPercentage: 15,
        prediction: 14000,
        recommendation: 'Your food expenses increased 15% this month. Consider meal planning to save ₹2,000.'
      },
      {
        category: 'Shopping',
        amount: 8500,
        percentage: 24,
        trend: 'down',
        trendPercentage: -8,
        prediction: 7800,
        recommendation: 'Great job! You reduced shopping expenses by 8%.'
      },
      {
        category: 'Transportation',
        amount: 6000,
        percentage: 17,
        trend: 'stable',
        trendPercentage: 2,
        prediction: 6100,
        recommendation: 'Transportation costs are stable. Consider carpooling to save more.'
      },
      {
        category: 'Entertainment',
        amount: 5500,
        percentage: 15,
        trend: 'up',
        trendPercentage: 25,
        prediction: 6500,
        recommendation: 'Entertainment spending spiked 25%. Set a monthly limit of ₹4,000.'
      },
      {
        category: 'Housing',
        amount: 3500,
        percentage: 9,
        trend: 'stable',
        trendPercentage: 0,
        prediction: 3500,
        recommendation: 'Housing costs are consistent and well-managed.'
      }
    ];

    setPatterns(mockPatterns);
    setTotalSpending(mockPatterns.reduce((sum, p) => sum + p.amount, 0));
  };

  const getBudgetStatus = () => {
    const percentage = (totalSpending / monthlyBudget) * 100;
    if (percentage >= 90) return { status: 'critical', color: 'text-red-500', bgColor: 'bg-red-500' };
    if (percentage >= 75) return { status: 'warning', color: 'text-yellow-500', bgColor: 'bg-yellow-500' };
    return { status: 'good', color: 'text-green-500', bgColor: 'bg-green-500' };
  };

  const budgetStatus = getBudgetStatus();
  const budgetPercentage = (totalSpending / monthlyBudget) * 100;

  return (
    <div className="space-y-6">
      {/* Budget Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Monthly Budget Overview
            </CardTitle>
            <div className="flex gap-2">
              {(['week', 'month', 'year'] as const).map((period) => (
                <Button
                  key={period}
                  variant={selectedPeriod === period ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedPeriod(period)}
                >
                  {period.charAt(0).toUpperCase() + period.slice(1)}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-end justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Spending</p>
                <p className="text-3xl font-bold">
                  ₹{totalSpending.toLocaleString('en-IN')}
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  of ₹{monthlyBudget.toLocaleString('en-IN')} budget
                </p>
              </div>
              <Badge 
                variant="secondary" 
                className={cn("h-fit", budgetStatus.color)}
              >
                {budgetPercentage.toFixed(0)}% Used
              </Badge>
            </div>
            
            <Progress 
              value={budgetPercentage} 
              className="h-3"
            />

            {budgetStatus.status === 'critical' && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg"
              >
                <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
                <div className="flex-1">
                  <p className="font-semibold text-sm text-red-700 dark:text-red-400">
                    Budget Alert
                  </p>
                  <p className="text-xs text-red-600 dark:text-red-500 mt-1">
                    You've exceeded 90% of your monthly budget. Review your expenses to avoid overspending.
                  </p>
                </div>
              </motion.div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Spending Patterns */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Spending Patterns & Predictions
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            AI-powered analysis of your spending habits with actionable recommendations
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {patterns.map((pattern, index) => {
              const Icon = categoryIcons[pattern.category] || categoryIcons.default;
              
              return (
                <motion.div
                  key={pattern.category}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 rounded-lg border bg-card/50 hover:bg-card transition-colors"
                >
                  <div className="flex items-start gap-4">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Icon className="h-5 w-5 text-primary" />
                    </div>
                    
                    <div className="flex-1 min-w-0 space-y-3">
                      {/* Category Header */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <h4 className="font-semibold">{pattern.category}</h4>
                          <Badge variant="outline" className="h-5">
                            {pattern.percentage}% of budget
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold">
                            ₹{pattern.amount.toLocaleString('en-IN')}
                          </span>
                          <div className={cn(
                            "flex items-center gap-1 text-xs font-medium",
                            pattern.trend === 'up' && "text-orange-500",
                            pattern.trend === 'down' && "text-green-500",
                            pattern.trend === 'stable' && "text-gray-500"
                          )}>
                            {pattern.trend === 'up' ? (
                              <TrendingUp className="h-3 w-3" />
                            ) : pattern.trend === 'down' ? (
                              <TrendingDown className="h-3 w-3" />
                            ) : null}
                            {pattern.trendPercentage !== 0 && `${Math.abs(pattern.trendPercentage)}%`}
                          </div>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <Progress 
                        value={pattern.percentage} 
                        className="h-2"
                      />

                      {/* Prediction & Recommendation */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <span>Next month prediction:</span>
                          <span className="font-medium">
                            ₹{pattern.prediction.toLocaleString('en-IN')}
                          </span>
                        </div>
                        
                        {pattern.recommendation && (
                          <div className="flex items-start gap-2 p-2 bg-muted/50 rounded text-xs">
                            <Calendar className="h-3 w-3 text-primary mt-0.5 flex-shrink-0" />
                            <p className="text-muted-foreground">
                              {pattern.recommendation}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Smart Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2">
            <Button variant="outline" className="justify-start h-auto p-4">
              <div className="text-left">
                <p className="font-semibold text-sm">Set Category Budgets</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Create spending limits for each category
                </p>
              </div>
            </Button>
            <Button variant="outline" className="justify-start h-auto p-4">
              <div className="text-left">
                <p className="font-semibold text-sm">View Detailed Report</p>
                <p className="text-xs text-muted-foreground mt-1">
                  See complete spending analysis
                </p>
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
