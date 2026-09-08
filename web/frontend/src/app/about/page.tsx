import type { Metadata } from "next";

import { Footer } from "@/components/layout/Footer";
import { PublicNav } from "@/components/layout/PublicNav";
import { CTASection } from "@/components/marketing/CTASection";
import { PageHero } from "@/components/marketing/PageHero";

export const metadata: Metadata = {
  title: "About",
  description: "Innohealth builds precise, transparent thermal and 3D analysis tools.",
};

export default function AboutPage() {
  return (
    <>
      <PublicNav />
      <main>
        <PageHero
          eyebrow="About Innohealth"
          title="Precision thermal intelligence, built for real workflows"
          description="Innohealth builds tools that treat raw measurement data as the product -- not just a pretty visualization."
        />
        <section className="mx-auto max-w-3xl space-y-6 px-6 py-16 text-muted-foreground">
          <p>
            ThermalMesh grew out of a simple frustration: thermal imaging and 3D reconstruction are usually treated as separate
            disciplines, forcing teams to manually reconcile temperature data with geometry after the fact.
          </p>
          <p>
            Our processing engine keeps raw numerical temperature as the authoritative data throughout -- alignment, camera pose
            estimation, projection, and blending are all real, inspectable geometric computer-vision steps, not approximations
            dressed up for a demo.
          </p>
          <p>
            This platform is the product of that engine: a place to run it, watch it work, and explore the results in an
            interactive 3D viewer built for scientific and engineering teams.
          </p>
        </section>
        <CTASection />
      </main>
      <Footer />
    </>
  );
}
