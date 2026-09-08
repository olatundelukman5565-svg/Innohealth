"use client";

import { Activity, ArrowLeft, FolderKanban, LayoutDashboard, LogOut, ScrollText, Server, Settings, Users } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo } from "react";

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
  const { user, isLoading, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const pageTitle = useMemo(() => {
    const match = NAV.find((item) => (item.exact ? pathname === item.href : pathname.startsWith(item.href)));
    return match?.label ?? "Admin";
  }, [pathname]);

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
      <aside className="hidden w-60 shrink-0 flex-col bg-sidebar text-sidebar-foreground md:flex">
        <div className="flex h-14 items-center gap-2.5 border-b border-sidebar-border px-5">
          <svg width="22" height="22" viewBox="0 0 32 32" fill="none" className="shrink-0">
            <path d="M16 2L29 9V23L16 30L3 23V9L16 2Z" stroke="currentColor" className="text-sidebar-accent" strokeWidth="1.6" strokeLinejoin="round" />
            <circle cx="16" cy="16" r="3.2" fill="currentColor" className="text-sidebar-accent" />
          </svg>
          <div>
            <p className="text-sm font-semibold leading-tight text-white">Innohealth</p>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-sidebar-accent">Admin</p>
          </div>
        </div>
        <nav className="flex flex-1 flex-col gap-0.5 px-3 py-4">
          {NAV.map((item) => {
            const Icon = item.icon;
            const active = item.exact ? pathname === item.href : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm text-sidebar-muted transition-colors hover:bg-sidebar-accent-bg hover:text-white",
                  active && "bg-sidebar-accent-bg text-white"
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="flex flex-col gap-1 border-t border-sidebar-border px-3 py-3">
          <Link href="/dashboard" className="flex items-center gap-2.5 rounded-md px-2 py-1.5 text-xs text-sidebar-muted hover:bg-sidebar-accent-bg hover:text-white">
            <ArrowLeft className="h-3.5 w-3.5" /> Back to app
          </Link>
          <button
            onClick={() => logout()}
            className="flex items-center gap-2.5 rounded-md px-2 py-1.5 text-left text-xs text-sidebar-muted hover:bg-sidebar-accent-bg hover:text-white"
          >
            <LogOut className="h-3.5 w-3.5" /> Sign out
          </button>
        </div>
      </aside>

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b border-border bg-surface px-4 md:px-6">
          <div className="flex items-center gap-1.5 text-sm">
            <span className="text-muted-foreground">Admin</span>
            <span className="text-muted-foreground">/</span>
            <span className="font-medium text-foreground">{pageTitle}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand text-xs font-semibold text-brand-foreground">
              {user.full_name.slice(0, 1).toUpperCase()}
            </span>
            <span className="hidden sm:inline">{user.full_name}</span>
          </div>
        </header>
        <main className="custom-scrollbar flex-1 overflow-y-auto bg-background p-4 md:p-6">
          <div className="mx-auto w-full max-w-[1400px]">{children}</div>
        </main>
      </div>
    </div>
  );
}
