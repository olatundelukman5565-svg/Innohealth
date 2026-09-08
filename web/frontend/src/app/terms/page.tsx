import { Footer } from "@/components/layout/Footer";
import { PublicNav } from "@/components/layout/PublicNav";

export const metadata = { title: "Terms" };

export default function TermsPage() {
  return (
    <>
      <PublicNav />
      <main className="mx-auto max-w-3xl px-6 py-20 text-muted-foreground">
        <h1 className="mb-6 text-3xl font-semibold text-foreground">Terms of Use</h1>
        <p>
          This platform is provided for evaluation and demonstration purposes. Demo projects contain synthetic data generated
          for validation and are clearly marked as such -- they do not represent real Innohealth measurements.
        </p>
      </main>
      <Footer />
    </>
  );
}
