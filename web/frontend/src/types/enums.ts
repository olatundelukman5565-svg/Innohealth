export type UserRole = "ADMIN" | "USER";

export type ProjectStatus =
  | "DRAFT"
  | "UPLOADING"
  | "VALIDATING"
  | "QUEUED"
  | "PROCESSING"
  | "COMPLETED"
  | "FAILED"
  | "ARCHIVED";

export const PROJECT_STATUS_META: Record<ProjectStatus, { label: string; description: string; tone: "neutral" | "info" | "success" | "danger" | "warning" }> = {
  DRAFT: { label: "Draft", description: "Not yet ready for processing", tone: "neutral" },
  UPLOADING: { label: "Uploading", description: "Files are being added", tone: "info" },
  VALIDATING: { label: "Validating", description: "Checking uploaded files", tone: "info" },
  QUEUED: { label: "Queued", description: "Waiting for a processing worker", tone: "warning" },
  PROCESSING: { label: "Processing", description: "Pipeline is running", tone: "info" },
  COMPLETED: { label: "Completed", description: "Ready to explore", tone: "success" },
  FAILED: { label: "Failed", description: "Processing encountered an error", tone: "danger" },
  ARCHIVED: { label: "Archived", description: "Hidden from the active list", tone: "neutral" },
};

export type ProjectFileType =
  | "FINAL_MESH"
  | "INITIAL_MESH"
  | "THERMAL_DATA"
  | "THERMAL_IMAGE"
  | "CAMERA_METADATA"
  | "RESULT"
  | "REPORT";

export type JobStatus = "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED";

export type ProcessingStageName =
  | "INPUT_VALIDATION"
  | "MESH_ALIGNMENT"
  | "CAMERA_POSE_ESTIMATION"
  | "THERMAL_PROJECTION"
  | "OCCLUSION_ANALYSIS"
  | "TEMPERATURE_MAPPING"
  | "UV_GENERATION"
  | "THERMAL_BLENDING"
  | "WEB_EXPORT"
  | "REPORT_GENERATION";

export const PROCESSING_STAGE_META: Record<ProcessingStageName, { label: string; description: string }> = {
  INPUT_VALIDATION: { label: "Input Validation", description: "Checking mesh, thermal, and camera files" },
  MESH_ALIGNMENT: { label: "Mesh Alignment", description: "Aligning acquisition geometry to the final mesh" },
  CAMERA_POSE_ESTIMATION: { label: "Camera Pose Estimation", description: "Estimating and refining camera positions" },
  THERMAL_PROJECTION: { label: "Thermal Projection", description: "Projecting thermal images onto the mesh" },
  OCCLUSION_ANALYSIS: { label: "Occlusion Analysis", description: "Determining visible vs. hidden surfaces" },
  TEMPERATURE_MAPPING: { label: "Temperature Mapping", description: "Blending observations onto geometry" },
  UV_GENERATION: { label: "UV Generation", description: "Automatically unwrapping the mesh" },
  THERMAL_BLENDING: { label: "Thermal Blending", description: "Combining views into UV-space layers" },
  WEB_EXPORT: { label: "Web Export", description: "Generating GLB/GLTF and numerical outputs" },
  REPORT_GENERATION: { label: "Report Generation", description: "Compiling the quality report" },
};

export type StageStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";

export type CameraPoseSource = "PROVIDED" | "ESTIMATED" | "REFINED";

export type ReportType = "THERMAL_ANALYSIS" | "PROCESSING" | "QUALITY";

export type AuditAction =
  | "LOGIN"
  | "LOGOUT"
  | "USER_CREATED"
  | "USER_UPDATED"
  | "PROJECT_CREATED"
  | "PROJECT_UPDATED"
  | "PROJECT_DELETED"
  | "FILE_UPLOADED"
  | "PROCESSING_STARTED"
  | "PROCESSING_COMPLETED"
  | "PROCESSING_FAILED"
  | "REPORT_GENERATED";
