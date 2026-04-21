import React, { useState } from 'react';
import { Truck, MapPin, Plus, RefreshCcw, ArrowRight, PackageOpen, PlayCircle, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useShipments } from '../hooks/useShipments';
import { useWarehouses } from '../hooks/useWarehouses';
import { useUsers } from '../hooks/useUsers';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { ShipmentForm } from '../components/shipments/ShipmentForm';
import { Skeleton } from '../components/ui/LoadingSpinner';

const statusConfig = {
  Pending: { variant: 'warning' as const, icon: PackageOpen, iconBg: 'bg-amber-50 dark:bg-amber-400/10', iconText: 'text-amber-600 dark:text-amber-400' },
  'In Transit': { variant: 'info' as const, icon: Truck, iconBg: 'bg-blue-50 dark:bg-blue-400/10', iconText: 'text-blue-600 dark:text-blue-400' },
  Delivered: { variant: 'success' as const, icon: CheckCircle2, iconBg: 'bg-emerald-50 dark:bg-emerald-400/10', iconText: 'text-emerald-600 dark:text-emerald-400' },
};

const ShipmentSkeleton: React.FC = () => (
  <div className="bg-white dark:bg-[#13131A] rounded-2xl border border-slate-100 dark:border-white/[0.07] shadow-sm dark:shadow-black/30 p-5">
    <div className="flex items-center gap-4">
      <Skeleton className="w-12 h-12 rounded-xl flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="w-24 h-4" />
        <Skeleton className="w-16 h-5 rounded-full" />
      </div>
    </div>
  </div>
);

const EmptyState: React.FC<{ onAdd?: () => void }> = ({ onAdd }) => (
  <div className="flex flex-col items-center justify-center py-20 text-center">
    <div className="w-16 h-16 bg-slate-50 dark:bg-white/[0.03] rounded-2xl flex items-center justify-center mb-4 border border-slate-100 dark:border-white/[0.07]">
      <Truck size={26} className="text-slate-300 dark:text-slate-600" />
    </div>
    <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1">No shipments found</h3>
    <p className="text-xs text-slate-400 dark:text-slate-500 max-w-xs leading-relaxed">
      No shipments are assigned to your sector yet.
    </p>
    {onAdd && (
      <Button size="sm" className="mt-4 gap-2" onClick={onAdd}>
        <Plus size={14} /> Create Shipment
      </Button>
    )}
  </div>
);

