from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME_PAGE = ROOT / "apps/public-site/app/page.tsx"
LIST_PAGE = ROOT / "apps/public-site/app/posts/page.tsx"
DETAIL_PAGE = ROOT / "apps/public-site/app/posts/[slug]/page.tsx"
CLIENT = ROOT / "apps/public-site/lib/public-posts.ts"

missing = [path for path in (HOME_PAGE, LIST_PAGE, DETAIL_PAGE, CLIENT) if not path.exists()]
if missing:
    raise SystemExit("missing public site metadata files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

home_page = HOME_PAGE.read_text()
list_page = LIST_PAGE.read_text()
detail_page = DETAIL_PAGE.read_text()
client = CLIENT.read_text()

required_home = [
    "import type { Metadata } from \"next\"",
    "export const metadata: Metadata",
    "title: \"Nairi | Project Experience Publishing\"",
    "description: \"Read project experience notes and published articles through the public Nairi site.\"",
]
required_list = [
    "import type { Metadata } from \"next\"",
    "export const metadata: Metadata",
    "title: \"Articles | Nairi\"",
    "description: \"Browse published project experience notes from Nairi.\"",
]
required_detail = [
    "generateMetadata",
    "fetchPublicPostBySlug(slug)",
    "title: `${post.title} | Nairi`",
    "description: post.summary ?? undefined",
    "Post not found | Nairi",
]

failures: list[str] = []
for needle in required_home:
    if needle not in home_page:
        failures.append(f"home metadata missing {needle}")
for needle in required_list:
    if needle not in list_page:
        failures.append(f"list metadata missing {needle}")
for needle in required_detail:
    if needle not in detail_page:
        failures.append(f"detail metadata missing {needle}")

for path, text in ((HOME_PAGE, home_page), (LIST_PAGE, list_page), (DETAIL_PAGE, detail_page), (CLIENT, client)):
    if "/api/v1/posts" in text.replace("/api/v1/public/posts/", "").replace("/api/v1/public/posts", ""):
        failures.append(f"{path.relative_to(ROOT)} must not call authenticated management posts routes")
    if "Authorization" in text:
        failures.append(f"{path.relative_to(ROOT)} must not send bearer tokens")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_public_metadata_check: ok")
