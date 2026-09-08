"use client";

import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Suspense, useMemo, useState } from "react";

import { CameraMarkers } from "./CameraMarkers";
import { HotspotMarker } from "./HotspotMarker";
import { DisplayMode, MeshModel } from "./MeshModel";
import { TemperatureLegend } from "./TemperatureLegend";
import { ViewerToolbar } from "./ViewerToolbar";
import { WebGLFallback } from "./WebGLFallback";
import { LoadingState } from "@/components/ui/states";
import { useAllVertexTemperatures } from "@/hooks/use-project-data";
import { useWebGLSupport } from "@/hooks/use-webgl";
import type { Camera, VertexTemperatureRow } from "@/types";

function nearestRow(rows: VertexTemperatureRow[], point: [number, number, number]): VertexTemperatureRow | null {
  if (!rows.length) return null;
  let best: VertexTemperatureRow | null = null;
  let bestDist = Infinity;
  for (const row of rows) {
    const dx = row.x - point[0];
    const dy = row.y - point[1];
    const dz = row.z - point[2];
    const dist = dx * dx + dy * dy + dz * dz;
    if (dist < bestDist) {
      bestDist = dist;
      best = row;
    }
  }
  return best;
}

interface ThermalMeshViewerProps {
  projectId: string;
  modelUrl: string | null;
  cameras: Camera[];
  minTemperature: number | null;
  maxTemperature: number | null;
}

export function ThermalMeshViewer({ projectId, modelUrl, cameras, minTemperature, maxTemperature }: ThermalMeshViewerProps) {
  const webglSupported = useWebGLSupport();
  const [mode, setMode] = useState<DisplayMode>("thermal");
  const [showCameras, setShowCameras] = useState(true);
  const [showFrustums, setShowFrustums] = useState(false);
  const [selectedCameraId, setSelectedCameraId] = useState<string | null>(null);
  const [resetKey, setResetKey] = useState(0);
  const [hotspot, setHotspot] = useState<{ point: [number, number, number]; row: VertexTemperatureRow | null } | null>(null);

  const { data: temperatureRows = [] } = useAllVertexTemperatures(projectId, Boolean(modelUrl));

  const handlePick = (point: [number, number, number]) => {
    setHotspot({ point, row: nearestRow(temperatureRows, point) });
  };

  if (webglSupported === false) {
    return <WebGLFallback message="3D thermal viewer unavailable" />;
  }

  if (!modelUrl) {
    return <LoadingState label="Waiting for the 3D model to be generated..." />;
  }

  return (
    <div className="relative h-full min-h-[420px] w-full overflow-hidden rounded-2xl border border-border bg-black/40">
      <Canvas key={resetKey} camera={{ position: [0, 0.6, 3.2], fov: 45 }} dpr={[1, 2]}>
        <ambientLight intensity={0.7} />
        <directionalLight position={[4, 6, 4]} intensity={1.1} />
        <directionalLight position={[-4, -2, -4]} intensity={0.4} />
        <Suspense fallback={null}>
          <MeshModel url={modelUrl} displayMode={mode} onPick={handlePick} />
          {showCameras && (
            <CameraMarkers cameras={cameras} selectedId={selectedCameraId} onSelect={(c) => setSelectedCameraId(c.id)} showFrustums={showFrustums} />
          )}
          {hotspot && <HotspotMarker point={hotspot.point} row={hotspot.row} />}
        </Suspense>
        <OrbitControls enableDamping dampingFactor={0.08} minDistance={0.8} maxDistance={10} />
      </Canvas>

      <div className="absolute left-4 top-4">
        <ViewerToolbar
          mode={mode}
          onModeChange={setMode}
          showCameras={showCameras}
          onToggleCameras={() => setShowCameras((v) => !v)}
          showFrustums={showFrustums}
          onToggleFrustums={() => setShowFrustums((v) => !v)}
          onReset={() => {
            setResetKey((k) => k + 1);
            setHotspot(null);
          }}
        />
      </div>

      <div className="absolute right-4 top-4">
        <TemperatureLegend min={minTemperature} max={maxTemperature} />
      </div>

      <p className="absolute bottom-3 left-4 text-[10px] text-white/40">Click the surface to inspect a point</p>
    </div>
  );
}
