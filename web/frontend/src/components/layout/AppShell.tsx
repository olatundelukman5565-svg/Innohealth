"use client";

import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import {
  AlertTriangle,
  Bell,
  CheckCircle2,
  FileText,
  FolderKanban,
  HelpCircle,
  LayoutDashboard,
  LogOut,
  Search,
  Settings,
  Shield,
  X,
} from "lucide-react";
import Link from "next/link";
import { useParams, usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { Logo } from "@/components/layout/Logo";
import { LoadingState } from "@/components/ui/states";
import { useProject, useProjects } from "@/hooks/use-projects";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/projects", label: "Projects", icon: FolderKanban },
  { href: "/reports", label: "Reports", icon: FileText },
  { href: "/settings", label: "Settings", icon: Settings },
];

function useBreadcrumbs(currentProjectName?: string) {
  const pathname = usePathname();

  return useMemo(() => {
    const segments = pathname.split("/").filter(Boolean);
    const crumbs: { label: string; href: string }[] = [];
    let acc = "";

    segments.forEach((segment, i) => {
      acc += `/${segment}`;
      if (segment === "projects" && i === 0) {
        crumbs.push({ label: "Projects", href: "/projects" });
      } else if (segments[0] === "projects" && i === 1) {
        crumbs.push({ label: segment === "new" ? "New Project" : currentProjectName ?? "Project", href: acc });
      } else if (segment === "processing") {
        crumbs.push({ label: "Processing", href: acc });
      } else if (i === 0) {
        crumbs.push({ label: segment.charAt(0).toUpperCase() + segment.slice(1), href: acc });
      }
    });

    return crumbs.length > 0 ? crumbs : [{ label: "Dashboard", href: "/dashboard" }];
  }, [pathname, currentProjectName]);
}

