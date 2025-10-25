import { useEffect, useState } from 'react';
import { AppLayout } from '@/components/layouts/AppLayout';
import { financeService, type Insurance } from '@/services/finance.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { 
  Shield, 
  Plus, 
  Trash2, 
  Edit,
  Heart,
  Home,
  Car,
  Briefcase,
  Activity,
  Calendar,
  DollarSign
} from 'lucide-react';
import { cn } from '@/lib/utils';

const INSURANCE_TYPES = [
  { value: 'life', label: 'Life Insurance', icon: Heart, color: 'bg-red-500' },
  { value: 'health', label: 'Health Insurance', icon: Activity, color: 'bg-green-500' },
  { value: 'home', label: 'Home Insurance', icon: Home, color: 'bg-blue-500' },
  { value: 'auto', label: 'Auto Insurance', icon: Car, color: 'bg-yellow-500' },
  { value: 'business', label: 'Business Insurance', icon: Briefcase, color: 'bg-purple-500' },
  { value: 'other', label: 'Other', icon: Shield, color: 'bg-gray-500' }
];

export default function InsurancePage() {
  const [policies, setPolicies] = useState<Insurance[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    type: '',
    provider: '',
    premium: '',
    coverage: '',
    start_date: new Date().toISOString().split('T')[0],
    end_date: ''
  });

  useEffect(() => {
    fetchInsurance();
  }, []);

  const fetchInsurance = async () => {
    try {
      setLoading(true);
      const data = await financeService.getInsurance();
      setPolicies(data);
    } catch (error) {
      console.error('Error fetching insurance:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financeService.createInsurance({
        ...formData,
        premium: parseFloat(formData.premium),
        coverage: parseFloat(formData.coverage),
      } as Insurance);
      setShowAddForm(false);
      setFormData({
        type: '',
        provider: '',
        premium: '',
        coverage: '',
        start_date: new Date().toISOString().split('T')[0],
        end_date: ''
      });
      fetchInsurance();
    } catch (error) {
      console.error('Error adding insurance:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this policy?')) {
      try {
        await financeService.deleteInsurance(id);
        fetchInsurance();
      } catch (error) {
        console.error('Error deleting insurance:', error);
      }
    }
  };

  const totalPremium = policies.reduce((sum, policy) => sum + policy.premium, 0);
  const totalCoverage = policies.reduce((sum, policy) => sum + policy.coverage, 0);
  const activePolicies = policies.filter(p => new Date(p.end_date) > new Date()).length;

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mx-auto"></div>
            <p className="text-muted-foreground">Loading insurance policies...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout 
      title="Insurance Management" 
      description="Track your insurance policies and coverage"
    >
      {/* Summary Cards */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <Card className="border-border/40 bg-gradient-to-br from-blue-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Active Policies
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{activePolicies}</div>
            <p className="text-xs text-muted-foreground mt-2">out of {policies.length} total</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-purple-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Annual Premium
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">₹{(totalPremium * 12).toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">₹{totalPremium.toLocaleString('en-IN')}/month</p>
          </CardContent>
        </Card>

        <Card className="border-border/40 bg-gradient-to-br from-green-500/10 via-background to-background">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Total Coverage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600 dark:text-green-400">₹{totalCoverage.toLocaleString('en-IN')}</div>
            <p className="text-xs text-muted-foreground mt-2">Protection amount</p>
          </CardContent>
        </Card>
      </div>

      {/* Add Insurance Button */}
      <div className="mb-6">
        <Button onClick={() => setShowAddForm(!showAddForm)} className="gap-2">
          <Plus className="h-4 w-4" />
          Add Insurance Policy
        </Button>
      </div>

      {/* Add Insurance Form */}
      {showAddForm && (
        <Card className="mb-8 border-primary/20 shadow-lg">
          <CardHeader>
            <CardTitle>Add New Insurance Policy</CardTitle>
            <CardDescription>Track a new insurance policy</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="type">Insurance Type</Label>
                  <select
                    id="type"
                    title="Select insurance type"
                    aria-label="Insurance Type"
                    className="w-full px-3 py-2 rounded-md border border-input bg-background"
                    value={formData.type}
                    onChange={(e) => setFormData({...formData, type: e.target.value})}
                    required
                  >
                    <option value="">Select type</option>
                    {INSURANCE_TYPES.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="provider">Provider</Label>
                  <Input
                    id="provider"
                    placeholder="e.g., HDFC Life, LIC"
                    value={formData.provider}
                    onChange={(e) => setFormData({...formData, provider: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="premium">Monthly Premium</Label>
                  <Input
                    id="premium"
                    type="number"
                    placeholder="5000"
                    value={formData.premium}
                    onChange={(e) => setFormData({...formData, premium: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="coverage">Coverage Amount</Label>
                  <Input
                    id="coverage"
                    type="number"
                    placeholder="1000000"
                    value={formData.coverage}
                    onChange={(e) => setFormData({...formData, coverage: e.target.value})}
                    required
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
                <Button type="submit">Save Policy</Button>
                <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Insurance List */}
      <div className="space-y-4">
        <h3 className="text-2xl font-bold">Your Policies</h3>
        {policies.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Shield className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-2">No insurance policies</p>
              <p className="text-sm text-muted-foreground mb-4">Start protecting yourself and your assets</p>
              <Button onClick={() => setShowAddForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Your First Policy
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {policies.map((policy) => {
              const insuranceType = INSURANCE_TYPES.find(t => t.value === policy.type) || INSURANCE_TYPES[INSURANCE_TYPES.length - 1];
              const Icon = insuranceType.icon;
              const startDate = new Date(policy.start_date);
              const endDate = new Date(policy.end_date);
              const now = new Date();
              const isActive = endDate > now;
              const daysRemaining = Math.ceil((endDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

              return (
                <Card key={policy.id} className={cn(
                  "border-border/40 hover:shadow-lg transition-all",
                  !isActive && "opacity-60"
                )}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className={cn("p-2 rounded-lg", insuranceType.color, "bg-opacity-20")}>
                          <Icon className="h-5 w-5" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-lg">{insuranceType.label}</h4>
                          <p className="text-sm text-muted-foreground">{policy.provider}</p>
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
                          onClick={() => policy.id && handleDelete(policy.id)}
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
                            Premium
                          </p>
                          <p className="font-semibold">₹{policy.premium.toLocaleString('en-IN')}/mo</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <Shield className="h-3 w-3" />
                            Coverage
                          </p>
                          <p className="font-semibold text-green-600">₹{policy.coverage.toLocaleString('en-IN')}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            Start Date
                          </p>
                          <p className="font-semibold">{startDate.toLocaleDateString()}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            End Date
                          </p>
                          <p className="font-semibold">{endDate.toLocaleDateString()}</p>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">
                            {isActive ? 'Time Remaining' : 'Expired'}
                          </span>
                          <span className={cn(
                            "font-semibold",
                            isActive ? "text-green-600" : "text-red-600"
                          )}>
                            {isActive ? `${daysRemaining} days` : 'Policy expired'}
                          </span>
                        </div>
                        {isActive && (
                          <Progress 
                            value={((endDate.getTime() - now.getTime()) / (endDate.getTime() - startDate.getTime())) * 100} 
                            className="h-2" 
                          />
                        )}
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
