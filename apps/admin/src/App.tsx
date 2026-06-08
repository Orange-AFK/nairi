import { useEffect, useState } from "react";

import "./styles.css";

export type AdminPostSummary = {
  id: string;
  title: string;
  status: string;
  updatedAt: string;
};

export type AdminApiClient = {
  listPosts: () => Promise<AdminPostSummary[]>;
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

export function App({ apiClient }: AppProps) {
  const [activeModule, setActiveModule] = useState<AdminModule>("content");
  const [posts, setPosts] = useState<AdminPostSummary[]>([]);
  const [selectedPost, setSelectedPost] = useState<AdminPostSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

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
            {posts.map((post) => (
              <button key={post.id} type="button" onClick={() => setSelectedPost(post)}>
                <span>{post.title}</span>
                <small>{post.status}</small>
              </button>
            ))}
          </nav>

          <article className="post-preview">
            {selectedPost ? (
              <>
                <p className="eyebrow">API-backed draft preview</p>
                <h2>{selectedPost.title}</h2>
                <dl>
                  <div>
                    <dt>Status</dt>
                    <dd>{selectedPost.status}</dd>
                  </div>
                  <div>
                    <dt>Updated</dt>
                    <dd>{selectedPost.updatedAt}</dd>
                  </div>
                </dl>
              </>
            ) : (
              <p>Select a draft to review.</p>
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
