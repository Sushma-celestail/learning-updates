import axiosInstance from './axiosInstance';
import type { Shipment, CreateShipmentRequest, ShipmentStatus } from '../types';

export const shipmentsApi = {
  getShipments: async () => {
    const response = await axiosInstance.get<Shipment[]>('/shipments/');
    return response.data;
  },
  createShipment: async (shipment: CreateShipmentRequest) => {
    const response = await axiosInstance.post<Shipment>('/shipments/', shipment);
    return response.data;
  },
  updateStatus: async (id: number, status: ShipmentStatus) => {
    const response = await axiosInstance.patch<Shipment>(`/shipments/${id}/status`, { status });
    return response.data;
  },
};
