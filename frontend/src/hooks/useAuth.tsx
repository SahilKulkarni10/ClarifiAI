/**
 * useAuth Hook
 * Custom React hook for managing authentication state
 */

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { authService, type UserProfile } from '@/services/auth.service';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user profile on mount if token exists
  useEffect(() => {
    const loadUser = async () => {
      if (authService.isAuthenticated()) {
        try {
          const profile = await authService.getProfile();
          setUser(profile);
        } catch (error) {
          console.error('Failed to load user profile:', error);
          authService.logout();
        }
      }
      setIsLoading(false);
    };

    loadUser();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await authService.login({ email, password });
      // Map response user to UserProfile format
      const userProfile: UserProfile = {
        id: response.user.user_id || response.user.id || '',
        email: response.user.email,
        name: response.user.name,
        created_at: response.user.created_at || new Date().toISOString(),
      };
      setUser(userProfile);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, name: string) => {
    setIsLoading(true);
    try {
      const response = await authService.register({ email, password, name });
      // Map response user to UserProfile format
      const userProfile: UserProfile = {
        id: response.user.user_id || response.user.id || '',
        email: response.user.email,
        name: response.user.name,
        created_at: response.user.created_at || new Date().toISOString(),
      };
      setUser(userProfile);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const refreshProfile = async () => {
    if (!authService.isAuthenticated()) return;
    
    try {
      const profile = await authService.getProfile();
      setUser(profile);
    } catch (error) {
      console.error('Failed to refresh profile:', error);
      logout();
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
