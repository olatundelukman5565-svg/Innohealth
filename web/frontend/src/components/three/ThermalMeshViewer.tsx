"use client";

import { Grid, OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Suspense, useState } from "react";

import { CameraMarkers } from "./CameraMarkers";
import { HotspotMarker } from "./HotspotMarker";
import { DisplayMode, MeshModel } from "./MeshModel";
import { TemperatureLegend } from "./TemperatureLegend";
import { ViewerToolbar } from "./ViewerToolbar";
import { WebGLFallback } from "./WebGLFallback";
import { LoadingState } from "@/components/ui/states";
import { useAllVertexTemperatures } from "@/hooks/use-project-data";
import { useWebGLSupport } from "@/hooks/use-webgl";
import { formatTemperature } from "@/lib/utils";
import type { Camera, ProcessingResult, VertexTemperatureRow } from "@/types";

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
  /** "full" adds a right-side Model + Data Inspection panel for the dedicated 3D Viewer tab. */
  variant?: "embedded" | "full";
  results?: ProcessingResult;
}

export function ThermalMeshViewer({ projectId, modelUrl, cameras, minTemperature, maxTemperature, variant = "embedded", results }: ThermalMeshViewerProps) {
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

  const isFull = variant === "full";

  return (
    <div className={isFull ? "flex h-full min-h-[420px] w-full gap-4" : "relative h-full min-h-[420px] w-full"}>
      <div className="relative min-w-0 flex-1 overflow-hidden rounded-lg border border-border bg-surface-secondary">
        <Canvas key={resetKey} camera={{ position: [0, 0.6, 3.2], fov: 45 }} dpr={[1, 2]}>
          <ambientLight intensity={0.7} />
          <directionalLight position={[4, 6, 4]} intensity={1.1} />
          <directionalLight position={[-4, -2, -4]} intensity={0.4} />
          <Suspense fallback={null}>
            <MeshModel url={modelUrl} displayMode={mode} onPick={handlePick} />
            {showCameras && (
              <CameraMarkers cameras={cameras} selectedId={selectedCameraId} onSelect={(c) => setSelectedCameraId(c.id)} showFrustums={showFrustums} />
            )}
            {hotspot && <HotspotMarker point={hotspot.point} row={hotspot.row} showLabel={!isFull} />}
            <Grid
              position={[0, -0.9, 0]}
              args={[6, 6]}
              cellSize={0.25}
              cellThickness={0.4}
              cellColor="#d5dae1"
              sectionSize={1}
              sectionThickness={0.6}
              sectionColor="#b7bfc9"
              fadeDistance={6}
              infiniteGrid
            />
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

        <p className="absolute bottom-3 left-4 text-[10px] text-muted-foreground">Click the surface to inspect a point</p>
      </div>

      {isFull && (
        <div className="w-64 shrink-0 space-y-4 overflow-y-auto">
          <div className="rounded-lg border border-border bg-surface p-4 shadow-card">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Model</p>
            <dl className="space-y-2 text-sm">
              <InfoRow label="Mesh" value="Final Mesh" />
              <InfoRow label="Thermal" value="Temperature Map" />
              <InfoRow label="Camera Views" value={String(cameras.length)} />
              <InfoRow label="UV" value={results ? "Generated" : "--"} />
            </dl>
          </div>

          <div className="rounded-lg border border-border bg-surface p-4 shadow-card">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Data Inspection</p>
            {hotspot ? (
              hotspot.row ? (
                <dl className="space-y-2 text-sm">
                  <InfoRow label="Temperature" value={<span className="font-semibold text-brand">{formatTemperature(hotspot.row.temperature)}</span>} />
                  <InfoRow label="Confidence" value={`${(hotspot.row.confidence * 100).toFixed(1)}%`} />
                  <InfoRow label="Observations" value={String(hotspot.row.observations)} />
                  <div className="border-t border-border pt-2">
                    <p className="mb-1 text-xs text-muted-foreground">Coordinates</p>
                    <div className="grid grid-cols-3 gap-1 tabular-data text-xs">
                      <span>X {hotspot.row.x.toFixed(3)}</span>
                      <span>Y {hotspot.row.y.toFixed(3)}</span>
                      <span>Z {hotspot.row.z.toFixed(3)}</span>
                    </div>
                  </div>
                </dl>
              ) : (
                <p className="text-sm text-muted-foreground">No temperature data at this point.</p>
              )
            ) : (
              <p className="text-sm text-muted-foreground">Click a point on the model to inspect it.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="font-medium text-foreground">{value}</dd>
    </div>
  );
}
