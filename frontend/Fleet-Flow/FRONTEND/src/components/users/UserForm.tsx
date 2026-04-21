import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { User, Mail, Lock, Shield, Building2 } from 'lucide-react';
import type { User as UserType, Warehouse } from '../../types';
import { Button } from '../ui/Button';
import toast from 'react-hot-toast';

const userSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Enter a valid email address'),
  password: z.string().optional(),
  role: z.string().min(1, 'Please select a role'),
  warehouse_id: z.number().nullable().optional(),
}).superRefine((data, ctx) => {
  // Check if facility is required
  if (['Manager', 'Clerk', 'Driver'].includes(data.role) && !data.warehouse_id) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'A facility is required for this role',
      path: ['warehouse_id'],
    });
  }
});

type UserFormData = z.infer<typeof userSchema>;

interface UserFormProps {
  onSubmit: (data: any) => void;
  initialData?: Partial<UserType>;
  isLoading?: boolean;
  warehouses?: Warehouse[];
}

const inputClass = (hasError: boolean) =>
  `w-full h-10 pl-9 pr-3 text-sm text-black border rounded-lg bg-white
   focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary
   transition-all duration-150 placeholder:text-slate-400
   ${hasError ? 'border-danger focus:ring-red-100' : 'border-slate-200'}`;

const FieldWrapper: React.FC<{
  label: string;
  required?: boolean;
  error?: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}> = ({ label, required, error, icon, children }) => (
  <div className="space-y-1.5">
    <label className="text-sm font-medium text-slate-700 ">
      {label} {required && <span className="text-danger">*</span>}
    </label>
    <div className="relative">
      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
        {icon}
      </span>
      {children}
    </div>
    {error && <p className="text-xs text-danger font-medium">{error}</p>}
  </div>
);

export const UserForm: React.FC<UserFormProps> = ({
  onSubmit,
  initialData,
  isLoading,
  warehouses = [],
}) => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      name: initialData?.name ?? '',
      email: initialData?.email ?? '',
      role: (initialData?.role as string) ?? '',
      warehouse_id: initialData?.warehouse_id ?? null,
      password: '',
    },
  });

  const selectedRole = watch('role');
  const needsWarehouse = ['Manager', 'Clerk', 'Driver'].includes(selectedRole);

  const handleFormSubmit = (data: UserFormData) => {
    if (!initialData && (!data.password || data.password.length < 6)) {
      toast.error('Password must be at least 6 characters for new users');
      return;
    }
    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">

      {/* Name */}
      <FieldWrapper label="Full name" required error={errors.name?.message} icon={<User size={15} />}>
        <input
          {...register('name')}
          className={inputClass(!!errors.name)}
          placeholder="Jane Smith"
        />
      </FieldWrapper>

      {/* Email */}
      <FieldWrapper label="Email address" required error={errors.email?.message} icon={<Mail size={15} />}>
        <input
          {...register('email')}
          type="email"
          className={inputClass(!!errors.email)}
          placeholder="jane@company.com"
          autoComplete="off"
        />
      </FieldWrapper>

      {/* Password section */}
      {initialData ? (
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
          <FieldWrapper label="Reset password (optional)" error={errors.password?.message} icon={<Lock size={15} />}>
            <input
              {...register('password')}
              type="password"
              className={inputClass(!!errors.password)}
              placeholder="Leave blank to keep current"
              autoComplete="new-password"
            />
          </FieldWrapper>
        </div>
      ) : (
        <FieldWrapper label="Password" required error={errors.password?.message} icon={<Lock size={15} />}>
          <input
            {...register('password')}
            type="password"
            className={inputClass(!!errors.password)}
            placeholder="Min. 6 characters"
            autoComplete="new-password"
          />
        </FieldWrapper>
      )}

      {/* Role + Facility — side by side */}
      <div className="grid grid-cols-2 gap-3">
        {/* Role */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-slate-700">
            Role <span className="text-danger">*</span>
          </label>
          <div className="relative">
            <Shield size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            <select
              {...register('role')}
              className={`w-full h-10 pl-9 pr-3 text-sm text-black border rounded-lg bg-white appearance-none cursor-pointer
                         focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary
                         transition-all duration-150
                         ${errors.role ? 'border-danger' : 'border-slate-200'}`}
            >
              <option value="" disabled>Select role</option>
              <option value="Admin">Admin</option>
              <option value="Manager">Manager</option>
              <option value="Clerk">Clerk</option>
              <option value="Driver">Driver</option>
            </select>
          </div>
          {errors.role && <p className="text-xs text-danger font-medium">{errors.role.message}</p>}
        </div>

        {/* Facility */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-slate-700">
            Facility {needsWarehouse && <span className="text-danger">*</span>}
          </label>
          <div className="relative">
            <Building2 size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            <select
              {...register('warehouse_id', {
                setValueAs: v => (v === '' ? null : parseInt(v, 10)),
              })}
              disabled={!needsWarehouse && selectedRole !== ''}
              className={`w-full h-10 pl-9 pr-3 text-sm text-black border rounded-lg bg-white appearance-none cursor-pointer
                         focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary
                         transition-all duration-150
                         ${errors.warehouse_id ? 'border-danger' : 'border-slate-200'}
                         ${!needsWarehouse && selectedRole !== '' ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <option value="">Select facility</option>
              {warehouses.map(w => (
                <option key={w.id} value={w.id}>{w.name}</option>
              ))}
            </select>
          </div>
          {errors.warehouse_id && (
            <p className="text-xs text-danger font-medium">{errors.warehouse_id.message}</p>
          )}
        </div>
      </div>

      {/* Submit */}
      <div className="pt-2">
        <Button
          type="submit"
          className="w-full"
          isLoading={isLoading}
          loadingText={initialData ? 'Saving…' : 'Creating…'}
        >
          {initialData ? 'Save Changes' : 'Create User'}
        </Button>
      </div>
    </form>
  );
};
