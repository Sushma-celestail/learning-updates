import axiosInstance from './axiosInstance';
import type { User } from '../types';

export const usersApi = {
  getUsers: async () => {
    const response = await axiosInstance.get<User[]>('/users/');
    return response.data;
  },
  createUser: async (userData: Partial<User>) => {
    const response = await axiosInstance.post<User>('/users/', userData);
    return response.data;
  },
  updateUser: async (id: number, userData: Partial<User>) => {
    const response = await axiosInstance.put<User>(`/users/${id}`, userData);
    return response.data;
  },
  patchUser: async (id: number, userData: Partial<User>) => {
    const response = await axiosInstance.patch<User>(`/users/${id}`, userData);
    return response.data;
  },
  deleteUser: async (id: number) => {
    await axiosInstance.delete(`/users/${id}`);
  },
};
