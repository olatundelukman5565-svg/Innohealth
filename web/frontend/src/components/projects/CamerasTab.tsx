"use client";

import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import dynamic from "next/dynamic";
import { Suspense, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/states";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { cn } from "@/lib/utils";
import type { Camera } from "@/types";

const CameraMarkers = dynamic(() => import("@/components/three/CameraMarkers").then((m) => m.CameraMarkers), { ssr: false });

const POSE_TONE = { PROVIDED: "success", ESTIMATED: "warning", REFINED: "info" } as const;

export function CamerasTab({ cameras }: { cameras: Camera[] }) {
  const [selected, setSelected] = useState<string | null>(null);

  // Camera positions are in the project's real-world scale, which varies a lot
  // between scans -- fit the preview camera to whatever that scale turns out to be
  // instead of assuming a fixed distance (a hard-coded distance left markers
  // outside the view frustum for real, larger-scale projects).
  const maxDistance = useMemo(() => {
    const distances = cameras.map((c) => Math.hypot(c.position[0], c.position[1], c.position[2]));
    return Math.max(...distances, 1);
  }, [cameras]);

  if (cameras.length === 0) {
    return <EmptyState title="No camera data yet" description="Camera poses will appear here once processing completes." />;
  }

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_1.2fr]">
      <div className="h-80 overflow-hidden rounded-lg border border-border bg-surface-secondary">
        <Canvas camera={{ position: [0, maxDistance * 0.4, maxDistance * 1.4], fov: 45, far: maxDistance * 10 }}>
          <ambientLight intensity={0.7} />
          <directionalLight position={[maxDistance, maxDistance, maxDistance]} intensity={0.6} />
          <mesh>
            <sphereGeometry args={[maxDistance * 0.15, 24, 24]} />
            <meshStandardMaterial color="#94a3b8" wireframe />
          </mesh>
          <Suspense fallback={null}>
            <CameraMarkers cameras={cameras} selectedId={selected} onSelect={(c) => setSelected(c.id)} showFrustums scale={maxDistance * 0.3} />
          </Suspense>
          <OrbitControls enableDamping minDistance={maxDistance * 0.2} maxDistance={maxDistance * 4} />
        </Canvas>
      </div>

      <div className="overflow-hidden rounded-lg border border-border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Camera</TableHead>
              <TableHead>Pose</TableHead>
              <TableHead>Confidence</TableHead>
              <TableHead>Reproj. Error</TableHead>
              <TableHead>Coverage</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {cameras.map((camera) => (
              <TableRow
                key={camera.id}
                onClick={() => setSelected(camera.id)}
                className={cn("cursor-pointer", selected === camera.id && "bg-brand-muted")}
              >
                <TableCell className="tabular-data">{camera.camera_key}</TableCell>
                <TableCell>
                  <Badge tone={POSE_TONE[camera.pose_source]}>{camera.pose_source}</Badge>
                </TableCell>
                <TableCell className="tabular-data">{(camera.confidence * 100).toFixed(0)}%</TableCell>
                <TableCell className="tabular-data">{camera.reprojection_error !== null ? camera.reprojection_error.toFixed(3) : "--"}</TableCell>
                <TableCell className="tabular-data">{camera.coverage_percent.toFixed(1)}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
