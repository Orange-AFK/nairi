import { fetchPublicPosts, type PublicPostSummary } from "../../lib/public-posts";

const DEFAULT_PUBLIC_SITE_URL = "http://localhost:3000";
const PUBLIC_FEED_FULL_HISTORY_PAGINATION_POLICY =
  "RSS uses bounded full-history feed pagination over anonymous public list pages.";
const PUBLIC_FEED_REVALIDATE_SECONDS = 300;
const PUBLIC_FEED_CACHE_POLICY =
  "RSS uses Next.js route revalidation only: no CDN headers, no purge, no publish-triggered invalidation execution.";
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
export const revalidate = 300;

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
  void PUBLIC_FEED_FULL_HISTORY_PAGINATION_POLICY;
  void PUBLIC_FEED_CACHE_POLICY;
  const siteUrl = PUBLIC_SITE_URL();
  const posts = await fetchAllPublicPosts();
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
