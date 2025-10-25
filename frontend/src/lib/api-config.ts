/**
 * API Configuration
 * Centralized configuration for API endpoints and base URL
 */

// Determine the API base URL based on environment
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API endpoints
export const API_ENDPOINTS = {
  // Authentication
  auth: {
    register: '/auth/register',
    login: '/auth/login',
    profile: '/auth/profile',
    updateProfile: '/auth/profile',
  },
  // Finance
  finance: {
    income: '/finance/income',
    expense: '/finance/expenses',
    investment: '/finance/investments',
    loan: '/finance/loans',
    insurance: '/finance/insurance',
    goal: '/finance/goals',
    dashboard: '/finance/dashboard',
  },
  // Chat
  chat: {
    message: '/chat/message',
    history: '/chat/history',
    clear: '/chat/clear',
  },
  // Analytics
  analytics: {
    overview: '/analytics/overview',
    trends: '/analytics/trends',
    reports: '/analytics/reports',
  },
} as const;

// Helper function to build full API URL
export const buildApiUrl = (endpoint: string): string => {
  return `${API_BASE_URL}${endpoint}`;
};
