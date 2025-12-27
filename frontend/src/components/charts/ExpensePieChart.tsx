import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { motion } from 'framer-motion';
import { TrendingDown } from 'lucide-react';

interface ExpensePieChartProps {
  data: Array<{ category: string; amount: number; color: string }>;
}

const COLORS = {
  housing: '#3b82f6',
  food: '#f59e0b',
  transport: '#06b6d4',
  shopping: '#ec4899',
  health: '#ef4444',
  utilities: '#eab308',
  entertainment: '#8b5cf6',
  other: '#6b7280',
};

export const ExpensePieChart = ({ data }: ExpensePieChartProps) => {
  const chartData = data.map(item => ({
    name: item.category.charAt(0).toUpperCase() + item.category.slice(1),
    value: item.amount,
    color: COLORS[item.category as keyof typeof COLORS] || COLORS.other,
  }));

  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const percentage = ((payload[0].value / total) * 100).toFixed(1);
      return (
        <div className="bg-popover border border-border rounded-lg p-3 shadow-lg">
          <p className="text-sm font-semibold">{payload[0].name}</p>
          <p className="text-sm text-muted-foreground">
            ₹{payload[0].value.toLocaleString('en-IN')}
          </p>
          <p className="text-xs text-primary">{percentage}%</p>
        </div>
      );
    }
    return null;
  };

  const renderCustomLabel = (entry: any) => {
    const percentage = ((entry.value / total) * 100).toFixed(0);
    return `${percentage}%`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="border-border/40 bg-card/50 backdrop-blur-sm">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-red-500/10">
              <TrendingDown className="h-5 w-5 text-red-600 dark:text-red-400" />
            </div>
            <div>
              <CardTitle>Expense Breakdown</CardTitle>
              <CardDescription>Your spending by category</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {chartData.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={renderCustomLabel}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    animationBegin={0}
                    animationDuration={800}
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend 
                    verticalAlign="bottom" 
                    height={36}
                    formatter={(value, entry: any) => (
                      <span className="text-sm">
                        {value}: ₹{entry.payload.value.toLocaleString('en-IN')}
                      </span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-4 text-center">
                <p className="text-2xl font-bold">₹{total.toLocaleString('en-IN')}</p>
                <p className="text-sm text-muted-foreground">Total Monthly Expenses</p>
              </div>
            </>
          ) : (
            <div className="h-[300px] flex items-center justify-center">
              <div className="text-center space-y-2">
                <TrendingDown className="h-12 w-12 text-muted-foreground/50 mx-auto" />
                <p className="text-muted-foreground">No expense data available</p>
                <p className="text-xs text-muted-foreground">Start adding expenses to see breakdown</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};
