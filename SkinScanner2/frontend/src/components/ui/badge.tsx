import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'border-blue-500/40 bg-blue-500/10 text-blue-400',
        secondary: 'border-slate-200 bg-slate-100 text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300',
        risk0: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400',
        risk1: 'border-amber-500/40 bg-amber-500/10 text-amber-400',
        risk2: 'border-red-500/40 bg-red-500/10 text-red-400',
        destructive: 'border-red-500/40 bg-red-500/10 text-red-400',
      },
    },
    defaultVariants: { variant: 'default' },
  },
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
