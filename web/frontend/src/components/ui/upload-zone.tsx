"use client";

import { CheckCircle2, FileWarning, Trash2, UploadCloud } from "lucide-react";
import * as React from "react";

import { cn, formatBytes } from "@/lib/utils";

export interface UploadZoneFile {
  name: string;
  size: number;
  status: "pending" | "uploading" | "done" | "error";
  progress?: number;
  error?: string;
}

interface UploadZoneProps {
  label: string;
  hint: string;
  accept: string;
  multiple?: boolean;
  files: UploadZoneFile[];
  onFilesSelected: (files: File[]) => void;
  onRemove?: (name: string) => void;
  disabled?: boolean;
}

export function UploadZone({ label, hint, accept, multiple, files, onFilesSelected, onRemove, disabled }: UploadZoneProps) {
  const [isDragging, setIsDragging] = React.useState(false);
  const inputRef = React.useRef<HTMLInputElement>(null);

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList || disabled) return;
    onFilesSelected(Array.from(fileList));
  };

  return (
    <div className="space-y-3">
      <div
        role="button"
        tabIndex={0}
        aria-disabled={disabled}
        onClick={() => !disabled && inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && !disabled && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        className={cn(
          "group flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border bg-surface-secondary px-6 py-10 text-center transition-colors",
          isDragging && "border-brand bg-brand-muted",
          disabled && "cursor-not-allowed opacity-50"
        )}
      >
        <UploadCloud className={cn("h-8 w-8 text-muted-foreground transition-colors", isDragging && "text-brand")} />
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs text-muted-foreground">{hint}</p>
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
          disabled={disabled}
        />
      </div>

      {files.length > 0 && (
        <ul className="space-y-2">
          {files.map((file) => (
            <li key={file.name} className="flex items-center gap-3 rounded-md border border-border bg-surface px-3 py-2 text-sm">
              {file.status === "error" ? (
                <FileWarning className="h-4 w-4 shrink-0 text-danger" />
              ) : file.status === "done" ? (
                <CheckCircle2 className="h-4 w-4 shrink-0 text-success" />
              ) : (
                <div className="h-4 w-4 shrink-0 animate-pulse rounded-full border-2 border-brand border-t-transparent" />
              )}
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {file.status === "error" ? file.error : formatBytes(file.size)}
                </p>
                {file.status === "uploading" && (
                  <div className="mt-1 h-1 w-full overflow-hidden rounded-full bg-surface-secondary">
                    <div className="h-full bg-brand transition-all" style={{ width: `${file.progress ?? 0}%` }} />
                  </div>
                )}
              </div>
              {onRemove && (
                <button
                  type="button"
                  onClick={() => onRemove(file.name)}
                  className="rounded-md p-1 text-muted-foreground hover:bg-surface-secondary hover:text-danger"
                  aria-label={`Remove ${file.name}`}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
