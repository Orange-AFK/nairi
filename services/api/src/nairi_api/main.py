from fastapi import Depends, FastAPI

from nairi_api.auth import ApiError, api_error_response, require_scope
from nairi_api.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = get_settings()
    app = FastAPI(title="Nairi API", version=settings.version)
    app.state.settings = settings
    app.add_exception_handler(ApiError, api_error_response)

    @app.get("/api/v1/health")
    def read_api_health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": settings.service_name,
            "version": settings.version,
        }

    @app.get("/api/v1/mdx-components")
    def list_mdx_components(_actor: object = Depends(require_scope("settings:read"))) -> dict[str, list[dict[str, str]]]:
        return {"items": []}

    return app


app = create_app()
