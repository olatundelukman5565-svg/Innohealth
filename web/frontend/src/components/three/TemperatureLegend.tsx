import { formatTemperature } from "@/lib/utils";

interface TemperatureLegendProps {
  min: number | null;
  max: number | null;
  className?: string;
}

export function TemperatureLegend({ min, max, className }: TemperatureLegendProps) {
  return (
    <div className={`flex flex-col items-center gap-2 rounded-xl border border-white/10 bg-black/40 p-3 backdrop-blur-sm ${className ?? ""}`}>
      <span className="text-[10px] font-medium uppercase tracking-wider text-white/60">High</span>
      <div
        className="h-32 w-3 rounded-full"
        style={{
          background: "linear-gradient(to top, #3b82f6, #22d3ee, #22c55e, #eab308, #f97316, #ef4444)",
        }}
      />
      <span className="text-[10px] font-medium uppercase tracking-wider text-white/60">Low</span>
      <div className="mt-1 flex flex-col items-center gap-0.5 font-mono text-[10px] text-white/70">
        <span>{formatTemperature(max)}</span>
        <span className="text-white/30">to</span>
        <span>{formatTemperature(min)}</span>
      </div>
    </div>
  );
}
