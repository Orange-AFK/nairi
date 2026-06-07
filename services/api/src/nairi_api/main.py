import re
from typing import Literal

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from nairi_api.auth import ApiError, AuthenticatedActor, api_error_response, require_scope
from nairi_api.config import Settings, get_settings
from nairi_api.posts import CreatedPostDraft, DuplicatePostSlugError, PostDraftInput, PostStore, StoredPostDraft


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


class PostDraftSummaryResponse(BaseModel):
    post_id: str = Field(alias="postId")
    title: str
    slug: str
    status: Literal["draft"]
    content_format: Literal["markdown", "mdx"] = Field(alias="contentFormat")
    summary: str | None = None
    tags: list[str]
    category_id: str | None = Field(alias="categoryId")
    series_id: str | None = Field(alias="seriesId")
    metadata: dict[str, object]
    revision_id: str = Field(alias="revisionId")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")


class ListPostDraftsResponse(BaseModel):
    items: list[PostDraftSummaryResponse]
    next_cursor: str | None = Field(default=None, alias="nextCursor")


class ReadPostDraftResponse(PostDraftSummaryResponse):
    content: str


SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")



def validate_post_draft_request(draft: CreatePostDraftRequest) -> None:
    details: dict[str, str] = {}
    if not draft.title.strip():
        details["title"] = "Title is required"
    if not SLUG_PATTERN.fullmatch(draft.slug):
        details["slug"] = "Slug must contain only lowercase letters, numbers, and hyphens"
    if not draft.content.strip():
        details["content"] = "Content is required"
    if details:
        raise ApiError(400, "invalid_request", "Invalid post draft request", details)


def post_draft_summary_response(draft: StoredPostDraft) -> PostDraftSummaryResponse:
    return PostDraftSummaryResponse(
        postId=draft.post_id,
        title=draft.title,
        slug=draft.slug,
        status="draft",
        contentFormat=draft.content_format,
        summary=draft.summary,
        tags=draft.tags,
        categoryId=draft.category_id,
        seriesId=draft.series_id,
        metadata=draft.metadata,
        revisionId=draft.revision_id,
        createdAt=draft.created_at,
        updatedAt=draft.updated_at,
    )


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

    @app.get("/api/v1/posts")
    def list_post_drafts(
        _actor: AuthenticatedActor = Depends(require_scope("posts:read")),
    ) -> ListPostDraftsResponse:
        drafts: list[StoredPostDraft] = app.state.post_store.list_drafts()
        return ListPostDraftsResponse(
            items=[post_draft_summary_response(draft) for draft in drafts],
            nextCursor=None,
        )

    @app.post("/api/v1/posts", status_code=201)
    def create_post_draft(
        draft: CreatePostDraftRequest,
        actor: AuthenticatedActor = Depends(require_scope("posts:write")),
    ) -> CreatePostDraftResponse:
        validate_post_draft_request(draft)
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

    @app.get("/api/v1/posts/{post_id}")
    def read_post_draft(
        post_id: str,
        _actor: AuthenticatedActor = Depends(require_scope("posts:read")),
    ) -> ReadPostDraftResponse:
        draft: StoredPostDraft | None = app.state.post_store.get_draft(post_id)
        if draft is None:
            raise ApiError(404, "not_found", "Post not found", {"postId": post_id})
        return ReadPostDraftResponse(
            **post_draft_summary_response(draft).model_dump(by_alias=True),
            content=draft.content,
        )

    return app


app = create_app()
