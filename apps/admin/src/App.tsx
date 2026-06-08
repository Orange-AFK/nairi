import { type FormEvent, useEffect, useRef, useState } from "react";

import "./styles.css";

export type AdminPostSummary = {
  id: string;
  title: string;
  slug: string;
  summary?: string | null;
  categoryId?: string | null;
  seriesId?: string | null;
  tags?: string[];
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
  contentFormat: "markdown" | "mdx";
  content: string;
  expectedRevisionId: string;
};

export type AdminApiClient = {
  listPosts: () => Promise<AdminPostSummary[]>;
  getPost: (postId: string) => Promise<AdminPostDetail>;
  updatePost: (postId: string, input: AdminPostUpdateInput) => Promise<AdminPostDetail>;
};

type AdminModule = "content" | "media" | "settings";

type AppProps = {
  apiClient: AdminApiClient;
};

const adminModules: Array<{ id: AdminModule; label: string }> = [
  { id: "content", label: "Content" },
  { id: "media", label: "Media" },
  { id: "settings", label: "Settings" }
];

function parseDraftTags(value: string): string[] {
  return [...new Set(value.split(",").map((tag) => tag.trim()).filter(Boolean))];
}

export function App({ apiClient }: AppProps) {
  const [activeModule, setActiveModule] = useState<AdminModule>("content");
  const [posts, setPosts] = useState<AdminPostSummary[]>([]);
  const [selectedPost, setSelectedPost] = useState<AdminPostSummary | null>(null);
  const [selectedPostDetail, setSelectedPostDetail] = useState<AdminPostDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [isSavingDraft, setIsSavingDraft] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [publishReviewStatus, setPublishReviewStatus] = useState<string | null>(null);
  const [publishConfirmationStatus, setPublishConfirmationStatus] = useState<string | null>(null);
  const detailRequestIdRef = useRef(0);
  const saveRequestIdRef = useRef(0);

  useEffect(() => {
    let cancelled = false;

    async function loadPosts() {
      try {
        const loadedPosts = await apiClient.listPosts();
        if (!cancelled) {
          setPosts(loadedPosts);
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

  async function selectPost(post: AdminPostSummary) {
    const detailRequestId = detailRequestIdRef.current + 1;
    detailRequestIdRef.current = detailRequestId;
    saveRequestIdRef.current += 1;
    setSelectedPost(post);
    setSelectedPostDetail(null);
    setDetailError(null);
    setSaveStatus(null);
    setSaveError(null);
    setPublishReviewStatus(null);
    setPublishConfirmationStatus(null);
    setIsDetailLoading(true);

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
                  status: updatedPost.status,
                  updatedAt: updatedPost.updatedAt
                }
              : post
          )
        );
        setSaveStatus("Draft changes saved.");
        setPublishReviewStatus(null);
        setPublishConfirmationStatus(null);
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

  const previewPost = selectedPostDetail ?? selectedPost;

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
              setActiveModule(adminModule.id);
            }}
          >
            {adminModule.label}
          </a>
        ))}
      </nav>

      {activeModule === "content" ? (
        <section className="admin-layout" aria-label="Admin content workspace">
          <nav className="post-list" aria-label="Draft posts">
            <h2>Content workspace</h2>
            <p className="section-label">Drafts</p>
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

          <article className="post-preview">
            {previewPost ? (
              <>
                <p className="eyebrow">{selectedPostDetail ? "API-backed draft detail" : "API-backed draft preview"}</p>
                <h2>{previewPost.title}</h2>
                {isDetailLoading ? <p>Loading draft detail…</p> : null}
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
                  <form className="draft-edit-form" onSubmit={(event) => void saveDraftEdits(event)}>
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
                      Draft content
                      <textarea name="content" defaultValue={selectedPostDetail.content} rows={8} />
                    </label>
                    <button type="submit" disabled={isSavingDraft}>
                      {isSavingDraft ? "Saving draft changes…" : "Save draft changes"}
                    </button>
                    <button
                      type="button"
                      disabled={isSavingDraft}
                      onClick={() => {
                        setPublishReviewStatus(
                          `Publish review request staged for revision ${selectedPostDetail.revisionId}.`
                        );
                        setPublishConfirmationStatus(null);
                      }}
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
                    {publishReviewStatus ? (
                      <section aria-label="Publish confirmation contract">
                        <h3>Publish confirmation contract</h3>
                        <p>Review revision {selectedPostDetail.revisionId} before any future publish action.</p>
                        <button
                          type="button"
                          disabled={publishConfirmationStatus !== null}
                          onClick={() => {
                            setPublishConfirmationStatus(
                              `Publication intent confirmed locally for revision ${selectedPostDetail.revisionId}.`
                            );
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
                  </form>
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
