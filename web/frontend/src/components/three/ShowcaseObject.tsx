"use client";

import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import * as THREE from "three";

import "./ThermalMaterial";

interface ShowcaseObjectProps {
  wireframe?: boolean;
}

/** A distinct geometric form from the hero object (torus knot) so different
 * sections of the site don't reuse the exact same 3D asset (spec section 10). */
export function ShowcaseObject({ wireframe }: ShowcaseObjectProps) {
  const groupRef = useRef<THREE.Group>(null);
  const materialRef = useRef<any>(null);

  useFrame((state, delta) => {
    if (groupRef.current) groupRef.current.rotation.y += delta * 0.18;
    if (materialRef.current) materialRef.current.uTime = state.clock.elapsedTime;
  });

  return (
    <group ref={groupRef}>
      <mesh>
        <torusKnotGeometry args={[1.05, 0.32, 220, 32]} />
        {wireframe ? (
          <meshBasicMaterial color="#22d3ee" wireframe />
        ) : (
          <thermalMaterialImpl ref={materialRef} transparent uOpacity={0.95} uScanSpeed={0.22} />
        )}
      </mesh>
    </group>
  );
}
