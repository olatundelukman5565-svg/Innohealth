import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/states";
import { formatPercent, formatTemperature } from "@/lib/utils";
import type { ThermalImage } from "@/types";

export function ThermalTab({ images }: { images: ThermalImage[] }) {
  if (images.length === 0) {
    return <EmptyState title="No thermal images processed yet" description="Thermal views will appear here once processing completes." />;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {images.map((image) => (
        <Card key={image.id}>
          <CardContent className="space-y-3 p-5">
            <div className="flex items-center justify-between">
              <p className="tabular-data text-sm font-medium">{image.camera_key}</p>
              <span className="text-xs text-muted-foreground">
                {image.width}×{image.height}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <p className="text-muted-foreground">Valid pixels</p>
                <p className="tabular-data">{formatPercent(image.valid_fraction * 100)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Mean temp</p>
                <p className="tabular-data">{formatTemperature(image.mean_temperature)}</p>
              </div>
              <div className="col-span-2">
                <p className="text-muted-foreground">Range</p>
                <p className="tabular-data">
                  {formatTemperature(image.min_temperature)} - {formatTemperature(image.max_temperature)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
