import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { 
  Building2, Mail, Lock, 
  ArrowRight, ShieldCheck, Loader2,
  Sparkles, Eye, EyeOff, ArrowLeft
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { authApi } from '../../api/auth.api';

interface AuthFormProps {
  onSuccess?: () => void;
  initialMode?: 'login' | 'forgot' | 'reset';
}

export const AuthForm: React.FC<AuthFormProps> = ({ onSuccess, initialMode = 'login' }) => {
    const [email, setEmail]       = useState('');
    const [password, setPassword] = useState('');
    const [otp, setOtp]           = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [showPass, setShowPass] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [mode, setMode] = useState<'login' | 'forgot' | 'reset'>(initialMode);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            if (mode === 'forgot') {
                const response = await authApi.forgotPassword(email);
                toast.success(response.message || 'OTP sent! Please check your email inbox.', { duration: 6000 });
                setMode('reset');
            } else if (mode === 'reset') {
                await authApi.resetPassword({ email, otp, new_password: newPassword });
                toast.success('Cipher key updated successfully. Please authenticate.');
                setMode('login');
                setOtp('');
                setNewPassword('');
            } else {
                const userData = await login({ email, password });
                
                toast.success('Access Granted. Redirecting...');
                
                if (onSuccess) {
                  onSuccess();
                } else {
                  // Intelligent Redirection based on role
                  const role = userData?.role;
                  if (role === 'Admin') navigate('/admin/users');
                  else if (role === 'Driver') navigate('/shipments');
                  else if (role === 'Clerk') navigate('/inventory');
                  else navigate('/dashboard');
                }
            }
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Operation failed. Access denied.', { duration: 5000 });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="w-full max-w-[420px] mx-auto">
            <div className="mb-8 text-center">
                <motion.div 
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center shadow-xl mx-auto mb-6"
                >
                    <Building2 size={28} className="text-white" />
                </motion.div>
                <motion.h2 
                    key={mode}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-2xl font-bold text-slate-900 tracking-tight"
                >
                    {mode === 'login' ? 'Welcome Back' : mode === 'forgot' ? 'Reset Password' : 'New Password'}
                </motion.h2>
                <motion.p 
                    key={`${mode}-desc`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-slate-500 text-sm mt-2 font-medium"
                >
                    {mode === 'login' 
                        ? 'Sign in to manage your warehouse operations' 
                        : mode === 'forgot' 
                            ? 'Enter your email to receive a recovery code' 
                            : 'Create a new password for your account'}
                </motion.p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
                <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700 ml-1">Email Address</label>
                    <div className="relative group/input">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within/input:text-indigo-600 transition-colors">
                            <Mail size={18} />
                        </div>
                        <input
                            type="email"
                            required
                            disabled={mode === 'reset'}
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="block w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:bg-white focus:border-indigo-500 transition-all font-medium disabled:opacity-50"
                            placeholder="user@precisionflow.io"
                        />
                    </div>
                </div>

                <AnimatePresence mode="wait">
                    {mode === 'login' && (
                        <motion.div 
                            key="login-fields"
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="space-y-5 overflow-hidden"
                        >
                            <div className="space-y-1.5">
                                <label className="text-xs font-semibold text-slate-700 ml-1">Password</label>
                                <div className="relative group/input">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within/input:text-indigo-600 transition-colors">
                                        <Lock size={18} />
                                    </div>
                                    <input
                                        type={showPass ? 'text' : 'password'}
                                        required={mode === 'login'}
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="block w-full pl-11 pr-12 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:bg-white focus:border-indigo-500 transition-all font-medium"
                                        placeholder="••••••••"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPass(!showPass)}
                                        className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 transition-colors"
                                    >
                                        {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {mode === 'reset' && (
                        <motion.div 
                            key="reset-fields"
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="space-y-5 overflow-hidden"
                        >
                            <div className="space-y-1.5">
                                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Recovery OTP</label>
                                <div className="relative group/input">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within/input:text-indigo-600 transition-colors">
                                        <Sparkles size={18} />
                                    </div>
                                    <input
                                        type="text"
                                        required
                                        value={otp}
                                        onChange={(e) => setOtp(e.target.value)}
                                        className="block w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:bg-white focus:border-indigo-500 transition-all font-medium"
                                        placeholder="Enter 6-digit OTP"
                                    />
                                </div>
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">New Cipher Key</label>
                                <div className="relative group/input">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within/input:text-indigo-600 transition-colors">
                                        <Lock size={18} />
                                    </div>
                                    <input
                                        type={showPass ? 'text' : 'password'}
                                        required
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                        className="block w-full pl-11 pr-12 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:bg-white focus:border-indigo-500 transition-all font-medium"
                                        placeholder="••••••••"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPass(!showPass)}
                                        className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 transition-colors"
                                    >
                                        {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                <div className="flex items-center justify-end px-1">
                    {mode !== 'login' ? (
                        <button 
                            type="button"
                            onClick={() => setMode('login')}
                            className="text-sm font-bold text-indigo-600 hover:text-indigo-700 transition-colors flex items-center gap-1.5"
                        >
                            <ArrowLeft size={14} /> Back to Login
                        </button>
                    ) : (
                        <button 
                            type="button" 
                            onClick={() => setMode('forgot')}
                            className="text-xs font-bold text-slate-400 hover:text-indigo-600 transition-colors"
                        >
                            Forgot Password?
                        </button>
                    )}
                </div>

                <button 
                    type="submit" 
                    disabled={isLoading}
                    className="group relative w-full h-12 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-bold text-sm uppercase tracking-widest flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-500/25 disabled:opacity-70"
                >
                    {isLoading ? (
                        <Loader2 className="animate-spin" size={18} />
                    ) : (
                        <>
                            {mode === 'login' ? 'Sign In' : mode === 'forgot' ? 'Send Code' : 'Reset Password'} 
                            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                        </>
                    )}
                </button>
            </form>
        </div>
    );
};
