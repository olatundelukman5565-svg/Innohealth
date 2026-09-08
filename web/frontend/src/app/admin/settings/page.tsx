"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingState } from "@/components/ui/states";
import { useAdminSettings } from "@/hooks/use-admin";

export default function AdminSettingsPage() {
  const { data, isLoading } = useAdminSettings();

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">System Settings</h1>
        <p className="mt-1 text-muted-foreground">Processing defaults, storage configuration, and upload limits.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Current configuration</CardTitle>
          <CardDescription>{(data?.note as string) ?? "Loaded from server environment variables."}</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading || !data ? (
            <LoadingState label="Loading settings..." />
          ) : (
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between border-b border-border pb-2">
                <dt className="text-muted-foreground">Max upload size</dt>
                <dd className="tabular-data">{data.max_upload_mb as number} MB</dd>
              </div>
              <div className="flex justify-between border-b border-border pb-2">
                <dt className="text-muted-foreground">Storage path</dt>
                <dd className="max-w-xs truncate tabular-data text-xs">{data.storage_path as string}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">CORS origins</dt>
                <dd className="tabular-data text-xs">{(data.cors_origins as string[]).join(", ")}</dd>
              </div>
            </dl>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
