from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "apps/admin/src/App.tsx"
TEST = ROOT / "apps/admin/src/App.test.tsx"
MAIN = ROOT / "apps/admin/src/main.tsx"
CLIENT = ROOT / "apps/admin/src/adminApiClient.ts"
CLIENT_TEST = ROOT / "apps/admin/src/adminApiClient.test.ts"
TOKEN_PROVIDER = ROOT / "apps/admin/src/adminTokenProvider.ts"
TOKEN_PROVIDER_TEST = ROOT / "apps/admin/src/adminTokenProvider.test.ts"
PACKAGE = ROOT / "apps/admin/package.json"
VITE_CONFIG = ROOT / "apps/admin/vite.config.mjs"

missing = [
    path
    for path in (APP, TEST, MAIN, CLIENT, CLIENT_TEST, TOKEN_PROVIDER, TOKEN_PROVIDER_TEST, PACKAGE, VITE_CONFIG)
    if not path.exists()
]
if missing:
    raise SystemExit("missing frontend admin foundation files: " + ", ".join(str(path.relative_to(ROOT)) for path in missing))

app = APP.read_text()
test = TEST.read_text()
main = MAIN.read_text()
client = CLIENT.read_text()
client_test = CLIENT_TEST.read_text()
token_provider = TOKEN_PROVIDER.read_text()
token_provider_test = TOKEN_PROVIDER_TEST.read_text()
package = PACKAGE.read_text()
vite_config = VITE_CONFIG.read_text()

required_app = [
    "AdminApiClient",
    "listPosts",
    "getPost",
    "AdminPostDetail",
    "AdminPostUpdateInput",
    "updatePost",
    "CMS Admin Console",
    "Nairi Admin",
    'aria-label="Admin modules"',
    'aria-current={activeModule === adminModule.id ? "page" : undefined}',
    "Content workspace",
    "Media library",
    "System settings",
    "API-backed draft preview",
    "API-backed draft detail",
    "Draft detail could not be loaded.",
    "Draft title",
    "Draft slug",
    "Draft summary",
    "Draft category ID",
    "Draft tags",
    "Draft content",
    "Save draft changes",
    "Draft changes saved.",
    "Draft changes could not be saved.",
    "No draft posts are ready for review.",
    "Select a draft from the list to load its API-backed detail.",
    'aria-pressed={selectedPost?.id === post.id}',
]
required_test = [
    "adminApiClient",
    "switches between reserved admin modules without leaving the injected API boundary",
    "loads draft content through an injected API client",
    "selects a post and reads draft detail through the injected API boundary",
    "renders a stable empty state when no draft summaries are available",
    "submits draft edits through the injected update contract without publishing",
    "renders a safe edit error state when injected update fails",
    "ignores stale draft edit responses after a newer selection",
    "aria-pressed",
    "userEvent.setup",
]
required_main = [
    "createRoot",
    "createAdminApiClient",
    "createAdminTokenProvider",
    "VITE_API_BASE_URL",
    "getAuthToken: adminTokenProvider.getAuthToken",
    "<App apiClient={apiClient}",
]
required_client = [
    "createAdminApiClient",
    "/api/v1/posts?status=draft",
    "/api/v1/posts/${encodeURIComponent(postId)}",
    "getAuthToken",
    "Authorization",
    "Admin API credentials are not configured.",
    "Admin API base URL is not configured.",
    "Admin API base URL must be absolute.",
    "Admin API request failed.",
    'method: "PATCH"',
    "slug: input.slug",
    "expectedRevisionId: input.expectedRevisionId",
]
required_client_test = [
    "lists draft posts through the authenticated management API with an injected token provider",
    "reads a draft detail through the authenticated management API",
    "fails closed when no admin API credentials are configured",
    "fails closed when no API base URL is configured",
    "rejects relative API base URLs instead of guessing a browser-local target",
    "reports a safe generic error when the management API rejects the request",
    "updates a draft through the authenticated management API with optimistic detail mapping",
    "fails closed before PATCH when update credentials are missing",
    "reports a safe generic error when the management API rejects an update",
]
required_token_provider = [
    "AdminTokenProvider",
    "createAdminTokenProvider",
    "getAuthToken",
]
required_token_provider_test = [
    "fails closed until an admin session boundary supplies a token",
    "does not read Vite environment token names",
    "does not persist admin bearer tokens in browser storage",
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
    ("admin token provider", token_provider, required_token_provider),
    ("admin token provider test", token_provider_test, required_token_provider_test),
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
if forbidden_token_env in token_provider or "import.meta.env" in token_provider:
    failures.append("admin token provider must not read browser-bundled token env")
if "localStorage" in token_provider or "sessionStorage" in token_provider:
    failures.append("admin token provider must not persist bearer tokens in browser storage")
if "createAdminApiClient" not in main:
    failures.append("admin main entry must wire the runtime API client")
if "createAdminTokenProvider" not in main:
    failures.append("admin main entry must wire the token provider boundary")

if failures:
    raise SystemExit("\n".join(failures))

print("frontend_admin_foundation_check: ok")
