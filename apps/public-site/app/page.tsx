import Link from "next/link";

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
