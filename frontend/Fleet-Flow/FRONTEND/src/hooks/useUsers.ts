import { useState, useEffect, useCallback } from 'react';
import { usersApi } from '../api/users.api';
import type { User } from '../types';

export const useUsers = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await usersApi.getUsers();
      setUsers(data);
    } catch (err: any) {
      console.warn('Backend offline or error, using fallback users');
      setUsers([
        { id: 1, name: 'Super Admin', email: 'admin@gmail.com', role: 'Admin', warehouse_id: null },

      ]);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const createUser = async (userData: Partial<User>) => {
    try {
      const newUser = await usersApi.createUser(userData);
      setUsers(prev => [...prev, newUser]);
      return newUser;
    } catch (err: any) {
      console.error('Failed to create user', err);
      throw err;
    }
  };

  const updateUser = async (id: number, userData: Partial<User>) => {
    try {
      const updatedUser = await usersApi.updateUser(id, userData);
      setUsers(prev => prev.map(u => u.id === id ? updatedUser : u));
      return updatedUser;
    } catch (err: any) {
      console.error('Failed to update user', err);
      throw err;
    }
  };

  const patchUser = async (id: number, userData: Partial<User>) => {
    try {
      const updatedUser = await usersApi.patchUser(id, userData);
      setUsers(prev => prev.map(u => u.id === id ? updatedUser : u));
      return updatedUser;
    } catch (err: any) {
      console.error('Failed to patch user', err);
      throw err;
    }
  };

  const deleteUser = async (id: number) => {
    try {
      await usersApi.deleteUser(id);
      setUsers(prev => prev.filter(u => u.id !== id));
    } catch (err: any) {
      console.error('Failed to delete user', err);
      throw err;
    }
  };

  return { users, isLoading, error, refresh: fetchUsers, createUser, updateUser, patchUser, deleteUser };
};