export const ShipmentsPage: React.FC = () => {
  const { user } = useAuth();
  const { shipments, isLoading, refresh, createShipment, updateShipmentStatus } =
    useShipments(user?.role, user?.id, user?.warehouse_id);
  const { warehouses } = useWarehouses();
  const { users } = useUsers();

  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  // ✅ Get ALL drivers from users — ShipmentForm will filter by selected warehouse
  const allDrivers = (users || []).filter(
    u => u.role?.toLowerCase() === 'driver' && u.warehouse_id !== null
  );

  const hubName = (id: number) =>
    warehouses.find(w => w.id === id)?.name ?? `Hub #${id}`;

  const handleCreateSubmit = async (data: any) => {
    setIsSubmitting(true);
    try {
      await createShipment(data);
      setIsAddModalOpen(false);
    } catch (err) {
      console.error('Failed to create shipment', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStatusUpdate = async (id: number, status: string) => {
    setUpdatingId(id);
    try {
      await updateShipmentStatus(id, status);
    } catch (err) {
      console.error('Failed to update status', err);
    } finally {
      setUpdatingId(null);
    }
  };

  const pending = shipments.filter(s => s.status === 'Pending').length;
  const inTransit = shipments.filter(s => s.status === 'In Transit').length;
  const delivered = shipments.filter(s => s.status === 'Delivered').length;

  return (
    <div className="space-y-6">

      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900 dark:text-slate-100">Shipments</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Track and manage logistics across all hubs</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => refresh()}
            className="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/5 rounded-lg transition-all"
            title="Refresh"
          >
            <RefreshCcw size={17} className={isLoading ? 'animate-spin' : ''} />
          </button>
          {user?.role === 'Clerk' && (
            <Button onClick={() => setIsAddModalOpen(true)} size="md" className="gap-2">
              <Plus size={16} /> New Shipment
            </Button>
          )}
        </div>
      </div>

      {/* ── Summary Badges ── */}
      {!isLoading && shipments.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 dark:text-slate-400 bg-white dark:bg-[#13131A] border border-slate-200 dark:border-white/10 px-3 py-1.5 rounded-full shadow-sm dark:shadow-black/30">
            <Truck size={13} className="text-indigo-600 dark:text-violet-400" />{shipments.length} total
          </span>
          {pending > 0 && (
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-400/10 border border-amber-200 dark:border-amber-400/20 px-3 py-1.5 rounded-full">
              <PackageOpen size={13} /> {pending} pending
            </span>
          )}
          {inTransit > 0 && (
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-700 dark:text-blue-400 bg-blue-50 dark:bg-blue-400/10 border border-blue-200 dark:border-blue-400/20 px-3 py-1.5 rounded-full">
              <Truck size={13} /> {inTransit} in transit
            </span>
          )}
          {delivered > 0 && (
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-400/10 border border-emerald-200 dark:border-emerald-400/20 px-3 py-1.5 rounded-full">
              <CheckCircle2 size={13} /> {delivered} delivered
            </span>
          )}
        </div>
      )}

      {/* ── Shipment List ── */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => <ShipmentSkeleton key={i} />)}
        </div>
      ) : shipments.length === 0 ? (
        <EmptyState onAdd={user?.role === 'Clerk' ? () => setIsAddModalOpen(true) : undefined} />
      ) : (
        <div className="space-y-3">
          {shipments.map(shipment => {
            const cfg = statusConfig[shipment.status as keyof typeof statusConfig] ?? statusConfig.Pending;
            const Icon = cfg.icon;
            const isUpdating = updatingId === shipment.id;
            return (
              <div
                key={shipment.id}
                className="bg-white dark:bg-[#13131A] rounded-2xl border border-slate-100 dark:border-white/[0.07] shadow-sm dark:shadow-black/30 p-5 hover:shadow-md hover:border-slate-200 dark:hover:border-white/10 transition-all duration-200 group"
              >
                <div className="flex items-center gap-4 flex-wrap">
                  <div className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 ${cfg.iconBg} ${cfg.iconText}`}>
                    <Icon size={20} />
                  </div>
                  <div className="min-w-[120px]">
                    <p className="text-xs text-slate-400 dark:text-slate-500 font-medium mb-0.5">Shipment ID</p>
                    <p className="text-sm font-semibold text-slate-900 dark:text-slate-100 font-mono">
                      PF-{shipment.id.toString().padStart(4, '0')}
                    </p>
                    <Badge variant={cfg.variant} dot className="mt-1.5">{shipment.status}</Badge>
                  </div>
                  <div className="hidden md:flex items-center gap-3 flex-1 min-w-0">
                    <div className="min-w-0">
                      <p className="text-xs text-slate-400 dark:text-slate-500 font-medium mb-0.5 flex items-center gap-1">
                        <MapPin size={11} /> Origin
                      </p>
                      <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">
                        {hubName(shipment.source_warehouse_id)}
                      </p>
                    </div>
                    <ArrowRight size={16} className="text-slate-300 dark:text-slate-600 flex-shrink-0" />
                    <div className="min-w-0">
                      <p className="text-xs text-slate-400 dark:text-slate-500 font-medium mb-0.5 flex items-center gap-1">
                        <MapPin size={11} /> Destination
                      </p>
                      <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">
                        {hubName(shipment.destination_warehouse_id)}
                      </p>
                    </div>
                  </div>
                  <div className="ml-auto flex items-center gap-2 flex-shrink-0">
                    {user?.role === 'Driver' && shipment.driver_id === user.id && shipment.status !== 'Delivered' && (
                      <>
                        {shipment.status === 'Pending' && (
                          <Button size="sm" variant="primary" className="gap-1.5" isLoading={isUpdating} loadingText="Starting…" onClick={() => handleStatusUpdate(shipment.id, 'In Transit')}>
                            <PlayCircle size={14} /> Start Transit
                          </Button>
                        )}
                        {shipment.status === 'In Transit' && (
                          <Button size="sm" variant="success" className="gap-1.5" isLoading={isUpdating} loadingText="Confirming…" onClick={() => handleStatusUpdate(shipment.id, 'Delivered')}>
                            <CheckCircle2 size={14} /> Mark Delivered
                          </Button>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ── Create Shipment Modal ── */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Create Shipment"
        subtitle="Initialize a new transfer between hubs."
      >
        {/* ✅ Pass allDrivers — form filters by selected source warehouse automatically */}
        <ShipmentForm
          onSubmit={handleCreateSubmit}
          warehouses={warehouses}
          drivers={allDrivers}
          isLoading={isSubmitting}
        />
      </Modal>

    </div>
  );
};