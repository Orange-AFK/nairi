from typing import Literal

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from nairi_api.auth import ApiError, AuthenticatedActor, api_error_response, require_scope
from nairi_api.config import Settings, get_settings
from nairi_api.posts import CreatedPostDraft, DuplicatePostSlugError, PostDraftInput, PostStore


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
    app.state.post_store = PostStore(settings.database_path)
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
        actor: AuthenticatedActor = Depends(require_scope("posts:write")),
    ) -> CreatePostDraftResponse:
        try:
            created: CreatedPostDraft = app.state.post_store.create_draft(
                PostDraftInput(
                    title=draft.title,
                    slug=draft.slug,
                    content_format=draft.content_format,
                    content=draft.content,
                    summary=draft.summary,
                    tags=draft.tags,
                    category_id=draft.category_id,
                    series_id=draft.series_id,
                    metadata=draft.metadata,
                ),
                actor.token,
            )
        except DuplicatePostSlugError as error:
            raise ApiError(409, "conflict", "Post slug already exists", {"slug": error.slug}) from error
        return CreatePostDraftResponse(
            postId=created.post_id,
            status="draft",
            revisionId=created.revision_id,
            createdAt=created.created_at,
        )

    return app


app = create_app()
