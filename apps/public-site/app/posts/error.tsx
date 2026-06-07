"use client";

export default function PostsError() {
  return (
    <main className="article-shell">
      <p className="article-meta">Published posts</p>
      <h1 className="article-title">Articles</h1>
      <section className="post-error" aria-label="Published posts error" role="status">
        <p>Articles are temporarily unavailable.</p>
        <p>Please try again later.</p>
      </section>
    </main>
  );
}
