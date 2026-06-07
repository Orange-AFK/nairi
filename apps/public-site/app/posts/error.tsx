"use client";

export default function PostsError() {
  return (
    <main className="article-shell">
      <header className="article-header">
        <p className="article-meta">Published posts</p>
        <h1 className="article-title">Articles</h1>
      </header>
      <section className="post-error surface-card" aria-label="Published posts error" role="status">
        <p>Articles are temporarily unavailable.</p>
        <p>Please try again later.</p>
      </section>
    </main>
  );
}
