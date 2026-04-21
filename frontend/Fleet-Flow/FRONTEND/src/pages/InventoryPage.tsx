import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Package, Plus, Search, CheckCircle, Edit,
  RefreshCcw, AlertTriangle, BoxSelect, Trash2, Eye
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useInventory } from '../hooks/useInventory';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { SkeletonTableRow } from '../components/ui/LoadingSpinner';
import { Modal } from '../components/ui/Modal';
import { InventoryForm } from '../components/inventory/InventoryForm';

const EmptyState: React.FC<{ onAdd?: () => void; isFiltered?: boolean }> = ({ onAdd, isFiltered }) => (
  <tr>
    <td colSpan={5}>
      <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
        <div className="w-14 h-14 bg-slate-50 dark:bg-white/[0.03] rounded-2xl flex items-center justify-center mb-4 border border-slate-100 dark:border-white/[0.07]">
          {isFiltered ? <Search size={22} className="text-slate-300 dark:text-slate-600" /> : <BoxSelect size={22} className="text-slate-300 dark:text-slate-600" />}
        </div>
        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1">
          {isFiltered ? 'No results found' : 'No inventory items yet'}
        </h3>
        <p className="text-xs text-slate-400 dark:text-slate-500 max-w-xs leading-relaxed">
          {isFiltered ? 'Try adjusting your search term or clearing the filter.' : 'Add your first inventory item to get started tracking stock levels.'}
        </p>
        {!isFiltered && onAdd && (
          <Button size="sm" className="mt-4 gap-2" onClick={onAdd}><Plus size={14} /> Add Item</Button>
        )}
      </div>
    </td>
  </tr>
);

