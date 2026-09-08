import { apiFetch } from "./client";
import type { AdminJob, AdminOverview, AdminProject, AdminUser, AuditLogEntry, SystemHealth, UserRole } from "@/types";

export function getOverview() {
  return apiFetch<AdminOverview>("/api/admin/overview");
}

export function listUsers(search?: string) {
  const query = search ? `?search=${encodeURIComponent(search)}` : "";
  return apiFetch<AdminUser[]>(`/api/admin/users${query}`);
}

export function createUser(payload: { email: string; full_name: string; password: string; role: UserRole }) {
  return apiFetch<AdminUser>("/api/admin/users", { method: "POST", json: payload });
}

export function updateUser(id: string, payload: Partial<{ full_name: string; role: UserRole; is_active: boolean }>) {
  return apiFetch<AdminUser>(`/api/admin/users/${id}`, { method: "PATCH", json: payload });
}

export function listAllProjects(params: { status?: string; search?: string } = {}) {
  const search = new URLSearchParams();
  if (params.status) search.set("status", params.status);
  if (params.search) search.set("search", params.search);
  const query = search.toString();
  return apiFetch<AdminProject[]>(`/api/admin/projects${query ? `?${query}` : ""}`);
}

export function listJobs(status?: string) {
  const query = status ? `?status=${status}` : "";
  return apiFetch<AdminJob[]>(`/api/admin/jobs${query}`);
}

export function getJob(id: string) {
  return apiFetch<AdminJob>(`/api/admin/jobs/${id}`);
}

export function listAuditLogs(limit = 100) {
  return apiFetch<AuditLogEntry[]>(`/api/admin/audit?limit=${limit}`);
}

export function getSystemHealth() {
  return apiFetch<SystemHealth>("/api/admin/system");
}

export function getSettings() {
  return apiFetch<Record<string, unknown>>("/api/admin/settings");
}
