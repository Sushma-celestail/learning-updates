import React from 'react';
import { createPortal } from 'react-dom';
import { AlertTriangle, Trash2, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button, cn } from './Button';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'warning' | 'info';
  isLoading?: boolean;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen, onClose, onConfirm,
  title, message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'danger',
  isLoading = false,
}) => {
  const config = {
    danger: { icon: Trash2, iconBg: 'bg-red-50', iconColor: 'text-red-500', confirmVariant: 'destructive' as const },
    warning: { icon: AlertTriangle, iconBg: 'bg-amber-50', iconColor: 'text-amber-600', confirmVariant: 'primary' as const },
    info: { icon: Info, iconBg: 'bg-blue-50', iconColor: 'text-blue-600', confirmVariant: 'primary' as const },
  }[variant];

  const Icon = config.icon;
  const modalRoot = document.getElementById('modal-root') || document.body;

  return createPortal(
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 overflow-hidden">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            onClick={onClose}
            className="absolute inset-0 bg-slate-950/40 dark:bg-black/80 backdrop-blur-md"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 1, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className={cn(
              'relative w-full max-w-sm bg-white rounded-[32px] overflow-hidden shadow-2xl border border-slate-200 z-10',
            )}
          >
            <div className="p-8">
              <div className={cn('w-14 h-14 rounded-2xl flex items-center justify-center mb-6', config.iconBg)}>
                <Icon size={24} className={config.iconColor} />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2 uppercase tracking-tight">{title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed font-medium">{message}</p>
            </div>
            <div className="px-8 pb-8 flex gap-3">
              <Button variant="secondary" className="flex-1 h-12 rounded-xl font-bold" onClick={onClose} disabled={isLoading}>
                {cancelLabel}
              </Button>
              <Button
                variant={config.confirmVariant}
                className="flex-1 h-12 rounded-xl font-bold"
                onClick={onConfirm}
                isLoading={isLoading}
                loadingText="Wait…"
              >
                {confirmLabel}
              </Button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>,
    modalRoot
  );
};
