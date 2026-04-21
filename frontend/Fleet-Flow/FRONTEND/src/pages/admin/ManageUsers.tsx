import React, { useState, useRef, useEffect } from 'react';
import { UserPlus, Search, Mail, Shield, Building2, Edit, Trash2, MoreVertical, Users } from 'lucide-react';
import toast from 'react-hot-toast';
import { useUsers } from '../../hooks/useUsers';
import { useWarehouses } from '../../hooks/useWarehouses';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { UserForm } from '../../components/users/UserForm';
import { SkeletonTableRow } from '../../components/ui/LoadingSpinner';

const roleBadge: Record<string, 'primary' | 'success' | 'neutral' | 'warning'> = {
  Admin: 'primary', Manager: 'success', Clerk: 'warning', Driver: 'neutral',
};



const EmptyState: React.FC<{ isFiltered: boolean; onAdd: () => void }> = ({ isFiltered, onAdd }) => (
  <tr>
    <td colSpan={4}>
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="w-14 h-14 bg-slate-50 dark:bg-white/[0.03] rounded-2xl flex items-center justify-center mb-4 border border-slate-100 dark:border-white/[0.07]">
          {isFiltered ? <Search size={22} className="text-slate-300 dark:text-slate-600" /> : <Users size={22} className="text-slate-300 dark:text-slate-600" />}
        </div>
        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1">{isFiltered ? 'No users found' : 'No team members yet'}</h3>
        <p className="text-xs text-slate-400 dark:text-slate-500 max-w-xs leading-relaxed">{isFiltered ? 'Try a different search term.' : 'Add your first team member to get started.'}</p>
        {!isFiltered && <Button size="sm" className="mt-4 gap-2" onClick={onAdd}><UserPlus size={14} /> Add Member</Button>}
      </div>
    </td>
  </tr>
);

