"use client";

import * as ToastPrimitive from "@radix-ui/react-toast";
import { AlertCircle, CheckCircle2, Info, X } from "lucide-react";
import { create } from "zustand";

import { cn } from "@/lib/utils";

export interface ToastItem {
  id: string;
  title: string;
  description?: string;
  tone?: "default" | "success" | "danger";
}

interface ToastState {
  toasts: ToastItem[];
  push: (toast: Omit<ToastItem, "id">) => void;
  dismiss: (id: string) => void;
}

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  push: (toast) => set((state) => ({ toasts: [...state.toasts, { ...toast, id: crypto.randomUUID() }] })),
  dismiss: (id) => set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),
}));

export function toast(item: Omit<ToastItem, "id">) {
  useToastStore.getState().push(item);
}

const TONE_ICON = {
  default: Info,
  success: CheckCircle2,
  danger: AlertCircle,
};

export function Toaster() {
  const { toasts, dismiss } = useToastStore();

  return (
    <ToastPrimitive.Provider swipeDirection="right">
      {toasts.map((item) => {
        const Icon = TONE_ICON[item.tone ?? "default"];
        return (
          <ToastPrimitive.Root
            key={item.id}
            duration={5000}
            onOpenChange={(open) => !open && dismiss(item.id)}
            className={cn(
              "pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-lg border border-border bg-surface p-4 shadow-popover data-[state=open]:animate-slide-down",
              item.tone === "success" && "border-success/30",
              item.tone === "danger" && "border-danger/30"
            )}
          >
            <Icon
              className={cn(
                "mt-0.5 h-4 w-4 shrink-0",
                item.tone === "success" && "text-success",
                item.tone === "danger" && "text-danger",
                (!item.tone || item.tone === "default") && "text-brand"
              )}
            />
            <div className="flex-1">
              <ToastPrimitive.Title className="text-sm font-medium">{item.title}</ToastPrimitive.Title>
              {item.description && <ToastPrimitive.Description className="mt-1 text-xs text-muted-foreground">{item.description}</ToastPrimitive.Description>}
            </div>
            <ToastPrimitive.Close className="text-muted-foreground hover:text-foreground">
              <X className="h-3.5 w-3.5" />
            </ToastPrimitive.Close>
          </ToastPrimitive.Root>
        );
      })}
      <ToastPrimitive.Viewport className="fixed bottom-0 right-0 z-[100] flex w-full max-w-sm flex-col gap-2 p-6" />
    </ToastPrimitive.Provider>
  );
}
