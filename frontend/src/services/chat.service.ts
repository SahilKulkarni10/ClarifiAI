/**
 * Chat Service
 * Handles all AI chat-related API calls
 */

import { apiClient } from '@/lib/api-client';
import { API_ENDPOINTS } from '@/lib/api-config';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  response: string;
  timestamp: string;
}

export interface ChatHistory {
  messages: ChatMessage[];
}

class ChatService {
  /**
   * Send a chat message to the AI assistant
   */
  async sendMessage(message: string): Promise<ChatResponse> {
    return apiClient.post<ChatResponse>(API_ENDPOINTS.chat.message, {
      message,
    });
  }

  /**
   * Get chat history
   */
  async getHistory(): Promise<ChatHistory> {
    return apiClient.get<ChatHistory>(API_ENDPOINTS.chat.history);
  }

  /**
   * Clear chat history
   */
  async clearHistory(): Promise<void> {
    return apiClient.delete<void>(API_ENDPOINTS.chat.clear);
  }
}

export const chatService = new ChatService();
