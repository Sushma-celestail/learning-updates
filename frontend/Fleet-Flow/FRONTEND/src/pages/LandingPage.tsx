import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Building2, ArrowRight, ShieldCheck,
    Package, Truck, Clock, Activity,
    ChevronRight, Users, CheckCircle2,
    Menu, X, Mail, Star, MapPin,
    LogOut, LayoutDashboard, Database,
    ArrowUpRight, Quote, Globe
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { AuthForm } from '../components/auth/AuthForm';
import { Modal } from '../components/ui/Modal';
import { Button } from '../components/ui/Button';

export const LandingPage: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [isLoginOpen, setIsLoginOpen] = useState(false);
    const [isScrolled, setIsScrolled] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    useEffect(() => {
        if (user) {
            const role = user.role;
            if (role === 'Admin') navigate('/admin/users');
            else if (role === 'Driver') navigate('/shipments');
            else if (role === 'Clerk') navigate('/inventory');
            else navigate('/dashboard');
        }
    }, [user, navigate]);

    useEffect(() => {
        const handleScroll = () => setIsScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollTo = (id: string) => {
        const el = document.getElementById(id);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth' });
            setMobileMenuOpen(false);
        }
    };

    return (

        <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-indigo-100 selection:text-indigo-700">

            {/* Navbar */}
            <nav className={`fixed top-0 w-full z-[80] transition-all duration-300 ${isScrolled ? 'bg-white/80 backdrop-blur-lg border-b border-slate-100 py-3 shadow-sm' : 'bg-transparent py-6'}`}>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between">
                    <div className="flex items-center gap-2.5 group cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
                        <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform">
                            <Building2 className="text-white" size={22} />
                        </div>
                        <span className="text-xl font-black tracking-tight text-slate-900">Fleet-Flow <span className="text-indigo-600">Pro</span></span>
                    </div>

                    {/* Desktop Nav */}
                    <div className="hidden md:flex items-center gap-8">
                        {['About', 'Services', 'Program', 'Feedback'].map((item) => (
                            <button
                                key={item}
                                onClick={() => scrollTo(item.toLowerCase())}
                                className="text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors uppercase tracking-widest px-2 py-1"
                            >
                                {item}
                            </button>
                        ))}
                    </div>

                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setIsLoginOpen(true)}
                            className="hidden sm:inline-flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white px-5 py-2.5 rounded-xl text-sm font-bold transition-all shadow-lg shadow-slate-900/10 active:scale-95"
                        >
                            Login
                        </button>
                        <button className="md:hidden p-2 text-slate-600" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
                            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>
                </div>
            </nav>

            {/* Mobile Menu */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="fixed inset-0 z-[70] bg-white pt-24 px-6 md:hidden"
                    >
                        <div className="flex flex-col gap-6">
                            {['About', 'Services', 'Program', 'Feedback'].map((item) => (
                                <button
                                    key={item}
                                    onClick={() => scrollTo(item.toLowerCase())}
                                    className="text-2xl font-black text-slate-900 text-left border-b border-slate-100 pb-4"
                                >
                                    {item}
                                </button>
                            ))}
                            <button
                                onClick={() => { setIsLoginOpen(true); setMobileMenuOpen(false); }}
                                className="w-full bg-indigo-600 text-white py-4 rounded-2xl text-lg font-bold shadow-xl shadow-indigo-200"
                            >
                                Login to Terminal
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Hero Section */}
            <section className="relative pt-40 pb-24 overflow-hidden">
                <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/4 w-[800px] h-[800px] bg-indigo-50 rounded-full blur-[120px] opacity-60 z-0" />

                <div className="max-w-7xl mx-auto px-4 sm:px-6 relative z-10 text-center">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-50 border border-indigo-100 rounded-full text-indigo-700 text-xs font-bold uppercase tracking-widest mb-8"
                    >
                        <ShieldCheck size={14} /> Comprehensive Warehouse Management System
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-4xl md:text-6xl font-black text-slate-900 leading-[1.1] tracking-tight max-w-4xl mx-auto"
                    >
                        Smarter Warehouse <br />
                        <span className="text-indigo-500">Operations</span>
                    </motion.h1>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="text-lg md:text-xl text-slate-500 mt-8 max-w-2xl mx-auto font-medium leading-relaxed"
                    >
                        Fleet-Flow streamlines real-time inventory tracking, role-based access control, and automated shipment workflows across all your warehouses.
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4"
                    >
                        <button
                            onClick={() => setIsLoginOpen(true)}
                            className="w-full sm:w-auto px-10 py-5 bg-indigo-600 hover:bg-slate-900 text-white rounded-2xl text-base font-black transition-all shadow-2xl shadow-indigo-200 active:scale-95"
                        >
                            Get Started
                        </button>
                        <button
                            onClick={() => scrollTo('services')}
                            className="w-full sm:w-auto px-10 py-5 bg-white border-2 border-slate-100 hover:border-indigo-600 text-slate-600 hover:text-indigo-600 rounded-2xl text-base font-black transition-all active:scale-95"
                        >
                            Explore Features
                        </button>
                    </motion.div>

                    {/* Stats Grid */}
                    <div className="mt-24 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-5xl mx-auto">
                        {[
                            { value: '4', label: 'User Roles' },
                            { value: '5', label: 'Core Modules' },
                            { value: '100%', label: 'Audit Logged' },
                            { value: 'JWT', label: 'Secure Auth' },
                        ].map((stat, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.4 + (i * 0.1) }}
                                className="text-center"
                            >
                                <p className="text-3xl md:text-4xl font-black text-indigo-600 mb-2">{stat.value}</p>
                                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{stat.label}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* About Section */}
            <section id="about" className="py-32 bg-slate-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
                        <motion.div
                            initial={{ opacity: 0, x: -30 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                        >
                            <span className="text-xs font-black text-indigo-600 uppercase tracking-[0.3em] mb-4 block">About</span>
                            <h2 className="text-4xl md:text-5xl font-black text-slate-900 leading-tight mb-8">
                                What is Fleet Flow Pro?
                            </h2>
                            <p className="text-lg text-slate-600 font-medium leading-relaxed mb-8">
                                Fleet Flow Pro is a full-featured WMS designed to streamline logistical operations and grant your team total control over your supply chain ecosystem.
                            </p>
                            <div className="space-y-6">
                                <p className="text-slate-500 font-medium leading-relaxed">
                                    Built on React, FastAPI, and PostgreSQL, our platform scales with your business from a single facility to a multi-hub distribution network. Every action is tracked, every role is secured, and every shipment is monitored — from the moment stock arrives at the primary hub to its final delivery point.
                                </p>
                            </div>
                        </motion.div>

                        <div className="grid gap-4">
                            {[
                                "Real-time sync across inventory and shipments",
                                "RBAC-driven security for multi-tier operations",
                                "Fast and secure terminal-style OTP recovery",
                                "Automated stock alerts and low-count triggers",
                                "Full audit logs for every warehouse action"
                            ].map((obj, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: i * 0.1 }}
                                    className="p-6 bg-white border border-slate-100 rounded-3xl flex items-start gap-4 shadow-sm hover:shadow-md transition-shadow group"
                                >
                                    <div className="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center shrink-0 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                                        <ChevronRight size={18} className="text-indigo-600 group-hover:text-white" />
                                    </div>
                                    <p className="font-bold text-slate-700 leading-snug">{obj}</p>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* Services Section */}
            <section id="services" className="py-32">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="text-center mb-20">
                        <span className="text-xs font-black text-indigo-600 uppercase tracking-[0.3em] mb-4 block">Process</span>
                        <h2 className="text-4xl md:text-5xl font-black text-slate-900 leading-tight mb-6">
                            Core Features & Modules
                        </h2>
                        <p className="text-lg text-slate-500 max-w-2xl mx-auto font-medium">
                            Our integrated modules cover every aspect of warehouse operations — from authentication to shipment tracking.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {[
                            { title: 'Authentication Module', desc: 'Secure JWT-based login with terminal-style OTP recovery logic.', icon: ShieldCheck, color: 'blue' },
                            { title: 'User Management', desc: 'Admin-controlled role assignments and multi-hub facility pairing.', icon: Users, color: 'emerald' },
                            { title: 'Inventory Module', desc: 'Real-time stock management with procurement flow and manager oversight.', icon: Package, color: 'amber' },
                            { title: 'Shipment Logic', desc: 'Transfer control from hub to destination with transit tracking.', icon: Truck, color: 'indigo' },
                            { title: 'Alert System', desc: 'Automated low-stock triggers and system health monitoring.', icon: Activity, color: 'rose' },
                            { title: 'Audit Logging', desc: 'Every warehouse action is recorded forever for transparency.', icon: Database, color: 'slate' },
                        ].map((s, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                className="p-10 bg-slate-50/50 border border-slate-100 rounded-[40px] hover:bg-white hover:border-indigo-100 hover:shadow-2xl hover:shadow-indigo-500/10 transition-all duration-300 group"
                            >
                                <div className={`w-14 h-14 rounded-2xl mb-8 flex items-center justify-center bg-white shadow-lg group-hover:scale-110 transition-transform`}>
                                    <s.icon size={28} className="text-indigo-600" />
                                </div>
                                <h3 className="text-xl font-bold text-slate-900 mb-4">{s.title}</h3>
                                <p className="text-slate-500 text-sm font-medium leading-relaxed">
                                    {s.desc}
                                </p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Program Section (User Roles) */}
            <section id="program" className="py-32 bg-slate-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="text-center mb-20">
                        <span className="text-xs font-black text-indigo-600 uppercase tracking-[0.3em] mb-4 block">Program</span>
                        <h2 className="text-4xl md:text-5xl font-black text-slate-900 leading-tight mb-6">
                            User Roles & Access Control
                        </h2>
                        <p className="text-lg text-slate-500 max-w-2xl mx-auto font-medium">
                            Streamlined access ensures every user sees only what they need to. Four tiers, four levels of access.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {[
                            { role: 'Admin', subtitle: 'All Warehouses / Full Access', perms: ['Member Management', 'Hub Control', 'System Audit'], icon: ShieldCheck },
                            { role: 'Warehouse Manager', subtitle: 'Regional Hub Lead', perms: ['Approve Inventory', 'Stock Monitoring', 'Team View'], icon: Activity },
                            { role: 'Inventory Clerk', subtitle: 'Assigned Hub Floor', perms: ['Add Stock', 'Manage Shipments', 'Procurement Log'], icon: Package },
                            { role: 'Driver', subtitle: 'The Road Warriors', perms: ['Track Transit', 'Mark Delivered', 'My Settlements'], icon: Truck },
                        ].map((r, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                viewport={{ once: true }}
                                className="p-8 bg-white border border-slate-100 rounded-[32px] shadow-sm hover:shadow-xl transition-all group"
                            >
                                <div className="flex items-center gap-6 mb-8">
                                    <div className="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                                        <r.icon size={24} className="text-indigo-600 group-hover:text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold text-slate-900">{r.role}</h3>
                                        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">{r.subtitle}</p>
                                    </div>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    {r.perms.map((p, pi) => (
                                        <span key={pi} className="px-3 py-1.5 bg-slate-50 text-slate-600 text-[10px] font-black uppercase tracking-widest rounded-lg border border-slate-100">
                                            {p}
                                        </span>
                                    ))}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Feedback Section */}
            <section id="feedback" className="py-32">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="flex flex-col items-center text-center">
                        <span className="text-xs font-black text-indigo-600 uppercase tracking-[0.3em] mb-4 block">Testimonials</span>
                        <h2 className="text-4xl md:text-5xl font-black text-slate-900 leading-tight mb-16">
                            Stories from the Frontline
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {[
                            { author: 'Rajesh Kumar', role: 'Clerk @ Bengaluru Hub', text: 'The new stack logic saves hours on inventory tracking. Logistics tracking is better than even current systems.' },
                            { author: 'Mridula Nair', role: 'Supply Chain Admin', text: 'Auth flow and user management are so fast. Finally feeling like back-office is in sync with floor work.' },
                            { author: 'Arun Shetty', role: 'Driver @ Hub No. 04', text: 'Status update logic is simple and fast. Clear of clutter and zero lag.' }
                        ].map((t, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                className="p-8 bg-slate-50 border border-slate-100 rounded-[32px] relative group hover:bg-white hover:shadow-xl transition-all h-full flex flex-col justify-between"
                            >
                                <div>
                                    <Quote size={40} className="absolute top-4 right-8 text-indigo-100 group-hover:text-indigo-50 transition-colors" />
                                    <div className="flex items-center gap-1 mb-4">
                                        {[1, 2, 3, 4, 5].map(s => <Star key={s} size={12} className="fill-amber-400 text-amber-400" />)}
                                    </div>
                                    <p className="text-slate-600 italic font-medium leading-relaxed mb-6">"{t.text}"</p>
                                </div>
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center font-bold text-indigo-600 text-xs">
                                        {t.author.split(' ').map(n => n[0]).join('')}
                                    </div>
                                    <div>
                                        <p className="text-sm font-bold text-slate-800">{t.author}</p>
                                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{t.role}</p>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-white pt-32 pb-12 border-t border-slate-100">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 mb-24">
                        <div className="lg:col-span-2">
                            <div className="flex items-center gap-2.5 mb-6 group cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
                                <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform">
                                    <Building2 className="text-white" size={22} />
                                </div>
                                <span className="text-xl font-black tracking-tight text-slate-900">Fleet-Flow <span className="text-indigo-600">Pro</span></span>
                            </div>
                            <p className="text-slate-500 text-sm font-medium leading-relaxed max-w-sm mb-8">
                                Next-Gen Warehouse Management System. Built for scale, designed for speed, and trusted for logistical security.
                            </p>
                            <div className="flex items-center gap-4 mb-12">
                                {[1, 2, 3].map((_, i) => (
                                    <a key={i} href="#" className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center text-slate-400 hover:bg-slate-900 hover:text-white transition-all shadow-sm">
                                        <Globe size={18} />
                                    </a>
                                ))}
                            </div>


                        </div>

                        <div>
                            <h4 className="text-xs font-black text-slate-900 uppercase tracking-[0.2em] mb-8">Process</h4>
                            <ul className="space-y-4">
                                {['About', 'Services', 'Program', 'Feedback'].map(item => (
                                    <li key={item}>
                                        <button onClick={() => scrollTo(item.toLowerCase())} className="text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors uppercase tracking-widest">{item}</button>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div>
                            <h4 className="text-xs font-black text-slate-900 uppercase tracking-[0.2em] mb-8">Insights</h4>
                            <ul className="space-y-4">
                                {['Inventory Tracking', 'Shipment Lifecycle', 'Audit Logs'].map(item => (
                                    <li key={item}>
                                        <a href="#" className="text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors uppercase tracking-widest">{item}</a>
                                    </li>
                                ))}
                                <li className="pt-2">
                                    <span className="px-2 py-1 bg-indigo-50 text-indigo-600 text-[10px] font-black rounded-md border border-indigo-100">JOIN PANEL</span>
                                </li>
                            </ul>
                        </div>

                        <div>
                            <h4 className="text-xs font-black text-slate-900 uppercase tracking-[0.2em] mb-8">Access</h4>
                            <ul className="space-y-4">
                                {['Admin Login', 'Manager Login', 'Clerk Login', 'Driver Login'].map(item => (
                                    <li key={item}>
                                        <button onClick={() => setIsLoginOpen(true)} className="text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors uppercase tracking-widest">{item}</button>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    <div className="pt-12 border-t border-slate-100 flex flex-col md:flex-row items-center justify-between gap-6">
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">© 2024 Fleet-Flow Pro — Enterprise Warehouse Management System</p>
                        <div className="flex gap-4">
                            {['API Status', 'Vault Service', 'Maintenance'].map(s => (
                                <div key={s} className="flex items-center gap-1.5 px-3 py-1 bg-slate-50 border border-slate-100 rounded-lg">
                                    <div className="w-1 h-1 rounded-full bg-emerald-500" />
                                    <span className="text-[9px] font-black text-slate-500 uppercase tracking-tighter">{s}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </footer>

            {/* Login Modal */}
            <Modal
                isOpen={isLoginOpen}
                onClose={() => setIsLoginOpen(false)}
                title="System Terminal Access"
                subtitle="Authenticate to your assigned operational hub."
                className="max-w-[500px]"
            >
                <AuthForm onSuccess={() => setIsLoginOpen(false)} />
            </Modal>
        </div>
    );
};
