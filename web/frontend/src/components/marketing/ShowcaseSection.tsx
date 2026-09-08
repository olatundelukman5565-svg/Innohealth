"use client";

import { Grid, OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import dynamic from "next/dynamic";
import { Suspense, useState } from "react";

import { TemperatureLegend } from "@/components/three/TemperatureLegend";
import { cn } from "@/lib/utils";

const ThermalInspectionObject = dynamic(
  () => import("@/components/three/ThermalInspectionObject").then((m) => m.ThermalInspectionObject),
  { ssr: false }
);

const STATS = [
  { label: "Temperature", value: "72.4°C" },
  { label: "Min", value: "18.2°C" },
  { label: "Max", value: "86.7°C" },
  { label: "Average", value: "54.8°C" },
  { label: "Coverage", value: "94.7%" },
  { label: "Views", value: "12" },
];

export function ShowcaseSection() {
  const [wireframe, setWireframe] = useState(false);

  return (
    <section className="mx-auto max-w-7xl px-6 py-24">
      <div className="mb-10 max-w-2xl">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-brand">3D + Thermal</p>
        <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">One interactive model. Full numerical truth underneath.</h2>
        <p className="mt-4 text-muted-foreground">Illustrative preview -- sign in to explore real project data in the full viewer.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.4fr_1fr]">
        <div className="relative h-[420px] overflow-hidden rounded-lg border border-border bg-surface-secondary shadow-card">
          <Canvas camera={{ position: [2.4, 1.2, 3.2], fov: 40 }}>
            <ambientLight intensity={0.7} />
            <directionalLight position={[4, 6, 3]} intensity={1.1} />
            <directionalLight position={[-4, -2, -3]} intensity={0.3} />
            <Suspense fallback={null}>
              <ThermalInspectionObject wireframe={wireframe} />
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
            <OrbitControls enableDamping dampingFactor={0.08} autoRotate={false} enablePan={false} minDistance={2.2} maxDistance={6} />
          </Canvas>
          <div className="absolute right-4 top-4">
            <TemperatureLegend min={18.2} max={86.7} />
          </div>
          <button
            onClick={() => setWireframe((v) => !v)}
            className={cn(
              "absolute left-4 top-4 rounded-md border border-border bg-surface px-3 py-1.5 text-xs text-muted-foreground shadow-card transition-colors hover:text-foreground",
              wireframe && "border-brand/40 text-brand"
            )}
          >
            {wireframe ? "Thermal view" : "Wireframe"}
          </button>
        </div>

        <div className="grid grid-cols-2 gap-6 rounded-lg border border-border bg-surface p-6 shadow-card">
          {STATS.map((stat) => (
            <div key={stat.label}>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">{stat.label}</p>
              <p className="mt-1 tabular-data text-2xl font-semibold text-foreground">{stat.value}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
