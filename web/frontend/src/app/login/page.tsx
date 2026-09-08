"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Logo } from "@/components/layout/Logo";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError } from "@/lib/api/client";
import { useAuth } from "@/lib/auth-context";

const ParticleField = dynamic(() => import("@/components/three/ParticleField").then((m) => m.ParticleField), { ssr: false });
import { Canvas } from "@react-three/fiber";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("demo@innohealth.com");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password, rememberMe);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to sign in. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-6">
      <div className="pointer-events-none absolute inset-0 opacity-60">
        <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
          <ParticleField count={180} radius={5} speed={0.6} />
        </Canvas>
      </div>
      <div className="pointer-events-none absolute inset-0 bg-grid-fade" />

      <div className="glass-panel relative w-full max-w-md rounded-2xl p-8 shadow-panel">
        <Link href="/" className="mb-8 flex justify-center">
          <Logo />
        </Link>
        <h1 className="text-center text-xl font-semibold">Sign in to your account</h1>
        <p className="mt-1 text-center text-sm text-muted">Explore your thermal 3D projects</p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>
          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center gap-2 text-muted">
              <Checkbox checked={rememberMe} onCheckedChange={(v) => setRememberMe(Boolean(v))} />
              Remember me
            </label>
            <Link href="/contact" className="text-brand hover:underline">
              Forgot password?
            </Link>
          </div>

          {error && <p className="rounded-lg border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p>}

          <Button type="submit" className="w-full" size="lg" disabled={submitting}>
            {submitting ? "Signing in..." : "Sign in"}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          Don&apos;t have an account?{" "}
          <Link href="/contact" className="text-brand hover:underline">
            Request access
          </Link>
        </p>

        <div className="mt-6 rounded-lg border border-white/10 bg-white/[0.03] p-3 text-xs text-muted">
          <p className="font-medium text-foreground/80">Demo credentials</p>
          <p className="mt-1 font-mono">demo@innohealth.com / demo1234</p>
          <p className="font-mono">admin@innohealth.com / admin123</p>
        </div>
      </div>
    </div>
  );
}
