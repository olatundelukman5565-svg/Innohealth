"use client";

import { useQuery } from "@tanstack/react-query";

import * as projectsApi from "@/lib/api/projects";
import type { VertexTemperatureRow } from "@/types";

const PAGE_SIZE = 500;

/** Fetches every vertex temperature row for a project (fine for the small/demo
 * meshes this platform targets; see docs note on pagination for production scale). */
export function useAllVertexTemperatures(projectId: string | undefined, enabled = true) {
  return useQuery({
    queryKey: ["temperature-all", projectId],
    enabled: Boolean(projectId) && enabled,
    queryFn: async () => {
      const rows: VertexTemperatureRow[] = [];
      let page = 1;
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const result = await projectsApi.getTemperatureData(projectId as string, { page, page_size: PAGE_SIZE });
        rows.push(...result.rows);
        if (rows.length >= result.total || result.rows.length === 0) break;
        page += 1;
      }
      return rows;
    },
    staleTime: 60_000,
  });
}
