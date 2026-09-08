import type { Metadata } from "next";

import { Footer } from "@/components/layout/Footer";
import { PublicNav } from "@/components/layout/PublicNav";
import { CTASection } from "@/components/marketing/CTASection";
import { PageHero } from "@/components/marketing/PageHero";
import { PipelineSection } from "@/components/marketing/PipelineSection";

export const metadata: Metadata = {
  title: "Technology",
  description: "How Innohealth ThermalMesh aligns geometry, estimates camera poses, and blends thermal observations into a single 3D model.",
};

export default function TechnologyPage() {
  return (
    <>
      <PublicNav />
      <main>
        <PageHero
          eyebrow="Technology"
          title="A real geometric and computer-vision pipeline"
          description="No black boxes: alignment, camera pose estimation, occlusion analysis, and thermal blending are all implemented as inspectable, independently testable stages."
        />
        <PipelineSection />
        <section id="docs" className="mx-auto max-w-3xl px-6 py-16 text-center">
          <h2 className="text-2xl font-semibold">Built on an open, documented engine</h2>
          <p className="mt-4 text-muted">
            The processing engine behind this platform is a standalone Python pipeline with its own architecture, alignment,
            camera model, and output-format documentation -- available to engineering teams evaluating the platform in depth.
          </p>
        </section>
        <CTASection />
      </main>
      <Footer />
    </>
  );
}
