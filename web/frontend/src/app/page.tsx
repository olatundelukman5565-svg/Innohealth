import { CTASection } from "@/components/marketing/CTASection";
import { FeatureGrid } from "@/components/marketing/FeatureGrid";
import { Hero } from "@/components/marketing/Hero";
import { PipelineSection } from "@/components/marketing/PipelineSection";
import { ShowcaseSection } from "@/components/marketing/ShowcaseSection";
import { Footer } from "@/components/layout/Footer";
import { PublicNav } from "@/components/layout/PublicNav";

export default function HomePage() {
  return (
    <>
      <PublicNav />
      <main>
        <Hero />
        <PipelineSection />
        <ShowcaseSection />
        <FeatureGrid />
        <CTASection />
      </main>
      <Footer />
    </>
  );
}
