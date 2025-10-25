/**
 * Example Chat Component
 * Demonstrates how to use the chat service for AI interactions
 */

import { useState } from 'react';
import { chatService, type ChatMessage } from '@/services/chat.service';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export const ChatExample = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatService.sendMessage(input);
      
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>AI Financial Assistant</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Messages */}
          <div className="h-96 overflow-y-auto space-y-4 p-4 bg-muted rounded-lg">
            {messages.length === 0 ? (
              <p className="text-center text-muted-foreground">
                Start a conversation with your AI financial assistant
              </p>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-background border'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    {message.timestamp && (
                      <p className="text-xs opacity-70 mt-1">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </p>
                    )}
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-background border rounded-lg p-3">
                  <p className="text-sm">Thinking...</p>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask me anything about your finances..."
              disabled={loading}
            />
            <Button onClick={handleSend} disabled={loading}>
              Send
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
