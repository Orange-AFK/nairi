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
    "fetchPublicPosts",
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
if "rss" in route.lower():
    failures.append("sitemap boundary must not implement RSS")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_public_sitemap_check: ok")