export const ManageUsers: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<number | null>(null);
  const [editingUser, setEditingUser] = useState<any | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeMenu, setActiveMenu] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { users, isLoading: usersLoading, createUser, updateUser, deleteUser } = useUsers();
  const { warehouses } = useWarehouses();

  const handleOpenModal = (user: any = null) => { setEditingUser(user); setIsModalOpen(true); };

  // const handleSubmit = async (data: any) => {
  //   setIsSubmitting(true);
  //   try {
  //     if (editingUser) { await updateUser(editingUser.id, data); toast.success('User updated successfully'); }
  //     else { await createUser(data); toast.success('Team member added'); }
  //     setIsModalOpen(false);
  //   } catch (err: any) { toast.error(err.response?.data?.detail || 'Something went wrong'); }
  //   finally { setIsSubmitting(false); }
  // };
  const handleSubmit = async (data: any) => {
  setIsSubmitting(true);
  try {
    if (data.role === 'Manager') {
      const alreadyManager = users.find(
        u =>  u.warehouse_id === data.warehouse_id && u.id !== editingUser?.id
      );

      if (alreadyManager) {
        toast.error('This warehouse already has a manager');
        setIsSubmitting(false);
        return;
      }
    }

    if (editingUser) {
      await updateUser(editingUser.id, data);
      toast.success('User updated successfully');
    } else {
      await createUser(data);
      toast.success('Team member added');
    }

    setIsModalOpen(false);

  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Something went wrong');
  } finally {
    setIsSubmitting(false);
  }
};

  const handleDeleteClick = (id: number) => { setUserToDelete(id); setIsDeleteOpen(true); };

  const confirmDelete = async () => {
    if (!userToDelete) return;
    setIsSubmitting(true);
    try { await deleteUser(userToDelete); toast.success('User removed'); setIsDeleteOpen(false); }
    catch { toast.error('Failed to delete user'); }
    finally { setIsSubmitting(false); setUserToDelete(null); }
  };

  const filteredUsers = users.filter(u =>
    u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900 dark:text-slate-100">Team Members</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Manage user accounts and role assignments</p>
        </div>
        <Button onClick={() => handleOpenModal()} size="md" className="gap-2"><UserPlus size={16} /> Add Member</Button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex items-center gap-3 px-4 h-11">
        <Search size={16} className="text-slate-400 flex-shrink-0" />
        <input type="text" placeholder="Search by name or email…" className="flex-1 text-sm bg-transparent focus:outline-none placeholder:text-slate-400 text-slate-700" value={searchTerm} onChange={e => setSearchTerm(e.target.value)} />
        {searchTerm && <button onClick={() => setSearchTerm('')} className="text-xs text-slate-400 hover:text-slate-600 font-medium transition-colors">Clear</button>}
      </div>

      <div className="w-full overflow-hidden rounded-2xl border border-slate-100 dark:border-white/[0.07] shadow-sm dark:shadow-black/30 bg-white dark:bg-[#13131A]">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-slate-50 dark:bg-white/[0.03] border-b border-slate-100 dark:border-white/[0.07]">
                <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Member</th>
                <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Role</th>
                <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Facility</th>
                <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-white/[0.07]">
              {usersLoading ? (
                Array.from({ length: 5 }).map((_, i) => <SkeletonTableRow key={i} />)
              ) : filteredUsers.length === 0 ? (
                <EmptyState isFiltered={searchTerm.length > 0} onAdd={() => handleOpenModal()} />
              ) : (
                filteredUsers.map(u => (
                  <tr key={u.id} className="border-t border-slate-100 dark:border-white/[0.07] hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-colors group">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-slate-100 dark:from-white/5 to-slate-200 dark:to-white/10 group-hover:from-indigo-100 dark:group-hover:from-violet-500/20 group-hover:to-indigo-200 dark:group-hover:to-violet-500/10 flex items-center justify-center font-semibold text-slate-500 dark:text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-violet-400 transition-all text-sm flex-shrink-0">
                          {u.name.charAt(0).toUpperCase()}
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">{u.name}</p>
                          <div className="flex items-center gap-1 text-slate-400 dark:text-slate-500 mt-0.5">
                            <Mail size={11} /><span className="text-xs truncate">{u.email}</span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        
                        <Shield size={13} className={u.role === 'Admin' ? 'text-indigo-600 dark:text-violet-400' : 'text-slate-300 dark:text-slate-600'} />
                        <Badge variant={roleBadge[u.role] ?? 'neutral'}>{u.role}</Badge>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                        <Building2 size={13} className="text-slate-300 dark:text-slate-600 flex-shrink-0" />

                        <span className="text-sm truncate">{warehouses.find(w => w.id === u.warehouse_id)?.name ?? 'All Facilities'}</span>
                        
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                          onClick={() => handleOpenModal(u)}
                          className="p-1.5 text-slate-400 hover:text-indigo-600 dark:hover:text-violet-400 hover:bg-indigo-50 dark:hover:bg-violet-500/10 rounded-lg transition-all"
                          title="Edit member"
                        >
                          <Edit size={15} />
                        </button>
                        <button 
                          onClick={() => handleDeleteClick(u.id)}
                          className="p-1.5 text-slate-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-400/10 rounded-lg transition-all"
                          title="Remove member"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {!usersLoading && filteredUsers.length > 0 && (
          <div className="px-6 py-3 border-t border-slate-100 dark:border-white/[0.07] bg-slate-50 dark:bg-white/[0.03]">
            <p className="text-xs text-slate-400 dark:text-slate-500">{filteredUsers.length} of {users.length} members</p>
          </div>
        )}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingUser ? 'Edit User' : 'Add Team Member'} subtitle={editingUser ? 'Update role and facility assignment.' : 'Create a new account and assign permissions.'}>
        <UserForm onSubmit={handleSubmit} initialData={editingUser ?? undefined} warehouses={warehouses} isLoading={isSubmitting} />
      </Modal>

      <ConfirmDialog isOpen={isDeleteOpen} onClose={() => setIsDeleteOpen(false)} onConfirm={confirmDelete} title="Delete User" message="This will permanently remove the user and revoke all access. This action cannot be undone." confirmLabel="Delete User" cancelLabel="Cancel" variant="danger" isLoading={isSubmitting} />
    </div>
  );
};
