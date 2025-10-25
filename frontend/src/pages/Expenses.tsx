import { useEffect, useState } from 'react';
import { AppLayout } from '@/components/layouts/AppLayout';
import { financeService, type Expense } from '@/services/finance.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { 
  CreditCard, 
  Plus, 
  Trash2, 
  Edit,
  ShoppingBag,
  Home,
  Car,
  Coffee,
  Activity,
  TrendingDown,
  Calendar
} from 'lucide-react';
import { cn } from '@/lib/utils';

const EXPENSE_CATEGORIES = [
  { value: 'housing', label: 'Housing', icon: Home, color: 'bg-blue-500' },
  { value: 'food', label: 'Food & Dining', icon: Coffee, color: 'bg-green-500' },
  { value: 'transportation', label: 'Transportation', icon: Car, color: 'bg-yellow-500' },
  { value: 'shopping', label: 'Shopping', icon: ShoppingBag, color: 'bg-pink-500' },
  { value: 'entertainment', label: 'Entertainment', icon: Activity, color: 'bg-purple-500' },
  { value: 'utilities', label: 'Utilities', icon: Home, color: 'bg-orange-500' },
  { value: 'healthcare', label: 'Healthcare', icon: Activity, color: 'bg-red-500' },
  { value: 'other', label: 'Other', icon: CreditCard, color: 'bg-gray-500' }
];

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    category: '',
    amount: '',
    date: new Date().toISOString().split('T')[0],
    description: ''
  });

  useEffect(() => {
    fetchExpenses();
  }, []);

  const fetchExpenses = async () => {
    try {
      setLoading(true);
      const data = await financeService.getExpenses();
      setExpenses(data);
    } catch (error) {
      console.error('Error fetching expenses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financeService.createExpense({
        ...formData,
        amount: parseFloat(formData.amount),
      } as Expense);
      setShowAddForm(false);
      setFormData({
        category: '',
        amount: '',
        date: new Date().toISOString().split('T')[0],
        description: ''
      });
      fetchExpenses();
    } catch (error) {
      console.error('Error adding expense:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this expense?')) {
      try {
        await financeService.deleteExpense(id);
        fetchExpenses();
      } catch (error) {
        console.error('Error deleting expense:', error);
      }
    }
  };

  // Calculate statistics
  const totalExpenses = expenses.reduce((sum, exp) => sum + exp.amount, 0);
  const categoryTotals = expenses.reduce((acc, exp) => {
    acc[exp.category] = (acc[exp.category] || 0) + exp.amount;
    return acc;
  }, {} as Record<string, number>);

  const categoryBreakdown = EXPENSE_CATEGORIES.map(cat => ({
    ...cat,
    amount: categoryTotals[cat.value] || 0,
    percentage: totalExpenses > 0 ? ((categoryTotals[cat.value] || 0) / totalExpenses) * 100 : 0
  })).filter(cat => cat.amount > 0);

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto"></div>
            <p className="text-muted-foreground">Loading expenses...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout 
      title="Expense Tracking" 
      description="Monitor your spending and stay within budget"
    >
      {/* Summary Cards */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <Card className="border-border/40 bg-gradient-to-br from-red-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <CreditCard className="h-4 w-4" />
              Total Expenses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600 dark:text-red-400">₹{totalExpenses.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">{expenses.length} transactions</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-orange-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              This Month
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">₹{totalExpenses.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">Current month spending</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-purple-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingDown className="h-4 w-4" />
              Top Category
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {categoryBreakdown[0]?.label || 'None'}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {categoryBreakdown[0] ? `₹${categoryBreakdown[0].amount.toLocaleString('en-IN')}` : 'No expenses'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Category Breakdown */}
      {categoryBreakdown.length > 0 && (
        <Card className="mb-8 border-border/40">
          <CardHeader>
            <CardTitle className="text-xl">Spending by Category</CardTitle>
            <CardDescription>Breakdown of your expenses</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {categoryBreakdown.map((category, index) => {
                const Icon = category.icon;
                return (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <Icon className="h-4 w-4" />
                        <span className="font-medium">{category.label}</span>
                      </div>
                      <span className="text-muted-foreground">
                        ₹{category.amount.toLocaleString('en-IN')} ({category.percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="relative h-3 bg-muted rounded-full overflow-hidden">
                      <div 
                        className={cn(category.color, "h-full transition-all")}
                        style={{ width: `${category.percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Add Expense Button */}
      <div className="mb-6">
        <Button onClick={() => setShowAddForm(!showAddForm)} className="gap-2">
          <Plus className="h-4 w-4" />
          Add Expense
        </Button>
      </div>

      {/* Add Expense Form */}
      {showAddForm && (
        <Card className="mb-8 border-primary/20 shadow-lg">
          <CardHeader>
            <CardTitle>Add New Expense</CardTitle>
            <CardDescription>Record a new expense transaction</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="category">Category</Label>
                  <select
                    id="category"
                    title="Select expense category"
                    aria-label="Expense Category"
                    className="w-full px-3 py-2 rounded-md border border-input bg-background"
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                    required
                  >
                    <option value="">Select category</option>
                    {EXPENSE_CATEGORIES.map(cat => (
                      <option key={cat.value} value={cat.value}>{cat.label}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="amount">Amount</Label>
                  <Input
                    id="amount"
                    type="number"
                    placeholder="1000"
                    value={formData.amount}
                    onChange={(e) => setFormData({...formData, amount: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="date">Date</Label>
                  <Input
                    id="date"
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    placeholder="e.g., Grocery shopping"
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button type="submit">Save Expense</Button>
                <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Expenses List */}
      <div className="space-y-4">
        <h3 className="text-2xl font-bold">Recent Expenses</h3>
        {expenses.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Activity className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-2">No expenses yet</p>
              <p className="text-sm text-muted-foreground mb-4">Start tracking your spending</p>
              <Button onClick={() => setShowAddForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Your First Expense
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {expenses.map((expense) => {
              const category = EXPENSE_CATEGORIES.find(cat => cat.value === expense.category) || EXPENSE_CATEGORIES[EXPENSE_CATEGORIES.length - 1];
              const Icon = category.icon;

              return (
                <Card key={expense.id} className="border-border/40 hover:shadow-lg transition-all">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <div className={cn("p-2 rounded-lg", category.color, "bg-opacity-20")}>
                            <Icon className="h-5 w-5" />
                          </div>
                          <div>
                            <h4 className="font-semibold text-lg">{category.label}</h4>
                            {expense.description && (
                              <p className="text-sm text-muted-foreground">{expense.description}</p>
                            )}
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4 mt-4">
                          <div>
                            <p className="text-xs text-muted-foreground">Amount</p>
                            <p className="font-semibold text-red-600 dark:text-red-400">₹{expense.amount.toLocaleString('en-IN')}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Date</p>
                            <p className="font-semibold">{new Date(expense.date).toLocaleDateString()}</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2 ml-4">
                        <Button variant="ghost" size="icon" className="hover:bg-primary/10">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="hover:bg-destructive/10 hover:text-destructive"
                          onClick={() => expense.id && handleDelete(expense.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
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
