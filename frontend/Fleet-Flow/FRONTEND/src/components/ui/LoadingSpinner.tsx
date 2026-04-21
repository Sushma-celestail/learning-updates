import React from 'react';
import { cn } from './Button';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  label?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'md', className, label }) => {
  const sizes = { sm: 'h-4 w-4', md: 'h-8 w-8', lg: 'h-12 w-12' };
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3', className)}>
      <svg
        className={cn('animate-spin text-indigo-600 dark:text-violet-400', sizes[size])}
        xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
      >
        <circle className="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
        <path className="opacity-80" fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      {label && <p className="text-xs font-medium text-slate-400 dark:text-slate-500">{label}</p>}
    </div>
  );
};

export const Skeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('skeleton', className)} />
);

export const SkeletonCard: React.FC = () => (
  <div className="bg-white dark:bg-[#13131A] border border-slate-100 dark:border-white/[0.07] rounded-2xl p-5 space-y-4">
    <div className="flex items-center justify-between">
      <Skeleton className="w-10 h-10 rounded-xl" />
      <Skeleton className="w-16 h-5 rounded-full" />
    </div>
    <div className="space-y-2 pt-2">
      <Skeleton className="w-24 h-3" />
      <Skeleton className="w-16 h-7" />
    </div>
    <Skeleton className="w-32 h-3" />
  </div>
);

export const SkeletonTableRow: React.FC = () => (
  <tr className="border-t border-slate-100 dark:border-white/[0.05]">
    <td className="px-6 py-4">
      <div className="flex items-center gap-3">
        <Skeleton className="w-9 h-9 rounded-xl flex-shrink-0" />
        <div className="space-y-2">
          <Skeleton className="w-32 h-3.5" />
          <Skeleton className="w-20 h-3" />
        </div>
      </div>
    </td>
    <td className="px-6 py-4"><Skeleton className="w-20 h-5 rounded-full" /></td>
    <td className="px-6 py-4"><Skeleton className="w-16 h-4 ml-auto" /></td>
    <td className="px-6 py-4"><Skeleton className="w-20 h-8 rounded-lg ml-auto" /></td>
  </tr>
);

export const SkeletonText: React.FC<{ lines?: number }> = ({ lines = 3 }) => (
  <div className="space-y-2">
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton key={i} className={cn('h-4', i === lines - 1 ? 'w-3/4' : 'w-full')} />
    ))}
  </div>
);
