import { Box } from "lucide-react";

export function WebGLFallback({ message = "3D visualization requires WebGL" }: { message?: string }) {
  return (
    <div className="flex h-full min-h-[320px] w-full flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border bg-surface-secondary px-6 text-center">
      <Box className="h-8 w-8 text-muted-foreground" />
      <p className="text-sm font-medium">{message}</p>
      <p className="max-w-sm text-xs text-muted-foreground">
        Your browser or device does not support WebGL, which this viewer needs to render 3D thermal models. Try a recent version
        of Chrome, Firefox, Edge, or Safari, or check that hardware acceleration is enabled.
      </p>
    </div>
  );
}
