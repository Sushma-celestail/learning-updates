import axiosInstance from './axiosInstance';
import type { InventoryItem, CreateInventoryRequest } from '../types';

export const inventoryApi = {
  getInventory: async () => {
    const response = await axiosInstance.get<InventoryItem[]>('/inventory/');
    return response.data;
  },
  addInventory: async (item: CreateInventoryRequest) => {
    const response = await axiosInstance.post<InventoryItem>('/inventory/', item);
    return response.data;
  },
  updateInventory: async (id: number, item: CreateInventoryRequest) => {
    const response = await axiosInstance.put<InventoryItem>(`/inventory/${id}`, item);
    return response.data;
  },
  approveInventory: async (id: number) => {
    const response = await axiosInstance.patch<InventoryItem>(`/inventory/approve/${id}`);
    return response.data;
  },
};
