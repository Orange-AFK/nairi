import html
import re
from typing import Literal

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from nairi_api.auth import ApiError, AuthenticatedActor, api_error_response, require_scope
from nairi_api.config import Settings, get_settings
from nairi_api.posts import (
    CreatedPostDraft,
    DuplicatePostSlugError,
    PostDraftInput,
    PostDraftNotFoundError,
    PostRevisionConflictError,
    PostStore,
    PublishedPost,
    StoredPostDraft,
    UpdatedPostDraft,
)


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


class UpdatePostDraftRequest(CreatePostDraftRequest):
    expected_revision_id: str = Field(alias="expectedRevisionId")


class UpdatePostDraftResponse(BaseModel):
    post_id: str = Field(alias="postId")
    status: Literal["draft"]
    revision_id: str = Field(alias="revisionId")
    updated_at: str = Field(alias="updatedAt")


class PublishPostRequest(BaseModel):
    revision_id: str = Field(alias="revisionId")
    publish_mode: Literal["immediate", "scheduled"] = Field(alias="publishMode")
    scheduled_at: str | None = Field(default=None, alias="scheduledAt")


class PublishPostResponse(BaseModel):
    post_id: str = Field(alias="postId")
    status: Literal["published"]
    published_at: str | None = Field(alias="publishedAt")
    job_id: str = Field(alias="jobId")


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


class PublishedPostSummaryResponse(BaseModel):
    post_id: str = Field(alias="postId")
    title: str
    slug: str
    status: Literal["published"]
    content_format: Literal["markdown", "mdx"] = Field(alias="contentFormat")
    summary: str | None = None
    tags: list[str]
    category_id: str | None = Field(alias="categoryId")
    series_id: str | None = Field(alias="seriesId")
    metadata: dict[str, object]
    revision_id: str = Field(alias="revisionId")
    published_at: str = Field(alias="publishedAt")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")


class PublicPostSummaryResponse(BaseModel):
    post_id: str = Field(alias="postId")
    title: str
    slug: str
    status: Literal["published"]
    content_format: Literal["markdown", "mdx"] = Field(alias="contentFormat")
    summary: str | None = None
    tags: list[str]
    category_id: str | None = Field(alias="categoryId")
    series_id: str | None = Field(alias="seriesId")
    published_at: str = Field(alias="publishedAt")


class ListPostDraftsResponse(BaseModel):
    items: list[PostDraftSummaryResponse | PublishedPostSummaryResponse]
    next_cursor: str | None = Field(default=None, alias="nextCursor")


class ListPublicPostsResponse(BaseModel):
    items: list[PublicPostSummaryResponse]
    next_cursor: str | None = Field(default=None, alias="nextCursor")


class ReadPublicPostResponse(PublicPostSummaryResponse):
    content: str
    body_html: str = Field(alias="bodyHtml")


class ReadPostDraftResponse(PostDraftSummaryResponse):
    content: str


class ReadPublishedPostResponse(PublishedPostSummaryResponse):
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


def published_post_summary_response(post: StoredPostDraft) -> PublishedPostSummaryResponse:
    return PublishedPostSummaryResponse(
        postId=post.post_id,
        title=post.title,
        slug=post.slug,
        status="published",
        contentFormat=post.content_format,
        summary=post.summary,
        tags=post.tags,
        categoryId=post.category_id,
        seriesId=post.series_id,
        metadata=post.metadata,
        revisionId=post.revision_id,
        publishedAt=post.published_at or post.updated_at,
        createdAt=post.created_at,
        updatedAt=post.updated_at,
    )


def public_post_summary_response(post: StoredPostDraft) -> PublicPostSummaryResponse:
    return PublicPostSummaryResponse(
        postId=post.post_id,
        title=post.title,
        slug=post.slug,
        status="published",
        contentFormat=post.content_format,
        summary=post.summary,
        tags=post.tags,
        categoryId=post.category_id,
        seriesId=post.series_id,
        publishedAt=post.published_at or post.updated_at,
    )


def render_public_body_html(content: str) -> str:
    paragraphs: list[str] = []
    for block in content.split("\n\n"):
        block = block.strip()
        if not block or "<script" in block.lower() or "</script" in block.lower():
            continue
        if block.startswith("# "):
            paragraphs.append(f"<h1>{html.escape(block[2:].strip())}</h1>")
            continue
        escaped = html.escape(block)
        escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
        paragraphs.append(f"<p>{escaped}</p>")
    return "\n".join(paragraphs)


