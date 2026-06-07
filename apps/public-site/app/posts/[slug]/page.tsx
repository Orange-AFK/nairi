import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { fetchPublicPostBySlug } from "@/lib/public-posts";

type PublicPostDetailPageProps = {
  params: Promise<{
    slug: string;
  }>;
};

export async function generateMetadata({ params }: PublicPostDetailPageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = await fetchPublicPostBySlug(slug);
  if (post === null) {
    return {
      title: "Post not found | Nairi",
    };
  }

  return {
    title: `${post.title} | Nairi`,
    description: post.summary ?? undefined,
  };
}

export default async function PublicPostDetailPage({ params }: PublicPostDetailPageProps) {
  const { slug } = await params;
  const post = await fetchPublicPostBySlug(slug);
  if (post === null) {
    notFound();
  }
  const publicPost = post;

  return (
    <main className="article-shell">
      <header className="article-header">
        <p className="article-meta">
          Published <time dateTime={publicPost.publishedAt}>{new Date(publicPost.publishedAt).toLocaleDateString("en-US")}</time>
        </p>
        <h1 className="article-title">{publicPost.title}</h1>
        <p className="article-summary">{publicPost.summary ?? "No summary provided."}</p>
        {publicPost.tags.length > 0 ? (
          <ul className="tag-list" aria-label="Tags">
            {publicPost.tags.map((tag) => (
              <li key={tag}>{tag}</li>
            ))}
          </ul>
        ) : null}
      </header>
      <article className="article-body surface-card" dangerouslySetInnerHTML={{ __html: publicPost.bodyHtml }} />
    </main>
  );
}
