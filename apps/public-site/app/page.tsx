import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Nairi | Project Experience Publishing",
  description: "Read project experience notes and published articles through the public Nairi site.",
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
