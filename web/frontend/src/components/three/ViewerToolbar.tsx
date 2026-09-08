"use client";

import { Box, Grid3x3, RotateCcw, Sparkles, Thermometer, Video } from "lucide-react";

import { cn } from "@/lib/utils";
import type { DisplayMode } from "./MeshModel";

const MODES: { value: DisplayMode; label: string; icon: React.ReactNode }[] = [
  { value: "thermal", label: "Thermal", icon: <Thermometer className="h-3.5 w-3.5" /> },
  { value: "solid", label: "Solid", icon: <Box className="h-3.5 w-3.5" /> },
  { value: "wireframe", label: "Wireframe", icon: <Grid3x3 className="h-3.5 w-3.5" /> },
  { value: "pointcloud", label: "Points", icon: <Sparkles className="h-3.5 w-3.5" /> },
  { value: "normals", label: "Normals", icon: <Video className="h-3.5 w-3.5" /> },
];

interface ViewerToolbarProps {
  mode: DisplayMode;
  onModeChange: (mode: DisplayMode) => void;
  showCameras: boolean;
  onToggleCameras: () => void;
  showFrustums: boolean;
  onToggleFrustums: () => void;
  onReset: () => void;
}

export function ViewerToolbar({ mode, onModeChange, showCameras, onToggleCameras, showFrustums, onToggleFrustums, onReset }: ViewerToolbarProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 rounded-xl border border-white/10 bg-black/40 p-1.5 backdrop-blur-sm">
      {MODES.map((item) => (
        <button
          key={item.value}
          type="button"
          onClick={() => onModeChange(item.value)}
          className={cn(
            "flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-white/60 transition-colors hover:text-white",
            mode === item.value && "bg-white/[0.1] text-white"
          )}
        >
          {item.icon}
          {item.label}
        </button>
      ))}
      <div className="mx-1 h-5 w-px bg-white/10" />
      <button
        type="button"
        onClick={onToggleCameras}
        className={cn("rounded-lg px-2.5 py-1.5 text-xs font-medium text-white/60 hover:text-white", showCameras && "bg-white/[0.1] text-white")}
      >
        Cameras
      </button>
      <button
        type="button"
        onClick={onToggleFrustums}
        className={cn("rounded-lg px-2.5 py-1.5 text-xs font-medium text-white/60 hover:text-white", showFrustums && "bg-white/[0.1] text-white")}
      >
        Frustums
      </button>
      <div className="mx-1 h-5 w-px bg-white/10" />
      <button type="button" onClick={onReset} className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-white/60 hover:text-white">
        <RotateCcw className="h-3.5 w-3.5" /> Reset
      </button>
    </div>
  );
}
