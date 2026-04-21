import { useState, useEffect, useCallback, useMemo } from 'react';
import { shipmentsApi } from '../api/shipments.api';
import type { Shipment, CreateShipmentRequest, ShipmentStatus } from '../types';

export const useShipments = (userRole?: string, userId?: number, warehouseId?: number | null) => {
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchShipments = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await shipmentsApi.getShipments();
      setShipments(data);
    } catch (err: any) {
      console.warn('Backend offline or error, using fallback shipments');
      setShipments([
        { id: 1, source_warehouse_id: 1, destination_warehouse_id: 2, driver_id: 4, status: 'Pending' },
        { id: 2, source_warehouse_id: 2, destination_warehouse_id: 1, driver_id: 4, status: 'In Transit' },
      ]);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchShipments();
  }, [fetchShipments]);

  const filteredShipments = useMemo(() => {
    if (userRole === 'Admin') return shipments;
    if (userRole === 'Driver') return shipments.filter(s => s.driver_id === userId);
    if (userRole === 'Manager' || userRole === 'Clerk') {
      return shipments.filter(s => s.source_warehouse_id === warehouseId || s.destination_warehouse_id === warehouseId);
    }
    return shipments;
  }, [shipments, userRole, userId, warehouseId]);

  const createShipment = async (data: CreateShipmentRequest) => {
    try {
      const newShipment = await shipmentsApi.createShipment(data);
      setShipments(prev => [...prev, newShipment]);
      return newShipment;
    } catch (err) {
      console.error('Failed to create shipment', err);
      throw err;
    }
  };

  const updateShipmentStatus = async (id: number, status: ShipmentStatus) => {
    try {
      const updatedShipment = await shipmentsApi.updateStatus(id, status);
      setShipments(prev => prev.map(s => s.id === id ? updatedShipment : s));
      return updatedShipment;
    } catch (err) {
      console.error('Failed to update shipment status', err);
      throw err;
    }
  };

  return { 
    shipments: filteredShipments, 
    allShipments: shipments,
    isLoading, 
    error, 
    refresh: fetchShipments, 
    createShipment, 
    updateShipmentStatus 
  };
};
