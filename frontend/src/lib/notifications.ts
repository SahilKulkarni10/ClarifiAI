import { toast } from 'sonner';
import { 
  CheckCircle2, 
  AlertCircle, 
  Info, 
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Target,
  DollarSign,
  Shield
} from 'lucide-react';

export type NotificationType = 'success' | 'error' | 'warning' | 'info' | 'financial';

export interface NotificationOptions {
  title: string;
  description?: string;
  type: NotificationType;
  action?: {
    label: string;
    onClick: () => void;
  };
  duration?: number;
}

const getIcon = (type: NotificationType) => {
  switch (type) {
    case 'success':
      return <CheckCircle2 className="h-5 w-5 text-green-600" />;
    case 'error':
      return <AlertCircle className="h-5 w-5 text-red-600" />;
    case 'warning':
      return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
    case 'info':
      return <Info className="h-5 w-5 text-blue-600" />;
    case 'financial':
      return <DollarSign className="h-5 w-5 text-purple-600" />;
    default:
      return <Info className="h-5 w-5" />;
  }
};

export const notify = (options: NotificationOptions) => {
  const { title, description, type, action, duration = 4000 } = options;

  toast(title, {
    description,
    icon: getIcon(type),
    duration,
    action: action ? {
      label: action.label,
      onClick: action.onClick,
    } : undefined,
    classNames: {
      toast: 'group-[.toaster]:bg-background group-[.toaster]:border-border group-[.toaster]:shadow-lg',
      title: 'group-[.toast]:text-foreground group-[.toast]:font-semibold',
      description: 'group-[.toast]:text-muted-foreground',
      actionButton: 'group-[.toast]:bg-primary group-[.toast]:text-primary-foreground',
    },
  });
};

// Preset notifications for common scenarios
export const notifications = {
  success: (title: string, description?: string) =>
    notify({ title, description, type: 'success' }),

  error: (title: string, description?: string) =>
    notify({ title, description, type: 'error' }),

  warning: (title: string, description?: string) =>
    notify({ title, description, type: 'warning' }),

  info: (title: string, description?: string) =>
    notify({ title, description, type: 'info' }),

  // Financial-specific notifications
  budgetAlert: (category: string, percentage: number) =>
    notify({
      title: `Budget Alert: ${category}`,
      description: `You've spent ${percentage}% of your ${category} budget this month`,
      type: 'warning',
      icon: <TrendingDown className="h-5 w-5 text-orange-600" />,
    }),

  goalAchieved: (goalName: string) =>
    notify({
      title: '🎉 Goal Achieved!',
      description: `Congratulations! You've reached your ${goalName} goal`,
      type: 'success',
      icon: <Target className="h-5 w-5 text-green-600" />,
      duration: 6000,
    }),

  savingsMilestone: (amount: number) =>
    notify({
      title: '💰 Savings Milestone!',
      description: `Great job! You've saved ₹${amount.toLocaleString('en-IN')} this month`,
      type: 'financial',
      icon: <TrendingUp className="h-5 w-5 text-green-600" />,
      duration: 5000,
    }),

  investmentAlert: (investment: string, change: number) =>
    notify({
      title: change >= 0 ? '📈 Investment Update' : '📉 Investment Alert',
      description: `${investment} ${change >= 0 ? 'gained' : 'lost'} ${Math.abs(change)}% today`,
      type: change >= 0 ? 'success' : 'warning',
      icon: change >= 0 
        ? <TrendingUp className="h-5 w-5 text-green-600" />
        : <TrendingDown className="h-5 w-5 text-red-600" />,
    }),

  loanReminder: (loanName: string, dueDate: string, amount: number) =>
    notify({
      title: '💳 EMI Due Soon',
      description: `${loanName} payment of ₹${amount.toLocaleString('en-IN')} due on ${dueDate}`,
      type: 'info',
      duration: 6000,
    }),

  insuranceRenewal: (policyName: string, daysLeft: number) =>
    notify({
      title: '🛡️ Insurance Renewal',
      description: `Your ${policyName} policy expires in ${daysLeft} days`,
      type: 'warning',
      icon: <Shield className="h-5 w-5 text-blue-600" />,
      duration: 6000,
    }),

  aiInsight: (insight: string) =>
    notify({
      title: '🤖 AI Financial Insight',
      description: insight,
      type: 'info',
      duration: 8000,
    }),
};
