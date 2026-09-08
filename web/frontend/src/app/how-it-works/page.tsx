import type { Metadata } from "next";

import { Footer } from "@/components/layout/Footer";
import { PublicNav } from "@/components/layout/PublicNav";
import { CTASection } from "@/components/marketing/CTASection";
import { PageHero } from "@/components/marketing/PageHero";

export const metadata: Metadata = {
  title: "How It Works",
  description: "The end-to-end workflow for turning a 3D scan and thermal views into an interactive model.",
};

const STEPS = [
  { title: "1. Create a project", description: "Name your scan and describe what it captures." },
  { title: "2. Upload geometry", description: "The final reconstructed PLY mesh, plus an optional initial acquisition scan." },
  { title: "3. Upload thermal data", description: "Raw per-pixel temperature files (CSV or numeric) for each camera view." },
  { title: "4. Add camera metadata", description: "Camera locations -- orientation is estimated automatically if not provided." },
  { title: "5. Start processing", description: "The real ThermalMesh engine aligns, projects, blends, and exports the model." },
  { title: "6. Explore in 3D", description: "Rotate, filter, and click the thermal model to inspect real temperature data." },
];

export default function HowItWorksPage() {
  return (
    <>
      <PublicNav />
      <main>
        <PageHero
          eyebrow="How It Works"
          title="Six steps from raw scan to interactive thermal model"
          description="Every step is visible: you always know what file is expected, why, and what happens to it."
        />
        <section className="mx-auto max-w-3xl px-6 py-20">
          <ol className="space-y-8 border-l border-white/10 pl-8">
            {STEPS.map((step) => (
              <li key={step.title} className="relative">
                <span className="absolute -left-[2.35rem] top-1 h-3 w-3 rounded-full border-2 border-brand bg-background" />
                <h3 className="font-semibold">{step.title}</h3>
                <p className="mt-1 text-sm text-muted">{step.description}</p>
              </li>
            ))}
          </ol>
        </section>
        <CTASection />
      </main>
      <Footer />
    </>
  );
}
