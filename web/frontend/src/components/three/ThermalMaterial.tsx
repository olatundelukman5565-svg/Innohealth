"use client";

import { shaderMaterial } from "@react-three/drei";
import { extend, type ThreeElements } from "@react-three/fiber";
import * as THREE from "three";

/**
 * Procedural thermal-gradient shader used for hero/marketing objects (no
 * real temperature data backs this -- it is a visual motif, not a
 * measurement). The actual project viewer instead uses the GLB's baked
 * texture, which *is* derived from real per-vertex temperature data (see
 * docs/thermal_mapping.md in the Python engine).
 */
const ThermalMaterialImpl = shaderMaterial(
  {
    uTime: 0,
    uOpacity: 0.92,
    uScanSpeed: 0.15,
    uColorCold: new THREE.Color("#3b82f6"),
    uColorMid: new THREE.Color("#22c55e"),
    uColorHot: new THREE.Color("#f97316"),
    uColorExtreme: new THREE.Color("#ef4444"),
  },
  /* glsl */ `
    varying vec3 vNormal;
    varying vec3 vPosition;
    void main() {
      vNormal = normalize(normalMatrix * normal);
      vPosition = position;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  /* glsl */ `
    uniform float uTime;
    uniform float uOpacity;
    uniform float uScanSpeed;
    uniform vec3 uColorCold;
    uniform vec3 uColorMid;
    uniform vec3 uColorHot;
    uniform vec3 uColorExtreme;
    varying vec3 vNormal;
    varying vec3 vPosition;

    vec3 thermalRamp(float t) {
      t = clamp(t, 0.0, 1.0);
      if (t < 0.4) return mix(uColorCold, uColorMid, t / 0.4);
      if (t < 0.7) return mix(uColorMid, uColorHot, (t - 0.4) / 0.3);
      return mix(uColorHot, uColorExtreme, (t - 0.7) / 0.3);
    }

    void main() {
      float wave = sin(vPosition.y * 2.4 + uTime * uScanSpeed * 6.0) * 0.5 + 0.5;
      float wave2 = sin(vPosition.x * 3.1 - uTime * uScanSpeed * 4.0) * 0.5 + 0.5;
      float t = clamp(wave * 0.6 + wave2 * 0.4, 0.0, 1.0);

      vec3 color = thermalRamp(t);

      float fresnel = pow(1.0 - abs(dot(normalize(vNormal), vec3(0.0, 0.0, 1.0))), 2.2);
      color += fresnel * 0.35;

      float scan = smoothstep(0.0, 0.02, 0.02 - abs(fract(vPosition.y * 0.5 - uTime * uScanSpeed) - 0.5) * 2.0);
      color += scan * 0.4;

      gl_FragColor = vec4(color, uOpacity);
    }
  `
);

extend({ ThermalMaterialImpl });

declare module "@react-three/fiber" {
  interface ThreeElements {
    thermalMaterialImpl: ThreeElements["shaderMaterial"] & {
      uTime?: number;
      uOpacity?: number;
      uScanSpeed?: number;
      uColorCold?: THREE.Color | string;
      uColorMid?: THREE.Color | string;
      uColorHot?: THREE.Color | string;
      uColorExtreme?: THREE.Color | string;
    };
  }
}

export { ThermalMaterialImpl };
