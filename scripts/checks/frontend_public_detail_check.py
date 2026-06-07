from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "apps/public-site/app/posts/[slug]/page.tsx"
CLIENT = ROOT / "apps/public-site/lib/public-posts.ts"
PACKAGE = ROOT / "apps/public-site/package.json"

missing = [path for path in (PAGE, CLIENT, PACKAGE) if not path.exists()]
if missing:
    raise SystemExit("missing frontend public detail files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

page = PAGE.read_text()
client = CLIENT.read_text()
package = PACKAGE.read_text()

required_page = [
    "generateMetadata",
    "PublicPostDetailPage",
    "fetchPublicPostBySlug",
    "dangerouslySetInnerHTML",
    "bodyHtml",
    "notFound()",
]
required_client = [
    "/api/v1/public/posts/",
    "bodyHtml",
    "encodeURIComponent(slug)",
    "status === 404",
]
required_package = ["next", "react", "react-dom", "build", "typecheck"]

failures: list[str] = []
for needle in required_page:
    if needle not in page:
        failures.append(f"page missing {needle}")
for needle in required_client:
    if needle not in client:
        failures.append(f"client missing {needle}")
for needle in required_package:
    if needle not in package:
        failures.append(f"package missing {needle}")

if "/api/v1/posts" in page or "/api/v1/posts" in client.replace("/api/v1/public/posts/", ""):
    failures.append("frontend must not call authenticated management posts routes")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_public_detail_check: ok")
