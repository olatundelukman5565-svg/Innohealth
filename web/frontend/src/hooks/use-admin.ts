"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import * as adminApi from "@/lib/api/admin";

export function useAdminOverview() {
  return useQuery({ queryKey: ["admin-overview"], queryFn: adminApi.getOverview, refetchInterval: 15_000 });
}

export function useAdminUsers(search?: string) {
  return useQuery({ queryKey: ["admin-users", search], queryFn: () => adminApi.listUsers(search) });
}

export function useCreateAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: adminApi.createUser, onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-users"] }) });
}

export function useUpdateAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof adminApi.updateUser>[1] }) => adminApi.updateUser(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-users"] }),
  });
}

export function useAdminProjects(params: { status?: string; search?: string } = {}) {
  return useQuery({ queryKey: ["admin-projects", params], queryFn: () => adminApi.listAllProjects(params) });
}

export function useAdminJobs(status?: string) {
  return useQuery({ queryKey: ["admin-jobs", status], queryFn: () => adminApi.listJobs(status), refetchInterval: 5_000 });
}

export function useAdminJob(id: string | null) {
  return useQuery({ queryKey: ["admin-job", id], queryFn: () => adminApi.getJob(id as string), enabled: Boolean(id) });
}

export function useAdminAuditLogs(limit = 100) {
  return useQuery({ queryKey: ["admin-audit", limit], queryFn: () => adminApi.listAuditLogs(limit) });
}

export function useAdminSystemHealth() {
  return useQuery({ queryKey: ["admin-system"], queryFn: adminApi.getSystemHealth, refetchInterval: 10_000 });
}

export function useAdminSettings() {
  return useQuery({ queryKey: ["admin-settings"], queryFn: adminApi.getSettings });
}
