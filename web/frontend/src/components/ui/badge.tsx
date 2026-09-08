import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva("inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium", {
  variants: {
    tone: {
      neutral: "border-border bg-white/[0.04] text-muted",
      info: "border-brand/30 bg-brand/10 text-brand",
      success: "border-success/30 bg-success/10 text-success",
      warning: "border-warning/30 bg-warning/10 text-warning",
      danger: "border-danger/30 bg-danger/10 text-danger",
    },
  },
  defaultVariants: { tone: "neutral" },
});

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {
  dot?: boolean;
}

function Badge({ className, tone, dot, children, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ tone, className }))} {...props}>
      {dot && <span className={cn("h-1.5 w-1.5 rounded-full", {
        "bg-muted": tone === "neutral" || !tone,
        "bg-brand": tone === "info",
        "bg-success": tone === "success",
        "bg-warning": tone === "warning",
        "bg-danger": tone === "danger",
      })} />}
      {children}
    </span>
  );
}

export { Badge, badgeVariants };
