import { useState, useRef, useEffect } from 'react';
import { AppLayout } from '@/components/layouts/AppLayout';
import { chatService } from '@/services/chat.service';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  MessageSquare, 
  Send, 
  Bot,
  User,
  Sparkles,
  Loader2,
  Trash2,
  Pause,
  Play
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  isStreaming?: boolean;
}

// Local storage key for chat history
const CHAT_STORAGE_KEY = 'clarifi_chat_history';

// Function to format markdown-like text to clean HTML
const formatMessage = (text: string): JSX.Element => {
  // Remove asterisks and format properly
  let formatted = text;
  
  // Remove bold asterisks
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '$1');
  formatted = formatted.replace(/\*(.*?)\*/g, '$1');
  
  // Split into sections for better formatting
  const sections = formatted.split('\n\n');
  
  return (
    <div className="space-y-3">
      {sections.map((section, idx) => {
        // Check if it's a heading
        if (section.startsWith('**') && section.endsWith('**')) {
          const heading = section.replace(/\*\*/g, '');
          return <h3 key={idx} className="font-bold text-lg mt-4 mb-2">{heading}</h3>;
        }
        
        // Check if it's a list
        if (section.includes('*   ') || section.includes('* ')) {
          const items = section.split('\n').filter(line => line.trim().startsWith('*'));
          return (
            <ul key={idx} className="space-y-1.5 ml-4">
              {items.map((item, itemIdx) => {
                const cleaned = item.replace(/^\s*\*\s+/, '').replace(/\*\*/g, '');
                return (
                  <li key={itemIdx} className="flex gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span className="flex-1">{cleaned}</span>
                  </li>
                );
              })}
            </ul>
          );
        }
        
        // Regular paragraph
        if (section.trim()) {
          return <p key={idx} className="leading-relaxed">{section}</p>;
        }
        
        return null;
      })}
    </div>
  );
};

// Save messages to localStorage
const saveMessagesToStorage = (messages: Message[]) => {
  try {
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
  } catch (error) {
    console.error('Failed to save messages to storage:', error);
  }
};

