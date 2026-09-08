"use client";

import { Html, Line } from "@react-three/drei";
import * as THREE from "three";

import type { Camera } from "@/types";

const POSE_COLOR: Record<Camera["pose_source"], string> = {
  PROVIDED: "#22c55e",
  ESTIMATED: "#eab308",
  REFINED: "#22d3ee",
};

interface CameraMarkersProps {
  cameras: Camera[];
  selectedId: string | null;
  onSelect: (camera: Camera) => void;
  showFrustums?: boolean;
  visibleKeys?: Set<string> | null;
  /** Scales marker size and frustum line length -- pass the scene's real
   * scale (e.g. based on camera distance from the origin) so markers stay
   * visible whether the project is a tabletop object or a large space. */
  scale?: number;
}

export function CameraMarkers({ cameras, selectedId, onSelect, showFrustums, visibleKeys, scale = 1 }: CameraMarkersProps) {
  return (
    <group>
      {cameras.map((camera) => {
        const visible = !visibleKeys || visibleKeys.has(camera.camera_key);
        if (!visible) return null;
        const color = POSE_COLOR[camera.pose_source] ?? "#94a3b8";
        const isSelected = camera.id === selectedId;
        const position = camera.position;

        const forward = new THREE.Vector3(0, 0, 1).applyMatrix3(
          new THREE.Matrix3().set(
            camera.rotation[0][0], camera.rotation[1][0], camera.rotation[2][0],
            camera.rotation[0][1], camera.rotation[1][1], camera.rotation[2][1],
            camera.rotation[0][2], camera.rotation[1][2], camera.rotation[2][2]
          )
        );
        const frustumLength = scale * 0.35;
        const target: [number, number, number] = [
          position[0] - forward.x * frustumLength,
          position[1] - forward.y * frustumLength,
          position[2] - forward.z * frustumLength,
        ];

        return (
          <group key={camera.id}>
            <mesh position={position} onClick={(e) => { e.stopPropagation(); onSelect(camera); }}>
              <octahedronGeometry args={[(isSelected ? 0.09 : 0.06) * scale, 0]} />
              <meshStandardMaterial color={color} emissive={color} emissiveIntensity={isSelected ? 1.2 : 0.4} />
            </mesh>
            {showFrustums && <Line points={[position, target]} color={color} lineWidth={1} transparent opacity={0.6} />}
            {isSelected && (
              <Html position={position} distanceFactor={8} zIndexRange={[20, 0]}>
                <div className="pointer-events-none -translate-y-8 whitespace-nowrap rounded-md border border-white/10 bg-black/70 px-2 py-1 font-mono text-[10px] text-white/90 backdrop-blur-sm">
                  {camera.camera_key}
                </div>
              </Html>
            )}
          </group>
        );
      })}
    </group>
  );
}
