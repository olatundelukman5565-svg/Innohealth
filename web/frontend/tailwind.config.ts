import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        surface: "hsl(var(--surface))",
        "surface-secondary": "hsl(var(--surface-secondary))",
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        foreground: "hsl(var(--foreground))",
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        brand: {
          DEFAULT: "hsl(var(--brand))",
          foreground: "hsl(var(--brand-foreground))",
          muted: "hsl(var(--brand-muted))",
        },
        success: { DEFAULT: "hsl(var(--success))", bg: "hsl(var(--success-bg))" },
        warning: { DEFAULT: "hsl(var(--warning))", bg: "hsl(var(--warning-bg))" },
        danger: { DEFAULT: "hsl(var(--danger))", bg: "hsl(var(--danger-bg))" },
        info: { DEFAULT: "hsl(var(--info))", bg: "hsl(var(--info-bg))" },
        sidebar: {
          DEFAULT: "hsl(var(--sidebar-background))",
          foreground: "hsl(var(--sidebar-foreground))",
          border: "hsl(var(--sidebar-border))",
          muted: "hsl(var(--sidebar-muted))",
          accent: "hsl(var(--sidebar-accent))",
          "accent-bg": "hsl(var(--sidebar-accent-bg))",
        },
        thermal: {
          1: "hsl(var(--thermal-1))",
          2: "hsl(var(--thermal-2))",
          3: "hsl(var(--thermal-3))",
          4: "hsl(var(--thermal-4))",
          5: "hsl(var(--thermal-5))",
          6: "hsl(var(--thermal-6))",
          7: "hsl(var(--thermal-7))",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: {
        sm: "calc(var(--radius) - 4px)",
        DEFAULT: "calc(var(--radius) - 2px)",
        md: "calc(var(--radius) - 2px)",
        lg: "var(--radius)",
        xl: "calc(var(--radius) + 4px)",
      },
      boxShadow: {
        xs: "0 1px 2px 0 rgb(15 23 42 / 0.04)",
        card: "0 1px 2px 0 rgb(15 23 42 / 0.04), 0 1px 1px 0 rgb(15 23 42 / 0.02)",
        popover: "0 4px 12px -2px rgb(15 23 42 / 0.10), 0 2px 4px -2px rgb(15 23 42 / 0.06)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-down": {
          "0%": { opacity: "0", transform: "translateY(-4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.15s ease-out both",
        "slide-down": "slide-down 0.15s ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;
