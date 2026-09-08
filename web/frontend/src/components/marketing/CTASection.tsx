import Link from "next/link";

import { Button } from "@/components/ui/button";

export function CTASection() {
  return (
    <section className="mx-auto max-w-7xl px-6 py-24">
      <div className="rounded-lg border border-border bg-surface px-8 py-16 text-center shadow-card sm:px-16">
        <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">Ready to see your thermal data in 3D?</h2>
        <p className="mx-auto mt-4 max-w-xl text-muted-foreground">
          Sign in to the platform to explore a fully processed demo project, or start a new analysis with your own data.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <Button asChild size="lg">
            <Link href="/login">Launch Platform</Link>
          </Button>
          <Button asChild size="lg" variant="secondary">
            <Link href="/contact">Talk to Innohealth</Link>
          </Button>
        </div>
      </div>
    </section>
  );
}
