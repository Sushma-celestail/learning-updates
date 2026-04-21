import React, { useState } from 'react';
import { Building2, Plus, MapPin, Edit, Trash2, Package, Hash, Activity, Warehouse } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../../hooks/useAuth';
import { useWarehouses } from '../../hooks/useWarehouses';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { Skeleton } from '../../components/ui/LoadingSpinner';

const WarehouseSkeleton: React.FC = () => (
  <div className="bg-white dark:bg-[#13131A] rounded-2xl border border-slate-100 dark:border-white/[0.07] shadow-sm dark:shadow-black/30 p-5 space-y-4">
    <div className="flex items-start justify-between">
      <Skeleton className="w-11 h-11 rounded-xl" />
      <div className="flex gap-2"><Skeleton className="w-8 h-8 rounded-lg" /><Skeleton className="w-8 h-8 rounded-lg" /></div>
    </div>
    <div className="space-y-2"><Skeleton className="w-40 h-5" /><Skeleton className="w-28 h-4" /></div>
    <div className="grid grid-cols-2 gap-3"><Skeleton className="h-16 rounded-xl" /><Skeleton className="h-16 rounded-xl" /></div>
    <Skeleton className="h-9 rounded-lg" />
  </div>
);

const EmptyState: React.FC<{ onAdd: () => void }> = ({ onAdd }) => (
  <div className="col-span-full flex flex-col items-center justify-center py-20 text-center">
    <div className="w-16 h-16 bg-slate-50 dark:bg-white/[0.03] rounded-2xl flex items-center justify-center mb-4 border border-slate-100 dark:border-white/[0.07]">
      <Warehouse size={26} className="text-slate-300 dark:text-slate-600" />
    </div>
    <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1">No warehouses yet</h3>
    <p className="text-xs text-slate-400 dark:text-slate-500 max-w-xs leading-relaxed">Register your first distribution facility to start managing inventory and shipments.</p>
    <Button size="sm" className="mt-4 gap-2" onClick={onAdd}><Plus size={14} /> Add Warehouse</Button>
  </div>
);

