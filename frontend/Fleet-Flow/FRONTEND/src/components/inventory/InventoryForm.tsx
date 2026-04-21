import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Package, Hash } from 'lucide-react';
import { Button } from '../ui/Button';

const inventorySchema = z.object({
  product_name: z.string().min(2, 'Product name must be at least 2 characters'),
  quantity: z.number({ invalid_type_error: 'Enter a valid number' }).min(1, 'Quantity must be at least 1'),
});

type InventoryFormData = z.infer<typeof inventorySchema>;

interface InventoryFormProps {
  onSubmit: (data: InventoryFormData) => void;
  initialData?: { product_name: string; quantity: number };
  isLoading?: boolean;
}

export const InventoryForm: React.FC<InventoryFormProps> = ({ onSubmit, initialData, isLoading }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<InventoryFormData>({
    resolver: zodResolver(inventorySchema),
    defaultValues: {
      product_name: initialData?.product_name ?? '',
      quantity: initialData?.quantity ?? undefined,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">

      {/* Product name */}
      <div className="space-y-1.5">
        <label className="text-sm font-medium text-slate-700">
          Product name <span className="text-danger">*</span>
        </label>
        <div className="relative">
          <Package size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <input
            {...register('product_name')}
            style={{ color: '#000000' }}
            className={`w-full h-10 pl-9 pr-3 text-sm border rounded-lg bg-white
                       focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary
                       transition-all duration-150 placeholder:text-slate-400
                       ${errors.product_name ? 'border-danger focus:ring-red-100' : 'border-slate-200'}`}
            placeholder="e.g. Steel Rods"
          />
        </div>
        {errors.product_name && (
          <p className="text-xs text-danger font-medium">{errors.product_name.message}</p>
        )}
      </div>

      {/* Quantity */}
      <div className="space-y-1.5">
        <label className="text-sm font-medium text-slate-700">
          Quantity <span className="text-danger">*</span>
        </label>
        <div className="relative">
          <Hash size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <input
            type="number"
            min={1}
            {...register('quantity', { valueAsNumber: true })}
            style={{ color: '#000000' }}
            className={`w-full h-10 pl-9 pr-3 text-sm border rounded-lg bg-white
                       focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary
                       transition-all duration-150 placeholder:text-slate-400
                       ${errors.quantity ? 'border-danger focus:ring-red-100' : 'border-slate-200'}`}
            placeholder="0"
          />
        </div>
        {errors.quantity && (
          <p className="text-xs text-danger font-medium">{errors.quantity.message}</p>
        )}
      </div>

      {/* Submit */}
      <div className="pt-2 flex gap-3">
        <Button
          type="submit"
          className="flex-1"
          isLoading={isLoading}
          loadingText={initialData ? 'Saving…' : 'Adding…'}
        >
          {initialData ? 'Save Changes' : 'Add to Inventory'}
        </Button>
      </div>

    </form>
  );
};