// ─── User ───────────────────────────────────────────────────────────────────
export type UserRole = 'Admin' | 'Manager' | 'Clerk' | 'Driver';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  warehouse_id: number | null;
}

// ─── Auth ────────────────────────────────────────────────────────────────────
export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

// ─── Warehouse ───────────────────────────────────────────────────────────────
export interface Warehouse {
  id: number;
  name: string;
  location: string;
}

// ─── Inventory ───────────────────────────────────────────────────────────────
export interface InventoryItem {
  id: number;
  product_name: string;
  quantity: number;
  warehouse_id: number;
  is_approved: boolean;
}

export interface CreateInventoryRequest {
  product_name: string;
  quantity: number;
}

// ─── Shipments ───────────────────────────────────────────────────────────────
export type ShipmentStatus = 'Pending' | 'In Transit' | 'Delivered';

export interface Shipment {
  id: number;
  source_warehouse_id: number;
  destination_warehouse_id: number;
  driver_id: number;
  status: ShipmentStatus;
}

export interface CreateShipmentRequest {
  source_warehouse_id: number;
  destination_warehouse_id: number;
  driver_id: number;
}
