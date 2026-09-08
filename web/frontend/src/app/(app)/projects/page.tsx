"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Plus, Search } from "lucide-react";
import { useMemo, useState } from "react";

import { ProjectsTable } from "@/components/projects/ProjectsTable";
import { Button } from "@/components/ui/button";
import { EmptyState, LoadingState } from "@/components/ui/states";
import { cn } from "@/lib/utils";
import { useProjects } from "@/hooks/use-projects";
import type { ProjectStatus } from "@/types";

type FilterKey = "ALL" | "PROCESSING" | "COMPLETED" | "FAILED" | "DRAFT";

const FILTERS: { key: FilterKey; label: string; statuses?: ProjectStatus[] }[] = [
  { key: "ALL", label: "All" },
  { key: "PROCESSING", label: "Processing", statuses: ["QUEUED", "PROCESSING", "UPLOADING", "VALIDATING"] },
  { key: "COMPLETED", label: "Completed", statuses: ["COMPLETED"] },
  { key: "FAILED", label: "Failed", statuses: ["FAILED"] },
  { key: "DRAFT", label: "Draft", statuses: ["DRAFT"] },
];

export default function ProjectsPage() {
  const { data: projects = [], isLoading } = useProjects();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState(searchParams.get("q") ?? "");
  const [filter, setFilter] = useState<FilterKey>("ALL");

  const filtered = useMemo(() => {
    const activeFilter = FILTERS.find((f) => f.key === filter);
    return projects.filter((p) => {
      const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase());
      const matchesFilter = !activeFilter?.statuses || activeFilter.statuses.includes(p.status);
      return matchesSearch && matchesFilter;
    });
  }, [projects, search, filter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Projects</h1>
          <p className="mt-1 text-muted-foreground">Manage thermal mesh reconstruction projects.</p>
        </div>
        <Button asChild>
          <Link href="/projects/new">
            <Plus className="h-4 w-4" /> New Project
          </Link>
        </Button>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-1 rounded-md border border-border bg-surface p-1">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={cn(
                "rounded-sm px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground",
                filter === f.key && "bg-brand-muted text-brand"
              )}
            >
              {f.label}
            </button>
          ))}
        </div>
        <div className="relative w-full max-w-xs">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <input
            placeholder="Search projects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-9 w-full rounded-md border border-input bg-surface pl-8 pr-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-brand"
          />
        </div>
      </div>

      {isLoading ? (
        <LoadingState label="Loading projects..." />
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No thermal projects have been created."
          description={search || filter !== "ALL" ? "No projects match your filters." : "Create your first project to get started."}
          action={
            !search && filter === "ALL" && (
              <Button asChild size="sm">
                <Link href="/projects/new">Create your first project</Link>
              </Button>
            )
          }
        />
      ) : (
        <div className="rounded-lg border border-border bg-surface shadow-card">
          <ProjectsTable projects={filtered} variant="list" />
        </div>
      )}
    </div>
  );
}
