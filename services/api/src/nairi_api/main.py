from typing import Literal

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from nairi_api.auth import ApiError, api_error_response, require_scope
from nairi_api.config import Settings, get_settings


class CreatePostDraftRequest(BaseModel):
    title: str
    slug: str
    content_format: Literal["markdown", "mdx"] = Field(alias="contentFormat")
    content: str
    summary: str | None = None
    tags: list[str] = Field(default_factory=list)
    category_id: str | None = Field(default=None, alias="categoryId")
    series_id: str | None = Field(default=None, alias="seriesId")
    metadata: dict[str, object] = Field(default_factory=dict)


class CreatePostDraftResponse(BaseModel):
    post_id: str = Field(alias="postId")
    status: Literal["draft"]
    revision_id: str = Field(alias="revisionId")
    created_at: str = Field(alias="createdAt")


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

    @app.post("/api/v1/posts", status_code=201)
    def create_post_draft(
        draft: CreatePostDraftRequest,
        _actor: object = Depends(require_scope("posts:write")),
    ) -> CreatePostDraftResponse:
        return CreatePostDraftResponse(
            postId=f"draft-{draft.slug}",
            status="draft",
            revisionId=f"revision-{draft.slug}-1",
            createdAt="1970-01-01T00:00:00Z",
        )

    return app


app = create_app()
