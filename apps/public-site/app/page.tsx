import type { Metadata } from "next";
import Link from "next/link";

const DEFAULT_PUBLIC_SITE_URL = "http://localhost:3000";

function PUBLIC_SITE_URL(): string {
  return (process.env.NEXT_PUBLIC_NAIRI_PUBLIC_SITE_URL ?? DEFAULT_PUBLIC_SITE_URL).replace(/\/$/, "");
}

export const metadata: Metadata = {
  metadataBase: new URL(PUBLIC_SITE_URL()),
  title: "Nairi | Project Experience Publishing",
  description: "Read project experience notes and published articles through the public Nairi site.",
  alternates: {
    canonical: "/",
  },
};

export default function HomePage() {
  return (
    <main className="article-shell">
      <header className="article-header">
        <p className="article-meta">Nairi public site</p>
        <h1 className="article-title">Project experience publishing</h1>
        <p className="article-summary">Read published posts and project experience notes through the public Nairi site.</p>
      </header>
      <section className="surface-card">
        <Link className="primary-link surface-card-link" href="/posts">
          Read published posts
        </Link>
      </section>
    </main>
  );
}
