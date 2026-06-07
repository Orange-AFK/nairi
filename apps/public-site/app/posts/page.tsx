import type { Metadata } from "next";
import Link from "next/link";

import { fetchPublicPosts } from "@/lib/public-posts";

export const metadata: Metadata = {
  title: "Articles | Nairi",
  description: "Browse published project experience notes from Nairi.",
};

export default async function PublicPostsPage() {
  const posts = await fetchPublicPosts();

  return (
    <main className="article-shell">
      <header className="article-header">
        <p className="article-meta">Published posts</p>
        <h1 className="article-title">Articles</h1>
        <p className="article-summary">Project experience notes published through Nairi.</p>
      </header>
      <section className="post-list" aria-label="Published posts">
        {posts.length === 0 ? (
          <p className="post-empty surface-card">No published posts yet.</p>
        ) : (
          posts.map((post) => (
            <article className="post-card surface-card" key={post.postId}>
              <p className="article-meta">
                Published <time dateTime={post.publishedAt}>{new Date(post.publishedAt).toLocaleDateString("en-US")}</time>
              </p>
              <h2 className="post-title">
                <Link href={`/posts/${post.slug}`}>{post.title}</Link>
              </h2>
              <p className="post-summary">{post.summary ?? "No summary provided."}</p>
              {post.tags.length > 0 ? (
                <ul className="tag-list" aria-label="Tags">
                  {post.tags.map((tag) => (
                    <li key={tag}>{tag}</li>
                  ))}
                </ul>
              ) : null}
            </article>
          ))
        )}
      </section>
    </main>
  );
}
