"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import * as projectsApi from "@/lib/api/projects";

export function useProjects() {
  return useQuery({ queryKey: ["projects"], queryFn: projectsApi.listProjects, refetchInterval: 10_000 });
}

export function useProject(id: string) {
  return useQuery({ queryKey: ["project", id], queryFn: () => projectsApi.getProject(id), enabled: Boolean(id) });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: projectsApi.createProject,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: projectsApi.deleteProject,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<{ name: string; description: string }> }) =>
      projectsApi.updateProject(id, payload),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["project", id] });
    },
  });
}

export function useProjectFiles(projectId: string) {
  return useQuery({ queryKey: ["project-files", projectId], queryFn: () => projectsApi.listFiles(projectId), enabled: Boolean(projectId) });
}

export function useProjectResults(projectId: string, enabled = true) {
  return useQuery({
    queryKey: ["project-results", projectId],
    queryFn: () => projectsApi.getResults(projectId),
    enabled: Boolean(projectId) && enabled,
    retry: false,
  });
}

export function useProjectCameras(projectId: string, enabled = true) {
  return useQuery({
    queryKey: ["project-cameras", projectId],
    queryFn: () => projectsApi.listCameras(projectId),
    enabled: Boolean(projectId) && enabled,
  });
}

export function useProjectThermalImages(projectId: string, enabled = true) {
  return useQuery({
    queryKey: ["project-thermal", projectId],
    queryFn: () => projectsApi.listThermalImages(projectId),
    enabled: Boolean(projectId) && enabled,
  });
}

export function useProjectReports(projectId: string, enabled = true) {
  return useQuery({
    queryKey: ["project-reports", projectId],
    queryFn: () => projectsApi.listReports(projectId),
    enabled: Boolean(projectId) && enabled,
  });
}
