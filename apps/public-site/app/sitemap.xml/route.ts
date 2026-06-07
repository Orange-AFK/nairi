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
  const { items: posts } = await fetchPublicPosts();
  const entries = [
    `<url><loc>${siteUrl}/</loc></url>`,
    `<url><loc>${siteUrl}/posts</loc></url>`,
    ...posts.map(
      (post) =>
        `<url><loc>${escapeXml(`${siteUrl}/posts/${encodeURIComponent(post.slug)}`)}</loc><lastmod>${post.publishedAt}</lastmod></url>`,
    ),
  ];
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${entries.join("")}</urlset>`;

  return new Response(body, {
    headers: {
      "Content-Type": "application/xml",
    },
  });
}
