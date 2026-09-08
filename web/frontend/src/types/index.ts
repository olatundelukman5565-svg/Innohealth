import type {
  AuditAction,
  CameraPoseSource,
  JobStatus,
  ProcessingStageName,
  ProjectFileType,
  ProjectStatus,
  ReportType,
  StageStatus,
  UserRole,
} from "./enums";

export * from "./enums";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface ProjectSummary {
  id: string;
  name: string;
  description: string;
  status: ProjectStatus;
  is_demo: boolean;
  created_at: string;
  updated_at: string;
  last_processed_at: string | null;
  num_views: number;
  coverage_percent: number | null;
  min_temperature: number | null;
  max_temperature: number | null;
  has_result: boolean;
}

export interface ProjectDetail extends ProjectSummary {
  owner_id: string;
}

export interface ProjectFile {
  id: string;
  filename: string;
  type: ProjectFileType;
  size: number;
  upload_status: string;
  created_at: string;
}

export interface ProcessingStage {
  name: ProcessingStageName;
  sequence: number;
  status: StageStatus;
  started_at: string | null;
  completed_at: string | null;
  metrics: Record<string, unknown>;
}

export interface ProcessingJob {
  id: string;
  project_id: string;
  status: JobStatus;
  current_stage: ProcessingStageName | null;
  progress_percent: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  stages: ProcessingStage[];
}

export interface Camera {
  id: string;
  camera_key: string;
  image_width: number;
  image_height: number;
  position: [number, number, number];
  rotation: number[][];
  pose_source: CameraPoseSource;
  confidence: number;
  reprojection_error: number | null;
  coverage_percent: number;
}

export interface ThermalImage {
  id: string;
  camera_key: string;
  width: number;
  height: number;
  valid_fraction: number;
  min_temperature: number | null;
  max_temperature: number | null;
  mean_temperature: number | null;
}

export interface ProcessingResult {
  num_vertices: number;
  num_faces: number;
  min_temperature: number | null;
  max_temperature: number | null;
  mean_temperature: number | null;
  median_temperature: number | null;
  std_temperature: number | null;
  coverage_percent: number;
  alignment_confidence: number | null;
  num_views: number;
  quality_report: Record<string, any>;
  model_url: string | null;
  is_synthetic: boolean;
}

export interface Report {
  id: string;
  type: ReportType;
  generated_at: string;
  summary: Record<string, any>;
}

export interface VertexTemperatureRow {
  vertex_id: number;
  x: number;
  y: number;
  z: number;
  temperature: number | null;
  confidence: number;
  observations: number;
}

export interface VertexTemperaturePage {
  rows: VertexTemperatureRow[];
  total: number;
  page: number;
  page_size: number;
}

export interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  project_count: number;
}

export interface AdminProject {
  id: string;
  name: string;
  owner_email: string;
  status: ProjectStatus;
  is_demo: boolean;
  created_at: string;
  updated_at: string;
}

export interface AdminJob {
  id: string;
  project_id: string;
  project_name: string;
  status: JobStatus;
  current_stage: string | null;
  progress_percent: number;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  error_message: string | null;
  error_detail: string | null;
}

export interface AuditLogEntry {
  id: string;
  user_email: string | null;
  action: AuditAction;
  project_id: string | null;
  status: string;
  detail: Record<string, unknown>;
  created_at: string;
}

export interface SystemComponentHealth {
  name: string;
  status: "healthy" | "warning" | "error";
  detail: string;
}

export interface SystemHealth {
  components: SystemComponentHealth[];
  checked_at: string;
}

export interface AdminOverview {
  total_users: number;
  active_projects: number;
  processing_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  storage_usage_mb: number;
  projects_over_time: { date: string; count: number }[];
  jobs_by_status: { status: string; count: number }[];
  recent_activity: AuditLogEntry[];
}
