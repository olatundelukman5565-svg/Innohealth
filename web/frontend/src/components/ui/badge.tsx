import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva("inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium", {
  variants: {
    tone: {
      neutral: "border-border bg-surface-secondary text-muted-foreground",
      info: "border-info/20 bg-info-bg text-info",
      success: "border-success/20 bg-success-bg text-success",
      warning: "border-warning/20 bg-warning-bg text-warning",
      danger: "border-danger/20 bg-danger-bg text-danger",
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
      {dot && (
        <span
          className={cn("h-1.5 w-1.5 rounded-full", {
            "bg-muted-foreground": tone === "neutral" || !tone,
            "bg-info": tone === "info",
            "bg-success": tone === "success",
            "bg-warning": tone === "warning",
            "bg-danger": tone === "danger",
          })}
        />
      )}
      {children}
    </span>
  );
}

export { Badge, badgeVariants };
