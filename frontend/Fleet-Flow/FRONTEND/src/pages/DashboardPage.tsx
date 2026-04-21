import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Package, Truck, Clock, CheckCircle2,
  ArrowUpRight, Building2, Activity, TrendingUp,
  ArrowRight, Download
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, BarChart, Bar, Cell 
} from 'recharts';
import { useAuth } from '../hooks/useAuth';
import { useInventory } from '../hooks/useInventory';
import { useShipments } from '../hooks/useShipments';
import { useWarehouses } from '../hooks/useWarehouses';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { Button } from '../components/ui/Button';
import { SkeletonCard } from '../components/ui/LoadingSpinner';

/* ─── Constants ────────────────────────────────────────────────────────── */
const iconColors: Record<string, { bg: string; text: string; gradient: string }> = {
  blue: { 
    bg: 'bg-blue-50 dark:bg-blue-400/10', 
    text: 'text-blue-600 dark:text-blue-400',
    gradient: 'from-blue-500/20 to-indigo-500/20'
  },
  amber: { 
    bg: 'bg-amber-50 dark:bg-amber-400/10', 
    text: 'text-amber-600 dark:text-amber-400',
    gradient: 'from-amber-500/20 to-orange-500/20'
  },
  indigo: { 
    bg: 'bg-indigo-50 dark:bg-violet-400/10', 
    text: 'text-indigo-600 dark:text-violet-400',
    gradient: 'from-indigo-500/20 to-purple-500/20'
  },
  emerald: { 
    bg: 'bg-emerald-50 dark:bg-emerald-400/10', 
    text: 'text-emerald-600 dark:text-emerald-400',
    gradient: 'from-emerald-500/20 to-teal-500/20'
  },
};

/* ─── Components ───────────────────────────────────────────────────────── */
const StatCard: React.FC<{ label: string; value: string | number; trend: string; icon: React.ElementType; color: string; delay: number; link?: string }> = 
({ label, value, trend, icon: Icon, color, delay, link }) => {
  const navigate = useNavigate();
  const c = iconColors[color] ?? iconColors.blue;
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      onClick={() => link && navigate(link)}
      className={`stat-card group relative overflow-hidden ${link ? 'cursor-pointer hover:border-indigo-500/50 dark:hover:border-violet-500/50 transition-all' : ''}`}
    >
      <div className={`absolute -right-4 -top-4 w-24 h-24 bg-gradient-to-br ${c.gradient} blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
      
      <div className="flex items-start justify-between relative z-10">
        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${c.bg} ${c.text} group-hover:scale-110 transition-transform duration-300 shadow-sm`}>
          <Icon size={24} />
        </div>
        <div className="flex flex-col items-end">
          <Badge variant={trend.includes('+') ? 'success' : 'neutral'} size="sm">
            {trend}
          </Badge>
        </div>
      </div>
      
      <div className="mt-5 relative z-10">
        <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-widest">{label}</p>
        <div className="flex items-baseline gap-2 mt-1">
          <h3 className="text-3xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">{value}</h3>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-slate-50 dark:border-white/[0.04] flex items-center justify-between text-[11px] relative z-10">
        <span className="text-slate-400 dark:text-slate-500 flex items-center gap-1">
          <Clock size={12} /> Live tracking
        </span>
      </div>
    </motion.div>
  );
};

