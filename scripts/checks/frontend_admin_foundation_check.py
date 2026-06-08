from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "apps/admin/src/App.tsx"
TEST = ROOT / "apps/admin/src/App.test.tsx"
MAIN = ROOT / "apps/admin/src/main.tsx"
CLIENT = ROOT / "apps/admin/src/adminApiClient.ts"
CLIENT_TEST = ROOT / "apps/admin/src/adminApiClient.test.ts"
PACKAGE = ROOT / "apps/admin/package.json"
VITE_CONFIG = ROOT / "apps/admin/vite.config.mjs"

missing = [path for path in (APP, TEST, MAIN, CLIENT, CLIENT_TEST, PACKAGE, VITE_CONFIG) if not path.exists()]
if missing:
    raise SystemExit("missing frontend admin foundation files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

app = APP.read_text()
test = TEST.read_text()
main = MAIN.read_text()
client = CLIENT.read_text()
client_test = CLIENT_TEST.read_text()
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
required_main = ["createRoot", "createAdminApiClient", "VITE_API_BASE_URL", "<App apiClient={apiClient}"]
required_client = [
    "createAdminApiClient",
    "/api/v1/posts?status=draft",
    "getAuthToken",
    "Authorization",
    "Admin API credentials are not configured.",
    "Admin API base URL is not configured.",
    "Admin API base URL must be absolute.",
    "Admin API request failed.",
]
required_client_test = [
    "lists draft posts through the authenticated management API with an injected token provider",
    "fails closed when no admin API credentials are configured",
    "fails closed when no API base URL is configured",
    "rejects relative API base URLs instead of guessing a browser-local target",
    "reports a safe generic error when the management API rejects the request",
]
required_package = ["vite", "vitest", "@testing-library/react", "@vitejs/plugin-react", "test", "typecheck", "build"]
required_vite = ["@vitejs/plugin-react", "jsdom", "setupFiles"]

failures: list[str] = []
for label, text, needles in (
    ("app", app, required_app),
    ("test", test, required_test),
    ("main", main, required_main),
    ("admin api client", client, required_client),
    ("admin api client test", client_test, required_client_test),
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
forbidden_token_env = "VITE_ADMIN" + "_API_TOKEN"
forbidden_bearer_marker = "Bear" + "er"
if forbidden_token_env in app or "import.meta.env" in app:
    failures.append("admin app component must not read runtime env directly")
if "Authorization" in main or forbidden_token_env in main or forbidden_bearer_marker in main:
    failures.append("admin main entry must not bundle bearer tokens")
if "createAdminApiClient" not in main:
    failures.append("admin main entry must wire the runtime API client")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_admin_foundation_check: ok")
