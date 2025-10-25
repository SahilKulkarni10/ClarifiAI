import { useEffect, useState } from 'react';
import { AppLayout } from '@/components/layouts/AppLayout';
import { financeService, type Loan } from '@/services/finance.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { 
  Wallet, 
  Plus, 
  Trash2, 
  Edit,
  Calendar,
  Percent,
  DollarSign,
  Activity,
  TrendingDown
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function LoansPage() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    type: '',
    principal: '',
    interest_rate: '',
    emi: '',
    outstanding: '',
    start_date: new Date().toISOString().split('T')[0],
    end_date: ''
  });

  useEffect(() => {
    fetchLoans();
  }, []);

  const fetchLoans = async () => {
    try {
      setLoading(true);
      const data = await financeService.getLoans();
      setLoans(data);
    } catch (error) {
      console.error('Error fetching loans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financeService.createLoan({
        ...formData,
        principal: parseFloat(formData.principal),
        interest_rate: parseFloat(formData.interest_rate),
        emi: parseFloat(formData.emi),
        outstanding: parseFloat(formData.outstanding || formData.principal),
      } as Loan);
      setShowAddForm(false);
      setFormData({
        type: '',
        principal: '',
        interest_rate: '',
        emi: '',
        outstanding: '',
        start_date: new Date().toISOString().split('T')[0],
        end_date: ''
      });
      fetchLoans();
    } catch (error) {
      console.error('Error adding loan:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this loan?')) {
      try {
        await financeService.deleteLoan(id);
        fetchLoans();
      } catch (error) {
        console.error('Error deleting loan:', error);
      }
    }
  };

  const totalPrincipal = loans.reduce((sum, loan) => sum + loan.principal, 0);
  const totalOutstanding = loans.reduce((sum, loan) => sum + loan.outstanding, 0);
  const totalEMI = loans.reduce((sum, loan) => sum + loan.emi, 0);
  const paidPercentage = totalPrincipal > 0 ? ((totalPrincipal - totalOutstanding) / totalPrincipal) * 100 : 0;

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto"></div>
            <p className="text-muted-foreground">Loading loans...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout 
      title="Loan Management" 
      description="Track your loans, EMIs, and payment schedules"
    >
      {/* Loan Summary */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <Card className="border-border/40 bg-gradient-to-br from-orange-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Total Borrowed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">₹{totalPrincipal.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">{loans.length} active loans</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-red-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Wallet className="h-4 w-4" />
              Total Outstanding
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600 dark:text-red-400">₹{totalOutstanding.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">Amount remaining</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-blue-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Monthly EMI
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">₹{totalEMI.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">Total monthly payment</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-green-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingDown className="h-4 w-4" />
              Paid Off
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600 dark:text-green-400">{paidPercentage.toFixed(1)}%</div>
            <Progress value={paidPercentage} className="mt-2 h-2" />
          </CardContent>
        </Card>
      </div>

      {/* Add Loan Button */}
      <div className="mb-6">
        <Button onClick={() => setShowAddForm(!showAddForm)} className="gap-2">
          <Plus className="h-4 w-4" />
          Add Loan
        </Button>
      </div>

      {/* Add Loan Form */}
      {showAddForm && (
        <Card className="mb-8 border-primary/20 shadow-lg">
          <CardHeader>
            <CardTitle>Add New Loan</CardTitle>
            <CardDescription>Track a new loan and its payment schedule</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="type">Loan Type</Label>
                  <Input
                    id="type"
                    placeholder="e.g., Home Loan, Car Loan, Personal"
                    value={formData.type}
                    onChange={(e) => setFormData({...formData, type: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="principal">Principal Amount</Label>
                  <Input
                    id="principal"
                    type="number"
                    placeholder="500000"
                    value={formData.principal}
                    onChange={(e) => setFormData({...formData, principal: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="interest_rate">Interest Rate (%)</Label>
                  <Input
                    id="interest_rate"
                    type="number"
                    step="0.01"
                    placeholder="8.5"
                    value={formData.interest_rate}
                    onChange={(e) => setFormData({...formData, interest_rate: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="emi">Monthly EMI</Label>
                  <Input
                    id="emi"
                    type="number"
                    placeholder="15000"
                    value={formData.emi}
                    onChange={(e) => setFormData({...formData, emi: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="outstanding">Outstanding Amount</Label>
                  <Input
                    id="outstanding"
                    type="number"
                    placeholder="450000"
                    value={formData.outstanding}
                    onChange={(e) => setFormData({...formData, outstanding: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="start_date">Start Date</Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="end_date">End Date</Label>
                  <Input
                    id="end_date"
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                    required
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button type="submit">Save Loan</Button>
                <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Loans List */}
      <div className="space-y-4">
        <h3 className="text-2xl font-bold">Active Loans</h3>
        {loans.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Activity className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-2">No loans tracked</p>
              <p className="text-sm text-muted-foreground mb-4">Start tracking your loans and EMI payments</p>
              <Button onClick={() => setShowAddForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Your First Loan
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {loans.map((loan) => {
              const paid = loan.principal - loan.outstanding;
              const paidPercent = (paid / loan.principal) * 100;
              const monthsRemaining = Math.ceil(loan.outstanding / loan.emi);

              return (
                <Card key={loan.id} className="border-border/40 hover:shadow-lg transition-all">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-orange-500/10">
                          <Wallet className="h-5 w-5 text-orange-600" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-lg">{loan.type}</h4>
                          <p className="text-sm text-muted-foreground">
                            {new Date(loan.start_date).toLocaleDateString()} - {new Date(loan.end_date).toLocaleDateString()}
                          </p>
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
                          onClick={() => loan.id && handleDelete(loan.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <DollarSign className="h-3 w-3" />
                            Principal
                          </p>
                          <p className="font-semibold">₹{loan.principal.toLocaleString('en-IN')}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <Wallet className="h-3 w-3" />
                            Outstanding
                          </p>
                          <p className="font-semibold text-red-600">₹{loan.outstanding.toLocaleString('en-IN')}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            Monthly EMI
                          </p>
                          <p className="font-semibold">₹{loan.emi.toLocaleString('en-IN')}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <Percent className="h-3 w-3" />
                            Interest Rate
                          </p>
                          <p className="font-semibold">{loan.interest_rate}%</p>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Repayment Progress</span>
                          <span className="font-semibold">{paidPercent.toFixed(1)}% paid</span>
                        </div>
                        <Progress value={paidPercent} className="h-3" />
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Paid: ₹{paid.toLocaleString('en-IN')}</span>
                          <span>~{monthsRemaining} months remaining</span>
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
