import React, { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Package, Truck, Users,
  Building2, LogOut, Menu, X, ChevronRight,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../../hooks/useAuth';
import { cn } from '../ui/Button';

const roleBadgeColor: Record<string, string> = {
  Admin: 'bg-indigo-500/20 dark:bg-violet-500/20 text-indigo-300 dark:text-violet-300 border border-indigo-500/30 dark:border-violet-500/30',
  Manager: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
  Clerk: 'bg-amber-500/20  text-amber-300  border border-amber-500/30',
  Driver: 'bg-blue-500/20   text-blue-300   border border-blue-500/30',
};

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => { setMobileOpen(false); }, [location.pathname]);
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') setMobileOpen(false); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const menuItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, roles: ['Admin', 'Manager', 'Clerk', 'Driver'] },
    { name: 'Inventory', path: '/inventory', icon: Package, roles: ['Admin', 'Manager', 'Clerk'] },
    { name: 'Shipments', path: '/shipments', icon: Truck, roles: ['Admin', 'Manager', 'Clerk', 'Driver'] },
    { name: 'Users', path: '/admin/users', icon: Users, roles: ['Admin'] },
    { name: 'Warehouses', path: '/admin/warehouses', icon: Building2, roles: ['Admin'] },
  ];

  const allowedItems = menuItems.filter(i => i.roles.includes(user?.role || ''));

  const SidebarContent = () => (
    <div className="flex flex-col h-full">

      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-100 dark:border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-600 dark:bg-violet-500 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-600/20 dark:shadow-violet-500/20 flex-shrink-0">
            <Building2 className="text-white" size={20} />
          </div>
          <div className="min-w-0">
            <h1 className="font-bold text-slate-900 dark:text-white text-base leading-tight tracking-tight truncate">
              Precision <span className="text-indigo-600 dark:text-violet-400">Flow</span>
            </h1>
            <p className="text-[10px] text-slate-400 dark:text-slate-500 font-bold tracking-widest uppercase truncate mt-0.5">
              Operations Hub
            </p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto custom-scrollbar">
        <p className="text-[10px] font-black text-slate-400 dark:text-slate-600 uppercase tracking-[0.2em] px-3 mb-4">
          Core Engine
        </p>
        {allowedItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => cn(
              'flex items-center justify-between px-4 py-3 rounded-2xl transition-all duration-200 group relative',
              isActive
                ? 'bg-indigo-50 dark:bg-violet-500/10 text-indigo-700 dark:text-violet-300 font-bold'
                : 'text-slate-500 dark:text-slate-500 hover:bg-slate-50 dark:hover:bg-white/[0.03] hover:text-slate-900 dark:hover:text-slate-200',
            )}
          >
            {({ isActive }) => (
              <>
                <div className="flex items-center gap-3.5 relative z-10">
                  <item.icon
                    size={18}
                    className={cn(
                      'flex-shrink-0 transition-colors',
                      isActive ? 'text-indigo-600 dark:text-violet-400' : 'text-slate-400 dark:text-slate-600 group-hover:text-slate-600 dark:group-hover:text-slate-400',
                    )}
                  />
                  <span className="text-sm">{item.name}</span>
                </div>
                {isActive && (
                   <motion.div layoutId="nav-active" className="absolute left-0 w-1 h-6 bg-indigo-600 dark:bg-violet-500 rounded-r-full" />
                )}
                {isActive && <ChevronRight size={14} className="text-indigo-600/40 dark:text-violet-400/40" />}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User / Logout */}
      <div className="px-4 py-6 border-t border-slate-100 dark:border-white/5 space-y-4">
        <div className="px-4 py-4 rounded-3xl bg-slate-50 dark:bg-white/[0.02] border border-slate-100 dark:border-white/5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 flex items-center justify-center text-indigo-600 dark:text-violet-300 font-bold text-sm shadow-sm">
            {user?.name?.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-bold text-slate-900 dark:text-white truncate leading-none">{user?.name}</p>
            <p className="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider mt-1">{user?.role}</p>
          </div>
        </div>

        <button
          onClick={logout}
          className="w-full h-12 flex items-center justify-center gap-3 px-4 text-slate-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-400/10 rounded-2xl transition-all duration-200 font-bold text-sm group"
        >
          <LogOut size={18} className="group-hover:translate-x-0.5 transition-transform" />
          <span>Authorize Logout</span>
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setMobileOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white dark:bg-[#030305] text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-white/10 rounded-xl shadow-xl"
        aria-label="Open menu"
      >
        <Menu size={20} />
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-slate-950/20 dark:bg-black/60 backdrop-blur-sm z-40"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile drawer */}
      <aside className={cn(
        'lg:hidden fixed left-0 top-0 h-screen w-72 bg-white dark:bg-[#030305] border-r border-slate-100 dark:border-white/5 z-50 transition-transform duration-300 ease-out',
        mobileOpen ? 'translate-x-0' : '-translate-x-full',
      )}>
        <button
          onClick={() => setMobileOpen(false)}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 dark:hover:text-white transition-colors"
        >
          <X size={20} />
        </button>
        <SidebarContent />
      </aside>

      {/* Desktop sidebar */}
      <aside className="hidden lg:flex fixed left-0 top-0 h-screen w-64 bg-white dark:bg-[#030305] border-r border-slate-100 dark:border-white/5 flex-col z-40">
        <SidebarContent />
      </aside>
    </>
  );
};
