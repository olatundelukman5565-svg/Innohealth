"use client";

import { Html } from "@react-three/drei";

import { formatTemperature } from "@/lib/utils";
import type { VertexTemperatureRow } from "@/types";

interface HotspotMarkerProps {
  point: [number, number, number];
  row: VertexTemperatureRow | null;
}

export function HotspotMarker({ point, row }: HotspotMarkerProps) {
  return (
    <group position={point}>
      <mesh>
        <sphereGeometry args={[0.025, 16, 16]} />
        <meshBasicMaterial color="#22d3ee" />
      </mesh>
      <mesh>
        <ringGeometry args={[0.04, 0.05, 32]} />
        <meshBasicMaterial color="#22d3ee" transparent opacity={0.6} side={2} />
      </mesh>
      <Html distanceFactor={6} zIndexRange={[30, 0]} position={[0, 0.08, 0]}>
        <div className="pointer-events-none w-44 -translate-x-1/2 rounded-lg border border-brand/30 bg-black/80 p-3 font-mono text-[11px] text-white/90 shadow-glow backdrop-blur-sm">
          {row ? (
            <>
              <div className="mb-1 flex items-baseline justify-between">
                <span className="text-white/50">Temp</span>
                <span className="text-sm font-semibold text-brand">{formatTemperature(row.temperature)}</span>
              </div>
              <div className="flex items-baseline justify-between">
                <span className="text-white/50">Confidence</span>
                <span>{(row.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="flex items-baseline justify-between">
                <span className="text-white/50">Observations</span>
                <span>{row.observations}</span>
              </div>
              <div className="mt-1 border-t border-white/10 pt-1 text-[10px] text-white/40">
                {row.x.toFixed(3)}, {row.y.toFixed(3)}, {row.z.toFixed(3)}
              </div>
            </>
          ) : (
            <span className="text-white/50">No temperature data at this point</span>
          )}
        </div>
      </Html>
    </group>
  );
}
