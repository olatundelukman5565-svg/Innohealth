import { Camera, Thermometer } from "lucide-react";
import Link from "next/link";

import { StatusBadge } from "./StatusBadge";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate, formatPercent, formatTemperature } from "@/lib/utils";
import type { ProjectSummary } from "@/types";

export function ProjectCard({ project }: { project: ProjectSummary }) {
  return (
    <Link href={`/projects/${project.id}`}>
      <Card className="group h-full transition-all hover:border-white/20 hover:shadow-glow">
        <div className="relative flex h-28 items-center justify-center overflow-hidden rounded-t-2xl border-b border-border bg-gradient-to-br from-brand/10 via-transparent to-brand-secondary/10">
          <div className="absolute inset-0 bg-grid-fade opacity-70" />
          <Thermometer className="h-8 w-8 text-brand/70 transition-transform group-hover:scale-110" />
          {project.is_demo && (
            <span className="absolute right-3 top-3">
              <Badge tone="info">Synthetic Demo</Badge>
            </span>
          )}
        </div>
        <div className="space-y-3 p-5">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-medium leading-tight">{project.name}</h3>
            <StatusBadge status={project.status} />
          </div>
          <p className="line-clamp-2 text-xs text-muted">{project.description || "No description provided."}</p>
          {project.has_result ? (
            <div className="grid grid-cols-2 gap-2 border-t border-border pt-3 text-xs">
              <div>
                <p className="text-muted">Views</p>
                <p className="flex items-center gap-1 font-mono font-medium">
                  <Camera className="h-3 w-3" /> {project.num_views}
                </p>
              </div>
              <div>
                <p className="text-muted">Coverage</p>
                <p className="font-mono font-medium">{formatPercent(project.coverage_percent)}</p>
              </div>
              <div className="col-span-2">
                <p className="text-muted">Temperature range</p>
                <p className="font-mono font-medium">
                  {formatTemperature(project.min_temperature)} - {formatTemperature(project.max_temperature)}
                </p>
              </div>
            </div>
          ) : (
            <p className="border-t border-border pt-3 text-xs text-muted">Not processed yet</p>
          )}
          <p className="text-[10px] text-muted">Updated {formatDate(project.updated_at)}</p>
        </div>
      </Card>
    </Link>
  );
}
