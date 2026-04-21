import React, { createContext, useState, useCallback, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import type { User, LoginCredentials } from '../types';
import { authApi } from '../api/auth.api';
import { tokenStorage } from '../utils/tokenStorage';

interface JWTPayload {
  user_id: number;
  role: string;
  warehouse_id: number | null;
  name: string;
  email: string;
  exp: number;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(tokenStorage.getUser());
  const [token, setToken] = useState<string | null>(tokenStorage.getToken());
  const [isLoading, setIsLoading] = useState(false);

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    try {
      let tokenValue = '';
      let userData: User | null = null;

      const { access_token } = await authApi.login(credentials);
      tokenValue = access_token;
      
      // Decode token to get user info
      const decoded = jwtDecode<JWTPayload>(tokenValue);
      userData = {
        id: decoded.user_id,
        name: decoded.name,
        email: decoded.email,
        role: decoded.role as any,
        warehouse_id: decoded.warehouse_id
      };

      if (tokenValue && userData) {
        setToken(tokenValue);
        tokenStorage.setToken(tokenValue);
        setUser(userData);
        tokenStorage.setUser(userData);
        return userData;
      }
    } catch (error) {
      console.error('Login failed', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    tokenStorage.clearAll();
    window.location.href = '/login';
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
