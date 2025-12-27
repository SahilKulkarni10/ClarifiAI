import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Target,
  TrendingUp,
  Calendar,
  DollarSign,
  Zap,
  CheckCircle2,
  Clock,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface Goal {
  id: string;
  name: string;
  targetAmount: number;
  currentAmount: number;
  deadline: string;
  category: 'emergency' | 'retirement' | 'vacation' | 'education' | 'home' | 'other';
  priority: 'high' | 'medium' | 'low';
}

interface GoalRecommendation {
  goalId: string;
  type: 'contribution' | 'timeline' | 'strategy' | 'achievement';
  title: string;
  description: string;
  action?: {
    label: string;
    amount?: number;
  };
  impact: string;
  urgency: 'high' | 'medium' | 'low';
}

interface GoalRecommendationsProps {
  goals?: Goal[];
  monthlyIncome?: number;
  currentSavings?: number;
}

const mockGoals: Goal[] = [
  {
    id: '1',
    name: 'Emergency Fund',
    targetAmount: 300000,
    currentAmount: 180000,
    deadline: '2024-12-31',
    category: 'emergency',
    priority: 'high'
  },
  {
    id: '2',
    name: 'Dream Vacation',
    targetAmount: 150000,
    currentAmount: 45000,
    deadline: '2025-06-30',
    category: 'vacation',
    priority: 'medium'
  },
  {
    id: '3',
    name: 'Home Down Payment',
    targetAmount: 1000000,
    currentAmount: 250000,
    deadline: '2026-12-31',
    category: 'home',
    priority: 'high'
  }
];

