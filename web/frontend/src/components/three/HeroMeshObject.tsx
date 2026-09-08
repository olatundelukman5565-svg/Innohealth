"use client";

import { useFrame, useThree } from "@react-three/fiber";
import { useMemo, useRef, useState } from "react";
import * as THREE from "three";

import "./ThermalMaterial";

interface HeroMeshObjectProps {
  reducedMotion?: boolean;
  onHotspot?: (data: { temperature: number; position: [number, number, number] }) => void;
}

/** Deterministic pseudo-temperature used only to color the hero object -- illustrative, not real sensor data. */
function pseudoTemperature(point: THREE.Vector3): number {
  const t = Math.sin(point.x * 2.4) * 0.5 + Math.sin(point.y * 2.0 + point.z) * 0.3 + 0.5;
  return 18 + THREE.MathUtils.clamp(t, 0, 1) * (86 - 18);
}

export function HeroMeshObject({ reducedMotion, onHotspot }: HeroMeshObjectProps) {
  const groupRef = useRef<THREE.Group>(null);
  const materialRef = useRef<any>(null);
  const wireRef = useRef<THREE.LineSegments>(null);
  const { pointer } = useThree();
  const [hovered, setHovered] = useState(false);

  const geometry = useMemo(() => {
    const geo = new THREE.IcosahedronGeometry(1.6, 5);
    const position = geo.attributes.position;
    const vertex = new THREE.Vector3();
    for (let i = 0; i < position.count; i++) {
      vertex.fromBufferAttribute(position, i);
      const noise =
        Math.sin(vertex.x * 3.1 + vertex.y * 1.7) * 0.05 + Math.sin(vertex.z * 4.3 - vertex.x * 2.1) * 0.035;
      vertex.addScaledVector(vertex.clone().normalize(), noise);
      position.setXYZ(i, vertex.x, vertex.y, vertex.z);
    }
    geo.computeVertexNormals();
    return geo;
  }, []);

  const wireGeometry = useMemo(() => new THREE.WireframeGeometry(geometry), [geometry]);

  useFrame((state, delta) => {
    const speed = reducedMotion ? 0.03 : 0.12;
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * speed;
      const targetX = reducedMotion ? 0 : pointer.y * 0.12;
      const targetZ = reducedMotion ? 0 : -pointer.x * 0.12;
      groupRef.current.rotation.x = THREE.MathUtils.lerp(groupRef.current.rotation.x, targetX, 0.04);
      groupRef.current.rotation.z = THREE.MathUtils.lerp(groupRef.current.rotation.z, targetZ, 0.04);
    }
    if (materialRef.current) {
      materialRef.current.uTime = state.clock.elapsedTime;
    }
  });

  return (
    <group ref={groupRef}>
      <mesh
        geometry={geometry}
        onClick={(event) => {
          event.stopPropagation();
          const point = event.point.clone();
          if (groupRef.current) groupRef.current.worldToLocal(point);
          const temperature = pseudoTemperature(point);
          onHotspot?.({ temperature, position: [point.x, point.y, point.z] });
        }}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <thermalMaterialImpl ref={materialRef} transparent side={THREE.DoubleSide} uOpacity={hovered ? 0.98 : 0.88} />
      </mesh>
      <lineSegments ref={wireRef} geometry={wireGeometry}>
        <lineBasicMaterial color="#67e8f9" transparent opacity={0.12} />
      </lineSegments>
    </group>
  );
}