function NotificationsMenu() {
  const { data: projects } = useProjects();

  const items = useMemo(() => {
    if (!projects) return [];
    const failed = projects
      .filter((p) => p.status === "FAILED")
      .map((p) => ({ id: `${p.id}-failed`, tone: "danger" as const, text: `${p.name} failed to process`, href: `/projects/${p.id}` }));
    const recentlyDone = projects
      .filter((p) => p.status === "COMPLETED" && p.last_processed_at)
      .filter((p) => Date.now() - new Date(p.last_processed_at as string).getTime() < 24 * 60 * 60 * 1000)
      .map((p) => ({ id: `${p.id}-done`, tone: "success" as const, text: `${p.name} finished processing`, href: `/projects/${p.id}` }));
    return [...failed, ...recentlyDone].slice(0, 6);
  }, [projects]);

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          className="relative flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-surface-secondary hover:text-foreground"
          aria-label="Notifications"
        >
          <Bell className="h-4 w-4" />
          {items.length > 0 && <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-brand" />}
        </button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align="end"
          sideOffset={8}
          className="z-50 w-80 rounded-lg border border-border bg-surface p-1 shadow-popover"
        >
          <div className="px-3 py-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Notifications</div>
          {items.length === 0 ? (
            <p className="px-3 py-4 text-sm text-muted-foreground">No new notifications.</p>
          ) : (
            items.map((item) => (
              <DropdownMenu.Item key={item.id} asChild>
                <Link href={item.href} className="flex cursor-pointer items-start gap-2.5 rounded-md px-3 py-2 text-sm hover:bg-surface-secondary">
                  {item.tone === "danger" ? (
                    <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-danger" />
                  ) : (
                    <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-success" />
                  )}
                  <span>{item.text}</span>
                </Link>
              </DropdownMenu.Item>
            ))
          )}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, isLoading, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const params = useParams<{ id?: string }>();
  const isProjectRoute = pathname.startsWith("/projects/") && params.id && params.id !== "new";
  const { data: project } = useProject(isProjectRoute ? (params.id as string) : "");
  const breadcrumbs = useBreadcrumbs(project?.name);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!isLoading && !user) router.replace("/login");
  }, [isLoading, user, router]);

  if (isLoading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingState label="Loading your workspace..." />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-60 shrink-0 flex-col bg-sidebar text-sidebar-foreground md:flex">
        <div className="flex h-14 items-center gap-2.5 border-b border-sidebar-border px-5">
          <Link href="/dashboard" className="flex items-center gap-2.5">
            <svg width="22" height="22" viewBox="0 0 32 32" fill="none" className="shrink-0">
              <path d="M16 2L29 9V23L16 30L3 23V9L16 2Z" stroke="currentColor" className="text-sidebar-accent" strokeWidth="1.6" strokeLinejoin="round" />
              <circle cx="16" cy="16" r="3.2" fill="currentColor" className="text-sidebar-accent" />
            </svg>
            <span className="text-sm font-semibold tracking-tight text-white">Innohealth</span>
          </Link>
        </div>
        <nav className="flex flex-1 flex-col gap-0.5 px-3 py-4">
          {NAV.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
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
          {user.role === "ADMIN" && (
            <Link
              href="/admin"
              className={cn(
                "mt-4 flex items-center gap-3 rounded-md border border-sidebar-border px-3 py-2 text-sm text-sidebar-foreground transition-colors hover:bg-sidebar-accent-bg",
                pathname.startsWith("/admin") && "bg-sidebar-accent-bg text-white"
              )}
            >
              <Shield className="h-4 w-4 shrink-0" />
              Admin Panel
            </Link>
          )}
        </nav>
        <div className="flex flex-col gap-2 border-t border-sidebar-border px-3 py-3">
          <div className="flex items-center gap-2.5 rounded-md px-2 py-1.5">
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-sidebar-accent-bg text-xs font-semibold text-white">
              {user.full_name.slice(0, 1).toUpperCase()}
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-medium text-white">{user.full_name}</p>
              <p className="truncate text-[11px] text-sidebar-muted">{user.role === "ADMIN" ? "Administrator" : "User"}</p>
            </div>
          </div>
          <Link href="/contact" className="flex items-center gap-2.5 rounded-md px-2 py-1.5 text-xs text-sidebar-muted hover:bg-sidebar-accent-bg hover:text-white">
            <HelpCircle className="h-3.5 w-3.5" /> Help &amp; support
          </Link>
          <div className="flex items-center gap-2 px-2 py-1 text-[11px] text-sidebar-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-success" />
            All systems operational
          </div>
        </div>
      </aside>

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="flex h-14 items-center gap-4 border-b border-border bg-surface px-4 md:px-6">
          <nav aria-label="Breadcrumb" className="hidden min-w-0 flex-1 items-center gap-1.5 text-sm md:flex">
            {breadcrumbs.map((crumb, i) => (
              <span key={crumb.href} className="flex items-center gap-1.5 truncate">
                {i > 0 && <span className="text-muted-foreground">/</span>}
                {i === breadcrumbs.length - 1 ? (
                  <span className="truncate font-medium text-foreground">{crumb.label}</span>
                ) : (
                  <Link href={crumb.href} className="truncate text-muted-foreground hover:text-foreground">
                    {crumb.label}
                  </Link>
                )}
              </span>
            ))}
          </nav>
          <div className="md:hidden">
            <Logo showWordmark={false} />
          </div>

          <form
            className="relative hidden w-64 lg:block"
            onSubmit={(e) => {
              e.preventDefault();
              if (search.trim()) router.push(`/projects?q=${encodeURIComponent(search.trim())}`);
            }}
          >
            <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search projects..."
              className="h-8 w-full rounded-md border border-border bg-surface-secondary pl-8 pr-7 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-brand"
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch("")}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                aria-label="Clear search"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </form>

          <NotificationsMenu />

          <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild>
              <button className="flex items-center gap-2 rounded-md px-1.5 py-1 text-sm hover:bg-surface-secondary">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand text-xs font-semibold text-brand-foreground">
                  {user.full_name.slice(0, 1).toUpperCase()}
                </span>
                <span className="hidden text-left sm:block">
                  <span className="block text-sm font-medium leading-tight">{user.full_name}</span>
                  <span className="block text-xs leading-tight text-muted-foreground">{user.role === "ADMIN" ? "Administrator" : "User"}</span>
                </span>
              </button>
            </DropdownMenu.Trigger>
            <DropdownMenu.Portal>
              <DropdownMenu.Content align="end" sideOffset={8} className="z-50 min-w-48 rounded-lg border border-border bg-surface p-1 shadow-popover">
                <DropdownMenu.Item asChild>
                  <Link href="/settings" className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-surface-secondary">
                    <Settings className="h-3.5 w-3.5" /> Settings
                  </Link>
                </DropdownMenu.Item>
                <DropdownMenu.Item
                  onSelect={() => logout()}
                  className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm text-danger hover:bg-danger-bg"
                >
                  <LogOut className="h-3.5 w-3.5" /> Sign out
                </DropdownMenu.Item>
              </DropdownMenu.Content>
            </DropdownMenu.Portal>
          </DropdownMenu.Root>
        </header>
        <main className="custom-scrollbar flex-1 overflow-y-auto bg-background p-4 md:p-6">
          <div className="mx-auto w-full max-w-[1400px]">{children}</div>
        </main>
      </div>
    </div>
  );
}
