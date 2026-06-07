from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE = ROOT / "apps/public-site/app/sitemap.xml/route.ts"
CLIENT = ROOT / "apps/public-site/lib/public-posts.ts"

missing = [path for path in (ROUTE, CLIENT) if not path.exists()]
if missing:
    raise SystemExit("missing public sitemap files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

route = ROUTE.read_text()
client = CLIENT.read_text()

required_route = [
    "export const dynamic = \"force-dynamic\"",
    "export async function GET()",
    "fetchAllPublicPosts",
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
    "<loc>${siteUrl}/</loc>",
    "<loc>${siteUrl}/posts</loc>",
    "encodeURIComponent(post.slug)",
    "<lastmod>${post.publishedAt}</lastmod>",
]

failures: list[str] = []
for needle in required_route:
    if needle not in route:
        failures.append(f"sitemap route missing {needle}")

if "/api/v1/posts" in route or "/api/v1/posts" in client.replace("/api/v1/public/posts/", "").replace("/api/v1/public/posts", ""):
    failures.append("sitemap must not call authenticated management posts routes")
if "Authorization" in route:
    failures.append("sitemap must not send bearer tokens")
if "Cache-Control" in route:
    failures.append("sitemap cache policy must not add CDN/cache headers yet")
if "cloudflare" in route.lower() or "purge" in route.lower().replace("no purge", ""):
    failures.append("sitemap cache policy must not call CDN purge APIs yet")
if "revalidateTag" in route or "revalidatePath" in route:
    failures.append("sitemap cache policy must not add tag/path invalidation calls yet")
if "export const revalidate = PUBLIC_SITEMAP_REVALIDATE_SECONDS" in route:
    failures.append("sitemap route revalidate export must stay statically analyzable for Next.js")
if "rss" in route.lower():
    failures.append("sitemap boundary must not implement RSS")
if "while" not in route:
    failures.append("sitemap full-history pagination must use an explicit bounded loop")
if "for await" in route:
    failures.append("sitemap full-history pagination must not use implicit async iteration")
if "PUBLIC_POSTS_MAX_PAGES" not in route or "page < PUBLIC_POSTS_MAX_PAGES" not in route:
    failures.append("sitemap full-history pagination must cap page traversal")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_public_sitemap_check: ok")
