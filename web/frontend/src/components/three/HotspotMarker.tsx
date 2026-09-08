"use client";

import { Html } from "@react-three/drei";

import { formatTemperature } from "@/lib/utils";
import type { VertexTemperatureRow } from "@/types";

interface HotspotMarkerProps {
  point: [number, number, number];
  row: VertexTemperatureRow | null;
  showLabel?: boolean;
}

export function HotspotMarker({ point, row, showLabel = true }: HotspotMarkerProps) {
  return (
    <group position={point}>
      <mesh>
        <sphereGeometry args={[0.025, 16, 16]} />
        <meshBasicMaterial color="#1d4ed8" />
      </mesh>
      <mesh>
        <ringGeometry args={[0.04, 0.05, 32]} />
        <meshBasicMaterial color="#1d4ed8" transparent opacity={0.6} side={2} />
      </mesh>
      {showLabel && <Html distanceFactor={6} zIndexRange={[30, 0]} position={[0, 0.08, 0]}>
        <div className="pointer-events-none w-44 -translate-x-1/2 rounded-md border border-border bg-surface p-3 tabular-data text-[11px] text-foreground shadow-popover">
          {row ? (
            <>
              <div className="mb-1 flex items-baseline justify-between">
                <span className="text-muted-foreground">Temp</span>
                <span className="text-sm font-semibold text-brand">{formatTemperature(row.temperature)}</span>
              </div>
              <div className="flex items-baseline justify-between">
                <span className="text-muted-foreground">Confidence</span>
                <span>{(row.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="flex items-baseline justify-between">
                <span className="text-muted-foreground">Observations</span>
                <span>{row.observations}</span>
              </div>
              <div className="mt-1 border-t border-border pt-1 text-[10px] text-muted-foreground">
                {row.x.toFixed(3)}, {row.y.toFixed(3)}, {row.z.toFixed(3)}
              </div>
            </>
          ) : (
            <span className="text-muted-foreground">No temperature data at this point</span>
          )}
        </div>
      </Html>}
    </group>
  );
}
