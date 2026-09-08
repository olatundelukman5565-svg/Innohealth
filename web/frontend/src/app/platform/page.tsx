import type { Metadata } from "next";

import { Footer } from "@/components/layout/Footer";
import { PublicNav } from "@/components/layout/PublicNav";
import { CTASection } from "@/components/marketing/CTASection";
import { FeatureGrid } from "@/components/marketing/FeatureGrid";
import { PageHero } from "@/components/marketing/PageHero";
import { Card, CardContent, CardDescription, CardTitle } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Platform",
  description: "A single platform for uploading, processing, and exploring thermal-mapped 3D reconstructions.",
};

const WORKSPACES = [
  { title: "Projects", description: "Organize every scan as a project: geometry, thermal data, cameras, and results in one place." },
  { title: "Processing", description: "Kick off the real ThermalMesh engine and watch alignment, projection, and blending run live." },
  { title: "3D Viewer", description: "Rotate, inspect, and filter a fully textured thermal reconstruction directly in the browser." },
  { title: "Reports", description: "Quality, processing, and thermal analysis reports generated automatically from every run." },
];

export default function PlatformPage() {
  return (
    <>
      <PublicNav />
      <main>
        <PageHero
          eyebrow="Platform"
          title="One workspace for thermal-mapped 3D reconstruction"
          description="From raw upload to interactive 3D model, Innohealth ThermalMesh keeps geometry, thermal data, and processing results organized around each project."
        />
        <section className="mx-auto max-w-7xl px-6 py-24">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {WORKSPACES.map((w) => (
              <Card key={w.title}>
                <CardContent className="p-6">
                  <CardTitle>{w.title}</CardTitle>
                  <CardDescription className="mt-2">{w.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
        <FeatureGrid />
        <CTASection />
      </main>
      <Footer />
    </>
  );
}