/* ─── Main Page ────────────────────────────────────────────────────────── */
export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { items, isLoading: inventoryLoading } = useInventory(user?.warehouse_id);
  const { shipments, isLoading: shipmentsLoading } = useShipments(user?.role, user?.id, user?.warehouse_id);
  const { warehouses } = useWarehouses();

  const [trendPeriod, setTrendPeriod] = useState<'Weekly' | 'Monthly'>('Weekly');
  const [isLogModalOpen, setIsLogModalOpen] = useState(false);

  const isLoading = inventoryLoading || shipmentsLoading;
  const isDriver = user?.role === 'Driver';
  const homeHub = warehouses.find(w => w.id === user?.warehouse_id)?.name || 'Central Command';

  const handleExport = () => {
    const csvRows = [
      ['Report Title', 'Fleet-Flow Operations Report'],
      ['Generated At', new Date().toLocaleString()],
      ['User', user?.name || 'Unknown'],
      [],
      ['--- INVENTORY DATA ---'],
      ['ID', 'Product Name', 'Status', 'Quantity'],
      ...items.map(i => [i.id, i.product_name, i.is_approved ? 'Approved' : 'Pending', i.quantity]),
      [],
      ['--- SHIPMENTS DATA ---'],
      ['ID', 'Status', 'Origin', 'Destination'],
      ...shipments.map(s => [s.id, s.status, s.origin_warehouse_id, s.destination_warehouse_id]),
    ];

    const csvContent = csvRows.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `fleet_flow_ops_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const stats = isDriver
    ? [
      { label: 'My Assignments', value: shipments.length, trend: 'Assigned', icon: Truck, color: 'blue' },
      { label: 'Active Transits', value: shipments.filter(s => s.status === 'In Transit').length, trend: 'Priority', icon: Activity, color: 'indigo' },
      { label: 'Deliveries', value: shipments.filter(s => s.status === 'Delivered').length, trend: 'Completed', icon: CheckCircle2, color: 'emerald' },
      { label: 'Home Hub', value: homeHub, trend: 'Active', icon: Building2, color: 'amber' },
    ]
    : [
      { label: 'Inventory', value: items.length, trend: '+4.2%', icon: Package, color: 'blue' },
      { label: 'Pending', value: items.filter(i => !i.is_approved).length, trend: 'Action!', icon: Clock, color: 'amber', link: '/inventory?filter=pending' },
      { label: 'Transits', value: shipments.filter(s => s.status === 'In Transit').length, trend: '+12%', icon: Truck, color: 'indigo' },
      { label: 'Completed', value: shipments.filter(s => s.status === 'Delivered').length, trend: 'Daily', icon: CheckCircle2, color: 'emerald' },
    ];

  const weeklyData = [
    { name: 'Mon', value: 400, shipments: 240 },
    { name: 'Tue', value: 300, shipments: 139 },
    { name: 'Wed', value: 600, shipments: 980 },
    { name: 'Thu', value: 800, shipments: 390 },
    { name: 'Fri', value: 500, shipments: 480 },
    { name: 'Sat', value: 900, shipments: 380 },
    { name: 'Sun', value: 700, shipments: 430 },
  ];

  const monthlyData = [
    { name: 'Week 1', value: 2400, shipments: 1800 },
    { name: 'Week 2', value: 4500, shipments: 3200 },
    { name: 'Week 3', value: 3100, shipments: 2100 },
    { name: 'Week 4', value: 6200, shipments: 4800 },
  ];

  const activeChartData = trendPeriod === 'Weekly' ? weeklyData : monthlyData;

  const activities = [
    { id: 1, title: 'Shipment #4529 Outbound', time: '3 mins ago', desc: 'Gate 04', icon: Truck, color: 'blue' },
    { id: 2, title: 'SKU-009 Low Stock Alert', time: '40 mins ago', desc: 'Zone C – Row 12', icon: Package, color: 'amber' },
    { id: 3, title: 'New Inventory Check-in', time: '1 hour ago', desc: 'Mumbai Hub', icon: CheckCircle2, color: 'emerald' },
    { id: 4, title: 'Shipment Delayed', time: '2 hours ago', desc: 'Weather Issue', icon: Truck, color: 'amber' },
  ];

  const isDark = true;

  return (
    <div className="space-y-8 animate-fade-in">

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2">
            Operations <span className="gradient-text">Hub</span>
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 font-medium">
            {user?.warehouse_id ? `Assigned: ${homeHub}` : 'Global Logistics Intelligence Platform'}
          </p>
        </motion.div>
        
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-white/50 dark:bg-white/5 border border-slate-100 dark:border-white/10 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-400">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Live System
          </div>
          <Button 
            variant="primary" 
            size="sm" 
            className="shadow-lg shadow-indigo-500/20 gap-2"
            onClick={handleExport}
          >
            <Download size={14} />
            Export Report
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
          : stats.map((stat, i) => <StatCard key={i} {...stat} delay={i * 0.1} />)
        }
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Trend Visualization */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2 premium-card flex flex-col"
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Throughput Analysis</h3>
              <p className="text-xs text-slate-500 dark:text-slate-500 font-medium">Real-time load balancing & traffic</p>
            </div>
            <div className="flex bg-slate-100 dark:bg-white/5 p-1 rounded-xl">
              {['Weekly', 'Monthly'].map(p => (
                <button
                  key={p}
                  onClick={() => setTrendPeriod(p as any)}
                  className={`px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${
                    trendPeriod === p 
                    ? 'bg-white dark:bg-white/10 text-indigo-600 dark:text-violet-400 shadow-sm' 
                    : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div className="h-[300px] w-full" key={trendPeriod}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activeChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={isDark ? "#A78BFA" : "#6366F1"} stopOpacity={0.3}/>
                    <stop offset="95%" stopColor={isDark ? "#A78BFA" : "#6366F1"} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={isDark ? "rgba(255,255,255,0.05)" : "#E2E8F0"} />
                <XAxis 
                  dataKey="name" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fontSize: 10, fill: isDark ? '#64748B' : '#94A3B8', fontWeight: 600 }}
                  dy={10}
                />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: isDark ? '#64748B' : '#94A3B8' }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: isDark ? '#0D0D15' : '#ffffff', 
                    border: isDark ? '1px solid rgba(255,255,255,0.08)' : '1px solid #E2E8F0', 
                    borderRadius: '16px',
                    color: isDark ? '#F1F5F9' : '#0F172A',
                    fontSize: '12px',
                    boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'
                  }} 
                  itemStyle={{ fontWeight: 'bold' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="value" 
                  stroke={isDark ? "#A78BFA" : "#6366F1"} 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorVal)" 
                  animationDuration={2000}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Live Logs */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="premium-card flex flex-col"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Live Activity</h3>
            {/* <button className="text-xs font-bold text-indigo-600 dark:text-violet-400 hover:underline">Clear</button> */}
          </div>

          <div className="space-y-6 flex-1 overflow-y-auto custom-scrollbar pr-2">
            {activities.map((item, idx) => (
              <div key={item.id} className="relative flex gap-4">
                {idx !== activities.length - 1 && (
                  <div className="absolute left-4 top-8 bottom-[-24px] w-[2px] bg-slate-100 dark:bg-white/5" />
                )}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 z-10 ${
                  item.color === 'blue' ? 'bg-blue-500' :
                  item.color === 'amber' ? 'bg-amber-500' : 'bg-emerald-500'
                }`}>
                  <item.icon size={14} className="text-white" />
                </div>
                <div>
                  <p className="text-sm font-bold text-slate-800 dark:text-slate-200">{item.title}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{item.desc}</p>
                  <span className="text-[10px] text-slate-400 dark:text-slate-600 font-medium block mt-1">{item.time}</span>
                </div>
              </div>
            ))}
          </div>

          <Button 
            variant="secondary" 
            className="mt-8 gap-2 group" 
            onClick={() => setIsLogModalOpen(true)}
          >
            Full Audit Logs
            <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
          </Button>
        </motion.div>
      </div>

      <Modal isOpen={isLogModalOpen} onClose={() => setIsLogModalOpen(false)} title="Security Audit Log">
        <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
           {Array.from({ length: 8 }).map((_, i) => (
             <div key={i} className="p-4 bg-slate-50 dark:bg-white/5 rounded-2xl border border-slate-100 dark:border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-indigo-500/10 flex items-center justify-center text-indigo-500">
                    <Activity size={18} />
                  </div>
                  <div>
                    <p className="text-sm font-bold">System Sync #{1000 + i}</p>
                    <p className="text-xs text-slate-500">Automated maintenance routine</p>
                  </div>
                </div>
                <Badge variant="success">Completed</Badge>
             </div>
           ))}
        </div>
      </Modal>
    </div>
  );
};
