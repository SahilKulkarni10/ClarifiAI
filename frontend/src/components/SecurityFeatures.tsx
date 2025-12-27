import { Shield, Lock, Eye, EyeOff, CheckCircle2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { useState } from 'react';
import { cn } from '@/lib/utils';

interface SecurityBadgeProps {
  level: 'high' | 'medium' | 'basic';
  features?: string[];
  className?: string;
}

export function SecurityBadge({ level, features = [], className }: SecurityBadgeProps) {
  const getSecurityConfig = () => {
    switch (level) {
      case 'high':
        return {
          icon: Shield,
          color: 'text-green-600',
          bg: 'bg-green-100 dark:bg-green-900/30',
          label: 'Bank-Grade Security',
          description: 'Your data is protected with industry-leading security measures'
        };
      case 'medium':
        return {
          icon: Lock,
          color: 'text-blue-600',
          bg: 'bg-blue-100 dark:bg-blue-900/30',
          label: 'Secure',
          description: 'Your data is encrypted and protected'
        };
      default:
        return {
          icon: Shield,
          color: 'text-gray-600',
          bg: 'bg-gray-100 dark:bg-gray-900/30',
          label: 'Protected',
          description: 'Basic security measures in place'
        };
    }
  };

  const config = getSecurityConfig();
  const Icon = config.icon;

  const defaultFeatures = [
    '256-bit AES Encryption',
    'Secure Authentication',
    'Data Privacy Compliant',
    'Regular Security Audits'
  ];

  const displayFeatures = features.length > 0 ? features : defaultFeatures;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge 
            variant="secondary" 
            className={cn(config.bg, config.color, 'gap-1.5 cursor-help', className)}
          >
            <Icon className="h-3 w-3" />
            {config.label}
          </Badge>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="max-w-xs">
          <div className="space-y-2">
            <p className="font-semibold">{config.description}</p>
            <ul className="space-y-1 text-xs">
              {displayFeatures.map((feature, index) => (
                <li key={index} className="flex items-center gap-2">
                  <CheckCircle2 className="h-3 w-3 text-green-500" />
                  {feature}
                </li>
              ))}
            </ul>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

interface MaskedDataProps {
  data: string;
  type?: 'account' | 'card' | 'custom';
  showByDefault?: boolean;
  className?: string;
}

export function MaskedData({ data, type = 'custom', showByDefault = false, className }: MaskedDataProps) {
  const [isVisible, setIsVisible] = useState(showByDefault);

  const maskData = (value: string) => {
    if (type === 'account') {
      // Show last 4 digits of account number
      return '••••••' + value.slice(-4);
    } else if (type === 'card') {
      // Show last 4 digits of card, format as XXXX XXXX XXXX 1234
      const last4 = value.slice(-4);
      return `•••• •••• •••• ${last4}`;
    } else {
      // Custom masking - show first and last character
      if (value.length <= 4) return '••••';
      return value[0] + '••••' + value.slice(-1);
    }
  };

  return (
    <div className={cn('inline-flex items-center gap-2', className)}>
      <span className="font-mono">
        {isVisible ? data : maskData(data)}
      </span>
      <Button
        variant="ghost"
        size="sm"
        className="h-6 w-6 p-0"
        onClick={() => setIsVisible(!isVisible)}
      >
        {isVisible ? (
          <EyeOff className="h-3 w-3" />
        ) : (
          <Eye className="h-3 w-3" />
        )}
      </Button>
    </div>
  );
}

interface SecurityStatusCardProps {
  className?: string;
}

export function SecurityStatusCard({ className }: SecurityStatusCardProps) {
  const securityChecks = [
    { label: 'Two-Factor Authentication', status: 'enabled', color: 'text-green-600' },
    { label: 'Password Strength', status: 'strong', color: 'text-green-600' },
    { label: 'Data Encryption', status: 'active', color: 'text-green-600' },
    { label: 'Session Security', status: 'secure', color: 'text-green-600' },
  ];

  return (
    <Card className={cn('border-green-500/20 bg-gradient-to-br from-green-500/5 to-emerald-500/5', className)}>
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-xl bg-green-500/10">
            <Shield className="h-6 w-6 text-green-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-lg mb-1">Security Status</h3>
            <p className="text-sm text-muted-foreground mb-4">
              All security features are active and protecting your data
            </p>
            <div className="space-y-2">
              {securityChecks.map((check, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{check.label}</span>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className={cn('h-4 w-4', check.color)} />
                    <span className={cn('font-medium capitalize', check.color)}>
                      {check.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
