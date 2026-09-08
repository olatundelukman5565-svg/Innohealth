"use client";

import { Camera, Combine, Flame, Grid3x3, Layers, Scan, Sigma, Thermometer } from "lucide-react";
import { useState } from "react";

import { cn } from "@/lib/utils";

const STAGES = [
  { icon: Thermometer, title: "Thermal Images", detail: "Raw per-pixel temperature arrays from up to N thermal cameras -- CSV or numeric formats, never colorized first." },
  { icon: Camera, title: "Camera Pose Estimation", detail: "Camera locations are initialized, then automatically estimated and refined against the geometry." },
  { icon: Scan, title: "3D Alignment", detail: "Initial acquisition geometry is registered onto the final reconstructed mesh via PCA + ICP." },
  { icon: Layers, title: "Thermal Projection", detail: "Each thermal image is ray-projected onto the mesh independently, with occlusion checked via ray casting." },
  { icon: Sigma, title: "Temperature Mapping", detail: "Per-image observations are preserved, then blended with configurable distance/angle/confidence weighting." },
  { icon: Grid3x3, title: "UV Generation", detail: "Automatic UV unwrapping prepares the mesh for texture-space thermal layers -- no manual work required." },
  { icon: Combine, title: "Multi-View Blending", detail: "Overlapping thermal views are combined into a single coherent, confidence-weighted texture." },
  { icon: Flame, title: "3D Thermal Model", detail: "A web-ready GLB/GLTF model plus full numerical temperature data -- CSV, NumPy, JSON, HDF5." },
];

export function PipelineSection() {
  const [active, setActive] = useState(0);

  return (
    <section className="mx-auto max-w-7xl px-6 py-24">
      <div className="mb-14 max-w-2xl">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-brand">The Pipeline</p>
        <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">From raw thermal data to measurable 3D intelligence</h2>
        <p className="mt-4 text-muted-foreground">
          Every stage is a real, independently verifiable step -- not a black box. Hover or tap a stage to see what it does.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {STAGES.map((stage, index) => {
          const Icon = stage.icon;
          const isActive = active === index;
          return (
            <button
              key={stage.title}
              onMouseEnter={() => setActive(index)}
              onFocus={() => setActive(index)}
              onClick={() => setActive(index)}
              className="text-left"
            >
              <div
                className={cn(
                  "flex h-full flex-col gap-3 rounded-lg border p-4 transition-colors",
                  isActive ? "border-brand bg-brand-muted" : "border-border bg-surface hover:border-brand/40"
                )}
              >
                <div className={cn("flex h-9 w-9 items-center justify-center rounded-md border", isActive ? "border-brand/30 bg-surface text-brand" : "border-border text-muted-foreground")}>
                  <Icon className="h-4 w-4" />
                </div>
                <div>
                  <p className="tabular-data text-[10px] text-muted-foreground">{String(index + 1).padStart(2, "0")}</p>
                  <p className="text-sm font-medium leading-tight text-foreground">{stage.title}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      <div className="mt-6 rounded-lg border border-border bg-surface p-6 shadow-card">
        <p className="text-sm font-medium text-brand">{STAGES[active].title}</p>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">{STAGES[active].detail}</p>
      </div>
    </section>
  );
}
