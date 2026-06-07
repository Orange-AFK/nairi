from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIST_PAGE = ROOT / "apps/public-site/app/posts/page.tsx"
DETAIL_PAGE = ROOT / "apps/public-site/app/posts/[slug]/page.tsx"
CLIENT = ROOT / "apps/public-site/lib/public-posts.ts"

missing = [path for path in (LIST_PAGE, DETAIL_PAGE, CLIENT) if not path.exists()]
if missing:
    raise SystemExit("missing public render coverage files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

list_page = LIST_PAGE.read_text()
detail_page = DETAIL_PAGE.read_text()
client = CLIENT.read_text()

required_list = [
    "post.publishedAt",
    "dateTime={post.publishedAt}",
    "post.summary ?? \"No summary provided.\"",
    "post.tags.length > 0",
    "tag-list",
    "href={`/posts/${post.slug}`}",
]
required_detail = [
    "notFound()",
    "publicPost.bodyHtml",
    "dangerouslySetInnerHTML",
    "dateTime={publicPost.publishedAt}",
    "publicPost.summary ?? \"No summary provided.\"",
    "publicPost.tags.length > 0",
    "tag-list",
]
required_client = [
    "status: \"published\";",
    "bodyHtml: string;",
    "summary: string | null;",
    "tags: string[];",
]

failures: list[str] = []
for needle in required_list:
    if needle not in list_page:
        failures.append(f"list render coverage missing {needle}")
for needle in required_detail:
    if needle not in detail_page:
        failures.append(f"detail render coverage missing {needle}")
for needle in required_client:
    if needle not in client:
        failures.append(f"client render contract missing {needle}")

for path, text in ((LIST_PAGE, list_page), (DETAIL_PAGE, detail_page), (CLIENT, client)):
    if "/api/v1/posts" in text.replace("/api/v1/public/posts/", "").replace("/api/v1/public/posts", ""):
        failures.append(f"{path.relative_to(ROOT)} must not call authenticated management posts routes")
    if "Authorization" in text:
        failures.append(f"{path.relative_to(ROOT)} must not send bearer tokens")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_public_render_check: ok")
