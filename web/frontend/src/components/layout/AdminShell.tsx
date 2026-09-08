"use client";

import { Activity, ArrowLeft, FolderKanban, LayoutDashboard, ScrollText, Server, Settings, Users } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { Logo } from "@/components/layout/Logo";
import { LoadingState } from "@/components/ui/states";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";

const NAV = [
  { href: "/admin", label: "Overview", icon: LayoutDashboard, exact: true },
  { href: "/admin/users", label: "Users", icon: Users },
  { href: "/admin/projects", label: "Projects", icon: FolderKanban },
  { href: "/admin/jobs", label: "Processing Jobs", icon: Activity },
  { href: "/admin/system", label: "System Health", icon: Server },
  { href: "/admin/audit", label: "Audit Logs", icon: ScrollText },
  { href: "/admin/settings", label: "Settings", icon: Settings },
];

export function AdminShell({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;
    if (!user) router.replace("/login");
    else if (user.role !== "ADMIN") router.replace("/dashboard");
  }, [isLoading, user, router]);

  if (isLoading || !user || user.role !== "ADMIN") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingState label="Verifying access..." />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-60 shrink-0 flex-col border-r border-white/5 bg-surface/60 md:flex">
        <div className="flex h-16 items-center px-6">
          <Logo />
        </div>
        <p className="px-6 pb-2 text-[10px] font-semibold uppercase tracking-widest text-brand">Admin</p>
        <nav className="flex flex-1 flex-col gap-1 px-3">
          {NAV.map((item) => {
            const Icon = item.icon;
            const active = item.exact ? pathname === item.href : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted transition-colors hover:bg-white/[0.05] hover:text-foreground",
                  active && "bg-white/[0.08] text-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-white/5 p-3">
          <Link href="/dashboard" className="flex items-center gap-2 rounded-lg px-3 py-2 text-xs text-muted hover:bg-white/[0.05] hover:text-foreground">
            <ArrowLeft className="h-3.5 w-3.5" /> Back to app
          </Link>
        </div>
      </aside>
      <main className="custom-scrollbar flex-1 overflow-y-auto p-6 md:p-8">{children}</main>
    </div>
  );
}
