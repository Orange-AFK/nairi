const DEFAULT_PUBLIC_SITE_URL = "http://localhost:3000";
const PUBLIC_SITEMAP_STATIC_SHARD_POLICY =
  "Static sitemap is a static public sitemap shard that lists stable public landing routes separately from the split posts sitemap.";
const PUBLIC_SITEMAP_REVALIDATE_SECONDS = 300;
const PUBLIC_SITEMAP_CACHE_POLICY =
  "Static sitemap uses Next.js route revalidation only: no CDN headers, no purge, no publish-triggered invalidation execution.";

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
  void PUBLIC_SITEMAP_STATIC_SHARD_POLICY;
  void PUBLIC_SITEMAP_REVALIDATE_SECONDS;
  void PUBLIC_SITEMAP_CACHE_POLICY;
  const siteUrl = PUBLIC_SITE_URL();
  const entries = [
    `<url><loc>${escapeXml(`${siteUrl}/`)}</loc></url>`,
    `<url><loc>${escapeXml(`${siteUrl}/posts`)}</loc></url>`,
  ];
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${entries.join("")}</urlset>`;

  return new Response(body, {
    headers: {
      "Content-Type": "application/xml",
    },
  });
}
