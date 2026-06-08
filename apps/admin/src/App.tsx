import { type FormEvent, useEffect, useRef, useState } from "react";

import "./styles.css";

export type AdminPostMetadata = Record<string, unknown>;

export type AdminPostSummary = {
  id: string;
  title: string;
  slug: string;
  summary?: string | null;
  categoryId?: string | null;
  seriesId?: string | null;
  tags?: string[];
  metadata?: AdminPostMetadata;
  status: string;
  updatedAt: string;
};

export type AdminPostDetail = AdminPostSummary & {
  contentFormat: "markdown" | "mdx";
  content: string;
  revisionId: string;
};

export type AdminPostUpdateInput = {
  title: string;
  slug: string;
  summary: string | null;
  categoryId: string | null;
  seriesId: string | null;
  tags: string[];
  metadata: AdminPostMetadata;
  contentFormat: "markdown" | "mdx";
  content: string;
  expectedRevisionId: string;
};

export type AdminPostPublishInput = {
  revisionId: string;
  publishMode: "immediate";
  scheduledAt: string | null;
};

export type AdminPublicInvalidationResult = {
  mode: "recorded";
  surfaces: string[];
  execution: {
    status: string;
    executor: string;
    executedAt: string | null;
    errorCode: string | null;
    errorMessage: string | null;
  };
  dispatch: {
    status: string;
    reason: string;
    attempted: boolean;
    attemptedAt: string | null;
  };
};

export type AdminPostPublishResult = {
  id: string;
  status: string;
  publishedAt: string;
  jobId: string;
  publicInvalidation: AdminPublicInvalidationResult;
};

export type AdminPublishReviewRequestInput = {
  revisionId: string;
};

export type AdminPublishReviewRequestResult = {
  requestId: string;
  postId: string;
  revisionId: string;
  status: "pending";
  requestedAt: string;
};

export type AdminApiClient = {
  listPosts: () => Promise<AdminPostSummary[]>;
  listPublishedPosts: () => Promise<AdminPostSummary[]>;
  getPost: (postId: string) => Promise<AdminPostDetail>;
  updatePost: (postId: string, input: AdminPostUpdateInput) => Promise<AdminPostDetail>;
  requestPublishReview: (
    postId: string,
    input: AdminPublishReviewRequestInput
  ) => Promise<AdminPublishReviewRequestResult>;
  publishPost: (postId: string, input: AdminPostPublishInput) => Promise<AdminPostPublishResult>;
};

type AdminModule = "content" | "media" | "settings";

type AdminRoute = {
  module: AdminModule;
  postId: string | null;
};

type AppProps = {
  apiClient: AdminApiClient;
};

const adminModules: Array<{ id: AdminModule; label: string }> = [
  { id: "content", label: "Content" },
  { id: "media", label: "Media" },
  { id: "settings", label: "Settings" }
];

