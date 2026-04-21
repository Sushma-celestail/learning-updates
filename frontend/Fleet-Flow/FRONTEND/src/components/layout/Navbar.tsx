import React, { useState, useRef, useEffect } from 'react';
import {
  Bell, Search, User as UserIcon, Settings,
  Shield, Mail, Building2, X, Sun, Moon,
} from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { Modal } from '../ui/Modal';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { cn } from '../ui/Button';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [searchFocused, setSearchFocused] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);

  const [notifications, setNotifications] = useState([
    { id: 1, title: 'Critical Stock Alert', time: '12m ago', level: 'danger' as const },
    { id: 2, title: 'Shipment PF-902 Arrived', time: '45m ago', level: 'info' as const },
    { id: 3, title: 'New User Registered', time: '2h ago', level: 'success' as const },
  ]);

  const notifDotClass: Record<string, string> = {
    danger: 'bg-red-500',
    success: 'bg-emerald-500',
    info: 'bg-blue-500 dark:bg-cyan-400',
  };

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node))
        setIsNotificationsOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const dismissNotification = (id: number) =>
    setNotifications(prev => prev.filter(n => n.id !== id));

  return (
    <>
      <header className={cn(
        'h-16 fixed top-0 right-0 left-64 z-30 px-8',
        'flex items-center justify-between',
        'max-lg:left-0 max-lg:pl-16',
        'bg-white/80 dark:bg-[#030305]/80 backdrop-blur-xl',
        'border-b border-slate-100 dark:border-white/[0.04]',
        'transition-all duration-300',
      )}>

        {/* Search */}
        <div className={cn('relative transition-all duration-200', searchFocused ? 'w-80 sm:w-96' : 'w-64 sm:w-80')}>
          <Search
            size={15}
            className={cn(
              'absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none transition-colors',
              searchFocused
                ? 'text-indigo-500 dark:text-violet-400'
                : 'text-slate-400 dark:text-slate-500',
            )}
          />
          <input
            type="text"
            placeholder="Search inventory, shipments…"
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
            className={cn(
              'w-full pl-9 pr-4 h-9 text-sm rounded-lg transition-all duration-200',
              'bg-slate-100 dark:bg-white/5',
              'border border-transparent',
              'text-slate-700 dark:text-slate-200',
              'placeholder:text-slate-400 dark:placeholder:text-slate-500',
              'focus:outline-none focus:bg-white dark:focus:bg-white/10',
              'focus:border-indigo-300 dark:focus:border-violet-500/40',
              'focus:ring-2 focus:ring-indigo-100 dark:focus:ring-violet-500/10',
            )}
          />
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-1.5">



          {/* Notifications */}
          <div className="relative" ref={notifRef}>
            <button
              onClick={() => setIsNotificationsOpen(v => !v)}
              className={cn(
                'relative p-2 rounded-lg transition-all duration-150',
                'text-slate-500 dark:text-slate-400',
                isNotificationsOpen
                  ? 'bg-slate-100 dark:bg-white/5 text-slate-700 dark:text-slate-200'
                  : 'hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-700 dark:hover:text-slate-200',
              )}
              aria-label="Notifications"
            >
              <Bell size={18} />
              {notifications.length > 0 && (
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-[#0A0A0F]" />
              )}
            </button>

            {/* Dropdown */}
            {isNotificationsOpen && (
              <div className={cn(
                'absolute right-0 mt-2 w-80 overflow-hidden z-50 animate-scale-in',
                'bg-white dark:bg-[#13131A]',
                'border border-slate-100 dark:border-white/[0.07]',
                'rounded-2xl shadow-xl dark:shadow-black/50',
              )}>
                <div className="px-4 py-3 border-b border-slate-100 dark:border-white/[0.07] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100">Notifications</h4>
                    {notifications.length > 0 && (
                      <span className="text-xs font-medium bg-indigo-50 dark:bg-violet-500/10 text-indigo-600 dark:text-violet-400 px-1.5 py-0.5 rounded-full">
                        {notifications.length}
                      </span>
                    )}
                  </div>
                  {notifications.length > 0 && (
                    <button
                      onClick={() => setNotifications([])}
                      className="text-xs font-medium text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
                    >
                      Clear all
                    </button>
                  )}
                </div>

                <div className="max-h-72 overflow-y-auto custom-scrollbar">
                  {notifications.length > 0 ? (
                    notifications.map(n => (
                      <div
                        key={n.id}
                        className="px-4 py-3 hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-colors border-b border-slate-50 dark:border-white/[0.04] last:border-0 group"
                      >
                        <div className="flex items-start gap-3">
                          <span className={cn('w-2 h-2 rounded-full mt-1.5 flex-shrink-0', notifDotClass[n.level])} />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-slate-800 dark:text-slate-200 leading-snug">{n.title}</p>
                            <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{n.time}</p>
                          </div>
                          <button
                            onClick={() => dismissNotification(n.id)}
                            className="opacity-0 group-hover:opacity-100 p-0.5 text-slate-300 dark:text-slate-600 hover:text-slate-500 dark:hover:text-slate-400 transition-all"
                          >
                            <X size={13} />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="py-10 text-center">
                      <div className="w-10 h-10 bg-slate-50 dark:bg-white/5 rounded-xl flex items-center justify-center mx-auto mb-3">
                        <Bell size={18} className="text-slate-300 dark:text-slate-600" />
                      </div>
                      <p className="text-sm font-medium text-slate-400 dark:text-slate-500">All caught up</p>
                      <p className="text-xs text-slate-300 dark:text-slate-600 mt-0.5">No new notifications</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Divider */}
          <div className="w-px h-6 bg-slate-200 dark:bg-white/10 mx-1" />

          {/* Profile */}
          <button
            onClick={() => setIsProfileOpen(true)}
            className="flex items-center gap-2.5 pl-1 pr-2 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-white/5 transition-all duration-150 group"
          >
            <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-violet-500/10 border border-indigo-100 dark:border-violet-500/20 flex items-center justify-center flex-shrink-0">
              <UserIcon size={15} className="text-indigo-600 dark:text-violet-400" />
            </div>
            <div className="text-left hidden sm:block">
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 leading-tight group-hover:text-indigo-600 dark:group-hover:text-violet-400 transition-colors">
                {user?.name}
              </p>
              <p className="text-xs text-slate-400 dark:text-slate-500 leading-tight">{user?.role}</p>
            </div>
          </button>
        </div>
      </header>

      {/* Profile Modal */}
      <Modal
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        title="My Profile"
        subtitle="Account details and preferences"
      >
        <div className="flex flex-col items-center mb-6 pt-2">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 dark:from-violet-500 to-indigo-600 dark:to-cyan-500 flex items-center justify-center text-white mb-3 shadow-lg shadow-indigo-200 dark:shadow-violet-500/20">
            <UserIcon size={36} />
          </div>
          <h4 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{user?.name}</h4>
          <Badge variant="primary" className="mt-1.5">{user?.role}</Badge>
        </div>

        <div className="space-y-2">
          {[
            { icon: Mail, label: 'Email', value: user?.email },
            { icon: Shield, label: 'Access Level', value: `Level 0${user?.role === 'Admin' ? '1' : '2'} — ${user?.role}` },
            { icon: Building2, label: 'Facility', value: user?.warehouse_id ? `Hub #${user.warehouse_id}` : 'Global — All Facilities' },
          ].map(({ icon: Icon, label, value }) => (
            <div key={label} className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-white/[0.03] rounded-xl border border-transparent dark:border-white/[0.05]">
              <div className="w-8 h-8 bg-white dark:bg-white/5 rounded-lg flex items-center justify-center border border-slate-100 dark:border-white/10 flex-shrink-0">
                <Icon size={14} className="text-slate-400 dark:text-slate-500" />
              </div>
              <div className="min-w-0">
                <p className="text-xs text-slate-400 dark:text-slate-500 font-medium">{label}</p>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">{value}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="flex gap-3 mt-6 pt-5 border-t border-slate-100 dark:border-white/[0.07]">
          <Button variant="ghost" size="sm" className="gap-2 text-slate-500 dark:text-slate-400">
            <Settings size={14} /> Settings
          </Button>
          <Button
            variant="destructive"
            size="sm"
            className="ml-auto"
            onClick={() => { setIsProfileOpen(false); logout(); }}
          >
            Sign out
          </Button>
        </div>
      </Modal>
    </>
  );
};
