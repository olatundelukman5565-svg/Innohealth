"use client";

import { Canvas } from "@react-three/fiber";
import { RotateCcw } from "lucide-react";
import { Suspense, useState } from "react";

import { AnnotationLabel } from "./AnnotationLabel";
import { HeroMeshObject } from "./HeroMeshObject";
import { ParticleField } from "./ParticleField";
import { WebGLFallback } from "./WebGLFallback";
import { useReducedMotion } from "@/hooks/use-reduced-motion";
import { useWebGLSupport } from "@/hooks/use-webgl";
import { formatTemperature } from "@/lib/utils";

const LABELS: { position: [number, number, number]; label: string; value?: string; delay: number }[] = [
  { position: [1.9, 1.1, 0.4], label: "Thermal Field", delay: 200 },
  { position: [-2.0, -0.6, 0.6], label: "3D Geometry", delay: 400 },
  { position: [0.2, -1.7, 1.2], label: "Temperature", value: "72.4°C", delay: 600 },
  { position: [1.6, -0.9, -1.3], label: "Camera 04", delay: 800 },
];

export function HeroScene() {
  const reducedMotion = useReducedMotion();
  const webglSupported = useWebGLSupport();
  const [hotspot, setHotspot] = useState<{ temperature: number } | null>(null);
  const [resetKey, setResetKey] = useState(0);

  if (webglSupported === false) {
    return <WebGLFallback message="Interactive 3D preview unavailable" />;
  }

  return (
    <div className="relative h-full w-full">
      <Canvas
        key={resetKey}
        dpr={[1, 1.75]}
        camera={{ position: [0, 0, 6], fov: 42 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[5, 4, 5]} intensity={40} color="#67e8f9" />
        <pointLight position={[-5, -3, -4]} intensity={20} color="#a78bfa" />
        <Suspense fallback={null}>
          <HeroMeshObject reducedMotion={reducedMotion} onHotspot={setHotspot} />
          {!reducedMotion && <ParticleField />}
          {LABELS.map((item) => (
            <AnnotationLabel key={item.label} {...item} />
          ))}
        </Suspense>
      </Canvas>

      {hotspot && (
        <div className="pointer-events-none absolute left-1/2 top-4 -translate-x-1/2 rounded-full border border-brand/30 bg-black/60 px-4 py-1.5 font-mono text-xs text-brand backdrop-blur-sm animate-fade-up">
          Reading: {formatTemperature(hotspot.temperature)}
        </div>
      )}

      <button
        type="button"
        onClick={() => {
          setResetKey((k) => k + 1);
          setHotspot(null);
        }}
        className="absolute bottom-4 right-4 flex items-center gap-1.5 rounded-full border border-white/10 bg-black/40 px-3 py-1.5 text-xs text-white/70 backdrop-blur-sm transition-colors hover:text-white"
      >
        <RotateCcw className="h-3 w-3" /> Reset view
      </button>
    </div>
  );
}
