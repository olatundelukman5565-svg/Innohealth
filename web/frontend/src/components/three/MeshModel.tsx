"use client";

import { useGLTF } from "@react-three/drei";
import type { ThreeEvent } from "@react-three/fiber";
import { useMemo } from "react";
import * as THREE from "three";

export type DisplayMode = "solid" | "wireframe" | "thermal" | "pointcloud" | "normals";

interface MeshModelProps {
  url: string;
  displayMode: DisplayMode;
  onPick?: (point: [number, number, number]) => void;
}

export function MeshModel({ url, displayMode, onPick }: MeshModelProps) {
  const gltf = useGLTF(url);

  const { geometry, texture } = useMemo(() => {
    let geo: THREE.BufferGeometry | null = null;
    let tex: THREE.Texture | null = null;
    gltf.scene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh && !geo) {
        const mesh = child as THREE.Mesh;
        geo = mesh.geometry;
        const material = mesh.material as THREE.MeshStandardMaterial;
        tex = material?.map ?? null;
      }
    });
    return { geometry: geo, texture: tex };
  }, [gltf]);

  if (!geometry) return null;

  const handleClick = (event: ThreeEvent<MouseEvent>) => {
    event.stopPropagation();
    onPick?.([event.point.x, event.point.y, event.point.z]);
  };

  if (displayMode === "pointcloud") {
    return (
      <points geometry={geometry} onClick={handleClick}>
        <pointsMaterial size={0.012} color="#22d3ee" sizeAttenuation />
      </points>
    );
  }

  return (
    <mesh geometry={geometry} onClick={handleClick}>
      {displayMode === "thermal" && texture && <meshStandardMaterial map={texture} roughness={0.6} metalness={0.05} />}
      {displayMode === "thermal" && !texture && <meshStandardMaterial color="#64748b" roughness={0.6} />}
      {displayMode === "solid" && <meshStandardMaterial color="#94a3b8" roughness={0.5} metalness={0.1} />}
      {displayMode === "wireframe" && <meshBasicMaterial color="#22d3ee" wireframe />}
      {displayMode === "normals" && <meshNormalMaterial />}
    </mesh>
  );
}
