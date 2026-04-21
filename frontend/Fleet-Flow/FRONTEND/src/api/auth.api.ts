import axiosInstance from './axiosInstance';
import type { LoginCredentials, AuthResponse } from '../types';

export const authApi = {
  login: async (credentials: LoginCredentials) => {
    const response = await axiosInstance.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },
  forgotPassword: async (email: string) => {
    const response = await axiosInstance.post('/auth/forgot-password', { email });
    return response.data;
  },
  verifyOTP: async (email: string, otp: string) => {
    const response = await axiosInstance.post('/auth/verify-otp', { email, otp });
    return response.data;
  },
  resetPassword: async (data: any) => {
    const response = await axiosInstance.post('/auth/reset-password', data);
    return response.data;
  },
};
