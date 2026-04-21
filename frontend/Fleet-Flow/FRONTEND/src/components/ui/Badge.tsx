import React from 'react';
import { cn } from './Button';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'primary' | 'cyan';
  size?: 'sm' | 'md';
  className?: string;
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  className,
  dot = false,
}) => {
  const variants = {
    success: 'bg-emerald-50  dark:bg-emerald-400/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-400/20',
    warning: 'bg-amber-50    dark:bg-amber-400/10   text-amber-700   dark:text-amber-400   border border-amber-200   dark:border-amber-400/20',
    error: 'bg-rose-50     dark:bg-red-400/10     text-rose-700    dark:text-red-400     border border-rose-200    dark:border-red-400/20',
    info: 'bg-blue-50     dark:bg-cyan-400/10    text-blue-700    dark:text-cyan-400    border border-blue-200    dark:border-cyan-400/20',
    neutral: 'bg-slate-100   dark:bg-white/5        text-slate-700   dark:text-slate-400   border border-slate-200   dark:border-white/10',
    primary: 'bg-indigo-50   dark:bg-violet-400/10  text-indigo-700  dark:text-violet-400  border border-indigo-200  dark:border-violet-400/20',
    cyan: 'bg-cyan-50     dark:bg-cyan-400/10    text-cyan-700    dark:text-cyan-400    border border-cyan-200    dark:border-cyan-400/20',
  };

  const dotColors = {
    success: 'bg-emerald-500 dark:bg-emerald-400',
    warning: 'bg-amber-500   dark:bg-amber-400',
    error: 'bg-rose-500    dark:bg-red-400',
    info: 'bg-blue-500    dark:bg-cyan-400',
    neutral: 'bg-slate-400   dark:bg-slate-500',
    primary: 'bg-indigo-500  dark:bg-violet-400',
    cyan: 'bg-cyan-500    dark:bg-cyan-400',
  };

  const sizes = {
    sm: 'px-2   py-0.5 text-[11px]',
    md: 'px-2.5 py-0.5 text-xs',
  };

  return (
    <span className={cn(
      'inline-flex items-center gap-1.5 font-medium rounded-full transition-all duration-200',
      variants[variant],
      sizes[size],
      className,
    )}>
      {dot && (
        <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', dotColors[variant])} />
      )}
      {children}
    </span>
  );
};
