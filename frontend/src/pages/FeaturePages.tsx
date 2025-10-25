/**
 * Placeholder Pages
 * These pages will be expanded with full functionality
 */

import { AppLayout } from '@/components/layouts/AppLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

// Expenses Page
export function ExpensesPage() {
  return (
    <AppLayout
      title="Expenses"
      description="Track and manage your spending"
    >
      <Card>
        <CardHeader>
          <CardTitle>Expense Management</CardTitle>
          <CardDescription>Monitor your expenses and stay within budget</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            This feature is coming soon. You'll be able to track all your expenses, categorize them, and analyze spending patterns.
          </p>
        </CardContent>
      </Card>
    </AppLayout>
  );
}

// Insurance Page
export function InsurancePage() {
  return (
    <AppLayout
      title="Insurance"
      description="Manage your insurance policies"
    >
      <Card>
        <CardHeader>
          <CardTitle>Insurance Policies</CardTitle>
          <CardDescription>Track all your insurance coverage and premiums</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            This feature is coming soon. You'll be able to manage life insurance, health insurance, and other policies in one place.
          </p>
        </CardContent>
      </Card>
    </AppLayout>
  );
}

// Goals Page
export function GoalsPage() {
  return (
    <AppLayout
      title="Financial Goals"
      description="Set and track your financial goals"
    >
      <Card>
        <CardHeader>
          <CardTitle>Goal Planning</CardTitle>
          <CardDescription>Set targets and track progress towards your financial goals</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            This feature is coming soon. You'll be able to set financial goals like buying a house, retirement planning, or saving for education.
          </p>
        </CardContent>
      </Card>
    </AppLayout>
  );
}
