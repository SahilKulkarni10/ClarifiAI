import { useEffect, useState } from 'react';
import { AppLayout } from '@/components/layouts/AppLayout';
import { financeService, type Investment } from '@/services/finance.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  TrendingUp, 
  TrendingDown,
  Plus, 
  Trash2, 
  Edit,
  PieChart,
  DollarSign,
  Activity
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function InvestmentsPage() {
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    type: '',
    name: '',
    amount: '',
    current_value: '',
    purchase_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    fetchInvestments();
  }, []);

  const fetchInvestments = async () => {
    try {
      setLoading(true);
      const data = await financeService.getInvestments();
      setInvestments(data);
    } catch (error) {
      console.error('Error fetching investments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financeService.createInvestment({
        ...formData,
        amount: parseFloat(formData.amount),
        current_value: parseFloat(formData.current_value || formData.amount),
      } as Investment);
      setShowAddForm(false);
      setFormData({
        type: '',
        name: '',
        amount: '',
        current_value: '',
        purchase_date: new Date().toISOString().split('T')[0]
      });
      fetchInvestments();
    } catch (error) {
      console.error('Error adding investment:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this investment?')) {
      try {
        await financeService.deleteInvestment(id);
        fetchInvestments();
      } catch (error) {
        console.error('Error deleting investment:', error);
      }
    }
  };

  const totalInvested = investments.reduce((sum, inv) => sum + inv.amount, 0);
  const totalCurrentValue = investments.reduce((sum, inv) => sum + (inv.current_value || inv.amount), 0);
  const totalGain = totalCurrentValue - totalInvested;
  const gainPercentage = totalInvested > 0 ? ((totalGain / totalInvested) * 100).toFixed(2) : '0';
  const isPositiveGain = totalGain >= 0;

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto"></div>
            <p className="text-muted-foreground">Loading investments...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout 
      title="Investment Portfolio" 
      description="Track and manage your investment holdings"
    >
      {/* Portfolio Summary */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <Card className="border-border/40 bg-gradient-to-br from-blue-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Total Invested
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">₹{totalInvested.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">{investments.length} holdings</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-green-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <PieChart className="h-4 w-4" />
              Current Value
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">₹{totalCurrentValue.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">Portfolio value</p>
          </CardContent>
        </Card>

        <Card className={cn(
          "border-border/40 bg-gradient-to-br via-background to-background",
          isPositiveGain ? "from-green-500/10" : "from-red-500/10"
        )}>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              {isPositiveGain ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
              Total Gain/Loss
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={cn(
              "text-3xl font-bold",
              isPositiveGain ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
            )}>
              {isPositiveGain ? '+' : ''}₹{totalGain.toLocaleString('en-IN')}
            </div>
            <p className={cn(
              "text-xs mt-2",
              isPositiveGain ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
            )}>
              {isPositiveGain ? '+' : ''}{gainPercentage}% return
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Add Investment Button */}
      <div className="mb-6">
        <Button onClick={() => setShowAddForm(!showAddForm)} className="gap-2">
          <Plus className="h-4 w-4" />
          Add Investment
        </Button>
      </div>

      {/* Add Investment Form */}
      {showAddForm && (
        <Card className="mb-8 border-primary/20 shadow-lg">
          <CardHeader>
            <CardTitle>Add New Investment</CardTitle>
            <CardDescription>Track a new investment in your portfolio</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="type">Investment Type</Label>
                  <Input
                    id="type"
                    placeholder="e.g., Stocks, Mutual Fund, Crypto"
                    value={formData.type}
                    onChange={(e) => setFormData({...formData, type: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="name">Investment Name</Label>
                  <Input
                    id="name"
                    placeholder="e.g., Apple Inc., HDFC Index Fund"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="amount">Amount Invested</Label>
                  <Input
                    id="amount"
                    type="number"
                    placeholder="10000"
                    value={formData.amount}
                    onChange={(e) => setFormData({...formData, amount: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="current_value">Current Value (Optional)</Label>
                  <Input
                    id="current_value"
                    type="number"
                    placeholder="12000"
                    value={formData.current_value}
                    onChange={(e) => setFormData({...formData, current_value: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="purchase_date">Purchase Date</Label>
                  <Input
                    id="purchase_date"
                    type="date"
                    value={formData.purchase_date}
                    onChange={(e) => setFormData({...formData, purchase_date: e.target.value})}
                    required
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button type="submit">Save Investment</Button>
                <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Investments List */}
      <div className="space-y-4">
        <h3 className="text-2xl font-bold">Your Holdings</h3>
        {investments.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Activity className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-2">No investments yet</p>
              <p className="text-sm text-muted-foreground mb-4">Start tracking your portfolio by adding your first investment</p>
              <Button onClick={() => setShowAddForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Your First Investment
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {investments.map((investment) => {
              const currentValue = investment.current_value || investment.amount;
              const gain = currentValue - investment.amount;
              const gainPercent = ((gain / investment.amount) * 100).toFixed(2);
              const isPositive = gain >= 0;

              return (
                <Card key={investment.id} className="border-border/40 hover:shadow-lg transition-all">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="p-2 rounded-lg bg-primary/10">
                            <TrendingUp className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <h4 className="font-semibold text-lg">{investment.name}</h4>
                            <p className="text-sm text-muted-foreground">{investment.type}</p>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                          <div>
                            <p className="text-xs text-muted-foreground">Invested</p>
                            <p className="font-semibold">₹{investment.amount.toLocaleString('en-IN')}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Current Value</p>
                            <p className="font-semibold">₹{currentValue.toLocaleString('en-IN')}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Gain/Loss</p>
                            <p className={cn(
                              "font-semibold",
                              isPositive ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
                            )}>
                              {isPositive ? '+' : ''}₹{gain.toLocaleString('en-IN')} ({gainPercent}%)
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Purchase Date</p>
                            <p className="font-semibold">{new Date(investment.purchase_date).toLocaleDateString()}</p>
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
                          onClick={() => investment.id && handleDelete(investment.id)}
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
