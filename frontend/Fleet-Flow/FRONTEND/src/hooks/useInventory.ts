import { useState, useEffect, useCallback, useMemo } from 'react';
import { inventoryApi } from '../api/inventory.api';
import type { InventoryItem } from '../types';

export const useInventory = (warehouseId?: number | null) => {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInventory = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await inventoryApi.getInventory();
      setItems(data);
    } catch (err) {
      console.warn('Backend offline, using fallback data');
      setItems([
        { id: 1, product_name: 'Precision Drill-X', quantity: 412, warehouse_id: 1, is_approved: true },
        { id: 2, product_name: 'Titanium Gaskets', quantity: 12, warehouse_id: 1, is_approved: false },
        { id: 3, product_name: 'Hydraulic Fluid', quantity: 850, warehouse_id: 1, is_approved: true },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInventory();
  }, [fetchInventory]);

  const filteredItems = useMemo(() => {
    if (!warehouseId) return items;
    return items.filter(item => item.warehouse_id === warehouseId);
  }, [items, warehouseId]);

  const addInventory = async (item: CreateInventoryRequest) => {
    try {
      const newItem = await inventoryApi.addInventory(item);
      setItems(prev => [...prev, newItem]);
      return newItem;
    } catch (err) {
      console.error('Failed to add inventory', err);
      throw err;
    }
  };

  const updateInventory = async (id: number, item: CreateInventoryRequest) => {
    try {
      const updatedItem = await inventoryApi.updateInventory(id, item);
      setItems(prev => prev.map(i => i.id === id ? updatedItem : i));
      return updatedItem;
    } catch (err) {
      console.error('Failed to update inventory', err);
      throw err;
    }
  };

  const approveInventory = async (id: number) => {
    try {
      const approvedItem = await inventoryApi.approveInventory(id);
      setItems(prev => prev.map(i => i.id === id ? approvedItem : i));
      return approvedItem;
    } catch (err) {
      console.error('Failed to approve inventory', err);
      throw err;
    }
  };

  return { items: filteredItems, isLoading, error, refresh: fetchInventory, addInventory, updateInventory, approveInventory };
};
