from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME_PAGE = ROOT / "apps/public-site/app/page.tsx"
LIST_PAGE = ROOT / "apps/public-site/app/posts/page.tsx"
DETAIL_PAGE = ROOT / "apps/public-site/app/posts/[slug]/page.tsx"

missing = [path for path in (HOME_PAGE, LIST_PAGE, DETAIL_PAGE) if not path.exists()]
if missing:
    raise SystemExit("missing public canonical files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

home_page = HOME_PAGE.read_text()
list_page = LIST_PAGE.read_text()
detail_page = DETAIL_PAGE.read_text()

required_shared = [
    "const DEFAULT_PUBLIC_SITE_URL = \"http://localhost:3000\"",
    "function PUBLIC_SITE_URL(): string",
    "process.env.NEXT_PUBLIC_NAIRI_PUBLIC_SITE_URL",
    "metadataBase: new URL(PUBLIC_SITE_URL())",
    "alternates:",
    "canonical:",
]
required_home = [
    "canonical: \"/\"",
]
required_list = [
    "canonical: \"/posts\"",
]
required_detail = [
    "canonical: `/posts/${encodeURIComponent(post.slug)}`",
    "title: `${post.title} | Nairi`",
    "description: post.summary ?? undefined",
]

failures: list[str] = []
for needle in required_shared:
    if needle not in home_page:
        failures.append(f"home canonical missing {needle}")
    if needle not in list_page:
        failures.append(f"list canonical missing {needle}")
    if needle not in detail_page:
        failures.append(f"detail canonical missing {needle}")
for needle in required_home:
    if needle not in home_page:
        failures.append(f"home canonical missing {needle}")
for needle in required_list:
    if needle not in list_page:
        failures.append(f"list canonical missing {needle}")
for needle in required_detail:
    if needle not in detail_page:
        failures.append(f"detail canonical missing {needle}")

for path, text in ((HOME_PAGE, home_page), (LIST_PAGE, list_page), (DETAIL_PAGE, detail_page)):
    if "/api/v1/posts" in text.replace("/api/v1/public/posts/", "").replace("/api/v1/public/posts", ""):
        failures.append(f"{path.relative_to(ROOT)} must not call authenticated management posts routes")
    if "Authorization" in text:
        failures.append(f"{path.relative_to(ROOT)} must not send bearer tokens")
    if "metadataBase: new URL(\"http://localhost:3000\")" in text:
        failures.append(f"{path.relative_to(ROOT)} must use NEXT_PUBLIC_NAIRI_PUBLIC_SITE_URL fallback, not a hardcoded metadataBase")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_public_canonical_check: ok")
