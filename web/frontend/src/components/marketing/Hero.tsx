"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import dynamic from "next/dynamic";

import { Button } from "@/components/ui/button";

const HeroScene = dynamic(() => import("@/components/three/HeroScene").then((m) => m.HeroScene), { ssr: false });

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12 } },
};
const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } },
};

export function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-grid-fade" />
      <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-6 pb-20 pt-16 lg:grid-cols-2 lg:pb-32 lg:pt-24">
        <motion.div variants={container} initial="hidden" animate="show" className="relative z-10">
          <motion.span variants={item} className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-brand animate-pulse-ring" />
            AI-Powered 3D Thermal Intelligence
          </motion.span>
          <motion.h1 variants={item} className="text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl lg:text-6xl">
            Turn Thermal Data Into <span className="text-gradient">Intelligent 3D Insight.</span>
          </motion.h1>
          <motion.p variants={item} className="mt-6 max-w-xl text-lg leading-relaxed text-muted">
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
          <motion.div variants={item} className="mt-12 flex items-center gap-8 border-t border-white/5 pt-6 text-xs text-muted">
            <div>
              <p className="font-mono text-lg font-semibold text-foreground">12</p>
              <p>Thermal Views</p>
            </div>
            <div>
              <p className="font-mono text-lg font-semibold text-foreground">96.4%</p>
              <p>Avg. Coverage</p>
            </div>
            <div>
              <p className="font-mono text-lg font-semibold text-foreground">±0.8px</p>
              <p>Reprojection Error</p>
            </div>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.94 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
          className="relative h-[420px] lg:h-[560px]"
        >
          <HeroScene />
        </motion.div>
      </div>
    </section>
  );
}
