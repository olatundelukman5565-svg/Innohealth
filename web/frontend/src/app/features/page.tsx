import type { Metadata } from "next";

import { Footer } from "@/components/layout/Footer";
import { PublicNav } from "@/components/layout/PublicNav";
import { CTASection } from "@/components/marketing/CTASection";
import { FeatureGrid } from "@/components/marketing/FeatureGrid";
import { PageHero } from "@/components/marketing/PageHero";

export const metadata: Metadata = {
  title: "Features",
  description: "Everything Innohealth ThermalMesh does, from automatic alignment to exportable numerical data.",
};

export default function FeaturesPage() {
  return (
    <>
      <PublicNav />
      <main>
        <PageHero
          eyebrow="Features"
          title="Everything you need to go from scan to insight"
          description="A complete workflow: upload, align, estimate, project, blend, export -- with quality metrics at every stage."
        />
        <FeatureGrid />
        <CTASection />
      </main>
      <Footer />
    </>
  );
}
