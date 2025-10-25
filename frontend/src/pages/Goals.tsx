import { useEffect, useState } from 'react';
import { AppLayout } from '@/components/layouts/AppLayout';
import { financeService, type Goal } from '@/services/finance.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { 
  Target, 
  Plus, 
  Trash2, 
  Edit,
  Home,
  GraduationCap,
  Plane,
  Car,
  Heart,
  Briefcase,
  TrendingUp,
  Calendar,
  DollarSign,
  Activity
} from 'lucide-react';
import { cn } from '@/lib/utils';

const GOAL_TYPES = [
  { value: 'home', label: 'Buy a Home', icon: Home, color: 'bg-blue-500' },
  { value: 'education', label: 'Education', icon: GraduationCap, color: 'bg-purple-500' },
  { value: 'vacation', label: 'Vacation', icon: Plane, color: 'bg-cyan-500' },
  { value: 'car', label: 'Buy a Car', icon: Car, color: 'bg-yellow-500' },
  { value: 'wedding', label: 'Wedding', icon: Heart, color: 'bg-pink-500' },
  { value: 'retirement', label: 'Retirement', icon: Briefcase, color: 'bg-green-500' },
  { value: 'emergency', label: 'Emergency Fund', icon: Activity, color: 'bg-red-500' },
  { value: 'other', label: 'Other', icon: Target, color: 'bg-gray-500' }
];

