"use client";

import { useMemo } from "react";
import * as THREE from "three";

import { thermalColorAt } from "@/lib/thermal-colormap";

interface ThermalInspectionObjectProps {
  wireframe?: boolean;
  onSelectPoint?: (data: { temperature: number; position: [number, number, number] }) => void;
}

const BODY_SEGMENTS = 9;
const BODY_HALF_LENGTH = 1.35;
const BODY_RADIUS = 0.55;
const FLANGE_RADIUS = 0.82;
const FLANGE_HEIGHT = 0.16;
const BOLT_COUNT = 8;
const MIN_TEMP_C = 22;
const MAX_TEMP_C = 84;

/**
 * A static, non-decorative visualization of a thermally inspected pipe
 * segment: a hot mid-span cooling toward two bolted flanges. This stands in
 * for a real per-project reconstruction on marketing pages that have no
 * signed-in project to load -- the actual product's ThermalMeshViewer
 * (components/three/ThermalMeshViewer.tsx) renders the real per-vertex
 * temperature data baked into each project's GLB.
 */
export function ThermalInspectionObject({ wireframe, onSelectPoint }: ThermalInspectionObjectProps) {
  const segments = useMemo(() => {
    const segmentLength = (BODY_HALF_LENGTH * 2) / BODY_SEGMENTS;
    return Array.from({ length: BODY_SEGMENTS }, (_, i) => {
      const y = -BODY_HALF_LENGTH + segmentLength * (i + 0.5);
      const axial = y / BODY_HALF_LENGTH; // -1..1
      const t = Math.cos((axial * Math.PI) / 2); // 1 at center, 0 at ends
      const temperature = MIN_TEMP_C + t * (MAX_TEMP_C - MIN_TEMP_C);
      return { y, height: segmentLength * 1.02, t, temperature };
    });
  }, []);

  const bolts = useMemo(() => {
    return Array.from({ length: BOLT_COUNT }, (_, i) => {
      const angle = (i / BOLT_COUNT) * Math.PI * 2;
      return [Math.cos(angle) * (FLANGE_RADIUS - 0.12), Math.sin(angle) * (FLANGE_RADIUS - 0.12)] as [number, number];
    });
  }, []);

  return (
    <group>
      {segments.map((segment, i) => (
        <mesh
          key={i}
          position={[0, segment.y, 0]}
          onClick={(event) => {
            event.stopPropagation();
            onSelectPoint?.({ temperature: segment.temperature, position: [event.point.x, event.point.y, event.point.z] });
          }}
        >
          <cylinderGeometry args={[BODY_RADIUS, BODY_RADIUS, segment.height, 48, 1, false]} />
          {wireframe ? (
            <meshBasicMaterial color="#64748b" wireframe />
          ) : (
            <meshStandardMaterial color={thermalColorAt(segment.t)} roughness={0.55} metalness={0.12} />
          )}
        </mesh>
      ))}

      {[-1, 1].map((side) => (
        <group key={side} position={[0, side * (BODY_HALF_LENGTH + FLANGE_HEIGHT / 2), 0]}>
          <mesh>
            <cylinderGeometry args={[FLANGE_RADIUS, FLANGE_RADIUS, FLANGE_HEIGHT, 48]} />
            {wireframe ? (
              <meshBasicMaterial color="#64748b" wireframe />
            ) : (
              <meshStandardMaterial color="#8b93a1" roughness={0.35} metalness={0.55} />
            )}
          </mesh>
          {!wireframe &&
            bolts.map(([bx, bz], i) => (
              <mesh key={i} position={[bx, 0, bz]}>
                <cylinderGeometry args={[0.055, 0.055, FLANGE_HEIGHT * 1.4, 12]} />
                <meshStandardMaterial color="#3f4753" roughness={0.4} metalness={0.6} />
              </mesh>
            ))}
        </group>
      ))}
    </group>
  );
}
