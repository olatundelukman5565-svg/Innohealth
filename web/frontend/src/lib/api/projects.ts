import { apiFetch, sseUrl } from "./client";
import type {
  Camera,
  ProcessingJob,
  ProcessingResult,
  ProjectDetail,
  ProjectFile,
  ProjectFileType,
  ProjectSummary,
  Report,
  ThermalImage,
  VertexTemperaturePage,
} from "@/types";

export function listProjects() {
  return apiFetch<ProjectSummary[]>("/api/projects");
}

export function getProject(id: string) {
  return apiFetch<ProjectDetail>(`/api/projects/${id}`);
}

export function createProject(payload: { name: string; description?: string }) {
  return apiFetch<ProjectDetail>("/api/projects", { method: "POST", json: payload });
}

export function updateProject(id: string, payload: Partial<{ name: string; description: string }>) {
  return apiFetch<ProjectDetail>(`/api/projects/${id}`, { method: "PUT", json: payload });
}

export function deleteProject(id: string) {
  return apiFetch<void>(`/api/projects/${id}`, { method: "DELETE" });
}

export function listFiles(projectId: string) {
  return apiFetch<ProjectFile[]>(`/api/projects/${projectId}/files`);
}

export function uploadFile(projectId: string, file: File, type: ProjectFileType) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("type", type);
  return apiFetch<ProjectFile>(`/api/projects/${projectId}/upload`, { method: "POST", body: formData });
}

export function deleteFile(projectId: string, fileId: string) {
  return apiFetch<void>(`/api/projects/${projectId}/files/${fileId}`, { method: "DELETE" });
}

export function startProcessing(projectId: string) {
  return apiFetch<{ job_id: string; status: string }>(`/api/projects/${projectId}/process`, { method: "POST" });
}

export function getProcessingStatus(projectId: string) {
  return apiFetch<ProcessingJob>(`/api/projects/${projectId}/processing`);
}

export function cancelProcessing(projectId: string) {
  return apiFetch<{ cancelled: boolean }>(`/api/projects/${projectId}/processing/cancel`, { method: "POST" });
}

export function getResults(projectId: string) {
  return apiFetch<ProcessingResult>(`/api/projects/${projectId}/results`);
}

export function getModelUrl(projectId: string) {
  // The GLTF loader fetches this URL directly (no Authorization header support),
  // so the auth token travels as a query param instead -- same trick as the SSE stream.
  return sseUrl(`/api/projects/${projectId}/model.glb`);
}

export type DownloadArtifact = "vertex_temperature" | "face_temperature" | "results_json" | "temperatures_csv";

export function getDownloadUrl(projectId: string, artifact: DownloadArtifact) {
  return `/api/projects/${projectId}/download/${artifact}`;
}

export function listCameras(projectId: string) {
  return apiFetch<Camera[]>(`/api/projects/${projectId}/cameras`);
}

export function listThermalImages(projectId: string) {
  return apiFetch<ThermalImage[]>(`/api/projects/${projectId}/thermal`);
}

export function getTemperatureData(
  projectId: string,
  params: { page?: number; page_size?: number; min_temperature?: number; max_temperature?: number } = {}
) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) search.set(key, String(value));
  });
  const query = search.toString();
  return apiFetch<VertexTemperaturePage>(`/api/projects/${projectId}/temperature${query ? `?${query}` : ""}`);
}

export function listReports(projectId: string) {
  return apiFetch<Report[]>(`/api/projects/${projectId}/reports`);
}

export function getReport(projectId: string, reportId: string) {
  return apiFetch<Report>(`/api/projects/${projectId}/reports/${reportId}`);
}
