import { useState, useEffect, useCallback } from 'react';
import { warehousesApi } from '../api/warehouses.api';
import type { Warehouse } from '../types';

export const useWarehouses = () => {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWarehouses = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await warehousesApi.getWarehouses();
      setWarehouses(data);
    } catch (err: any) {
      console.warn('Backend offline or error, using fallback warehouses');
      setWarehouses([
        { id: 1, name: 'Warehouse Alpha', location: 'Bengaluru' },
        { id: 2, name: 'Warehouse Beta', location: 'Mumbai' },
      ]);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWarehouses();
  }, [fetchWarehouses]);

  const addWarehouse = async (warehouse: Partial<Warehouse>) => {
    try {
      const newWarehouse = await warehousesApi.createWarehouse(warehouse);
      setWarehouses(prev => [...prev, newWarehouse]);
      return newWarehouse;
    } catch (err: any) {
      console.error('Failed to create warehouse', err);
      throw err;
    }
  };

  const updateWarehouse = async (id: number, warehouse: Partial<Warehouse>) => {
    try {
      const updated = await warehousesApi.updateWarehouse(id, warehouse);
      setWarehouses(prev => prev.map(w => w.id === id ? updated : w));
      return updated;
    } catch (err: any) {
      console.error('Failed to update warehouse', err);
      throw err;
    }
  };

  const patchWarehouse = async (id: number, warehouse: Partial<Warehouse>) => {
    try {
      const updated = await warehousesApi.patchWarehouse(id, warehouse);
      setWarehouses(prev => prev.map(w => w.id === id ? updated : w));
      return updated;
    } catch (err: any) {
      console.error('Failed to patch warehouse', err);
      throw err;
    }
  };

  const deleteWarehouse = async (id: number) => {
    try {
      await warehousesApi.deleteWarehouse(id);
      setWarehouses(prev => prev.filter(w => w.id !== id));
    } catch (err: any) {
      console.error('Failed to delete warehouse', err);
      throw err;
    }
  };

  return { warehouses, isLoading, error, refresh: fetchWarehouses, addWarehouse, updateWarehouse, patchWarehouse, deleteWarehouse };
};
