import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { MapPin, ArrowRight, User } from 'lucide-react';
import type { Warehouse, User as UserType } from '../../types';
import { Button } from '../ui/Button';

const shipmentSchema = z.object({
  source_warehouse_id: z.number({ invalid_type_error: 'Select a source hub' }).min(1, 'Source hub is required'),
  destination_warehouse_id: z.number({ invalid_type_error: 'Select a destination hub' }).min(1, 'Destination hub is required'),
  driver_id: z.number({ invalid_type_error: 'Select a driver' }).min(1, 'Driver is required'),
}).refine(
  data => data.source_warehouse_id !== data.destination_warehouse_id,
  { message: 'Source and destination cannot be the same hub', path: ['destination_warehouse_id'] }
);

type ShipmentFormData = z.infer<typeof shipmentSchema>;

interface ShipmentFormProps {
  onSubmit: (data: ShipmentFormData) => void;
  warehouses: Warehouse[];
  drivers: UserType[];
  isLoading?: boolean;
}

const SelectField: React.FC<{
  label: string;
  icon: React.ReactNode;
  error?: string;
  children: React.ReactNode;
}> = ({ label, icon, error, children }) => (
  <div className="space-y-1.5">
    <label className="text-sm font-medium text-slate-700">
      {label} <span className="text-danger">*</span>
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

export const ShipmentForm: React.FC<ShipmentFormProps> = ({ onSubmit, warehouses, drivers, isLoading }) => {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<ShipmentFormData>({
    resolver: zodResolver(shipmentSchema),
  });

  const sourceWarehouseId = watch('source_warehouse_id');

  // ✅ Number() on both sides fixes string vs number type mismatch from DB
  const availableDrivers = sourceWarehouseId
    ? drivers.filter(d => Number(d.warehouse_id) === Number(sourceWarehouseId))
    : [];

  // Reset driver selection when source warehouse changes
  useEffect(() => {
    setValue('driver_id', '' as any);
  }, [sourceWarehouseId, setValue]);

  const selectClass = (hasError: boolean) =>
    `w-full h-10 pl-9 pr-3 text-sm border rounded-lg bg-white appearance-none cursor-pointer
     focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary
     transition-all duration-150
     ${hasError ? 'border-danger focus:ring-red-100' : 'border-slate-200'}`;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">

      {/* Origin hub */}
      <SelectField label="Origin hub" icon={<MapPin size={15} />} error={errors.source_warehouse_id?.message}>
        <select
          {...register('source_warehouse_id', { valueAsNumber: true })}
          style={{ color: '#000000' }}
          className={selectClass(!!errors.source_warehouse_id)}
        >
          <option value="">Select origin hub</option>
          {warehouses.map(w => (
            <option key={w.id} value={w.id}>{w.name}</option>
          ))}
        </select>
      </SelectField>

      {/* Arrow divider */}
      <div className="flex items-center justify-center">
        <div className="flex items-center gap-2 text-slate-300">
          <div className="h-px w-16 bg-slate-200" />
          <ArrowRight size={16} />
          <div className="h-px w-16 bg-slate-200" />
        </div>
      </div>

      {/* Destination hub */}
      <SelectField label="Destination hub" icon={<MapPin size={15} />} error={errors.destination_warehouse_id?.message}>
        <select
          {...register('destination_warehouse_id', { valueAsNumber: true })}
          style={{ color: '#000000' }}
          className={selectClass(!!errors.destination_warehouse_id)}
        >
          <option value="">Select destination hub</option>
          {warehouses.map(w => (
            <option key={w.id} value={w.id}>{w.name}</option>
          ))}
        </select>
      </SelectField>

      {/* Assign driver — auto-filtered by selected source warehouse */}
      <SelectField label="Assign driver" icon={<User size={15} />} error={errors.driver_id?.message}>
        <select
          {...register('driver_id', { valueAsNumber: true })}
          style={{ color: '#000000' }}
          disabled={!sourceWarehouseId}
          className={selectClass(!!errors.driver_id)}
        >
          <option value="">
            {!sourceWarehouseId
              ? 'Select origin hub first'
              : availableDrivers.length === 0
                ? 'No drivers assigned to this hub'
                : 'Select available driver'}
          </option>
          {availableDrivers.map(d => (
            <option key={d.id} value={d.id}>{d.name}</option>
          ))}
        </select>
      </SelectField>

      {/* Submit */}
      <div className="pt-2">
        <Button
          type="submit"
          className="w-full"
          isLoading={isLoading}
          loadingText="Creating shipment…"
        >
          Create Shipment
        </Button>
      </div>

    </form>
  );
};