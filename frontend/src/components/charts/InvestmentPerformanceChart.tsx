import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { motion } from 'framer-motion';
import { BarChart3 } from 'lucide-react';

interface InvestmentPerformanceChartProps {
  data: Array<{ name: string; currentValue: number; invested: number; returns: number }>;
}

export const InvestmentPerformanceChart = ({ data }: InvestmentPerformanceChartProps) => {
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const returns = payload[0].payload.returns;
      const returnsPercent = payload[0].payload.invested > 0 
        ? ((returns / payload[0].payload.invested) * 100).toFixed(2)
        : '0';
      
      return (
        <div className="bg-popover border border-border rounded-lg p-3 shadow-lg">
          <p className="text-sm font-semibold mb-2">{payload[0].payload.name}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-4 text-xs">
              <span style={{ color: entry.color }}>{entry.name}:</span>
              <span className="font-semibold">₹{entry.value.toLocaleString('en-IN')}</span>
            </div>
          ))}
          <div className="mt-2 pt-2 border-t border-border">
            <div className="flex items-center justify-between gap-4 text-xs">
              <span>Returns:</span>
              <span className={`font-semibold ${returns >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {returns >= 0 ? '+' : ''}{returnsPercent}%
              </span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <Card className="border-border/40 bg-card/50 backdrop-blur-sm">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-500/10">
              <BarChart3 className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <CardTitle>Investment Performance</CardTitle>
              <CardDescription>Compare invested vs current value</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {data.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis 
                  dataKey="name" 
                  className="text-xs"
                  stroke="currentColor"
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  className="text-xs"
                  stroke="currentColor"
                  tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend 
                  wrapperStyle={{ paddingTop: '20px' }}
                />
                <Bar 
                  dataKey="invested" 
                  fill="#94a3b8" 
                  name="Invested"
                  radius={[4, 4, 0, 0]}
                  animationDuration={800}
                />
                <Bar 
                  dataKey="currentValue" 
                  fill="#3b82f6" 
                  name="Current Value"
                  radius={[4, 4, 0, 0]}
                  animationDuration={800}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center">
              <div className="text-center space-y-2">
                <BarChart3 className="h-12 w-12 text-muted-foreground/50 mx-auto" />
                <p className="text-muted-foreground">No investment data available</p>
                <p className="text-xs text-muted-foreground">Add investments to track performance</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};
