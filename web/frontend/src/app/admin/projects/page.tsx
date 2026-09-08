"use client";

import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LoadingState } from "@/components/ui/states";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAdminProjects } from "@/hooks/use-admin";
import { formatDateTime } from "@/lib/utils";
import { PROJECT_STATUS_META, type ProjectStatus } from "@/types";

const STATUSES: ProjectStatus[] = ["DRAFT", "UPLOADING", "VALIDATING", "QUEUED", "PROCESSING", "COMPLETED", "FAILED", "ARCHIVED"];

export default function AdminProjectsPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<string>("ALL");
  const { data: projects = [], isLoading } = useAdminProjects({ search: search || undefined, status: status === "ALL" ? undefined : status });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Projects</h1>
        <p className="mt-1 text-muted-foreground">Every project across all users.</p>
      </div>

      <div className="flex flex-wrap gap-3">
        <Input placeholder="Search projects..." value={search} onChange={(e) => setSearch(e.target.value)} className="max-w-sm" />
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All statuses</SelectItem>
            {STATUSES.map((s) => (
              <SelectItem key={s} value={s}>
                {PROJECT_STATUS_META[s].label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <LoadingState label="Loading projects..." />
      ) : (
        <div className="overflow-hidden rounded-lg border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Owner</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Updated</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects.map((project) => (
                <TableRow key={project.id}>
                  <TableCell>{project.name}</TableCell>
                  <TableCell className="text-muted-foreground">{project.owner_email}</TableCell>
                  <TableCell>
                    <Badge tone={PROJECT_STATUS_META[project.status].tone === "neutral" ? "neutral" : (PROJECT_STATUS_META[project.status].tone as any)}>
                      {PROJECT_STATUS_META[project.status].label}
                    </Badge>
                  </TableCell>
                  <TableCell>{project.is_demo ? <Badge tone="info">Demo</Badge> : "Real"}</TableCell>
                  <TableCell className="text-muted-foreground">{formatDateTime(project.updated_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
