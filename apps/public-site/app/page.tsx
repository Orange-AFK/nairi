import Link from "next/link";

export default function HomePage() {
  return (
    <main className="article-shell">
      <p className="article-meta">Nairi public site</p>
      <h1 className="article-title">Project experience publishing</h1>
      <p className="article-summary">Read published posts and project experience notes through the public Nairi site.</p>
      <p>
        <Link className="primary-link" href="/posts">
          Read published posts
        </Link>
      </p>
    </main>
  );
}
