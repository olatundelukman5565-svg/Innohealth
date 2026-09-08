import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";

import { AuthProvider } from "@/lib/auth-context";
import { QueryProvider } from "@/lib/query-provider";

import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  title: {
    default: "Innohealth ThermalMesh",
    template: "%s | Innohealth ThermalMesh",
  },
  description:
    "Turn thermal data into intelligent 3D insight. Innohealth ThermalMesh automatically aligns thermal imagery with reconstructed 3D geometry and transforms temperature measurements into interactive 3D intelligence.",
  openGraph: {
    title: "Innohealth ThermalMesh",
    description: "AI-powered 3D mesh and thermal analysis platform.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <body className="min-h-screen bg-background font-sans text-foreground antialiased">
        <QueryProvider>
          <AuthProvider>{children}</AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
