from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX_ROUTE = ROOT / "apps/public-site/app/sitemap.xml/route.ts"
POSTS_ROUTE = ROOT / "apps/public-site/app/sitemap-posts.xml/route.ts"
STATIC_ROUTE = ROOT / "apps/public-site/app/sitemap-static.xml/route.ts"
CLIENT = ROOT / "apps/public-site/lib/public-posts.ts"

missing = [path for path in (INDEX_ROUTE, POSTS_ROUTE, STATIC_ROUTE, CLIENT) if not path.exists()]
if missing:
    raise SystemExit("missing public sitemap files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

index_route = INDEX_ROUTE.read_text()
posts_route = POSTS_ROUTE.read_text()
static_route = STATIC_ROUTE.read_text()
client = CLIENT.read_text()

required_index_route = [
    "export const dynamic = \"force-dynamic\"",
    "export async function GET()",
    "PUBLIC_SITEMAP_INDEX_SPLIT_POLICY",
    "split sitemap index",
    "PUBLIC_SITEMAP_REVALIDATE_SECONDS",
    "PUBLIC_SITEMAP_CACHE_POLICY",
    "Next.js route revalidation only",
    "no CDN headers",
    "no purge",
    "no publish-triggered invalidation execution",
    "export const revalidate = 300",
    "PUBLIC_SITE_URL",
    "application/xml",
    "<sitemapindex xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">",
    "sitemap-posts.xml",
    "sitemap-static.xml",
    "escapeXml(`${siteUrl}/sitemap-posts.xml`)",
    "escapeXml(`${siteUrl}/sitemap-static.xml`)",
]

required_posts_route = [
    "export const dynamic = \"force-dynamic\"",
    "export async function GET()",
    "fetchAllPublicPosts",
    "PUBLIC_SITEMAP_POSTS_SPLIT_POLICY",
    "split posts sitemap",
    "PUBLIC_SITEMAP_FULL_HISTORY_PAGINATION_POLICY",
    "full-history sitemap pagination",
    "PUBLIC_SITEMAP_REVALIDATE_SECONDS",
    "PUBLIC_SITEMAP_CACHE_POLICY",
    "Next.js route revalidation only",
    "no CDN headers",
    "no purge",
    "no publish-triggered invalidation execution",
    "export const revalidate = 300",
    "PUBLIC_POSTS_PAGE_SIZE",
    "PUBLIC_POSTS_MAX_PAGES",
    "cursor",
    "nextCursor",
    "PUBLIC_SITE_URL",
    "application/xml",
    "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">",
    "encodeURIComponent(post.slug)",
    "<lastmod>${post.publishedAt}</lastmod>",
]


required_static_route = [
    "export const dynamic = \"force-dynamic\"",
    "export async function GET()",
    "PUBLIC_SITEMAP_STATIC_SHARD_POLICY",
    "static public sitemap shard",
    "PUBLIC_SITEMAP_REVALIDATE_SECONDS",
    "PUBLIC_SITEMAP_CACHE_POLICY",
    "Next.js route revalidation only",
    "no CDN headers",
    "no purge",
    "no publish-triggered invalidation execution",
    "export const revalidate = 300",
    "PUBLIC_SITE_URL",
    "application/xml",
    "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">",
    "escapeXml(`${siteUrl}/`)",
    "escapeXml(`${siteUrl}/posts`)",
]

failures: list[str] = []
for needle in required_index_route:
    if needle not in index_route:
        failures.append(f"sitemap index route missing {needle}")
for needle in required_posts_route:
    if needle not in posts_route:
        failures.append(f"sitemap posts route missing {needle}")
for needle in required_static_route:
    if needle not in static_route:
        failures.append(f"sitemap static route missing {needle}")

if "fetchAllPublicPosts" in index_route or "fetchPublicPosts" in index_route:
    failures.append("sitemap index must not fetch post pages directly")
if "<urlset" in index_route:
    failures.append("sitemap index must not remain a urlset")
if "<sitemapindex" in posts_route:
    failures.append("posts sitemap must not be a sitemap index")
if "<sitemapindex" in static_route:
    failures.append("static sitemap must not be a sitemap index")
if "fetchAllPublicPosts" in static_route or "fetchPublicPosts" in static_route:
    failures.append("static sitemap must not fetch post pages directly")

for route_name, route in (("sitemap index", index_route), ("posts sitemap", posts_route), ("static sitemap", static_route)):
    if "/api/v1/posts" in route or "/api/v1/posts" in client.replace("/api/v1/public/posts/", "").replace("/api/v1/public/posts", ""):
        failures.append(f"{route_name} must not call authenticated management posts routes")
    if "Authorization" in route:
        failures.append(f"{route_name} must not send bearer tokens")
    if "Cache-Control" in route:
        failures.append(f"{route_name} cache policy must not add CDN/cache headers yet")
    if "cloudflare" in route.lower() or "purge" in route.lower().replace("no purge", ""):
        failures.append(f"{route_name} cache policy must not call CDN purge APIs yet")
    if "revalidateTag" in route or "revalidatePath" in route:
        failures.append(f"{route_name} cache policy must not add tag/path invalidation calls yet")
    if "export const revalidate = PUBLIC_SITEMAP_REVALIDATE_SECONDS" in route:
        failures.append(f"{route_name} revalidate export must stay statically analyzable for Next.js")
    if "rss" in route.lower():
        failures.append(f"{route_name} boundary must not implement RSS")

if "while" not in posts_route:
    failures.append("posts sitemap full-history pagination must use an explicit bounded loop")
if "for await" in posts_route:
    failures.append("posts sitemap full-history pagination must not use implicit async iteration")
if "PUBLIC_POSTS_MAX_PAGES" not in posts_route or "page < PUBLIC_POSTS_MAX_PAGES" not in posts_route:
    failures.append("posts sitemap full-history pagination must cap page traversal")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_public_sitemap_check: ok")
