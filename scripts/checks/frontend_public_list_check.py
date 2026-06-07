from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "apps/public-site/app/posts/page.tsx"
ERROR_PAGE = ROOT / "apps/public-site/app/posts/error.tsx"
CLIENT = ROOT / "apps/public-site/lib/public-posts.ts"
ROOT_PAGE = ROOT / "apps/public-site/app/page.tsx"

missing = [path for path in (PAGE, ERROR_PAGE, CLIENT, ROOT_PAGE) if not path.exists()]
if missing:
    raise SystemExit("missing frontend public list files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

page = PAGE.read_text()
error_page = ERROR_PAGE.read_text()
client = CLIENT.read_text()
root_page = ROOT_PAGE.read_text()

required_page = [
    "PublicPostsPage",
    "fetchPublicPosts",
    "/posts/",
    "publishedAt",
    "tags",
    "summary",
    "post-empty",
    "No published posts yet.",
]
required_error_page = [
    "use client",
    "PostsError",
    "post-error",
    "Articles are temporarily unavailable.",
]
required_client = [
    "PublicPostSummary",
    "ListPublicPostsResponse",
    "fetchPublicPosts",
    "/api/v1/public/posts",
    "nextCursor",
]
required_root_page = ["/posts", "Read published posts"]

failures: list[str] = []
for needle in required_page:
    if needle not in page:
        failures.append(f"page missing {needle}")
for needle in required_error_page:
    if needle not in error_page:
        failures.append(f"error page missing {needle}")
for needle in required_client:
    if needle not in client:
        failures.append(f"client missing {needle}")
for needle in required_root_page:
    if needle not in root_page:
        failures.append(f"root page missing {needle}")

for path, text in ((PAGE, page), (ERROR_PAGE, error_page), (CLIENT, client), (ROOT_PAGE, root_page)):
    if "/api/v1/posts" in text.replace("/api/v1/public/posts/", "").replace("/api/v1/public/posts", ""):
        failures.append(f"{path.relative_to(ROOT)} must not call authenticated management posts routes")
    if "Authorization" in text:
        failures.append(f"{path.relative_to(ROOT)} must not send bearer tokens for public list reads")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_public_list_check: ok")
