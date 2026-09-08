import { formatTemperature } from "@/lib/utils";
import { thermalCssGradient } from "@/lib/thermal-colormap";
import { cn } from "@/lib/utils";

interface TemperatureLegendProps {
  min: number | null;
  max: number | null;
  className?: string;
}

export function TemperatureLegend({ min, max, className }: TemperatureLegendProps) {
  return (
    <div className={cn("flex flex-col items-center gap-2 rounded-md border border-border bg-surface p-3 shadow-card", className)}>
      <span className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">High</span>
      <div className="h-32 w-3 rounded-full" style={{ background: thermalCssGradient() }} />
      <span className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">Low</span>
      <div className="mt-1 flex flex-col items-center gap-0.5 tabular-data text-[10px] text-foreground">
        <span>{formatTemperature(max)}</span>
        <span className="text-muted-foreground">to</span>
        <span>{formatTemperature(min)}</span>
      </div>
    </div>
  );
}
