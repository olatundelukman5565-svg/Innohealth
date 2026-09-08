import { Footer } from "@/components/layout/Footer";
import { PublicNav } from "@/components/layout/PublicNav";

export const metadata = { title: "Privacy" };

export default function PrivacyPage() {
  return (
    <>
      <PublicNav />
      <main className="mx-auto max-w-3xl px-6 py-20 text-muted">
        <h1 className="mb-6 text-3xl font-semibold text-foreground">Privacy Policy</h1>
        <p>
          This is a demonstration platform. Data uploaded here -- meshes, thermal files, and camera metadata -- is processed
          locally by the ThermalMesh engine and stored only within this deployment&apos;s own storage and database. It is not
          shared with third parties or external services.
        </p>
      </main>
      <Footer />
    </>
  );
}
