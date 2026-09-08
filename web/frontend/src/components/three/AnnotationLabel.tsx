"use client";

import { Html } from "@react-three/drei";

interface AnnotationLabelProps {
  position: [number, number, number];
  label: string;
  value?: string;
  delay?: number;
}

export function AnnotationLabel({ position, label, value, delay = 0 }: AnnotationLabelProps) {
  return (
    <Html position={position} center distanceFactor={8} occlude={false} zIndexRange={[10, 0]}>
      <div
        className="pointer-events-none flex select-none flex-col items-start gap-0.5 whitespace-nowrap rounded-md border border-white/10 bg-black/40 px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-cyan-200/90 backdrop-blur-sm animate-fade-up"
        style={{ animationDelay: `${delay}ms` }}
      >
        <span className="flex items-center gap-1 text-cyan-300/70">
          <span className="h-1 w-1 rounded-full bg-cyan-300" /> {label}
        </span>
        {value && <span className="text-[11px] font-semibold text-white/90">{value}</span>}
      </div>
    </Html>
  );
}
