/**
 * Income Page
 * Manage income sources and track earnings
 */

import { useEffect, useState } from 'react';
import { AppLayout } from '@/components/layouts/AppLayout';
import { financeService, type Income } from '@/services/finance.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  DollarSign, 
  Plus, 
  Trash2, 
  TrendingUp, 
  Calendar,
  Briefcase,
  Activity 
} from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

const INCOME_CATEGORIES = [
  { value: 'salary', label: 'Salary', icon: Briefcase },
  { value: 'freelance', label: 'Freelance', icon: Activity },
  { value: 'business', label: 'Business', icon: TrendingUp },
  { value: 'investment', label: 'Investment Returns', icon: DollarSign },
  { value: 'rental', label: 'Rental Income', icon: DollarSign },
  { value: 'other', label: 'Other', icon: DollarSign }
];

export default function IncomePage() {
  const [incomeList, setIncomeList] = useState<Income[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    source: '',
    amount: '',
    date: new Date().toISOString().split('T')[0],
    category: 'salary',
    description: '',
  });

  const fetchIncome = async () => {
    try {
      setLoading(true);
      const data = await financeService.getIncome();
      setIncomeList(data);
    } catch (error) {
      console.error('Failed to fetch income:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncome();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await financeService.createIncome({
        source: formData.source,
        amount: Number(formData.amount),
        date: formData.date,
        category: formData.category,
        description: formData.description || undefined,
      });
      
      setDialogOpen(false);
      setFormData({
        source: '',
        amount: '',
        date: new Date().toISOString().split('T')[0],
        category: 'salary',
        description: '',
      });
      fetchIncome();
    } catch (error) {
      console.error('Failed to add income:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this income entry?')) {
      try {
        await financeService.deleteIncome(id);
        fetchIncome();
      } catch (error) {
        console.error('Error deleting income:', error);
      }
    }
  };

  const totalIncome = incomeList.reduce((sum, income) => sum + income.amount, 0);
  const thisMonthIncome = incomeList.filter(inc => {
    const incomeDate = new Date(inc.date);
    const now = new Date();
    return incomeDate.getMonth() === now.getMonth() && incomeDate.getFullYear() === now.getFullYear();
  }).reduce((sum, income) => sum + income.amount, 0);

  // Group by category
  const categoryTotals = incomeList.reduce((acc, inc) => {
    acc[inc.category] = (acc[inc.category] || 0) + inc.amount;
    return acc;
  }, {} as Record<string, number>);

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto"></div>
            <p className="text-muted-foreground">Loading income data...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout 
      title="Income Tracking" 
      description="Monitor your income sources and earnings"
    >
      {/* Summary Cards */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <Card className="border-border/40 bg-gradient-to-br from-green-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Total Income
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600 dark:text-green-400">₹{totalIncome.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">{incomeList.length} entries</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-blue-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              This Month
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">₹{thisMonthIncome.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">Current month income</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-purple-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Income Sources
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{Object.keys(categoryTotals).length}</div>
            <p className="text-xs text-muted-foreground mt-2">Active categories</p>
          </CardContent>
        </Card>
      </div>

      {/* Add Income Button */}
      <div className="mb-8">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Add Income
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Income</DialogTitle>
              <DialogDescription>
                Record a new income transaction
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="source">Source</Label>
                <Input
                  id="source"
                  placeholder="e.g., Monthly Salary"
                  value={formData.source}
                  onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <select
                  id="category"
                  aria-label="Income Category"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  required
                >
                  {INCOME_CATEGORIES.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="amount">Amount (₹)</Label>
                <Input
                  id="amount"
                  type="number"
                  placeholder="50000"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Input
                  id="description"
                  placeholder="Additional notes"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit">Add Income</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Income List */}
      {incomeList.length === 0 ? (
        <Card className="border-border/40">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <DollarSign className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Income Recorded</h3>
            <p className="text-muted-foreground text-center mb-4">
              Start tracking your income by adding your first entry
            </p>
            <Button onClick={() => setDialogOpen(true)} className="gap-2">
              <Plus className="h-4 w-4" />
              Add Your First Income
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          <Card className="border-border/40">
            <CardHeader>
              <CardTitle>Income History</CardTitle>
              <CardDescription>All your income transactions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {incomeList.map((income) => {
                  const categoryInfo = INCOME_CATEGORIES.find(c => c.value === income.category);
                  const Icon = categoryInfo?.icon || DollarSign;
                  
                  return (
                    <div
                      key={income.id}
                      className="flex items-center justify-between p-4 rounded-lg border border-border/40 hover:border-primary/40 transition-all hover:shadow-sm"
                    >
                      <div className="flex items-center gap-4">
                        <div className="p-3 rounded-lg bg-green-500/10">
                          <Icon className="h-5 w-5 text-green-600 dark:text-green-400" />
                        </div>
                        <div>
                          <h4 className="font-semibold">{income.source}</h4>
                          <p className="text-sm text-muted-foreground">
                            {categoryInfo?.label || income.category} • {new Date(income.date).toLocaleDateString('en-IN', {
                              day: 'numeric',
                              month: 'short',
                              year: 'numeric'
                            })}
                          </p>
                          {income.description && (
                            <p className="text-xs text-muted-foreground mt-1">{income.description}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <div className="text-lg font-bold text-green-600 dark:text-green-400">
                            +₹{income.amount.toLocaleString('en-IN')}
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(income.id!)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </AppLayout>
  );
}
