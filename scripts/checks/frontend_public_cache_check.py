from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLIENT = ROOT / "apps/public-site/lib/public-posts.ts"
LIST_PAGE = ROOT / "apps/public-site/app/posts/page.tsx"
DETAIL_PAGE = ROOT / "apps/public-site/app/posts/[slug]/page.tsx"

missing = [path for path in (CLIENT, LIST_PAGE, DETAIL_PAGE) if not path.exists()]
if missing:
    raise SystemExit("missing public frontend cache files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

client = CLIENT.read_text()
list_page = LIST_PAGE.read_text()
detail_page = DETAIL_PAGE.read_text()

required_client = [
    "PUBLIC_POST_LIST_REVALIDATE_SECONDS",
    "PUBLIC_POST_DETAIL_REVALIDATE_SECONDS",
    "next: { revalidate: PUBLIC_POST_LIST_REVALIDATE_SECONDS }",
    "next: { revalidate: PUBLIC_POST_DETAIL_REVALIDATE_SECONDS }",
    "PUBLIC_CDN_INVALIDATION_POLICY",
    "no CDN headers",
    "no publish-triggered invalidation",
    "no tag-based revalidation",
    "/api/v1/public/posts",
    "/api/v1/public/posts/",
]

failures: list[str] = []
for needle in required_client:
    if needle not in client:
        failures.append(f"public cache policy missing {needle}")

for path, text in ((LIST_PAGE, list_page), (DETAIL_PAGE, detail_page)):
    if 'export const dynamic = "force-dynamic"' not in text:
        failures.append(f"{path.relative_to(ROOT)} must opt out of build-time API prerendering")

if 'cache: "no-store"' in client or "cache: 'no-store'" in client:
    failures.append("public frontend fetches must not use no-store after the cache policy boundary")

if "/api/v1/posts" in client.replace("/api/v1/public/posts/", "").replace("/api/v1/public/posts", ""):
    failures.append("public frontend cache policy must not call authenticated management posts routes")
if "Authorization" in client:
    failures.append("public frontend cache policy must not send bearer tokens")
if "revalidateTag" in client or "revalidatePath" in client:
    failures.append("public CDN/invalidation boundary must not add Next.js invalidation calls yet")
if "Cache-Control" in client:
    failures.append("public CDN/invalidation boundary must not add CDN headers yet")
if "cloudflare" in client.lower() or "purge" in client.lower():
    failures.append("public CDN/invalidation boundary must not call CDN purge APIs yet")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_public_cache_check: ok")
