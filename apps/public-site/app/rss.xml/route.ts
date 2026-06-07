import { fetchPublicPosts } from "../../lib/public-posts";

const DEFAULT_PUBLIC_SITE_URL = "http://localhost:3000";

function PUBLIC_SITE_URL(): string {
  return (process.env.NEXT_PUBLIC_NAIRI_PUBLIC_SITE_URL ?? DEFAULT_PUBLIC_SITE_URL).replace(/\/$/, "");
}

function escapeXml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

export const dynamic = "force-dynamic";

export async function GET() {
  const siteUrl = PUBLIC_SITE_URL();
  const posts = await fetchPublicPosts();
  const items = posts.map((post) => {
    const postUrl = `${siteUrl}/posts/${encodeURIComponent(post.slug)}`;
    return `<item><title>${escapeXml(post.title)}</title><link>${postUrl}</link><guid>${postUrl}</guid><pubDate>${new Date(post.publishedAt).toUTCString()}</pubDate><description>${escapeXml(post.summary ?? "")}</description></item>`;
  });
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Nairi</title><link>${siteUrl}/</link><description>Published project experience notes from Nairi.</description>${items.join("")}</channel></rss>`;

  return new Response(body, {
    headers: {
      "Content-Type": "application/rss+xml",
    },
  });
}