export const ManageWarehouses: React.FC = () => {
  const { user } = useAuth();
  const { warehouses, isLoading, addWarehouse, updateWarehouse, deleteWarehouse } = useWarehouses();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [hubToDelete, setHubToDelete] = useState<number | null>(null);
  const [editingWarehouse, setEditingWarehouse] = useState<any | null>(null);
  const [formData, setFormData] = useState({ name: '', location: '' });
  const [formErrors, setFormErrors] = useState({ name: '', location: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleOpenModal = (warehouse: any = null) => {
    if (warehouse) { setEditingWarehouse(warehouse); setFormData({ name: warehouse.name, location: warehouse.location }); }
    else { setEditingWarehouse(null); setFormData({ name: '', location: '' }); }
    setFormErrors({ name: '', location: '' });
    setIsModalOpen(true);
  };

const validate = () => {
  const errors = { name: '', location: '' };

  const nameTrim = formData.name.trim().toLowerCase();
  const locationTrim = formData.location.trim().toLowerCase();

  if (!nameTrim) {
    errors.name = 'Facility name is required';
  }

  if (!locationTrim) {
    errors.location = 'Location is required';
  }


  const duplicateName = warehouses.some(w => 
    w.name.toLowerCase() === nameTrim &&
    (!editingWarehouse || w.id !== editingWarehouse.id)
  );

  const duplicateLocation = warehouses.some(w => 
    w.location.toLowerCase() === locationTrim &&
    (!editingWarehouse || w.id !== editingWarehouse.id)
  );

  if (duplicateName) {
    errors.name = 'Warehouse name already exists';
  }

  if (duplicateLocation) {
    errors.location = 'Warehouse location already exists';
  }

  setFormErrors(errors);

  return !errors.name && !errors.location;
};
  
  const handleSubmit = async () => {
    if (!validate()) return;
    setIsSubmitting(true);
    
    try {
      if (editingWarehouse) { await updateWarehouse(editingWarehouse.id, formData); toast.success('Warehouse updated'); }
      else { await addWarehouse(formData); toast.success('Warehouse added'); }
      setIsModalOpen(false);
      setFormData({ name: '', location: '' });
    } catch { toast.error('Something went wrong. Please try again.'); }
    finally { setIsSubmitting(false); }
  };

  const handleDeleteClick = (id: number) => { setHubToDelete(id); setIsDeleteOpen(true); };

  const confirmDelete = async () => {
    if (!hubToDelete) return;
    setIsSubmitting(true);
    try { await deleteWarehouse(hubToDelete); toast.success('Warehouse removed'); setIsDeleteOpen(false); }
    catch { toast.error('Failed to delete warehouse'); }
    finally { setIsSubmitting(false); setHubToDelete(null); }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900 dark:text-slate-100">Warehouses</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Manage distribution facilities and locations</p>
        </div>
        {user?.role === 'Admin' && <Button onClick={() => handleOpenModal()} size="md" className="gap-2"><Plus size={16} /> Add Warehouse</Button>}
      </div>

      {!isLoading && warehouses.length > 0 && (
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 dark:text-slate-400 bg-white dark:bg-[#13131A] border border-slate-200 dark:border-white/10 px-3 py-1.5 rounded-full shadow-sm dark:shadow-black/30">
            <Building2 size={13} className="text-indigo-600 dark:text-violet-400" />
            {warehouses.length} {warehouses.length === 1 ? 'facility' : 'facilities'}
          </span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => <WarehouseSkeleton key={i} />)
        ) : warehouses.length === 0 ? (
          <EmptyState onAdd={() => handleOpenModal()} />
        ) : (
          warehouses.map(hub => (
            <div key={hub.id} className="bg-white dark:bg-[#13131A] rounded-2xl border border-slate-100 dark:border-white/[0.07] shadow-sm dark:shadow-black/30 p-5 hover:shadow-md hover:border-slate-200 dark:hover:border-white/10 transition-all duration-200 group">
              <div className="flex items-start justify-between mb-4">
                <div className="w-11 h-11 bg-indigo-50 dark:bg-violet-500/10 text-indigo-600 dark:text-violet-400 rounded-xl flex items-center justify-center group-hover:bg-indigo-600 dark:group-hover:bg-violet-500 group-hover:text-white transition-all duration-200">
                  <Building2 size={20} />
                </div>
                <div className="flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => handleOpenModal(hub)} className="p-1.5 text-slate-400 dark:text-slate-500 hover:text-indigo-600 dark:hover:text-violet-400 hover:bg-indigo-50 dark:hover:bg-violet-500/10 rounded-lg transition-all" title="Edit"><Edit size={15} /></button>
                  <button onClick={() => handleDeleteClick(hub.id)} className="p-1.5 text-slate-400 dark:text-slate-500 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-400/10 rounded-lg transition-all" title="Delete"><Trash2 size={15} /></button>
                </div>
              </div>
              <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100 mb-1 truncate">{hub.name}</h3>
              <div className="flex items-center gap-1.5 text-slate-400 dark:text-slate-500 mb-4">
                <MapPin size={13} className="flex-shrink-0" /><span className="text-sm truncate">{hub.location}</span>
              </div>
              <div className="grid grid-cols-2 gap-2 mb-4">
                <div className="p-3 bg-slate-50 dark:bg-white/[0.03] rounded-xl border border-slate-100 dark:border-white/[0.07]">
                  <div className="flex items-center gap-1.5 text-slate-400 dark:text-slate-500 mb-1"><Package size={12} /><span className="text-xs font-medium">Type</span></div>
                  <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">Regional</p>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-white/[0.03] rounded-xl border border-slate-100 dark:border-white/[0.07]">
                  <div className="flex items-center gap-1.5 text-slate-400 dark:text-slate-500 mb-1"><Hash size={12} /><span className="text-xs font-medium">Code</span></div>
                  <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 font-mono">#{hub.id}</p>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <Badge variant="success" dot>Active</Badge>
                <button className="p-1.5 text-slate-300 dark:text-slate-600 hover:text-indigo-600 dark:hover:text-violet-400 hover:bg-indigo-50 dark:hover:bg-violet-500/10 rounded-lg transition-all"><Activity size={15} /></button>
              </div>
            </div>
          ))
        )}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingWarehouse ? 'Edit Warehouse' : 'Add Warehouse'} subtitle={editingWarehouse ? 'Update facility details.' : 'Register a new distribution facility.'}>
        <div className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Facility name <span className="text-red-500 dark:text-red-400">*</span></label>
            <input
              value={formData.name}
              onChange={e => { setFormData(d => ({ ...d, name: e.target.value })); if (formErrors.name) setFormErrors(err => ({ ...err, name: '' })); }}
              className={`w-full h-10 px-3 text-sm border rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 transition-all duration-150 placeholder:text-slate-400 ${formErrors.name ? 'border-red-500 focus:ring-red-100' : 'border-slate-200 focus:ring-indigo-100 focus:border-indigo-400'}`}
              placeholder="e.g. Northern Distribution Center"
            />
            {formErrors.name && <p className="text-xs text-red-500 dark:text-red-400 font-medium">{formErrors.name}</p>}
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Location <span className="text-red-500 dark:text-red-400">*</span></label>
            <div className="relative">
              <MapPin size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 pointer-events-none" />
              <input
                value={formData.location}
                onChange={e => { setFormData(d => ({ ...d, location: e.target.value })); if (formErrors.location) setFormErrors(err => ({ ...err, location: '' })); }}
                className={`w-full h-10 pl-9 pr-3 text-sm border rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 transition-all duration-150 placeholder:text-slate-400 ${formErrors.location ? 'border-red-500 focus:ring-red-100' : 'border-slate-200 focus:ring-indigo-100 focus:border-indigo-400'}`}
                placeholder="e.g. Bengaluru, Karnataka"
              />
            </div>
            {formErrors.location && <p className="text-xs text-red-500 dark:text-red-400 font-medium">{formErrors.location}</p>}
          </div>
        </div>
        <div className="flex gap-3 mt-6 pt-5 border-t border-slate-100 dark:border-white/[0.07]">
          <Button variant="secondary" className="flex-1" onClick={() => setIsModalOpen(false)}>Cancel</Button>
          <Button className="flex-1" onClick={handleSubmit} isLoading={isSubmitting} loadingText={editingWarehouse ? 'Saving…' : 'Adding…'} disabled={!formData.name.trim() || !formData.location.trim()}>
            {editingWarehouse ? 'Save Changes' : 'Add Warehouse'}
          </Button>
        </div>
      </Modal>

      <ConfirmDialog isOpen={isDeleteOpen} onClose={() => setIsDeleteOpen(false)} onConfirm={confirmDelete} title="Delete Warehouse" message="This will permanently remove the facility and may affect active shipments and inventory. This cannot be undone." confirmLabel="Delete Warehouse" cancelLabel="Cancel" variant="danger" isLoading={isSubmitting} />
    </div>
  );
};
