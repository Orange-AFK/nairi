from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSS = ROOT / "apps/public-site/app/globals.css"
HOME_PAGE = ROOT / "apps/public-site/app/page.tsx"
LIST_PAGE = ROOT / "apps/public-site/app/posts/page.tsx"
DETAIL_PAGE = ROOT / "apps/public-site/app/posts/[slug]/page.tsx"
ERROR_PAGE = ROOT / "apps/public-site/app/posts/error.tsx"

missing = [path for path in (CSS, HOME_PAGE, LIST_PAGE, DETAIL_PAGE, ERROR_PAGE) if not path.exists()]
if missing:
    raise SystemExit("missing public site styling files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

css = CSS.read_text()
home_page = HOME_PAGE.read_text()
list_page = LIST_PAGE.read_text()
detail_page = DETAIL_PAGE.read_text()
error_page = ERROR_PAGE.read_text()

required_css = [
    "--nairi-surface",
    "--nairi-border",
    "--nairi-muted",
    "--nairi-shadow-soft",
    ".article-header",
    ".surface-card",
    ".surface-card-link",
    ".article-body.surface-card",
    ".post-card.surface-card",
    ".post-empty.surface-card",
    ".post-error.surface-card",
]
required_home = ["article-header", "surface-card", "surface-card-link"]
required_list = ["article-header", "post-card surface-card", "post-empty surface-card"]
required_detail = ["article-header", "article-body surface-card"]
required_error = ["article-header", "post-error surface-card"]

failures: list[str] = []
for needle in required_css:
    if needle not in css:
        failures.append(f"css missing {needle}")
for needle in required_home:
    if needle not in home_page:
        failures.append(f"home page missing {needle}")
for needle in required_list:
    if needle not in list_page:
        failures.append(f"list page missing {needle}")
for needle in required_detail:
    if needle not in detail_page:
        failures.append(f"detail page missing {needle}")
for needle in required_error:
    if needle not in error_page:
        failures.append(f"error page missing {needle}")

for path, text in ((HOME_PAGE, home_page), (LIST_PAGE, list_page), (DETAIL_PAGE, detail_page), (ERROR_PAGE, error_page)):
    if "/api/v1/posts" in text.replace("/api/v1/public/posts/", "").replace("/api/v1/public/posts", ""):
        failures.append(f"{path.relative_to(ROOT)} must not call authenticated management posts routes")
    if "Authorization" in text:
        failures.append(f"{path.relative_to(ROOT)} must not send bearer tokens")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_public_style_check: ok")
