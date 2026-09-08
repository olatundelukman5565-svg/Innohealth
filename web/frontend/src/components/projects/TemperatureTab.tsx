"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { LoadingState } from "@/components/ui/states";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import * as projectsApi from "@/lib/api/projects";
import { formatTemperature } from "@/lib/utils";

const PAGE_SIZE = 25;

export function TemperatureTab({ projectId }: { projectId: string }) {
  const [page, setPage] = useState(1);
  const [minTemp, setMinTemp] = useState("");
  const [maxTemp, setMaxTemp] = useState("");
  const [appliedFilter, setAppliedFilter] = useState<{ min?: number; max?: number }>({});

  const { data, isLoading } = useQuery({
    queryKey: ["temperature", projectId, page, appliedFilter],
    queryFn: () =>
      projectsApi.getTemperatureData(projectId, {
        page,
        page_size: PAGE_SIZE,
        min_temperature: appliedFilter.min,
        max_temperature: appliedFilter.max,
      }),
  });

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-3">
        <div className="space-y-1.5">
          <Label htmlFor="min-temp">Min temperature</Label>
          <Input id="min-temp" type="number" value={minTemp} onChange={(e) => setMinTemp(e.target.value)} className="w-32" placeholder="°C" />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="max-temp">Max temperature</Label>
          <Input id="max-temp" type="number" value={maxTemp} onChange={(e) => setMaxTemp(e.target.value)} className="w-32" placeholder="°C" />
        </div>
        <Button
          variant="secondary"
          onClick={() => {
            setPage(1);
            setAppliedFilter({ min: minTemp ? Number(minTemp) : undefined, max: maxTemp ? Number(maxTemp) : undefined });
          }}
        >
          Apply Filter
        </Button>
        {data && <p className="ml-auto text-xs text-muted-foreground">{data.total.toLocaleString()} vertices</p>}
      </div>

      {isLoading || !data ? (
        <LoadingState label="Loading temperature data..." />
      ) : (
        <>
          <div className="overflow-hidden rounded-lg border border-border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Vertex</TableHead>
                  <TableHead>X</TableHead>
                  <TableHead>Y</TableHead>
                  <TableHead>Z</TableHead>
                  <TableHead>Temperature</TableHead>
                  <TableHead>Confidence</TableHead>
                  <TableHead>Observations</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.rows.map((row) => (
                  <TableRow key={row.vertex_id}>
                    <TableCell className="tabular-data">{row.vertex_id}</TableCell>
                    <TableCell className="tabular-data">{row.x.toFixed(3)}</TableCell>
                    <TableCell className="tabular-data">{row.y.toFixed(3)}</TableCell>
                    <TableCell className="tabular-data">{row.z.toFixed(3)}</TableCell>
                    <TableCell className="tabular-data">{formatTemperature(row.temperature, 2)}</TableCell>
                    <TableCell className="tabular-data">{(row.confidence * 100).toFixed(0)}%</TableCell>
                    <TableCell className="tabular-data">{row.observations}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <div className="flex items-center justify-between text-sm">
            <p className="text-muted-foreground">
              Page {page} of {totalPages}
            </p>
            <div className="flex gap-2">
              <Button size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                Previous
              </Button>
              <Button size="sm" variant="secondary" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
