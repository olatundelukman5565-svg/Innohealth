import { Cpu, Database, GitBranch, Globe2, ShieldCheck, Sparkles } from "lucide-react";

const FEATURES = [
  {
    icon: Sparkles,
    title: "Real numerical truth",
    description: "Raw temperature values stay authoritative end-to-end -- colorized textures are visualization only, never the source of truth.",
  },
  {
    icon: GitBranch,
    title: "Automatic camera alignment",
    description: "Camera location alone is enough. Pose estimation and refinement handle orientation automatically, with confidence scoring.",
  },
  {
    icon: Cpu,
    title: "Full processing transparency",
    description: "Watch every stage -- alignment, projection, occlusion, blending -- run live with real progress, not a spinner.",
  },
  {
    icon: Database,
    title: "Structured, exportable data",
    description: "Vertex, face, and point-cloud temperature data available as CSV, NumPy, JSON, and HDF5 -- ready for downstream analysis.",
  },
  {
    icon: Globe2,
    title: "Web-native 3D delivery",
    description: "Every reconstruction is exported to GLB/GLTF for instant, dependency-free viewing in any modern browser.",
  },
  {
    icon: ShieldCheck,
    title: "Built for real workflows",
    description: "Role-based access, audit logging, and a processing job architecture designed to scale beyond a single machine.",
  },
];

export function FeatureGrid() {
  return (
    <section className="mx-auto max-w-7xl px-6 py-24">
      <div className="mb-14 max-w-2xl">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-brand">Why Innohealth ThermalMesh</p>
        <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">Built for scientific rigor, designed like modern software</h2>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((feature) => {
          const Icon = feature.icon;
          return (
            <div key={feature.title} className="rounded-lg border border-border bg-surface p-6 shadow-card transition-colors hover:border-brand/30">
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-md border border-brand/20 bg-brand-muted text-brand">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="text-base font-semibold text-foreground">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{feature.description}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
