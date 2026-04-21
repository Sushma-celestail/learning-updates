import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Loader2 } from 'lucide-react';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'success';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  isLoading?: boolean;
  loadingText?: string;
}

export const Button: React.FC<ButtonProps> = ({
  className,
  variant = 'primary',
  size = 'md',
  isLoading,
  loadingText,
  children,
  disabled,
  ...props
}) => {
  const variants = {
    primary: cn(
      'bg-indigo-600 dark:bg-violet-500 text-white',
      'hover:bg-indigo-700 dark:hover:bg-violet-400',
      'shadow-sm hover:shadow-md',
      'focus-visible:ring-2 focus-visible:ring-indigo-500 dark:focus-visible:ring-violet-400 focus-visible:ring-offset-2 dark:focus-visible:ring-offset-[#13131A]',
    ),
    secondary: cn(
      'bg-white dark:bg-[#1A1A24] text-slate-900 dark:text-slate-100',
      'border border-slate-200 dark:border-white/10',
      'hover:bg-slate-50 dark:hover:bg-white/5',
      'shadow-sm hover:shadow-md',
    ),
    outline: cn(
      'bg-transparent text-indigo-600 dark:text-violet-400',
      'border border-indigo-600 dark:border-violet-400',
      'hover:bg-indigo-50 dark:hover:bg-violet-400/10',
    ),
    ghost: cn(
      'bg-transparent text-slate-600 dark:text-slate-400',
      'hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-slate-100',
    ),
    destructive: cn(
      'bg-red-500 dark:bg-red-500/90 text-white',
      'hover:bg-red-600 dark:hover:bg-red-500',
      'shadow-sm hover:shadow-md',
    ),
    success: cn(
      'bg-emerald-500 dark:bg-emerald-500/90 text-white',
      'hover:bg-emerald-600 dark:hover:bg-emerald-500',
      'shadow-sm hover:shadow-md',
    ),
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs  font-medium rounded-lg  h-8',
    md: 'px-4 py-2   text-sm  font-medium rounded-lg  h-10',
    lg: 'px-6 py-3   text-base font-semibold rounded-xl h-12',
    icon: 'p-2 rounded-lg w-10 h-10',
  };

  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2',
        'transition-all duration-150 ease-out',
        'font-medium whitespace-nowrap',
        'focus:outline-none',
        'active:scale-95',
        'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
        variants[variant],
        sizes[size],
        className,
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
      {isLoading && loadingText ? loadingText : children}
    </button>
  );
};
