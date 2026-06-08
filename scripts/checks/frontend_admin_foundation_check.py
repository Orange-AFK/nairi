from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "apps/admin/src/App.tsx"
TEST = ROOT / "apps/admin/src/App.test.tsx"
MAIN = ROOT / "apps/admin/src/main.tsx"
PACKAGE = ROOT / "apps/admin/package.json"
VITE_CONFIG = ROOT / "apps/admin/vite.config.mjs"

missing = [path for path in (APP, TEST, MAIN, PACKAGE, VITE_CONFIG) if not path.exists()]
if missing:
    raise SystemExit("missing frontend admin foundation files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

app = APP.read_text()
test = TEST.read_text()
main = MAIN.read_text()
package = PACKAGE.read_text()
vite_config = VITE_CONFIG.read_text()

required_app = [
    "AdminApiClient",
    "listPosts",
    "CMS Admin Console",
    "Nairi Admin",
    "API-backed draft preview",
]
required_test = [
    "adminApiClient",
    "loads draft content through an injected API client",
    "selects a post without bypassing the injected API boundary",
    "userEvent.setup",
]
required_main = ["createRoot", "<App apiClient={apiClient}"]
required_package = ["vite", "vitest", "@testing-library/react", "@vitejs/plugin-react", "test", "typecheck", "build"]
required_vite = ["@vitejs/plugin-react", "jsdom", "setupFiles"]

failures: list[str] = []
for label, text, needles in (
    ("app", app, required_app),
    ("test", test, required_test),
    ("main", main, required_main),
    ("package", package, required_package),
    ("vite config", vite_config, required_vite),
):
    for needle in needles:
        if needle not in text:
            failures.append(f"{label} missing {needle}")

if "/api/v1/posts" in app or "fetch(" in app:
    failures.append("admin app must use an injected API client in this foundation boundary")
if "sqlite" in app.lower() or "database" in app.lower():
    failures.append("admin app must not mention direct database access")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_admin_foundation_check: ok")
