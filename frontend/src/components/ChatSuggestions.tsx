import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  MessageSquare, 
  Sparkles, 
  TrendingUp,
  DollarSign,
  PiggyBank,
  Target,
  Shield,
  BookOpen,
  Zap
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

interface QuickPrompt {
  id: string;
  category: 'budget' | 'savings' | 'investment' | 'debt' | 'general';
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  prompt: string;
  color: string;
}

const quickPrompts: QuickPrompt[] = [
  {
    id: '1',
    category: 'budget',
    icon: DollarSign,
    title: 'Budget Analysis',
    description: 'Get insights on your spending patterns',
    prompt: 'Analyze my spending patterns and suggest a monthly budget breakdown',
    color: 'text-green-500'
  },
  {
    id: '2',
    category: 'savings',
    icon: PiggyBank,
    title: 'Savings Plan',
    description: 'Create a personalized savings strategy',
    prompt: 'Help me create a savings plan to save ₹5 lakhs in 12 months',
    color: 'text-blue-500'
  },
  {
    id: '3',
    category: 'investment',
    icon: TrendingUp,
    title: 'Investment Advice',
    description: 'Learn about investment options',
    prompt: 'What are the best investment options for a 30-year-old with moderate risk appetite?',
    color: 'text-purple-500'
  },
  {
    id: '4',
    category: 'debt',
    icon: Shield,
    title: 'Debt Management',
    description: 'Strategies to manage loans',
    prompt: 'What\'s the best strategy to pay off multiple loans efficiently?',
    color: 'text-orange-500'
  },
  {
    id: '5',
    category: 'general',
    icon: Target,
    title: 'Financial Goals',
    description: 'Set and achieve your goals',
    prompt: 'Help me plan for buying a house worth ₹80 lakhs in 5 years',
    color: 'text-pink-500'
  },
  {
    id: '6',
    category: 'general',
    icon: BookOpen,
    title: 'Financial Education',
    description: 'Learn financial concepts',
    prompt: 'Explain the concept of compound interest with examples',
    color: 'text-cyan-500'
  }
];

interface ChatSuggestionsProps {
  onPromptSelect?: (prompt: string) => void;
}

export function ChatSuggestions({ onPromptSelect }: ChatSuggestionsProps) {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const categories = [
    { value: 'all', label: 'All Topics' },
    { value: 'budget', label: 'Budget' },
    { value: 'savings', label: 'Savings' },
    { value: 'investment', label: 'Investment' },
    { value: 'debt', label: 'Debt' }
  ];

  const filteredPrompts = selectedCategory === 'all' 
    ? quickPrompts 
    : quickPrompts.filter(p => p.category === selectedCategory);

  const handlePromptClick = (prompt: string) => {
    if (onPromptSelect) {
      onPromptSelect(prompt);
    } else {
      // Navigate to chat with the prompt
      navigate('/chat', { state: { initialPrompt: prompt } });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-purple-500/5">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-2xl">
                <Sparkles className="h-6 w-6 text-primary" />
                Quick Start Prompts
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-2">
                Get started with these AI-powered financial assistance prompts
              </p>
            </div>
            <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
              <Zap className="h-3 w-3 mr-1" />
              Smart AI
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <Button
            key={cat.value}
            variant={selectedCategory === cat.value ? "default" : "outline"}
            size="sm"
            onClick={() => setSelectedCategory(cat.value)}
          >
            {cat.label}
          </Button>
        ))}
      </div>

      {/* Prompt Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredPrompts.map((prompt, index) => {
          const Icon = prompt.icon;
          
          return (
            <motion.div
              key={prompt.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card 
                className="h-full hover:shadow-lg transition-all cursor-pointer group border-border/40 hover:border-primary/30"
                onClick={() => handlePromptClick(prompt.prompt)}
              >
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-br from-background to-muted group-hover:scale-110 transition-transform`}>
                      <Icon className={`h-6 w-6 ${prompt.color}`} />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">
                        {prompt.title}
                      </h3>
                      <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                        {prompt.description}
                      </p>
                      <div className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4 text-muted-foreground" />
                        <p className="text-xs text-muted-foreground line-clamp-1">
                          {prompt.prompt}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Call to Action */}
      <Card className="bg-gradient-to-br from-primary/10 to-purple-500/10 border-primary/20">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-lg mb-1">Need Custom Advice?</h3>
              <p className="text-sm text-muted-foreground">
                Start a conversation with our AI assistant for personalized financial guidance
              </p>
            </div>
            <Button 
              size="lg"
              onClick={() => navigate('/chat')}
              className="gap-2"
            >
              <MessageSquare className="h-5 w-5" />
              Open Chat
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
