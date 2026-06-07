import { fetchPublicPosts, type PublicPostSummary } from "../../lib/public-posts";

const DEFAULT_PUBLIC_SITE_URL = "http://localhost:3000";
const PUBLIC_SITEMAP_FULL_HISTORY_PAGINATION_POLICY =
  "Sitemap uses bounded full-history sitemap pagination over anonymous public list pages.";
const PUBLIC_POSTS_PAGE_SIZE = 100;
const PUBLIC_POSTS_MAX_PAGES = 100;

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

async function fetchAllPublicPosts(): Promise<PublicPostSummary[]> {
  const posts: PublicPostSummary[] = [];
  let cursor: string | undefined;
  let page = 0;

  while (page < PUBLIC_POSTS_MAX_PAGES) {
    const response = await fetchPublicPosts({ limit: PUBLIC_POSTS_PAGE_SIZE, cursor });
    posts.push(...response.items);
    page += 1;
    if (!response.nextCursor) {
      break;
    }
    cursor = response.nextCursor;
  }

  return posts;
}

export async function GET() {
  void PUBLIC_SITEMAP_FULL_HISTORY_PAGINATION_POLICY;
  const siteUrl = PUBLIC_SITE_URL();
  const posts = await fetchAllPublicPosts();
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
