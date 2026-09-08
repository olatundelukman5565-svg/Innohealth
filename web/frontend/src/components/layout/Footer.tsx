import Link from "next/link";

import { Logo } from "./Logo";

export function Footer() {
  return (
    <footer className="border-t border-white/5 bg-surface/40">
      <div className="mx-auto flex max-w-7xl flex-col gap-8 px-6 py-12 md:flex-row md:items-start md:justify-between">
        <div className="max-w-xs">
          <Logo />
          <p className="mt-3 text-sm text-muted">
            Transforming 3D reconstruction and thermal imaging data into interactive, measurable thermal intelligence.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted">Platform</p>
            <ul className="space-y-2 text-sm text-muted">
              <li><Link href="/platform" className="hover:text-foreground">Overview</Link></li>
              <li><Link href="/features" className="hover:text-foreground">Features</Link></li>
              <li><Link href="/how-it-works" className="hover:text-foreground">How It Works</Link></li>
            </ul>
          </div>
          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted">Technology</p>
            <ul className="space-y-2 text-sm text-muted">
              <li><Link href="/technology" className="hover:text-foreground">Pipeline</Link></li>
              <li><Link href="/technology#docs" className="hover:text-foreground">Documentation</Link></li>
            </ul>
          </div>
          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted">Company</p>
            <ul className="space-y-2 text-sm text-muted">
              <li><Link href="/about" className="hover:text-foreground">About Innohealth</Link></li>
              <li><Link href="/contact" className="hover:text-foreground">Contact</Link></li>
            </ul>
          </div>
          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted">Legal</p>
            <ul className="space-y-2 text-sm text-muted">
              <li><Link href="/privacy" className="hover:text-foreground">Privacy</Link></li>
              <li><Link href="/terms" className="hover:text-foreground">Terms</Link></li>
            </ul>
          </div>
        </div>
      </div>
      <div className="border-t border-white/5 px-6 py-6 text-center text-xs text-muted">
        © {new Date().getFullYear()} Innohealth. ThermalMesh is a demonstration platform running on synthetic validation data.
      </div>
    </footer>
  );
}
