import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { App, type AdminApiClient, type AdminPostDetail, type AdminPostUpdateInput } from "./App";

function adminApiClient(overrides: Partial<AdminApiClient> = {}): AdminApiClient {
  return {
    async listPosts() {
      return [
        {
          id: "post-1",
          title: "First draft",
          slug: "first-draft",
          status: "draft",
          updatedAt: "2026-06-08T00:00:00Z"
        }
      ];
    },
    async getPost(postId: string) {
      return {
        id: postId,
        title: "First draft",
        slug: "first-draft",
        status: "draft",
        contentFormat: "markdown",
        content: "# First draft\n\nDraft body from the management API.",
        revisionId: "revision-post-1-1",
        updatedAt: "2026-06-08T00:00:00Z"
      };
    },
    async updatePost(_postId: string, input: AdminPostUpdateInput) {
      return {
        id: "post-1",
        title: input.title,
        slug: input.slug,
        status: "draft",
        contentFormat: input.contentFormat,
        content: input.content,
        revisionId: "revision-post-1-2",
        updatedAt: "2026-06-08T00:02:00Z"
      };
    },
    ...overrides
  };
}

describe("Nairi admin console shell", () => {
  it("switches between reserved admin modules without leaving the injected API boundary", async () => {
    const user = userEvent.setup();
    render(<App apiClient={adminApiClient()} />);

    const navigation = screen.getByRole("navigation", { name: "Admin modules" });
    const contentModule = screen.getByRole("link", { name: "Content" });

    expect(navigation).toBeInTheDocument();
    expect(contentModule).toHaveAttribute("aria-current", "page");
    expect(await screen.findByRole("heading", { name: "Content workspace" })).toBeInTheDocument();

    await user.click(screen.getByRole("link", { name: "Media" }));
    expect(screen.getByRole("link", { name: "Media" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("heading", { name: "Media library" })).toBeInTheDocument();
    expect(screen.getByText("Media workflows remain reserved for a later boundary.")).toBeInTheDocument();

    await user.click(screen.getByRole("link", { name: "Settings" }));
    expect(screen.getByRole("link", { name: "Settings" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("heading", { name: "System settings" })).toBeInTheDocument();
    expect(screen.getByText("Settings workflows remain reserved for a later boundary.")).toBeInTheDocument();
  });

  it("loads draft content through an injected API client", async () => {
    render(<App apiClient={adminApiClient()} />);

    expect(screen.getByRole("heading", { name: "Nairi Admin" })).toBeInTheDocument();
    expect(screen.getByText("Loading admin content…")).toBeInTheDocument();

    const firstDraft = await screen.findByRole("button", { name: /First draft/ });
    expect(firstDraft).toBeInTheDocument();
    expect(firstDraft).toHaveAttribute("aria-pressed", "true");
    expect(firstDraft).toHaveClass("is-selected");
    expect(screen.getAllByText("draft").length).toBeGreaterThan(0);
  });

  it("renders a stable empty state when no draft summaries are available", async () => {
    render(
      <App
        apiClient={adminApiClient({
          async listPosts() {
            return [];
          }
        })}
      />
    );

    expect(await screen.findByText("No draft posts are ready for review.")).toBeInTheDocument();
    expect(screen.getByText("Select a draft from the list to load its API-backed detail.")).toBeInTheDocument();
  });

  it("selects a post and reads draft detail through the injected API boundary", async () => {
    const user = userEvent.setup();
    const getPost = vi.fn(async (postId: string): Promise<AdminPostDetail> => ({
      id: postId,
      title: "First draft",
      slug: "first-draft",
      status: "draft",
      contentFormat: "markdown",
      content: "# First draft\n\nDraft body from the management API.",
      revisionId: "revision-post-1-1",
      updatedAt: "2026-06-08T00:00:00Z"
    }));
    render(<App apiClient={adminApiClient({ getPost })} />);

    const firstDraft = await screen.findByRole("button", { name: /First draft/ });
    await user.click(firstDraft);

    expect(firstDraft).toHaveAttribute("aria-pressed", "true");
    expect(firstDraft).toHaveClass("is-selected");
    expect(getPost).toHaveBeenCalledWith("post-1");
    expect(await screen.findByRole("heading", { name: "First draft" })).toBeInTheDocument();
    expect(screen.getByText("API-backed draft detail"));
    expect(screen.getByText(/Draft body from the management API\./)).toBeInTheDocument();
    expect(screen.getByText("revision-post-1-1")).toBeInTheDocument();
  });

  it("submits draft edits through the injected update contract without publishing", async () => {
    const user = userEvent.setup();
    const updatePost = vi.fn(async (_postId: string, input: AdminPostUpdateInput): Promise<AdminPostDetail> => ({
      id: "post-1",
      title: input.title,
      slug: input.slug,
      status: "draft",
      contentFormat: input.contentFormat,
      content: input.content,
      revisionId: "revision-post-1-2",
      updatedAt: "2026-06-08T00:02:00Z"
    }));
    render(<App apiClient={adminApiClient({ updatePost })} />);

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");

    const titleField = screen.getByLabelText("Draft title");
    const contentField = screen.getByLabelText("Draft content");
    await user.clear(titleField);
    await user.type(titleField, "Updated draft title");
    await user.clear(contentField);
    await user.type(contentField, "Updated draft body from the admin form.");
    await user.click(screen.getByRole("button", { name: "Save draft changes" }));

    expect(updatePost).toHaveBeenCalledWith("post-1", {
      title: "Updated draft title",
      slug: "first-draft",
      contentFormat: "markdown",
      content: "Updated draft body from the admin form.",
      expectedRevisionId: "revision-post-1-1"
    });
    expect(await screen.findByText("Draft changes saved.")).toBeInTheDocument();
    expect(screen.getByText("revision-post-1-2")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /publish/i })).not.toBeInTheDocument();
  });

  it("ignores stale draft edit responses after a newer selection", async () => {
    const user = userEvent.setup();
    const updateResolvers = new Map<string, (detail: AdminPostDetail) => void>();
    const updatePost = vi.fn(
      (postId: string, input: AdminPostUpdateInput) =>
        new Promise<AdminPostDetail>((resolve) => {
          updateResolvers.set(postId, () =>
            resolve({
              id: postId,
              title: input.title,
              slug: input.slug,
              status: "draft",
              contentFormat: input.contentFormat,
              content: input.content,
              revisionId: `revision-${postId}-saved`,
              updatedAt: "2026-06-08T00:03:00Z"
            })
          );
        })
    );

    render(
      <App
        apiClient={adminApiClient({
          async listPosts() {
            return [
              {
                id: "post-1",
                title: "First draft",
                slug: "first-draft",
                status: "draft",
                updatedAt: "2026-06-08T00:00:00Z"
              },
              {
                id: "post-2",
                title: "Second draft",
                slug: "second-draft",
                status: "draft",
                updatedAt: "2026-06-08T00:01:00Z"
              }
            ];
          },
          async getPost(postId: string) {
            return {
              id: postId,
              title: postId === "post-1" ? "First draft" : "Second draft",
              slug: postId === "post-1" ? "first-draft" : "second-draft",
              status: "draft",
              contentFormat: "markdown",
              content: postId === "post-1" ? "First draft body." : "Second draft body.",
              revisionId: `revision-${postId}-1`,
              updatedAt: "2026-06-08T00:00:00Z"
            };
          },
          updatePost
        })}
      />
    );

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");
    await user.clear(screen.getByLabelText("Draft title"));
    await user.type(screen.getByLabelText("Draft title"), "Saved stale first draft");
    await user.click(screen.getByRole("button", { name: "Save draft changes" }));

    await user.click(await screen.findByRole("button", { name: /Second draft/ }));
    expect(await screen.findByRole("heading", { name: "Second draft" })).toBeInTheDocument();

    await act(async () => {
      updateResolvers.get("post-1")?.({
        id: "post-1",
        title: "Saved stale first draft",
        slug: "first-draft",
        status: "draft",
        contentFormat: "markdown",
        content: "Stale first draft body.",
        revisionId: "revision-post-1-saved",
        updatedAt: "2026-06-08T00:03:00Z"
      });
    });

    expect(screen.getByRole("heading", { name: "Second draft" })).toBeInTheDocument();
    expect(screen.queryByText("Saved stale first draft")).not.toBeInTheDocument();
    expect(screen.queryByText("revision-post-1-saved")).not.toBeInTheDocument();
  });

  it("renders a safe edit error state when injected update fails", async () => {
    const user = userEvent.setup();
    render(
      <App
        apiClient={adminApiClient({
          async updatePost() {
            throw new Error("stale revision");
          }
        })}
      />
    );

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");
    await user.click(screen.getByRole("button", { name: "Save draft changes" }));

    expect(await screen.findByText("Draft changes could not be saved.")).toBeInTheDocument();
  });

  it("renders a safe detail error state when injected detail loading fails", async () => {
    const user = userEvent.setup();
    render(
      <App
        apiClient={adminApiClient({
          async getPost() {
            throw new Error("detail unavailable");
          }
        })}
      />
    );

    await user.click(await screen.findByRole("button", { name: /First draft/ }));

    expect(await screen.findByText("Draft detail could not be loaded.")).toBeInTheDocument();
  });

  it("ignores stale draft detail responses after a newer selection", async () => {
    const user = userEvent.setup();
    const detailResolvers = new Map<string, (detail: AdminPostDetail) => void>();
    const getPost = vi.fn(
      (postId: string) =>
        new Promise<AdminPostDetail>((resolve) => {
          detailResolvers.set(postId, resolve);
        })
    );

    render(
      <App
        apiClient={adminApiClient({
          async listPosts() {
            return [
              {
                id: "post-1",
                title: "First draft",
                slug: "first-draft",
                status: "draft",
                updatedAt: "2026-06-08T00:00:00Z"
              },
              {
                id: "post-2",
                title: "Second draft",
                slug: "second-draft",
                status: "draft",
                updatedAt: "2026-06-08T00:01:00Z"
              }
            ];
          },
          getPost
        })}
      />
    );

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await user.click(await screen.findByRole("button", { name: /Second draft/ }));

    await act(async () => {
      detailResolvers.get("post-2")?.({
        id: "post-2",
        title: "Second draft",
        slug: "second-draft",
        status: "draft",
        contentFormat: "markdown",
        content: "Second body from the management API.",
        revisionId: "revision-post-2-1",
        updatedAt: "2026-06-08T00:01:00Z"
      });
    });
    expect(await screen.findByText("revision-post-2-1")).toBeInTheDocument();

    await act(async () => {
      detailResolvers.get("post-1")?.({
        id: "post-1",
        title: "First draft",
        slug: "first-draft",
        status: "draft",
        contentFormat: "markdown",
        content: "Stale first body from the management API.",
        revisionId: "revision-post-1-stale",
        updatedAt: "2026-06-08T00:00:00Z"
      });
    });

    expect(screen.getByRole("heading", { name: "Second draft" })).toBeInTheDocument();
    expect(screen.getByText("revision-post-2-1")).toBeInTheDocument();
    expect(screen.queryByText("revision-post-1-stale")).not.toBeInTheDocument();
  });

  it("renders a safe error state when injected post loading fails", async () => {
    render(
      <App
        apiClient={adminApiClient({
          listPosts: async () => {
            throw new Error("network unavailable");
          }
        })}
      />
    );

    expect(await screen.findByText("Admin content could not be loaded."));
    expect(screen.queryByText("Loading admin content…")).not.toBeInTheDocument();
  });
});
