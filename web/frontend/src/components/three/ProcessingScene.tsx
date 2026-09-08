"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Suspense, useMemo, useRef } from "react";
import * as THREE from "three";

import "./ThermalMaterial";
import type { ProcessingStageName } from "@/types";

interface ProcessingSceneProps {
  currentStage: ProcessingStageName | null;
  progressPercent: number;
}

const STAGE_INDEX: Record<ProcessingStageName, number> = {
  INPUT_VALIDATION: 0,
  MESH_ALIGNMENT: 1,
  CAMERA_POSE_ESTIMATION: 2,
  THERMAL_PROJECTION: 3,
  OCCLUSION_ANALYSIS: 4,
  TEMPERATURE_MAPPING: 5,
  UV_GENERATION: 6,
  THERMAL_BLENDING: 7,
  WEB_EXPORT: 8,
  REPORT_GENERATION: 9,
};

function Scene({ currentStage, progressPercent }: ProcessingSceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const materialRef = useRef<any>(null);
  const camerasRef = useRef<THREE.Group>(null);

  const geometry = useMemo(() => new THREE.IcosahedronGeometry(1.3, 4), []);
  const wireGeometry = useMemo(() => new THREE.WireframeGeometry(geometry), [geometry]);
  const cameraPositions = useMemo(() => {
    const positions: [number, number, number][] = [];
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2;
      positions.push([Math.cos(angle) * 2.4, Math.sin(angle * 0.6) * 0.6, Math.sin(angle) * 2.4]);
    }
    return positions;
  }, []);

  const stageIndex = currentStage ? STAGE_INDEX[currentStage] : 0;
  const camerasVisible = stageIndex >= STAGE_INDEX.CAMERA_POSE_ESTIMATION;
  const thermalProgress = THREE.MathUtils.clamp(
    (stageIndex - STAGE_INDEX.THERMAL_PROJECTION) / (STAGE_INDEX.WEB_EXPORT - STAGE_INDEX.THERMAL_PROJECTION),
    0,
    1
  );

  useFrame((state, delta) => {
    if (groupRef.current) groupRef.current.rotation.y += delta * 0.15;
    if (materialRef.current) {
      materialRef.current.uTime = state.clock.elapsedTime;
      materialRef.current.uOpacity = 0.15 + thermalProgress * 0.8;
    }
    if (camerasRef.current) {
      const targetScale = camerasVisible ? 1 : 0;
      camerasRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.08);
    }
  });

  return (
    <group ref={groupRef}>
      <mesh geometry={geometry}>
        <thermalMaterialImpl ref={materialRef} transparent side={THREE.DoubleSide} uOpacity={0.15} />
      </mesh>
      <lineSegments geometry={wireGeometry}>
        <lineBasicMaterial color="#67e8f9" transparent opacity={0.3} />
      </lineSegments>
      <group ref={camerasRef}>
        {cameraPositions.map((pos, i) => (
          <mesh key={i} position={pos}>
            <octahedronGeometry args={[0.08, 0]} />
            <meshStandardMaterial color="#eab308" emissive="#eab308" emissiveIntensity={0.6} />
          </mesh>
        ))}
      </group>
    </group>
  );
}

export function ProcessingScene(props: ProcessingSceneProps) {
  return (
    <Canvas camera={{ position: [0, 0.6, 4.5], fov: 42 }}>
      <ambientLight intensity={0.6} />
      <pointLight position={[4, 4, 4]} intensity={30} color="#67e8f9" />
      <Suspense fallback={null}>
        <Scene {...props} />
      </Suspense>
    </Canvas>
  );
}
