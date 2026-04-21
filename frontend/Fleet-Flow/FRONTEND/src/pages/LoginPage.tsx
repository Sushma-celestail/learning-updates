import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { AuthForm } from '../components/auth/AuthForm';
import { motion } from 'framer-motion';
import { ShieldCheck } from 'lucide-react';
import { useEffect } from 'react';

export const LoginPage: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (user) {
            const role = user.role;
            if (role === 'Admin') navigate('/admin/users');
            else if (role === 'Driver') navigate('/shipments');
            else if (role === 'Clerk') navigate('/inventory');
            else navigate('/dashboard');
        }
    }, [user, navigate]);
    return (
        <div className="min-h-screen w-full flex items-center justify-center p-4 bg-slate-50">
            <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                className="w-full max-w-[440px]"
            >
                <div className="bg-white border border-slate-200 rounded-[32px] p-8 md:p-10 shadow-sm">
                    <AuthForm />
                </div>
            </motion.div>
        </div>
    );
};
