"use client";

import { useState } from "react";

import { Footer } from "@/components/layout/Footer";
import { PublicNav } from "@/components/layout/PublicNav";
import { PageHero } from "@/components/marketing/PageHero";
import { Button } from "@/components/ui/button";
import { Input, Textarea } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "@/components/ui/toast";
import { requestAccess } from "@/lib/api/auth";

export default function ContactPage() {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await requestAccess({ email, full_name: fullName, message });
      setSent(true);
    } catch {
      toast({ title: "Could not send your message", description: "Please try again in a moment.", tone: "danger" });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <PublicNav />
      <main>
        <PageHero eyebrow="Contact" title="Talk to the Innohealth team" description="Questions about the platform, the engine, or your data? Reach out below." />
        <section className="mx-auto max-w-lg px-6 py-16">
          {sent ? (
            <div className="rounded-lg border border-border bg-surface p-8 text-center shadow-card">
              <p className="text-lg font-medium text-foreground">Message received</p>
              <p className="mt-2 text-sm text-muted-foreground">An administrator will follow up with you shortly.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border border-border bg-surface p-8 shadow-card">
              <div className="space-y-1.5">
                <Label htmlFor="full_name">Full name</Label>
                <Input id="full_name" required value={fullName} onChange={(e) => setFullName(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="message">Message</Label>
                <Textarea id="message" rows={4} value={message} onChange={(e) => setMessage(e.target.value)} />
              </div>
              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? "Sending..." : "Send message"}
              </Button>
            </form>
          )}
        </section>
      </main>
      <Footer />
    </>
  );
}
