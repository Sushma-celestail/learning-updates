import axiosInstance from './axiosInstance';
import type { Warehouse } from '../types';

export const warehousesApi = {
  getWarehouses: async () => {
    const response = await axiosInstance.get<Warehouse[]>('/warehouses/');
    return response.data;
  },
  createWarehouse: async (warehouse: Partial<Warehouse>) => {
    const response = await axiosInstance.post<Warehouse>('/warehouses/', warehouse);
    return response.data;
  },
  updateWarehouse: async (id: number, warehouse: Partial<Warehouse>) => {
    const response = await axiosInstance.put<Warehouse>(`/warehouses/${id}`, warehouse);
    return response.data;
  },
  patchWarehouse: async (id: number, warehouse: Partial<Warehouse>) => {
    const response = await axiosInstance.patch<Warehouse>(`/warehouses/${id}`, warehouse);
    return response.data;
  },
  deleteWarehouse: async (id: number) => {
    await axiosInstance.delete(`/warehouses/${id}`);
  },
};