function parseAdminRoute(hash = typeof window === "undefined" ? "" : window.location.hash): AdminRoute {
  const [moduleSegment, postIdSegment] = hash.replace(/^#/, "").split("/");
  const module = adminModules.some((adminModule) => adminModule.id === moduleSegment)
    ? (moduleSegment as AdminModule)
    : "content";
  let postId: string | null = null;

  if (module === "content" && postIdSegment) {
    try {
      postId = decodeURIComponent(postIdSegment);
    } catch {
      postId = null;
    }
  }

  return { module, postId };
}

function adminRouteHash(route: AdminRoute): string {
  if (route.module === "content" && route.postId) {
    return `#content/${encodeURIComponent(route.postId)}`;
  }
  return `#${route.module}`;
}

function parseDraftTags(value: string): string[] {
  return [...new Set(value.split(",").map((tag) => tag.trim()).filter(Boolean))];
}

function stringifyDraftMetadata(metadata: AdminPostMetadata | undefined): string {
  return JSON.stringify(metadata ?? {}, null, 2);
}

function parseDraftMetadata(value: string): AdminPostMetadata {
  const trimmedValue = value.trim();
  if (!trimmedValue) {
    return {};
  }

  const parsed = JSON.parse(trimmedValue) as unknown;
  if (parsed === null || Array.isArray(parsed) || typeof parsed !== "object") {
    throw new Error("Draft metadata must be a JSON object.");
  }
  return parsed as AdminPostMetadata;
}

export function App({ apiClient }: AppProps) {
  const [adminRoute, setAdminRoute] = useState<AdminRoute>(() => parseAdminRoute());
  const [posts, setPosts] = useState<AdminPostSummary[]>([]);
  const [publishedPosts, setPublishedPosts] = useState<AdminPostSummary[]>([]);
  const [selectedPost, setSelectedPost] = useState<AdminPostSummary | null>(null);
  const [selectedPostDetail, setSelectedPostDetail] = useState<AdminPostDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [isSavingDraft, setIsSavingDraft] = useState(false);
  const [isPublishingDraft, setIsPublishingDraft] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [publishReviewStatus, setPublishReviewStatus] = useState<string | null>(null);
  const [publishReviewRequest, setPublishReviewRequest] = useState<AdminPublishReviewRequestResult | null>(null);
  const [publishConfirmationStatus, setPublishConfirmationStatus] = useState<string | null>(null);
  const [publishActionStatus, setPublishActionStatus] = useState<string | null>(null);
  const [publishActionError, setPublishActionError] = useState<string | null>(null);
  const detailRequestIdRef = useRef(0);
  const saveRequestIdRef = useRef(0);
  const publishRequestIdRef = useRef(0);
  const activeModule = adminRoute.module;

  function setRoute(route: AdminRoute) {
    setAdminRoute(route);
    if (window.location.hash !== adminRouteHash(route)) {
      window.history.pushState(null, "", adminRouteHash(route));
    }
  }

  useEffect(() => {
    function syncRouteFromHash() {
      setAdminRoute(parseAdminRoute());
    }

    window.addEventListener("hashchange", syncRouteFromHash);
    window.addEventListener("popstate", syncRouteFromHash);
    return () => {
      window.removeEventListener("hashchange", syncRouteFromHash);
      window.removeEventListener("popstate", syncRouteFromHash);
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadPosts() {
      try {
        const [loadedPosts, loadedPublishedPosts] = await Promise.all([
          apiClient.listPosts(),
          apiClient.listPublishedPosts()
        ]);
        if (!cancelled) {
          setPosts(loadedPosts);
          setPublishedPosts(loadedPublishedPosts);
          setSelectedPost(loadedPosts[0] ?? null);
          setIsLoading(false);
        }
      } catch {
        if (!cancelled) {
          setLoadError("Admin content could not be loaded.");
          setIsLoading(false);
        }
      }
    }

    void loadPosts();

    return () => {
      cancelled = true;
    };
  }, [apiClient]);

  async function selectPost(post: AdminPostSummary, updateRoute = true) {
    const detailRequestId = detailRequestIdRef.current + 1;
    detailRequestIdRef.current = detailRequestId;
    saveRequestIdRef.current += 1;
    publishRequestIdRef.current += 1;
    setSelectedPost(post);
    setSelectedPostDetail(null);
    setDetailError(null);
    setSaveStatus(null);
    setSaveError(null);
    setPublishReviewStatus(null);
    setPublishReviewRequest(null);
    setPublishConfirmationStatus(null);
    setPublishActionStatus(null);
    setPublishActionError(null);
    setIsPublishingDraft(false);
    setIsDetailLoading(true);
    if (updateRoute) {
      setRoute({ module: "content", postId: post.id });
    }

    try {
      const detail = await apiClient.getPost(post.id);
      if (detailRequestIdRef.current === detailRequestId) {
        setSelectedPostDetail(detail);
      }
    } catch {
      if (detailRequestIdRef.current === detailRequestId) {
        setDetailError("Draft detail could not be loaded.");
      }
    } finally {
      if (detailRequestIdRef.current === detailRequestId) {
        setIsDetailLoading(false);
      }
    }
  }

  async function saveDraftEdits(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedPostDetail) {
      return;
    }

    const formData = new FormData(event.currentTarget);
    const saveRequestId = saveRequestIdRef.current + 1;
    const savedPostId = selectedPostDetail.id;
    const savedRevisionId = selectedPostDetail.revisionId;
    saveRequestIdRef.current = saveRequestId;
    publishRequestIdRef.current += 1;
    setIsPublishingDraft(false);
    setIsSavingDraft(true);
    setSaveStatus(null);
    setSaveError(null);

    try {
      const summary = String(formData.get("summary") ?? "").trim();
      const categoryId = String(formData.get("categoryId") ?? "").trim();
      const seriesId = String(formData.get("seriesId") ?? "").trim();
      const updatedPost = await apiClient.updatePost(savedPostId, {
        title: String(formData.get("title") ?? ""),
        slug: String(formData.get("slug") ?? ""),
        summary: summary || null,
        categoryId: categoryId || null,
        seriesId: seriesId || null,
        tags: parseDraftTags(String(formData.get("tags") ?? "")),
        metadata: parseDraftMetadata(String(formData.get("metadata") ?? "")),
        contentFormat: selectedPostDetail.contentFormat,
        content: String(formData.get("content") ?? ""),
        expectedRevisionId: savedRevisionId
      });
      if (
        saveRequestIdRef.current === saveRequestId &&
        selectedPostDetail?.id === savedPostId &&
        selectedPostDetail.revisionId === savedRevisionId
      ) {
        setSelectedPost(updatedPost);
        setSelectedPostDetail(updatedPost);
        setPosts((currentPosts) =>
          currentPosts.map((post) =>
            post.id === updatedPost.id
              ? {
                  id: updatedPost.id,
                  title: updatedPost.title,
                  slug: updatedPost.slug,
                  summary: updatedPost.summary,
                  categoryId: updatedPost.categoryId,
                  seriesId: updatedPost.seriesId,
                  tags: updatedPost.tags,
                  metadata: updatedPost.metadata,
                  status: updatedPost.status,
                  updatedAt: updatedPost.updatedAt
                }
              : post
          )
        );
        setSaveStatus("Draft changes saved.");
        setPublishReviewStatus(null);
        setPublishReviewRequest(null);
        setPublishConfirmationStatus(null);
        setPublishActionStatus(null);
        setPublishActionError(null);
      }
    } catch {
      if (saveRequestIdRef.current === saveRequestId) {
        setSaveError("Draft changes could not be saved.");
      }
    } finally {
      if (saveRequestIdRef.current === saveRequestId) {
        setIsSavingDraft(false);
      }
    }
  }

  async function publishConfirmedDraft() {
    if (isPublishingDraft || !selectedPostDetail || publishConfirmationStatus === null) {
      return;
    }

    const publishRequestId = publishRequestIdRef.current + 1;
    const publishedPostId = selectedPostDetail.id;
    const publishedRevisionId = selectedPostDetail.revisionId;
    publishRequestIdRef.current = publishRequestId;
    setIsPublishingDraft(true);
    setPublishActionStatus(null);
    setPublishActionError(null);

    try {
      const publishedPost = await apiClient.publishPost(publishedPostId, {
        revisionId: publishedRevisionId,
        publishMode: "immediate",
        scheduledAt: null
      });
      if (publishedPost.id !== publishedPostId) {
        throw new Error("publish response id mismatch");
      }
      if (
        publishRequestIdRef.current === publishRequestId &&
        selectedPostDetail?.id === publishedPostId &&
        selectedPostDetail.revisionId === publishedRevisionId
      ) {
        const updatedSummary = {
          id: publishedPost.id,
          title: selectedPostDetail.title,
          slug: selectedPostDetail.slug,
          summary: selectedPostDetail.summary,
          categoryId: selectedPostDetail.categoryId,
          seriesId: selectedPostDetail.seriesId,
          tags: selectedPostDetail.tags,
          metadata: selectedPostDetail.metadata,
          status: publishedPost.status,
          updatedAt: publishedPost.publishedAt
        };
        setSelectedPost(updatedSummary);
        setSelectedPostDetail({
          ...selectedPostDetail,
          status: publishedPost.status,
          updatedAt: publishedPost.publishedAt
        });
        setPosts((currentPosts) => currentPosts.filter((post) => post.id !== publishedPost.id));
        setPublishedPosts((currentPublishedPosts) => [
          updatedSummary,
          ...currentPublishedPosts.filter((post) => post.id !== publishedPost.id)
        ]);
        setPublishActionStatus(`Draft published at ${publishedPost.publishedAt}.`);
        setPublishActionError(null);
        setPublishReviewStatus(null);
        setPublishConfirmationStatus(null);
      }
    } catch {
      if (publishRequestIdRef.current === publishRequestId) {
        setPublishActionError("Draft could not be published.");
      }
    } finally {
      if (publishRequestIdRef.current === publishRequestId) {
        setIsPublishingDraft(false);
      }
    }
  }

  async function requestDraftPublishReview() {
    if (!selectedPostDetail || isSavingDraft || isPublishingDraft) {
      return;
    }

    const publishRequestId = publishRequestIdRef.current + 1;
    const requestedPostId = selectedPostDetail.id;
    const requestedRevisionId = selectedPostDetail.revisionId;
    publishRequestIdRef.current = publishRequestId;
    setPublishReviewStatus(null);
    setPublishReviewRequest(null);
    setPublishConfirmationStatus(null);
    setPublishActionStatus(null);
    setPublishActionError(null);

    try {
      const publishRequest = await apiClient.requestPublishReview(requestedPostId, {
        revisionId: requestedRevisionId
      });
      if (publishRequest.postId !== requestedPostId || publishRequest.revisionId !== requestedRevisionId) {
        throw new Error("publish review response mismatch");
      }
      if (
        publishRequestIdRef.current === publishRequestId &&
        selectedPostDetail?.id === requestedPostId &&
        selectedPostDetail.revisionId === requestedRevisionId
      ) {
        setPublishReviewRequest(publishRequest);
        setPublishReviewStatus(
          `Publish review request ${publishRequest.requestId} is ${publishRequest.status} for revision ${publishRequest.revisionId}.`
        );
      }
    } catch {
      if (publishRequestIdRef.current === publishRequestId) {
        setPublishReviewRequest(null);
        setPublishReviewStatus("Publish review request could not be created.");
      }
    }
  }

  const previewPost = selectedPostDetail ?? selectedPost;
  const listContainsOnlyDrafts = posts.every((post) => post.status === "draft");
  const postListLabel = listContainsOnlyDrafts ? "Drafts" : "Content items";
  const detailLoadingCopy = selectedPost?.status === "draft" ? "Loading draft detail…" : "Loading item detail…";

  useEffect(() => {
    if (adminRoute.module !== "content" || !adminRoute.postId || posts.length === 0) {
      return;
    }

    const routedPost = posts.find((post) => post.id === adminRoute.postId);
    if (routedPost && selectedPost?.id !== routedPost.id) {
      void selectPost(routedPost, false);
    }
  }, [adminRoute, posts, selectedPost?.id]);

  return (
    <main className="admin-shell">
      <header className="admin-header">
        <p className="eyebrow">CMS Admin Console</p>
        <h1>Nairi Admin</h1>
        <p>API-backed human control plane foundation.</p>
      </header>

      <nav className="module-nav" aria-label="Admin modules">
        {adminModules.map((adminModule) => (
          <a
            key={adminModule.id}
            href={`#${adminModule.id}`}
            aria-current={activeModule === adminModule.id ? "page" : undefined}
            onClick={(event) => {
              event.preventDefault();
              setRoute({ module: adminModule.id, postId: null });
            }}
          >
            {adminModule.label}
          </a>
        ))}
      </nav>

      {activeModule === "content" ? (
        <section className="admin-layout" aria-label="Admin content workspace">
          <nav className="post-list" aria-label={postListLabel === "Drafts" ? "Draft posts" : "Content items"}>
            <h2>Content workspace</h2>
            <p className="section-label">{postListLabel}</p>
            {isLoading ? <p>Loading admin content…</p> : null}
            {loadError ? <p role="status">{loadError}</p> : null}
            {!isLoading && !loadError && posts.length === 0 ? <p>No draft posts are ready for review.</p> : null}
            {posts.map((post) => (
              <button
                key={post.id}
                type="button"
                aria-pressed={selectedPost?.id === post.id}
                className={selectedPost?.id === post.id ? "is-selected" : undefined}
                onClick={() => void selectPost(post)}
              >
                <span>{post.title}</span>
                <small>{post.status}</small>
              </button>
            ))}
          </nav>

          {!isLoading && !loadError ? (
            <section className="post-list" aria-label="Published history">
              <h2>Published history</h2>
              <p className="section-label">Published history</p>
              {publishedPosts.length === 0 ? <p>No published posts are in history yet.</p> : null}
              {publishedPosts.map((post) => (
                <button
                  key={post.id}
                  type="button"
                  aria-pressed={selectedPost?.id === post.id}
                  className={selectedPost?.id === post.id ? "is-selected" : undefined}
                  onClick={() => void selectPost(post)}
                >
                  <span>{post.title}</span>
                  <small>{post.status}</small>
                </button>
              ))}
            </section>
          ) : null}

          <article className="post-preview">
            {previewPost ? (
              <>
                <p className="eyebrow">
                  {selectedPostDetail
                    ? selectedPostDetail.status === "draft"
                      ? "API-backed draft detail"
                      : "API-backed published detail"
                    : "API-backed draft preview"}
                </p>
                <h2>{previewPost.title}</h2>
                {isDetailLoading ? <p>{detailLoadingCopy}</p> : null}
                {detailError ? <p role="status">{detailError}</p> : null}
                <dl>
                  <div>
                    <dt>Status</dt>
                    <dd>{previewPost.status}</dd>
                  </div>
                  <div>
                    <dt>Updated</dt>
                    <dd>{previewPost.updatedAt}</dd>
                  </div>
                  {selectedPostDetail ? (
                    <>
                      <div>
                        <dt>Content format</dt>
                        <dd>{selectedPostDetail.contentFormat}</dd>
                      </div>
                      <div>
                        <dt>Revision</dt>
                        <dd>{selectedPostDetail.revisionId}</dd>
                      </div>
                    </>
                  ) : null}
                </dl>
                {selectedPostDetail ? (
                  selectedPostDetail.status === "draft" ? (
                    <form className="draft-edit-form" onSubmit={(event) => void saveDraftEdits(event)}>
                      <p>Draft controls only affect the selected draft.</p>
                      <label>
                        Draft title
                        <input name="title" defaultValue={selectedPostDetail.title} />
                      </label>
                      <label>
                        Draft slug
                        <input name="slug" defaultValue={selectedPostDetail.slug} />
                      </label>
                      <label>
                        Draft summary
                        <textarea name="summary" defaultValue={selectedPostDetail.summary ?? ""} rows={3} />
                      </label>
                      <label>
                        Draft category ID
                        <input name="categoryId" defaultValue={selectedPostDetail.categoryId ?? ""} />
                      </label>
                      <label>
                        Draft series ID
                        <input name="seriesId" defaultValue={selectedPostDetail.seriesId ?? ""} />
                      </label>
                      <label>
                        Draft tags
                        <input name="tags" defaultValue={(selectedPostDetail.tags ?? []).join(", ")} />
                      </label>
                      <label>
                        Draft metadata JSON
                        <textarea
                          name="metadata"
                          defaultValue={stringifyDraftMetadata(selectedPostDetail.metadata)}
                          rows={6}
                        />
                      </label>
                      <label>
                        Draft content
                        <textarea name="content" defaultValue={selectedPostDetail.content} rows={8} />
                      </label>
                      <button type="submit" disabled={isSavingDraft || isPublishingDraft}>
                        {isSavingDraft ? "Saving draft changes…" : "Save draft changes"}
                      </button>
                      <button
                        type="button"
                        disabled={isSavingDraft || isPublishingDraft}
                        onClick={() => void requestDraftPublishReview()}
                      >
                        Request publish review
                      </button>
                      {saveStatus ? <p role="status">{saveStatus}</p> : null}
                      {saveError ? <p role="status">{saveError}</p> : null}
                      {publishReviewStatus ? (
                        <p role="status" aria-label="Publish review request status">
                          {publishReviewStatus}
                        </p>
                      ) : null}
                      {publishReviewRequest ? (
                        <section aria-label="Publish confirmation contract">
                          <h3>Publish confirmation contract</h3>
                          <p>Review revision {selectedPostDetail.revisionId} before any future publish action.</p>
                          <button
                            type="button"
                            disabled={publishConfirmationStatus !== null || isPublishingDraft}
                            onClick={() => {
                              setPublishConfirmationStatus(
                                `Publication intent confirmed locally for revision ${selectedPostDetail.revisionId}.`
                              );
                              setPublishActionStatus(null);
                              setPublishActionError(null);
                            }}
                          >
                            Confirm publication intent
                          </button>
                        </section>
                      ) : null}
                      {publishConfirmationStatus ? (
                        <p role="status" aria-label="Publish confirmation intent status">
                          {publishConfirmationStatus}
                        </p>
                      ) : null}
                      {publishConfirmationStatus ? (
                        <button type="button" disabled={isPublishingDraft} onClick={() => void publishConfirmedDraft()}>
                          {isPublishingDraft ? "Publishing confirmed draft…" : "Publish confirmed draft"}
                        </button>
                      ) : null}
                    </form>
                  ) : (
                    <>
                      <p>Published detail is read-only in the draft review workflow.</p>
                      <p>Draft editing and publishing controls are hidden for this content item.</p>
                    </>
                  )
                ) : null}
                {publishActionStatus ? (
                  <p role="status" aria-label="Publish action status">
                    {publishActionStatus}
                  </p>
                ) : null}
                {publishActionError ? (
                  <p role="status" aria-label="Publish action error">
                    {publishActionError}
                  </p>
                ) : null}
              </>
            ) : (
              <p>Select a draft from the list to load its API-backed detail.</p>
            )}
          </article>
        </section>
      ) : null}

      {activeModule === "media" ? (
        <section className="module-panel" aria-label="Media module">
          <h2>Media library</h2>
          <p>Media workflows remain reserved for a later boundary.</p>
        </section>
      ) : null}

      {activeModule === "settings" ? (
        <section className="module-panel" aria-label="Settings module">
          <h2>System settings</h2>
          <p>Settings workflows remain reserved for a later boundary.</p>
        </section>
      ) : null}
    </main>
  );
}