export const InventoryPage: React.FC = () => {
  const { user } = useAuth();
  const { items, isLoading, refresh, addInventory, approveInventory } = useInventory(user?.warehouse_id);
  const [searchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [approvingId, setApprovingId] = useState<number | null>(null);

  const [filter, setFilter] = useState<'all' | 'pending'>((searchParams.get('filter') as any) || 'all');

  useEffect(() => {
    const f = searchParams.get('filter');
    if (f === 'pending') setFilter('pending');
  }, [searchParams]);

  const filteredItems = items
    .filter(item => item.product_name.toLowerCase().includes(searchTerm.toLowerCase()))
    .filter(item => filter === 'all' ? true : !item.is_approved);

  const handleAddSubmit = async (data: any) => {
    setIsSubmitting(true);
    try { await addInventory(data); setIsAddModalOpen(false); }
    catch (err) { console.error('Add failed', err); }
    finally { setIsSubmitting(false); }
  };

  const handleApprove = async (id: number) => {
    setApprovingId(id);
    try { await approveInventory(id); }
    catch (err) { console.error('Approval failed', err); }
    finally { setApprovingId(null); }
  };

  const pendingCount = items.filter(i => !i.is_approved).length;
  const lowStockCount = items.filter(i => i.quantity < 50).length;

  return (
    <div className="space-y-6">

      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900 dark:text-slate-100">Inventory</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Real-time stock monitoring and procurement control</p>
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
              <Plus size={16} /> Add Item
            </Button>
          )}
        </div>
      </div>

      {/* ── Summary Badges ── */}
      {!isLoading && items.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 dark:text-slate-400 bg-white dark:bg-[#13131A] border border-slate-200 dark:border-white/10 px-3 py-1.5 rounded-full shadow-sm dark:shadow-black/30">
            <Package size={13} className="text-indigo-600 dark:text-violet-400" />{items.length} total items
          </span>
          {pendingCount > 0 && (
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-400/10 border border-amber-200 dark:border-amber-400/20 px-3 py-1.5 rounded-full">
              <AlertTriangle size={13} />{pendingCount} pending approval
            </span>
          )}
          {lowStockCount > 0 && (
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-400/10 border border-red-200 dark:border-red-400/20 px-3 py-1.5 rounded-full">
              <AlertTriangle size={13} />{lowStockCount} low stock
            </span>
          )}
        </div>
      )}

      {/* ── Search + Filter ── */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        <div className="bg-white dark:bg-[#13131A] rounded-xl border border-slate-200 dark:border-white/10 shadow-sm dark:shadow-black/30 flex items-center gap-3 px-4 h-11 flex-1 w-full">
          <Search size={16} className="text-slate-400 dark:text-slate-500 flex-shrink-0" />
          {/* ✅ inline style forces black regardless of dark mode */}
          <input
            type="text"
            placeholder="Search by product name…"
            className="flex-1 text-sm bg-transparent focus:outline-none placeholder:text-slate-400"
            style={{ color: '#000000' }}
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="text-xs text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 font-medium transition-colors"
            >
              Clear
            </button>
          )}
        </div>

        <div className="flex bg-slate-100 dark:bg-white/5 p-1 rounded-xl">
          {[
            { id: 'all', label: 'All Stock' },
            { id: 'pending', label: `Pending (${pendingCount})` }
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setFilter(t.id as any)}
              className={`px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${filter === t.id
                  ? 'bg-white dark:bg-white/10 text-indigo-600 dark:text-violet-400 shadow-sm'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Table ── */}
      <div className="w-full overflow-hidden rounded-2xl border border-slate-100 dark:border-white/[0.07] shadow-sm dark:shadow-black/30 bg-white dark:bg-[#13131A]">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-slate-50 dark:bg-white/[0.03] border-b border-slate-100 dark:border-white/[0.07]">
                <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Product</th>
                <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-right">Stock</th>
                {(user?.role === 'Manager' || user?.role === 'Clerk') && (
                  <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-right">Actions</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-white/[0.07]">
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => <SkeletonTableRow key={i} />)
              ) : filteredItems.length === 0 ? (
                <EmptyState
                  isFiltered={searchTerm.length > 0}
                  onAdd={user?.role === 'Clerk' ? () => setIsAddModalOpen(true) : undefined}
                />
              ) : (
                filteredItems.map(item => (
                  <tr key={item.id} className="border-t border-slate-100 dark:border-white/[0.07] hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-colors group">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 bg-slate-100 dark:bg-white/5 rounded-xl flex items-center justify-center text-slate-400 dark:text-slate-500 group-hover:bg-indigo-50 dark:group-hover:bg-violet-500/10 group-hover:text-indigo-600 dark:group-hover:text-violet-400 transition-colors flex-shrink-0">
                          <Package size={17} />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">{item.product_name}</p>
                          <p className="text-xs text-slate-400 dark:text-slate-500 font-mono">SKU-{item.id.toString().padStart(4, '0')}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={item.is_approved ? 'success' : 'warning'} dot>
                        {item.is_approved ? 'Approved' : 'Pending'}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={`text-sm font-semibold ${item.quantity < 50 ? 'text-red-500 dark:text-red-400' : 'text-slate-900 dark:text-slate-100'}`}>
                        {item.quantity.toLocaleString()}
                      </span>
                      <span className="text-xs text-slate-400 dark:text-slate-500 ml-1">units</span>
                      {item.quantity < 50 && (
                        <div className="flex items-center justify-end gap-1 mt-0.5">
                          <AlertTriangle size={11} className="text-red-500 dark:text-red-400" />
                          <span className="text-xs text-red-500 dark:text-red-400 font-medium">Low stock</span>
                        </div>
                      )}
                    </td>
                    {(user?.role === 'Manager' || user?.role === 'Clerk') && (
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {user?.role === 'Manager' && !item.is_approved && (
                            <Button
                              variant="success"
                              size="sm"
                              onClick={() => handleApprove(item.id)}
                              isLoading={approvingId === item.id}
                              loadingText="Approving…"
                              className="gap-1.5 h-8"
                            >
                              <CheckCircle size={14} /> Approve
                            </Button>
                          )}
                          {user?.role === 'Clerk' && (
                            <button
                              title="Edit Item"
                              className="p-1.5 text-slate-400 dark:text-slate-500 hover:text-indigo-600 dark:hover:text-violet-400 hover:bg-indigo-50 dark:hover:bg-violet-500/10 rounded-lg transition-all"
                            >
                              <Edit size={15} />
                            </button>
                          )}
                        </div>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {!isLoading && filteredItems.length > 0 && (
          <div className="px-6 py-3 border-t border-slate-100 dark:border-white/[0.07] bg-slate-50 dark:bg-white/[0.03] flex items-center justify-between">
            <p className="text-xs text-slate-400 dark:text-slate-500">Showing {filteredItems.length} of {items.length} items</p>
          </div>
        )}
      </div>

      {/* ── Add Modal ── */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add Inventory Item"
        subtitle="Register a new batch. Requires manager approval."
      >
        <InventoryForm onSubmit={handleAddSubmit} isLoading={isSubmitting} />
      </Modal>

    </div>
  );
};