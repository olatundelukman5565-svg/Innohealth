"use client";

import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { Copy, FileText, FolderOpen, MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { StatusBadge } from "./StatusBadge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { toast } from "@/components/ui/toast";
import { useCreateProject, useDeleteProject, useUpdateProject } from "@/hooks/use-projects";
import { formatDate, formatTemperature } from "@/lib/utils";
import type { ProjectSummary } from "@/types";

interface ProjectsTableProps {
  projects: ProjectSummary[];
  variant?: "dashboard" | "list";
}

export function ProjectsTable({ projects, variant = "list" }: ProjectsTableProps) {
  const [renaming, setRenaming] = useState<ProjectSummary | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const deleteProject = useDeleteProject();
  const updateProject = useUpdateProject();
  const createProject = useCreateProject();

  const handleDelete = async (project: ProjectSummary) => {
    if (!confirm(`Delete "${project.name}"? This cannot be undone.`)) return;
    try {
      await deleteProject.mutateAsync(project.id);
      toast({ title: "Project deleted", tone: "success" });
    } catch {
      toast({ title: "Failed to delete project", tone: "danger" });
    }
  };

  const handleDuplicate = async (project: ProjectSummary) => {
    try {
      await createProject.mutateAsync({ name: `${project.name} (Copy)`, description: project.description });
      toast({ title: "Project duplicated", description: "The new project starts as a draft -- upload files to process it.", tone: "success" });
    } catch {
      toast({ title: "Failed to duplicate project", tone: "danger" });
    }
  };

  const handleRenameSubmit = async () => {
    if (!renaming || !renameValue.trim()) return;
    try {
      await updateProject.mutateAsync({ id: renaming.id, payload: { name: renameValue.trim() } });
      toast({ title: "Project renamed", tone: "success" });
      setRenaming(null);
    } catch {
      toast({ title: "Failed to rename project", tone: "danger" });
    }
  };

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Project</TableHead>
            <TableHead>Mesh</TableHead>
            <TableHead>Thermal Views</TableHead>
            <TableHead>Temperature Range</TableHead>
            {variant === "list" && <TableHead>Coverage</TableHead>}
            <TableHead>Status</TableHead>
            <TableHead>{variant === "dashboard" ? "Last Processed" : "Updated"}</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {projects.map((project) => (
            <TableRow key={project.id}>
              <TableCell>
                <Link href={`/projects/${project.id}`} className="font-medium text-foreground hover:text-brand">
                  {project.name}
                </Link>
              </TableCell>
              <TableCell className="text-muted-foreground">{project.has_result ? "Final Mesh" : "Not processed"}</TableCell>
              <TableCell className="tabular-data">{project.num_views}</TableCell>
              <TableCell className="tabular-data">
                {project.has_result ? `${formatTemperature(project.min_temperature)} - ${formatTemperature(project.max_temperature)}` : "--"}
              </TableCell>
              {variant === "list" && (
                <TableCell className="tabular-data">{project.coverage_percent !== null ? `${project.coverage_percent.toFixed(1)}%` : "--"}</TableCell>
              )}
              <TableCell>
                <StatusBadge status={project.status} />
              </TableCell>
              <TableCell className="text-muted-foreground">
                {formatDate(variant === "dashboard" ? project.last_processed_at : project.updated_at)}
              </TableCell>
              <TableCell className="text-right">
                <DropdownMenu.Root>
                  <DropdownMenu.Trigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenu.Trigger>
                  <DropdownMenu.Portal>
                    <DropdownMenu.Content align="end" sideOffset={4} className="z-50 min-w-40 rounded-md border border-border bg-surface p-1 shadow-popover">
                      <DropdownMenu.Item asChild>
                        <Link href={`/projects/${project.id}`} className="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-surface-secondary">
                          <FolderOpen className="h-3.5 w-3.5" /> Open
                        </Link>
                      </DropdownMenu.Item>
                      <DropdownMenu.Item asChild>
                        <Link
                          href={`/projects/${project.id}?tab=reports`}
                          className="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-surface-secondary"
                        >
                          <FileText className="h-3.5 w-3.5" /> View Report
                        </Link>
                      </DropdownMenu.Item>
                      <DropdownMenu.Item
                        onSelect={() => {
                          setRenaming(project);
                          setRenameValue(project.name);
                        }}
                        className="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-surface-secondary"
                      >
                        <Pencil className="h-3.5 w-3.5" /> Rename
                      </DropdownMenu.Item>
                      <DropdownMenu.Item
                        onSelect={() => handleDuplicate(project)}
                        className="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-surface-secondary"
                      >
                        <Copy className="h-3.5 w-3.5" /> Duplicate
                      </DropdownMenu.Item>
                      <DropdownMenu.Item
                        onSelect={() => handleDelete(project)}
                        className="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-danger hover:bg-danger-bg"
                      >
                        <Trash2 className="h-3.5 w-3.5" /> Delete
                      </DropdownMenu.Item>
                    </DropdownMenu.Content>
                  </DropdownMenu.Portal>
                </DropdownMenu.Root>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <Dialog open={Boolean(renaming)} onOpenChange={(open) => !open && setRenaming(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename project</DialogTitle>
          </DialogHeader>
          <div className="space-y-1.5">
            <Label htmlFor="rename-input">Project name</Label>
            <Input id="rename-input" value={renameValue} onChange={(e) => setRenameValue(e.target.value)} autoFocus />
          </div>
          <div className="mt-4 flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setRenaming(null)}>
              Cancel
            </Button>
            <Button onClick={handleRenameSubmit} disabled={updateProject.isPending}>
              Save
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
