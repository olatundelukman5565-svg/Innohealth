"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import dynamic from "next/dynamic";

import { Button } from "@/components/ui/button";

const HeroScene = dynamic(() => import("@/components/three/HeroScene").then((m) => m.HeroScene), { ssr: false });

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
};
const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
};

export function Hero() {
  return (
    <section className="border-b border-border">
      <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-6 pb-20 pt-16 lg:grid-cols-2 lg:pb-32 lg:pt-24">
        <motion.div variants={container} initial="hidden" animate="show">
          <motion.span className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-surface-secondary px-3 py-1 text-xs text-muted-foreground">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-brand" />
            AI-Powered 3D Thermal Intelligence
          </motion.span>
          <motion.h1 variants={item} className="text-4xl font-semibold leading-[1.1] tracking-tight text-foreground sm:text-5xl">
            Turn Thermal Data Into <span className="text-brand">Intelligent 3D Insight.</span>
          </motion.h1>
          <motion.p variants={item} className="mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground">
            Automatically align thermal imagery with reconstructed 3D geometry, preserve real temperature data, and transform
            complex thermal measurements into interactive 3D intelligence.
          </motion.p>
          <motion.div variants={item} className="mt-9 flex flex-wrap items-center gap-4">
            <Button asChild size="lg">
              <Link href="/login">Launch Platform</Link>
            </Button>
            <Button asChild size="lg" variant="secondary">
              <Link href="/how-it-works">See How It Works</Link>
            </Button>
          </motion.div>
          <motion.div variants={item} className="mt-12 flex items-center gap-8 border-t border-border pt-6 text-xs text-muted-foreground">
            <div>
              <p className="tabular-data text-lg font-semibold text-foreground">12</p>
              <p>Thermal Views</p>
            </div>
            <div>
              <p className="tabular-data text-lg font-semibold text-foreground">96.4%</p>
              <p>Avg. Coverage</p>
            </div>
            <div>
              <p className="tabular-data text-lg font-semibold text-foreground">±0.8px</p>
              <p>Reprojection Error</p>
            </div>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="relative h-[420px] rounded-lg border border-border bg-surface-secondary lg:h-[560px]"
        >
          <HeroScene />
        </motion.div>
      </div>
    </section>
  );
}
