"use client";

import { Grid, OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { RotateCcw } from "lucide-react";
import { Suspense, useState } from "react";

import { ThermalInspectionObject } from "./ThermalInspectionObject";
import { WebGLFallback } from "./WebGLFallback";
import { useWebGLSupport } from "@/hooks/use-webgl";
import { formatTemperature } from "@/lib/utils";

export function HeroScene() {
  const webglSupported = useWebGLSupport();
  const [reading, setReading] = useState<{ temperature: number } | null>(null);
  const [resetKey, setResetKey] = useState(0);

  if (webglSupported === false) {
    return <WebGLFallback message="Interactive 3D preview unavailable" />;
  }

  return (
    <div className="relative h-full w-full">
      <Canvas key={resetKey} dpr={[1, 1.75]} camera={{ position: [2.6, 1.4, 3.4], fov: 40 }} gl={{ antialias: true }}>
        <ambientLight intensity={0.7} />
        <directionalLight position={[4, 6, 3]} intensity={1.1} />
        <directionalLight position={[-4, -2, -3]} intensity={0.3} />
        <Suspense fallback={null}>
          <ThermalInspectionObject onSelectPoint={setReading} />
          <Grid
            position={[0, -1.6, 0]}
            args={[10, 10]}
            cellSize={0.5}
            cellThickness={0.5}
            cellColor="#d5dae1"
            sectionSize={2}
            sectionThickness={0.8}
            sectionColor="#b7bfc9"
            fadeDistance={9}
            infiniteGrid
          />
        </Suspense>
        <OrbitControls enableDamping dampingFactor={0.1} enablePan={false} minDistance={2.5} maxDistance={6} autoRotate={false} />
      </Canvas>

      {reading && (
        <div className="pointer-events-none absolute left-4 top-4 rounded-md border border-border bg-surface px-3 py-1.5 tabular-data text-xs text-foreground shadow-card">
          Reading: <span className="font-semibold text-brand">{formatTemperature(reading.temperature)}</span>
        </div>
      )}

      <button
        type="button"
        onClick={() => {
          setResetKey((k) => k + 1);
          setReading(null);
        }}
        className="absolute bottom-4 right-4 flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5 text-xs text-muted-foreground shadow-card transition-colors hover:text-foreground"
      >
        <RotateCcw className="h-3 w-3" /> Reset view
      </button>
      <p className="pointer-events-none absolute bottom-4 left-4 text-[11px] text-muted-foreground">Drag to rotate &middot; click surface to inspect</p>
    </div>
  );
}
