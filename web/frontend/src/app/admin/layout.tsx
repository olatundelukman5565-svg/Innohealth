import { AdminShell } from "@/components/layout/AdminShell";
import { Toaster } from "@/components/ui/toast";
import { TooltipProvider } from "@/components/ui/tooltip";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <TooltipProvider>
      <AdminShell>{children}</AdminShell>
      <Toaster />
    </TooltipProvider>
  );
}