export function GoalRecommendations({ 
  goals = mockGoals, 
  monthlyIncome = 75000,
  currentSavings = 200000 
}: GoalRecommendationsProps) {
  const [recommendations] = useState<GoalRecommendation[]>(() => 
    generateRecommendations(goals, monthlyIncome)
  );

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-purple-500/5">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-2xl">
                <Sparkles className="h-6 w-6 text-primary" />
                Goal-Based Recommendations
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-2">
                AI-powered strategies to help you achieve your financial goals faster
              </p>
            </div>
            <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
              {goals.length} Active Goals
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Active Goals Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {goals.map((goal, index) => {
          const progress = (goal.currentAmount / goal.targetAmount) * 100;
          const daysLeft = Math.ceil((new Date(goal.deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
          const monthsLeft = Math.ceil(daysLeft / 30);
          const requiredMonthly = Math.ceil((goal.targetAmount - goal.currentAmount) / monthsLeft);
          
          return (
            <motion.div
              key={goal.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="h-full hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="space-y-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-lg">{goal.name}</h3>
                        <Badge 
                          variant="outline" 
                          className={cn(
                            "mt-2",
                            goal.priority === 'high' && "border-red-500/50 text-red-600",
                            goal.priority === 'medium' && "border-yellow-500/50 text-yellow-600",
                            goal.priority === 'low' && "border-green-500/50 text-green-600"
                          )}
                        >
                          {goal.priority} priority
                        </Badge>
                      </div>
                      <Target className="h-8 w-8 text-primary/60" />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Progress</span>
                        <span className="font-semibold">{progress.toFixed(0)}%</span>
                      </div>
                      <Progress value={progress} className="h-2" />
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>₹{goal.currentAmount.toLocaleString('en-IN')}</span>
                        <span>₹{goal.targetAmount.toLocaleString('en-IN')}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 pt-2 border-t text-xs">
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        <span>{monthsLeft} months left</span>
                      </div>
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <TrendingUp className="h-3 w-3" />
                        <span>₹{requiredMonthly.toLocaleString('en-IN')}/mo</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-500" />
            Smart Recommendations
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Personalized strategies based on your income, expenses, and goals
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recommendations.map((rec, index) => (
              <motion.div
                key={`${rec.goalId}-${index}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={cn(
                  "p-4 rounded-lg border-l-4",
                  rec.urgency === 'high' && "border-l-red-500 bg-red-500/5",
                  rec.urgency === 'medium' && "border-l-yellow-500 bg-yellow-500/5",
                  rec.urgency === 'low' && "border-l-green-500 bg-green-500/5"
                )}
              >
                <div className="flex items-start gap-4">
                  <div className={cn(
                    "p-2 rounded-lg",
                    rec.type === 'achievement' && "bg-green-500/10",
                    rec.type === 'contribution' && "bg-blue-500/10",
                    rec.type === 'timeline' && "bg-purple-500/10",
                    rec.type === 'strategy' && "bg-orange-500/10"
                  )}>
                    {rec.type === 'achievement' && <CheckCircle2 className="h-5 w-5 text-green-500" />}
                    {rec.type === 'contribution' && <DollarSign className="h-5 w-5 text-blue-500" />}
                    {rec.type === 'timeline' && <Calendar className="h-5 w-5 text-purple-500" />}
                    {rec.type === 'strategy' && <TrendingUp className="h-5 w-5 text-orange-500" />}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <h4 className="font-semibold">{rec.title}</h4>
                      <Badge 
                        variant="secondary"
                        className={cn(
                          "text-xs",
                          rec.urgency === 'high' && "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
                          rec.urgency === 'medium' && "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
                          rec.urgency === 'low' && "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                        )}
                      >
                        {rec.urgency} priority
                      </Badge>
                    </div>
                    
                    <p className="text-sm text-muted-foreground mb-3">
                      {rec.description}
                    </p>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Sparkles className="h-3 w-3" />
                        <span>Impact: {rec.impact}</span>
                      </div>
                      
                      {rec.action && (
                        <Button size="sm" variant="outline" className="h-8">
                          {rec.action.label}
                          {rec.action.amount && (
                            <span className="ml-1 font-semibold">
                              ₹{rec.action.amount.toLocaleString('en-IN')}
                            </span>
                          )}
                          <ArrowRight className="ml-2 h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function generateRecommendations(goals: Goal[], monthlyIncome: number): GoalRecommendation[] {
  const recs: GoalRecommendation[] = [];

  goals.forEach(goal => {
    const progress = (goal.currentAmount / goal.targetAmount) * 100;
    const daysLeft = Math.ceil((new Date(goal.deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    const monthsLeft = Math.ceil(daysLeft / 30);
    const requiredMonthly = Math.ceil((goal.targetAmount - goal.currentAmount) / monthsLeft);
    const affordablePercentage = (requiredMonthly / monthlyIncome) * 100;

    // Achievement near completion
    if (progress >= 80) {
      recs.push({
        goalId: goal.id,
        type: 'achievement',
        title: `${goal.name} - Almost There!`,
        description: `You're ${progress.toFixed(0)}% complete! Just ₹${(goal.targetAmount - goal.currentAmount).toLocaleString('en-IN')} more to reach your goal.`,
        impact: 'Achieve goal within 2 months',
        urgency: 'low',
        action: {
          label: 'Add',
          amount: Math.ceil((goal.targetAmount - goal.currentAmount) / 2)
        }
      });
    }

    // Contribution recommendation
    if (affordablePercentage <= 20 && progress < 80) {
      recs.push({
        goalId: goal.id,
        type: 'contribution',
        title: `Increase ${goal.name} Contributions`,
        description: `Contributing ₹${requiredMonthly.toLocaleString('en-IN')}/month (${affordablePercentage.toFixed(0)}% of income) will help you reach this goal on time.`,
        impact: 'Reach goal on schedule',
        urgency: goal.priority === 'high' ? 'high' : 'medium',
        action: {
          label: 'Contribute',
          amount: requiredMonthly
        }
      });
    }

    // Timeline warning
    if (monthsLeft <= 6 && progress < 70) {
      recs.push({
        goalId: goal.id,
        type: 'timeline',
        title: `${goal.name} - Timeline Risk`,
        description: `Only ${monthsLeft} months left. Consider increasing contributions to ₹${Math.ceil(requiredMonthly * 1.2).toLocaleString('en-IN')}/month or extending deadline.`,
        impact: 'Avoid missing deadline',
        urgency: 'high',
        action: {
          label: 'Adjust Plan'
        }
      });
    }

    // Strategy recommendation
    if (progress < 30 && monthsLeft > 12) {
      recs.push({
        goalId: goal.id,
        type: 'strategy',
        title: `Optimize ${goal.name} Strategy`,
        description: `Consider investing in low-risk mutual funds to potentially grow your savings faster with an estimated 8-10% annual return.`,
        impact: 'Reach goal 3-6 months earlier',
        urgency: 'medium',
        action: {
          label: 'Explore Options'
        }
      });
    }
  });

  // Sort by urgency
  const urgencyOrder = { high: 0, medium: 1, low: 2 };
  recs.sort((a, b) => urgencyOrder[a.urgency] - urgencyOrder[b.urgency]);

  return recs;
}
