"use client";

import { motion } from "framer-motion";
import Link from "next/link";

import { Button } from "@/components/ui/button";

export function CTASection() {
  return (
    <section className="mx-auto max-w-7xl px-6 py-24">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="glass-panel relative overflow-hidden rounded-3xl px-8 py-16 text-center sm:px-16"
      >
        <div className="pointer-events-none absolute inset-0 bg-grid-fade" />
        <h2 className="relative text-3xl font-semibold tracking-tight sm:text-4xl">Ready to see your thermal data in 3D?</h2>
        <p className="relative mx-auto mt-4 max-w-xl text-muted">
          Sign in to the platform to explore a fully processed demo project, or start a new analysis with your own data.
        </p>
        <div className="relative mt-8 flex flex-wrap items-center justify-center gap-4">
          <Button asChild size="lg">
            <Link href="/login">Launch Platform</Link>
          </Button>
          <Button asChild size="lg" variant="secondary">
            <Link href="/contact">Talk to Innohealth</Link>
          </Button>
        </div>
      </motion.div>
    </section>
  );
}