// Load messages from localStorage
const loadMessagesFromStorage = (): Message[] => {
  try {
    const stored = localStorage.getItem(CHAT_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Failed to load messages from storage:', error);
  }
  return [];
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>(() => {
    const stored = loadMessagesFromStorage();
    if (stored.length > 0) {
      return stored;
    }
    return [
      {
        role: 'assistant',
        content: 'Hello! I\'m your AI financial assistant. I can help you understand your finances, answer questions about investments, loans, budgeting, and provide personalized financial advice. What would you like to know?',
        timestamp: new Date().toISOString()
      }
    ];
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [isStreamingPaused, setIsStreamingPaused] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const streamingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  // Save messages whenever they change
  useEffect(() => {
    if (messages.length > 1) { // Don't save if only the initial message
      saveMessagesToStorage(messages);
    }
  }, [messages]);

  // Cleanup streaming timeout on unmount
  useEffect(() => {
    return () => {
      if (streamingTimeoutRef.current) {
        clearTimeout(streamingTimeoutRef.current);
      }
    };
  }, []);

  // Streaming effect: Display message word by word
  const streamResponse = (fullText: string): Promise<void> => {
    return new Promise((resolve) => {
      setIsStreaming(true);
      const words = fullText.split(' ');
      let currentIndex = 0;
      let currentText = '';

      const streamWord = () => {
        if (isStreamingPaused) {
          // If paused, check again after a short delay
          streamingTimeoutRef.current = setTimeout(streamWord, 100);
          return;
        }

        if (currentIndex < words.length) {
          currentText += (currentIndex > 0 ? ' ' : '') + words[currentIndex];
          setStreamingMessage(currentText);
          currentIndex++;
          streamingTimeoutRef.current = setTimeout(streamWord, 50); // 50ms delay between words
        } else {
          setStreamingMessage('');
          setIsStreamingPaused(false);
          setIsStreaming(false);
          resolve();
        }
      };

      streamWord();
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    try {
      const response = await chatService.sendMessage(input);
      
      // Stream the response
      await streamResponse(response.response);
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp || new Date().toISOString()
      };
      
      setMessages([...updatedMessages, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    if (confirm('Are you sure you want to clear all chat history?')) {
      const initialMessage: Message = {
        role: 'assistant',
        content: 'Hello! I\'m your AI financial assistant. I can help you understand your finances, answer questions about investments, loans, budgeting, and provide personalized financial advice. What would you like to know?',
        timestamp: new Date().toISOString()
      };
      setMessages([initialMessage]);
      localStorage.removeItem(CHAT_STORAGE_KEY);
    }
  };

  const toggleStreamingPause = () => {
    setIsStreamingPaused(!isStreamingPaused);
  };

  const suggestions = [
    "How's my investment portfolio performing?",
    "What's my current savings rate?",
    "Help me create a budget plan",
    "Should I pay off my loans faster?",
    "Analyze my spending patterns"
  ];

  return (
    <AppLayout 
      title="AI Financial Assistant" 
      description="Get personalized financial advice powered by AI"
    >
      <div className="max-w-4xl mx-auto">
        <Card className="border-border/40 shadow-2xl min-h-[calc(100vh-16rem)]">
          <CardHeader className="border-b border-border/40 bg-gradient-to-r from-primary/5 via-background to-accent/5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-primary to-accent">
                  <Sparkles className="h-6 w-6 text-primary-foreground" />
                </div>
                <div>
                  <CardTitle className="text-2xl">Financial AI Assistant</CardTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    Ask me anything about your finances
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {isStreaming && (
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={toggleStreamingPause}
                    className="gap-2"
                  >
                    {isStreamingPaused ? (
                      <>
                        <Play className="h-4 w-4" />
                        Resume
                      </>
                    ) : (
                      <>
                        <Pause className="h-4 w-4" />
                        Pause
                      </>
                    )}
                  </Button>
                )}
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={clearChat}
                  className="gap-2"
                >
                  <Trash2 className="h-4 w-4" />
                  Clear Chat
                </Button>
              </div>
            </div>
          </CardHeader>

          <CardContent className="p-0">
            {/* Messages Container */}
            <div className="h-[calc(100vh-28rem)] overflow-y-auto p-6 space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={cn(
                    "flex gap-3 items-start",
                    message.role === 'user' ? 'flex-row-reverse' : ''
                  )}
                >
                  <div className={cn(
                    "p-2 rounded-lg shrink-0",
                    message.role === 'user' 
                      ? 'bg-primary/10' 
                      : 'bg-gradient-to-br from-primary/10 to-accent/10'
                  )}>
                    {message.role === 'user' ? (
                      <User className="h-5 w-5 text-primary" />
                    ) : (
                      <Bot className="h-5 w-5 text-primary" />
                    )}
                  </div>
                  <div className={cn(
                    "flex-1 max-w-[85%]",
                    message.role === 'user' ? 'flex justify-end' : ''
                  )}>
                    <div className={cn(
                      "rounded-2xl px-5 py-3 shadow-sm",
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground ml-auto'
                        : 'bg-muted'
                    )}>
                      <div className="text-sm leading-relaxed">
                        {message.role === 'assistant' ? (
                          formatMessage(message.content)
                        ) : (
                          <p>{message.content}</p>
                        )}
                      </div>
                      <p className={cn(
                        "text-xs mt-3 opacity-60",
                        message.role === 'user' ? 'text-right' : ''
                      )}>
                        {new Date(message.timestamp).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              ))}

              {/* Streaming Message */}
              {streamingMessage && (
                <div className="flex gap-3 items-start">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-primary/10 to-accent/10 shrink-0">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1 max-w-[85%]">
                    <div className="bg-muted rounded-2xl px-5 py-3 shadow-sm">
                      <div className="text-sm leading-relaxed">
                        {formatMessage(streamingMessage)}
                      </div>
                      <div className="mt-2 flex gap-1">
                        <div className="h-2 w-2 rounded-full bg-primary animate-pulse"></div>
                        <div className="h-2 w-2 rounded-full bg-primary animate-pulse delay-75"></div>
                        <div className="h-2 w-2 rounded-full bg-primary animate-pulse delay-150"></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Loading Indicator */}
              {loading && !streamingMessage && (
                <div className="flex gap-3 items-start">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-primary/10 to-accent/10">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                  <div className="bg-muted rounded-2xl px-5 py-3">
                    <div className="flex gap-2 items-center">
                      <Loader2 className="h-4 w-4 animate-spin text-primary" />
                      <span className="text-sm text-muted-foreground">Analyzing your finances...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Suggestions */}
            {messages.length === 1 && !loading && (
              <div className="px-6 pb-4 border-b border-border/40">
                <p className="text-sm text-muted-foreground mb-3 font-medium">Suggested questions:</p>
                <div className="flex flex-wrap gap-2">
                  {suggestions.map((suggestion, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      className="text-xs hover:bg-primary/5 hover:text-primary hover:border-primary/50"
                      onClick={() => setInput(suggestion)}
                    >
                      <Sparkles className="h-3 w-3 mr-1" />
                      {suggestion}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Input Form */}
            <div className="border-t border-border/40 p-4 bg-gradient-to-r from-background via-muted/20 to-background">
              <form onSubmit={handleSubmit} className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask me about your finances..."
                  className="flex-1 border-border/40 focus:ring-primary/20"
                  disabled={loading}
                />
                <Button 
                  type="submit" 
                  disabled={!input.trim() || loading}
                  className="gap-2 min-w-[100px]"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Sending
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4" />
                      Send
                    </>
                  )}
                </Button>
              </form>
              <p className="text-xs text-muted-foreground mt-2 text-center">
                AI responses are generated based on your financial data. Chat history is saved locally.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Quick Tips */}
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <Card className="border-border/40 hover:shadow-lg transition-all">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Tips for Better Answers
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-muted-foreground space-y-2">
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>Be specific about what you want to know</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>Mention timeframes (monthly, yearly, etc.)</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>Ask about specific categories or accounts</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-border/40 hover:shadow-lg transition-all">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                What I Can Help With
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-muted-foreground space-y-2">
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>Analyze spending and savings patterns</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>Investment advice and portfolio analysis</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">•</span>
                  <span>Budget planning and goal setting</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
