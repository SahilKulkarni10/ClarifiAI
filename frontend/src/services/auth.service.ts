/**
 * Authentication Service
 * Handles all authentication-related API calls
 */

import { apiClient } from '@/lib/api-client';
import { API_ENDPOINTS } from '@/lib/api-config';

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id?: string;
    user_id?: string;
    email: string;
    name: string;
    created_at?: string;
  };
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

class AuthService {
  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      API_ENDPOINTS.auth.register,
      data
    );
    
    // Store the token
    if (response.access_token) {
      localStorage.setItem('auth_token', response.access_token);
    }
    
    return response;
  }

  /**
   * Login user
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>(
        API_ENDPOINTS.auth.login,
        {
          email: data.email,
          password: data.password,
        }
      );
      
      // Store the token
      if (response.access_token) {
        localStorage.setItem('auth_token', response.access_token);
      }
      
      return response;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Login failed');
    }
  }

  /**
   * Get user profile
   */
  async getProfile(): Promise<UserProfile> {
    return apiClient.get<UserProfile>(API_ENDPOINTS.auth.profile);
  }

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    return apiClient.put<UserProfile>(API_ENDPOINTS.auth.updateProfile, data);
  }

  /**
   * Logout user
   */
  logout(): void {
    localStorage.removeItem('auth_token');
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }

  /**
   * Get auth token
   */
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }
}

export const authService = new AuthService();
