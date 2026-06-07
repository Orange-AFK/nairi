const DEFAULT_PUBLIC_SITE_URL = "http://localhost:3000";
const PUBLIC_SITEMAP_INDEX_SPLIT_POLICY =
  "Root sitemap is a split sitemap index that points to dedicated sitemap documents.";
const PUBLIC_SITEMAP_REVALIDATE_SECONDS = 300;
const PUBLIC_SITEMAP_CACHE_POLICY =
  "Sitemap index uses Next.js route revalidation only: no CDN headers, no purge, no publish-triggered invalidation execution.";

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

export async function GET() {
  void PUBLIC_SITEMAP_INDEX_SPLIT_POLICY;
  void PUBLIC_SITEMAP_CACHE_POLICY;
  const siteUrl = PUBLIC_SITE_URL();
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>${escapeXml(`${siteUrl}/sitemap-posts.xml`)}</loc></sitemap></sitemapindex>`;

  return new Response(body, {
    headers: {
      "Content-Type": "application/xml",
    },
  });
}
