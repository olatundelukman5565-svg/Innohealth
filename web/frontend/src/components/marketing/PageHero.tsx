export function PageHero({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return (
    <div className="relative overflow-hidden border-b border-white/5">
      <div className="pointer-events-none absolute inset-0 bg-grid-fade" />
      <div className="relative mx-auto max-w-4xl px-6 py-20 text-center">
        <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-brand">{eyebrow}</p>
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">{title}</h1>
        <p className="mx-auto mt-5 max-w-2xl text-lg text-muted">{description}</p>
      </div>
    </div>
  );
}