const PRIORITY_OPTIONS = [
  { value: 'high', label: 'High', color: 'text-red-600' },
  { value: 'medium', label: 'Medium', color: 'text-yellow-600' },
  { value: 'low', label: 'Low', color: 'text-green-600' }
];

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    target_amount: '',
    current_amount: '',
    target_date: '',
    priority: 'medium'
  });

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      setLoading(true);
      const data = await financeService.getGoals();
      setGoals(data);
    } catch (error) {
      console.error('Error fetching goals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financeService.createGoal({
        ...formData,
        target_amount: parseFloat(formData.target_amount),
        current_amount: parseFloat(formData.current_amount || '0'),
      } as Goal);
      setShowAddForm(false);
      setFormData({
        name: '',
        target_amount: '',
        current_amount: '',
        target_date: '',
        priority: 'medium'
      });
      fetchGoals();
    } catch (error) {
      console.error('Error adding goal:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this goal?')) {
      try {
        await financeService.deleteGoal(id);
        fetchGoals();
      } catch (error) {
        console.error('Error deleting goal:', error);
      }
    }
  };

  const totalTargetAmount = goals.reduce((sum, goal) => sum + goal.target_amount, 0);
  const totalCurrentAmount = goals.reduce((sum, goal) => sum + goal.current_amount, 0);
  const overallProgress = totalTargetAmount > 0 ? (totalCurrentAmount / totalTargetAmount) * 100 : 0;
  const achievedGoals = goals.filter(g => g.current_amount >= g.target_amount).length;

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto"></div>
            <p className="text-muted-foreground">Loading goals...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout 
      title="Financial Goals" 
      description="Set, track, and achieve your financial objectives"
    >
      {/* Summary Cards */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <Card className="border-border/40 bg-gradient-to-br from-blue-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Target className="h-4 w-4" />
              Active Goals
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{goals.length}</div>
            <p className="text-xs text-muted-foreground mt-2">{achievedGoals} achieved</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-purple-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Target Amount
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">₹{totalTargetAmount.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">Total goals</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-green-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Saved So Far
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600 dark:text-green-400">₹{totalCurrentAmount.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">Towards goals</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-orange-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Overall Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{overallProgress.toFixed(1)}%</div>
            <Progress value={overallProgress} className="mt-2 h-2" />
          </CardContent>
        </Card>
      </div>

      {/* Add Goal Button */}
      <div className="mb-6">
        <Button onClick={() => setShowAddForm(!showAddForm)} className="gap-2">
          <Plus className="h-4 w-4" />
          Add Financial Goal
        </Button>
      </div>

      {/* Add Goal Form */}
      {showAddForm && (
        <Card className="mb-8 border-primary/20 shadow-lg">
          <CardHeader>
            <CardTitle>Add New Financial Goal</CardTitle>
            <CardDescription>Set a target and track your progress</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="name">Goal Name</Label>
                  <Input
                    id="name"
                    placeholder="e.g., Buy a House, Emergency Fund"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="target_amount">Target Amount</Label>
                  <Input
                    id="target_amount"
                    type="number"
                    placeholder="500000"
                    value={formData.target_amount}
                    onChange={(e) => setFormData({...formData, target_amount: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="current_amount">Current Amount (Optional)</Label>
                  <Input
                    id="current_amount"
                    type="number"
                    placeholder="50000"
                    value={formData.current_amount}
                    onChange={(e) => setFormData({...formData, current_amount: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="target_date">Target Date</Label>
                  <Input
                    id="target_date"
                    type="date"
                    value={formData.target_date}
                    onChange={(e) => setFormData({...formData, target_date: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="priority">Priority</Label>
                  <select
                    id="priority"
                    title="Select goal priority"
                    aria-label="Goal Priority"
                    className="w-full px-3 py-2 rounded-md border border-input bg-background"
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: e.target.value})}
                    required
                  >
                    {PRIORITY_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex gap-2">
                <Button type="submit">Save Goal</Button>
                <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Goals List */}
      <div className="space-y-4">
        <h3 className="text-2xl font-bold">Your Goals</h3>
        {goals.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Target className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-2">No goals yet</p>
              <p className="text-sm text-muted-foreground mb-4">Start planning your financial future</p>
              <Button onClick={() => setShowAddForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Goal
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {goals.map((goal) => {
              const progress = (goal.current_amount / goal.target_amount) * 100;
              const isAchieved = goal.current_amount >= goal.target_amount;
              const remaining = goal.target_amount - goal.current_amount;
              const targetDate = new Date(goal.target_date);
              const now = new Date();
              const daysRemaining = Math.ceil((targetDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
              const priority = PRIORITY_OPTIONS.find(p => p.value === goal.priority) || PRIORITY_OPTIONS[1];

              // Find matching goal type icon
              const goalType = GOAL_TYPES.find(t => 
                goal.name.toLowerCase().includes(t.label.toLowerCase().split(' ')[0])
              ) || GOAL_TYPES[GOAL_TYPES.length - 1];
              const Icon = goalType.icon;

              return (
                <Card key={goal.id} className={cn(
                  "border-border/40 hover:shadow-lg transition-all",
                  isAchieved && "border-green-500/50 bg-green-500/5"
                )}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className={cn("p-2 rounded-lg", goalType.color, "bg-opacity-20")}>
                          <Icon className="h-5 w-5" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-lg">{goal.name}</h4>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={cn("text-xs font-semibold px-2 py-1 rounded-full", priority.color, "bg-opacity-10")}>
                              {priority.label} Priority
                            </span>
                            {isAchieved && (
                              <span className="text-xs font-semibold px-2 py-1 rounded-full bg-green-500/20 text-green-600">
                                Achieved!
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="ghost" size="icon" className="hover:bg-primary/10">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="hover:bg-destructive/10 hover:text-destructive"
                          onClick={() => goal.id && handleDelete(goal.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-muted-foreground">Target</p>
                          <p className="font-semibold">₹{goal.target_amount.toLocaleString('en-IN')}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Saved</p>
                          <p className="font-semibold text-green-600">₹{goal.current_amount.toLocaleString('en-IN')}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Remaining</p>
                          <p className="font-semibold">₹{remaining.toLocaleString('en-IN')}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Target Date</p>
                          <p className="font-semibold">{targetDate.toLocaleDateString()}</p>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Progress</span>
                          <span className={cn(
                            "font-semibold",
                            isAchieved ? "text-green-600" : ""
                          )}>
                            {progress.toFixed(1)}%
                          </span>
                        </div>
                        <Progress value={Math.min(progress, 100)} className="h-3" />
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>{daysRemaining > 0 ? `${daysRemaining} days remaining` : 'Past target date'}</span>
                          {!isAchieved && remaining > 0 && daysRemaining > 0 && (
                            <span>~₹{Math.ceil(remaining / daysRemaining).toLocaleString('en-IN')}/day needed</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
