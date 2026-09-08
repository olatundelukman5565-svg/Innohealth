import { cn } from "@/lib/utils";

/**
 * Geometric brand mark: a faceted mesh node crossed by a thermal gradient
 * arc -- 3D reconstruction + thermal imaging, deliberately not a medical
 * cross.
 */
export function Logo({ className, showWordmark = true }: { className?: string; showWordmark?: boolean }) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <svg width="28" height="28" viewBox="0 0 32 32" fill="none" className="shrink-0">
        <defs>
          <linearGradient id="logo-grad" x1="2" y1="28" x2="30" y2="4" gradientUnits="userSpaceOnUse">
            <stop stopColor="#3b82f6" />
            <stop offset="0.5" stopColor="#22d3ee" />
            <stop offset="1" stopColor="#f97316" />
          </linearGradient>
        </defs>
        <path d="M16 2L29 9V23L16 30L3 23V9L16 2Z" stroke="url(#logo-grad)" strokeWidth="1.6" strokeLinejoin="round" />
        <path d="M16 2V16M16 16L29 9M16 16L3 9M16 16V30M16 16L29 23M16 16L3 23" stroke="url(#logo-grad)" strokeWidth="1" strokeOpacity="0.5" />
        <circle cx="16" cy="16" r="3.2" fill="url(#logo-grad)" />
      </svg>
      {showWordmark && (
        <span className="text-sm font-semibold tracking-tight text-foreground">
          Innohealth <span className="text-muted-foreground font-normal">ThermalMesh</span>
        </span>
      )}
    </div>
  );
}
