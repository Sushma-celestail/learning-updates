import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from '../components/layout/Layout';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import { LandingPage } from '../pages/LandingPage';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import { ManageUsers } from '../pages/admin/ManageUsers';
import { ManageWarehouses } from '../pages/admin/ManageWarehouses';
import { InventoryPage } from '../pages/InventoryPage';
import { ShipmentsPage } from '../pages/ShipmentsPage';

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      
      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Layout><DashboardPage /></Layout>} />
        <Route path="/inventory" element={<Layout><InventoryPage /></Layout>} />
        <Route path="/shipments" element={<Layout><ShipmentsPage /></Layout>} />
        
        {/* Admin only routes */}
        <Route element={<ProtectedRoute allowedRoles={['Admin']} />}>
          <Route path="/admin/users" element={<Layout><ManageUsers /></Layout>} />
          <Route path="/admin/warehouses" element={<Layout><ManageWarehouses /></Layout>} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};