def paginate_posts(
    posts: list[StoredPostDraft],
    limit: int | None,
    cursor: str | None,
) -> tuple[list[StoredPostDraft], str | None]:
    start_index = 0
    if cursor is not None:
        for index, post in enumerate(posts):
            if post.post_id == cursor:
                start_index = index + 1
                break
    if limit is None or limit < 1:
        return posts[start_index:], None
    page = posts[start_index : start_index + limit]
    next_index = start_index + limit
    next_cursor = page[-1].post_id if page and next_index < len(posts) else None
    return page, next_cursor


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

    @app.get("/api/v1/public/posts")
    def list_public_posts(
        limit: int | None = None,
        cursor: str | None = None,
    ) -> ListPublicPostsResponse:
        published_posts: list[StoredPostDraft] = app.state.post_store.list_published()
        published_posts, next_cursor = paginate_posts(published_posts, limit, cursor)
        return ListPublicPostsResponse(
            items=[public_post_summary_response(post) for post in published_posts],
            nextCursor=next_cursor,
        )

    @app.get("/api/v1/public/posts/{slug}")
    def read_public_post(slug: str) -> ReadPublicPostResponse:
        published_post = app.state.post_store.get_published_by_slug(slug)
        if published_post is None:
            raise ApiError(404, "not_found", "Post not found", {"slug": slug})
        return ReadPublicPostResponse(
            **public_post_summary_response(published_post).model_dump(by_alias=True),
            content=published_post.content,
            bodyHtml=render_public_body_html(published_post.content),
        )

    @app.get("/api/v1/posts")
    def list_posts(
        status: Literal["draft", "published"] = "draft",
        tag: str | None = None,
        category: str | None = None,
        series: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        _actor: AuthenticatedActor = Depends(require_scope("posts:read")),
    ) -> ListPostDraftsResponse:
        if status == "published":
            published_posts: list[StoredPostDraft] = app.state.post_store.list_published(
                tag=tag,
                category_id=category,
                series_id=series,
            )
            published_posts, next_cursor = paginate_posts(published_posts, limit, cursor)
            return ListPostDraftsResponse(
                items=[published_post_summary_response(post) for post in published_posts],
                nextCursor=next_cursor,
            )
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

    @app.patch("/api/v1/posts/{post_id}")
    def update_post_draft(
        post_id: str,
        draft: UpdatePostDraftRequest,
        actor: AuthenticatedActor = Depends(require_scope("posts:write")),
    ) -> UpdatePostDraftResponse:
        validate_post_draft_request(draft)
        try:
            updated: UpdatedPostDraft = app.state.post_store.update_draft(
                post_id,
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
                draft.expected_revision_id,
            )
        except PostDraftNotFoundError as error:
            raise ApiError(404, "not_found", "Post not found", {"postId": error.post_id}) from error
        except DuplicatePostSlugError as error:
            raise ApiError(409, "conflict", "Post slug already exists", {"slug": error.slug}) from error
        except PostRevisionConflictError as error:
            raise ApiError(
                409,
                "conflict",
                "Post revision conflict",
                {"currentRevisionId": error.current_revision_id},
            ) from error
        return UpdatePostDraftResponse(
            postId=updated.post_id,
            status="draft",
            revisionId=updated.revision_id,
            updatedAt=updated.updated_at,
        )

    @app.get("/api/v1/posts/{post_id}")
    def read_post_draft(
        post_id: str,
        _actor: AuthenticatedActor = Depends(require_scope("posts:read")),
    ) -> ReadPostDraftResponse | ReadPublishedPostResponse:
        draft: StoredPostDraft | None = app.state.post_store.get_draft(post_id)
        if draft is not None:
            return ReadPostDraftResponse(
                **post_draft_summary_response(draft).model_dump(by_alias=True),
                content=draft.content,
            )
        published_post: StoredPostDraft | None = app.state.post_store.get_published(post_id)
        if published_post is None:
            raise ApiError(404, "not_found", "Post not found", {"postId": post_id})
        return ReadPublishedPostResponse(
            **published_post_summary_response(published_post).model_dump(by_alias=True),
            content=published_post.content,
        )

    @app.post("/api/v1/posts/{post_id}/publish")
    def publish_post(
        post_id: str,
        request: PublishPostRequest,
        actor: AuthenticatedActor = Depends(require_scope("posts:publish")),
    ) -> PublishPostResponse:
        try:
            published: PublishedPost = app.state.post_store.publish_draft(post_id, request.revision_id, actor.token)
        except PostDraftNotFoundError as error:
            raise ApiError(404, "not_found", "Post not found", {"postId": error.post_id}) from error
        except PostRevisionConflictError as error:
            raise ApiError(
                409,
                "conflict",
                "Post revision conflict",
                {"currentRevisionId": error.current_revision_id},
            ) from error
        return PublishPostResponse(
            postId=published.post_id,
            status="published",
            publishedAt=published.published_at,
            jobId=published.job_id,
        )

    return app


app = create_app()
