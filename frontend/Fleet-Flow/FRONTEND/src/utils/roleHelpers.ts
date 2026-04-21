import type { User } from '../types';

export const roleHelpers = {
  isAdmin: (user: User | null) => user?.role === 'Admin',
  isManager: (user: User | null) => user?.role === 'Manager',
  isClerk: (user: User | null) => user?.role === 'Clerk',
  isDriver: (user: User | null) => user?.role === 'Driver',
  
  canManageUsers: (user: User | null) => user?.role === 'Admin',
  canManageInventory: (user: User | null) => ['Admin', 'Manager', 'Clerk'].includes(user?.role || ''),
  canApproveInventory: (user: User | null) => user?.role === 'Manager' || user?.role === 'Admin',
  canCreateShipment: (user: User | null) => user?.role === 'Clerk' || user?.role === 'Admin',
};
