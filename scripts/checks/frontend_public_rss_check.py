from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE = ROOT / "apps/public-site/app/rss.xml/route.ts"
CLIENT = ROOT / "apps/public-site/lib/public-posts.ts"

missing = [path for path in (ROUTE, CLIENT) if not path.exists()]
if missing:
    raise SystemExit("missing public RSS files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

route = ROUTE.read_text()
client = CLIENT.read_text()

required_route = [
    "export const dynamic = \"force-dynamic\"",
    "export async function GET()",
    "fetchAllPublicPosts",
    "PUBLIC_FEED_FULL_HISTORY_PAGINATION_POLICY",
    "full-history feed pagination",
    "PUBLIC_POSTS_PAGE_SIZE",
    "PUBLIC_POSTS_MAX_PAGES",
    "cursor",
    "nextCursor",
    "PUBLIC_SITE_URL",
    "application/rss+xml",
    "<rss version=\"2.0\">",
    "<channel>",
    "<title>Nairi</title>",
    "<link>${siteUrl}/</link>",
    "<description>Published project experience notes from Nairi.</description>",
    "<item>",
    "<title>${escapeXml(post.title)}</title>",
    "<link>${postUrl}</link>",
    "<guid>${postUrl}</guid>",
    "<pubDate>${new Date(post.publishedAt).toUTCString()}</pubDate>",
    "<description>${escapeXml(post.summary ?? \"\")}</description>",
]

failures: list[str] = []
for needle in required_route:
    if needle not in route:
        failures.append(f"RSS route missing {needle}")

if "bodyHtml" in route or "content:encoded" in route:
    failures.append("RSS boundary must not publish full bodyHtml/content")
if "atom" in route.lower():
    failures.append("RSS boundary must not implement Atom")
if "/api/v1/posts" in route or "/api/v1/posts" in client.replace("/api/v1/public/posts/", "").replace("/api/v1/public/posts", ""):
    failures.append("RSS must not call authenticated management posts routes")
if "Authorization" in route:
    failures.append("RSS must not send bearer tokens")
if "while" not in route:
    failures.append("RSS full-history pagination must use an explicit bounded loop")
if "for await" in route:
    failures.append("RSS full-history pagination must not use implicit async iteration")
if "PUBLIC_POSTS_MAX_PAGES" not in route or "page < PUBLIC_POSTS_MAX_PAGES" not in route:
    failures.append("RSS full-history pagination must cap page traversal")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_public_rss_check: ok")
