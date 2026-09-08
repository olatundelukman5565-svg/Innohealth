"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import dynamic from "next/dynamic";
import { Suspense, useState } from "react";
import { motion } from "framer-motion";

import { TemperatureLegend } from "@/components/three/TemperatureLegend";
import { cn } from "@/lib/utils";

const ShowcaseObject = dynamic(() => import("@/components/three/ShowcaseObject").then((m) => m.ShowcaseObject), { ssr: false });

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
        <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-brand">3D + Thermal</p>
        <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">One interactive model. Full numerical truth underneath.</h2>
        <p className="mt-4 text-muted">Illustrative preview -- sign in to explore real project data in the full viewer.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.4fr_1fr]">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="relative h-[420px] overflow-hidden rounded-2xl border border-border bg-black/40"
        >
          <Canvas camera={{ position: [0, 0.4, 4.2], fov: 42 }}>
            <ambientLight intensity={0.6} />
            <pointLight position={[4, 4, 4]} intensity={30} color="#67e8f9" />
            <Suspense fallback={null}>
              <ShowcaseObject wireframe={wireframe} />
            </Suspense>
            <OrbitControls enableDamping dampingFactor={0.08} autoRotate={false} minDistance={2} maxDistance={7} />
          </Canvas>
          <div className="absolute right-4 top-4">
            <TemperatureLegend min={18.2} max={86.7} />
          </div>
          <button
            onClick={() => setWireframe((v) => !v)}
            className={cn(
              "absolute left-4 top-4 rounded-lg border border-white/10 bg-black/40 px-3 py-1.5 text-xs text-white/70 backdrop-blur-sm transition-colors hover:text-white",
              wireframe && "border-brand/40 text-brand"
            )}
          >
            {wireframe ? "Thermal view" : "Wireframe"}
          </button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="glass-panel grid grid-cols-2 gap-6 rounded-2xl p-6"
        >
          {STATS.map((stat) => (
            <div key={stat.label}>
              <p className="text-xs uppercase tracking-wide text-muted">{stat.label}</p>
              <p className="mt-1 font-mono text-2xl font-semibold">{stat.value}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
