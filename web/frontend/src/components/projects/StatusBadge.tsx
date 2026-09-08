import { Badge } from "@/components/ui/badge";
import { PROJECT_STATUS_META, type ProjectStatus } from "@/types";

const TONE_MAP = { neutral: "neutral", info: "info", success: "success", danger: "danger", warning: "warning" } as const;

export function StatusBadge({ status }: { status: ProjectStatus }) {
  const meta = PROJECT_STATUS_META[status];
  return (
    <Badge tone={TONE_MAP[meta.tone]} dot>
      {meta.label}
    </Badge>
  );
}
