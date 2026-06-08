import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import {
  App,
  type AdminApiClient,
  type AdminPostDetail,
  type AdminPostPublishInput,
  type AdminPostPublishResult,
  type AdminPostUpdateInput
} from "./App";

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
        summary: "First draft summary.",
        categoryId: "dispatches",
        seriesId: "field-journal",
        tags: ["draft", "release-notes"],
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
        summary: input.summary,
        categoryId: input.categoryId,
        seriesId: input.seriesId,
        tags: input.tags,
        status: "draft",
        contentFormat: input.contentFormat,
        content: input.content,
        revisionId: "revision-post-1-2",
        updatedAt: "2026-06-08T00:02:00Z"
      };
    },
    async publishPost(postId: string) {
      return {
        id: postId,
        status: "published",
        publishedAt: "2026-06-08T00:10:00Z",
        jobId: "publish-job-post-1",
        publicInvalidation: {
          mode: "recorded",
          surfaces: ["/posts", "/posts/first-draft", "/rss.xml", "/sitemap.xml"],
          execution: {
            status: "recorded",
            executor: "none",
            executedAt: "2026-06-08T00:10:00Z",
            errorCode: null,
            errorMessage: null
          },
          dispatch: {
            status: "dispatch_skipped",
            reason: "no_dispatcher_configured",
            attempted: false,
            attemptedAt: null
          }
        }
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

    expect(screen.getByText("Drafts")).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Draft posts" })).toBeInTheDocument();

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

  it("labels a mixed-status admin list as content items without adding published navigation", async () => {
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
                title: "Published field note",
                slug: "published-field-note",
                status: "published",
                updatedAt: "2026-06-08T00:10:00Z"
              }
            ];
          }
        })}
      />
    );

    expect(await screen.findByText("Content items")).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Content items" })).toBeInTheDocument();
    expect(screen.queryByRole("navigation", { name: "Draft posts" })).not.toBeInTheDocument();
    expect(screen.queryByText("Drafts")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /First draft/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Published field note/ })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /Published/i })).not.toBeInTheDocument();
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

  it("renders non-draft detail as read-only without draft workflow controls", async () => {
    const user = userEvent.setup();
    render(
      <App
        apiClient={adminApiClient({
          async getPost(postId: string) {
            return {
              id: postId,
              title: "Published field note",
              slug: "published-field-note",
              status: "published",
              contentFormat: "markdown",
              content: "# Published field note\n\nPublished body from the management API.",
              revisionId: "revision-post-1-published",
              updatedAt: "2026-06-08T00:10:00Z"
            };
          }
        })}
      />
    );

    await user.click(await screen.findByRole("button", { name: /First draft/ }));

    expect(await screen.findByRole("heading", { name: "Published field note" })).toBeInTheDocument();
    expect(screen.getByText("published")).toBeInTheDocument();
    expect(screen.getByText("API-backed published detail")).toBeInTheDocument();
    expect(screen.queryByText("API-backed draft detail")).not.toBeInTheDocument();
    expect(screen.getByText("revision-post-1-published")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Save draft changes" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Request publish review" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirm publication intent" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Publish confirmed draft" })).not.toBeInTheDocument();
    expect(screen.getByText("Published detail is read-only in the draft review workflow.")).toBeInTheDocument();
  });

  it("submits draft edits through the injected update contract without publishing", async () => {
    const user = userEvent.setup();
    const updatePost = vi.fn(async (_postId: string, input: AdminPostUpdateInput): Promise<AdminPostDetail> => ({
      id: "post-1",
      title: input.title,
      slug: input.slug,
      summary: input.summary,
      categoryId: input.categoryId,
      seriesId: input.seriesId,
      tags: input.tags,
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
    const slugField = screen.getByLabelText("Draft slug");
    const summaryField = screen.getByLabelText("Draft summary");
    const categoryField = screen.getByLabelText("Draft category ID");
    const seriesField = screen.getByLabelText("Draft series ID");
    const tagsField = screen.getByLabelText("Draft tags");
    const contentField = screen.getByLabelText("Draft content");
    expect(slugField).toHaveValue("first-draft");
    expect(summaryField).toHaveValue("First draft summary.");
    expect(categoryField).toHaveValue("dispatches");
    expect(seriesField).toHaveValue("field-journal");
    expect(tagsField).toHaveValue("draft, release-notes");
    await user.clear(titleField);
    await user.type(titleField, "Updated draft title");
    await user.clear(slugField);
    await user.type(slugField, "updated-draft-slug");
    await user.clear(summaryField);
    await user.type(summaryField, "Updated draft summary from the admin form.");
    await user.clear(categoryField);
    await user.type(categoryField, "field-notes");
    await user.clear(seriesField);
    await user.type(seriesField, "monthly-field-journal");
    await user.clear(tagsField);
    await user.type(tagsField, "updated, release-notes, updated");
    await user.clear(contentField);
    await user.type(contentField, "Updated draft body from the admin form.");
    await user.click(screen.getByRole("button", { name: "Save draft changes" }));

    expect(updatePost).toHaveBeenCalledWith("post-1", {
      title: "Updated draft title",
      slug: "updated-draft-slug",
      summary: "Updated draft summary from the admin form.",
      categoryId: "field-notes",
      seriesId: "monthly-field-journal",
      tags: ["updated", "release-notes"],
      contentFormat: "markdown",
      content: "Updated draft body from the admin form.",
      expectedRevisionId: "revision-post-1-1"
    });
    expect(await screen.findByText("Draft changes saved.")).toBeInTheDocument();
    expect(screen.getByText("revision-post-1-2")).toBeInTheDocument();
  });

  it("stages a publish review request without calling a publish mutation", async () => {
    const user = userEvent.setup();
    const updatePost = vi.fn(async (_postId: string, input: AdminPostUpdateInput): Promise<AdminPostDetail> => ({
      id: "post-1",
      title: input.title,
      slug: input.slug,
      summary: input.summary,
      categoryId: input.categoryId,
      seriesId: input.seriesId,
      tags: input.tags,
      status: "draft",
      contentFormat: input.contentFormat,
      content: input.content,
      revisionId: "revision-post-1-2",
      updatedAt: "2026-06-08T00:02:00Z"
    }));
    render(<App apiClient={adminApiClient({ updatePost })} />);

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");

    await user.click(screen.getByRole("button", { name: "Request publish review" }));

    expect(updatePost).not.toHaveBeenCalled();
    expect(screen.getByRole("status", { name: "Publish review request status" })).toHaveTextContent(
      "Publish review request staged for revision revision-post-1-1."
    );
    expect(screen.queryByRole("button", { name: /^publish$/i })).not.toBeInTheDocument();
  });

  it("publishes a confirmed draft through the injected publish contract", async () => {
    const user = userEvent.setup();
    const updatePost = vi.fn(async (_postId: string, input: AdminPostUpdateInput): Promise<AdminPostDetail> => ({
      id: "post-1",
      title: input.title,
      slug: input.slug,
      summary: input.summary,
      categoryId: input.categoryId,
      seriesId: input.seriesId,
      tags: input.tags,
      status: "draft",
      contentFormat: input.contentFormat,
      content: input.content,
      revisionId: "revision-post-1-2",
      updatedAt: "2026-06-08T00:02:00Z"
    }));
    const publishPost = vi.fn(
      async (postId: string, _input: AdminPostPublishInput): Promise<AdminPostPublishResult> => ({
        id: postId,
        status: "published",
        publishedAt: "2026-06-08T00:10:00Z",
        jobId: "publish-job-post-1",
        publicInvalidation: {
          mode: "recorded",
          surfaces: ["/posts", "/posts/first-draft", "/rss.xml", "/sitemap.xml"],
          execution: {
            status: "recorded",
            executor: "none",
            executedAt: "2026-06-08T00:10:00Z",
            errorCode: null,
            errorMessage: null
          },
          dispatch: {
            status: "dispatch_skipped",
            reason: "no_dispatcher_configured",
            attempted: false,
            attemptedAt: null
          }
        }
      })
    );
    render(<App apiClient={adminApiClient({ updatePost, publishPost })} />);

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");
    await user.click(screen.getByRole("button", { name: "Request publish review" }));

    expect(screen.getByText("Publish confirmation contract")).toBeInTheDocument();
    expect(screen.getByText("Review revision revision-post-1-1 before any future publish action.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Publish confirmed draft" })).not.toBeInTheDocument();
    const confirmationButton = screen.getByRole("button", { name: "Confirm publication intent" });
    await user.click(confirmationButton);

    expect(updatePost).not.toHaveBeenCalled();
    expect(confirmationButton).toBeDisabled();
    expect(screen.getByRole("status", { name: "Publish confirmation intent status" })).toHaveTextContent(
      "Publication intent confirmed locally for revision revision-post-1-1."
    );
    await user.click(screen.getByRole("button", { name: "Publish confirmed draft" }));

    expect(publishPost).toHaveBeenCalledWith("post-1", {
      revisionId: "revision-post-1-1",
      publishMode: "immediate",
      scheduledAt: null
    });
    expect(await screen.findByRole("status", { name: "Publish action status" })).toHaveTextContent(
      "Draft published at 2026-06-08T00:10:00Z."
    );
    expect(screen.queryByRole("button", { name: /First draft/ })).not.toBeInTheDocument();
    expect(screen.getByText("No draft posts are ready for review.")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "First draft" })).toBeInTheDocument();
    expect(screen.getByText("published")).toBeInTheDocument();
    expect(screen.getByText("API-backed published detail")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Publish confirmed draft" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Save draft changes" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Request publish review" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirm publication intent" })).not.toBeInTheDocument();
    expect(screen.getByText("Published detail is read-only in the draft review workflow.")).toBeInTheDocument();
  });

  it("removes only the published draft from a multi-draft review list", async () => {
    const user = userEvent.setup();
    const publishPost = vi.fn(
      async (postId: string, _input: AdminPostPublishInput): Promise<AdminPostPublishResult> => ({
        id: postId,
        status: "published",
        publishedAt: "2026-06-08T00:10:00Z",
        jobId: "publish-job-post-1",
        publicInvalidation: {
          mode: "recorded",
          surfaces: ["/posts", "/posts/first-draft", "/rss.xml", "/sitemap.xml"],
          execution: {
            status: "recorded",
            executor: "none",
            executedAt: "2026-06-08T00:10:00Z",
            errorCode: null,
            errorMessage: null
          },
          dispatch: {
            status: "dispatch_skipped",
            reason: "no_dispatcher_configured",
            attempted: false,
            attemptedAt: null
          }
        }
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
          publishPost
        })}
      />
    );

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");
    await user.click(screen.getByRole("button", { name: "Request publish review" }));
    await user.click(screen.getByRole("button", { name: "Confirm publication intent" }));
    await user.click(screen.getByRole("button", { name: "Publish confirmed draft" }));

    expect(await screen.findByRole("status", { name: "Publish action status" })).toHaveTextContent(
      "Draft published at 2026-06-08T00:10:00Z."
    );
    expect(screen.queryByRole("button", { name: /First draft/ })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Second draft/ })).toBeInTheDocument();
    expect(screen.queryByText("No draft posts are ready for review.")).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "First draft" })).toBeInTheDocument();
  });

  it("renders a safe publish action error when injected publish fails", async () => {
    const user = userEvent.setup();
    const publishPost = vi.fn(async () => {
      throw new Error("stale revision");
    });
    render(<App apiClient={adminApiClient({ publishPost })} />);

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");
    await user.click(screen.getByRole("button", { name: "Request publish review" }));
    await user.click(screen.getByRole("button", { name: "Confirm publication intent" }));
    await user.click(screen.getByRole("button", { name: "Publish confirmed draft" }));

    expect(publishPost).toHaveBeenCalledWith("post-1", {
      revisionId: "revision-post-1-1",
      publishMode: "immediate",
      scheduledAt: null
    });
    expect(await screen.findByRole("status", { name: "Publish action error" })).toHaveTextContent(
      "Draft could not be published."
    );
  });

  it("ignores stale publish responses after selecting another draft", async () => {
    const user = userEvent.setup();
    const publishResolvers = new Map<string, (result: AdminPostPublishResult) => void>();
    const publishPost = vi.fn(
      (postId: string) =>
        new Promise<AdminPostPublishResult>((resolve) => {
          publishResolvers.set(postId, resolve);
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
          publishPost
        })}
      />
    );

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");
    await user.click(screen.getByRole("button", { name: "Request publish review" }));
    await user.click(screen.getByRole("button", { name: "Confirm publication intent" }));
    await user.click(screen.getByRole("button", { name: "Publish confirmed draft" }));

    await user.click(await screen.findByRole("button", { name: /Second draft/ }));
    expect(await screen.findByRole("heading", { name: "Second draft" })).toBeInTheDocument();

    await act(async () => {
      publishResolvers.get("post-1")?.({
        id: "post-1",
        status: "published",
        publishedAt: "2026-06-08T00:10:00Z",
        jobId: "publish-job-post-1",
        publicInvalidation: {
          mode: "recorded",
          surfaces: ["/posts", "/posts/first-draft", "/rss.xml", "/sitemap.xml"],
          execution: {
            status: "recorded",
            executor: "none",
            executedAt: "2026-06-08T00:10:00Z",
            errorCode: null,
            errorMessage: null
          },
          dispatch: {
            status: "dispatch_skipped",
            reason: "no_dispatcher_configured",
            attempted: false,
            attemptedAt: null
          }
        }
      });
    });

    expect(screen.getByRole("heading", { name: "Second draft" })).toBeInTheDocument();
    expect(screen.queryByRole("status", { name: "Publish action status" })).not.toBeInTheDocument();
    expect(screen.queryByText("Draft published at 2026-06-08T00:10:00Z.")).not.toBeInTheDocument();
  });

  it("renders a safe publish error when the publish response id does not match the selected draft", async () => {
    const user = userEvent.setup();
    const publishPost = vi.fn(async (): Promise<AdminPostPublishResult> => ({
      id: "post-2",
      status: "published",
      publishedAt: "2026-06-08T00:10:00Z",
      jobId: "publish-job-post-1",
      publicInvalidation: {
        mode: "recorded",
        surfaces: ["/posts", "/posts/second-draft", "/rss.xml", "/sitemap.xml"],
        execution: {
          status: "recorded",
          executor: "none",
          executedAt: "2026-06-08T00:10:00Z",
          errorCode: null,
          errorMessage: null
        },
        dispatch: {
          status: "dispatch_skipped",
          reason: "no_dispatcher_configured",
          attempted: false,
          attemptedAt: null
        }
      }
    }));
    render(<App apiClient={adminApiClient({ publishPost })} />);

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");
    await user.click(screen.getByRole("button", { name: "Request publish review" }));
    await user.click(screen.getByRole("button", { name: "Confirm publication intent" }));
    await user.click(screen.getByRole("button", { name: "Publish confirmed draft" }));

    expect(await screen.findByRole("status", { name: "Publish action error" })).toHaveTextContent(
      "Draft could not be published."
    );
    expect(screen.queryByRole("status", { name: "Publish action status" })).not.toBeInTheDocument();
  });

  it("normalizes a cleared draft summary to null before update", async () => {
    const user = userEvent.setup();
    const updatePost = vi.fn(async (_postId: string, input: AdminPostUpdateInput): Promise<AdminPostDetail> => ({
      id: "post-1",
      title: input.title,
      slug: input.slug,
      summary: input.summary,
      categoryId: input.categoryId,
      seriesId: input.seriesId,
      tags: input.tags,
      status: "draft",
      contentFormat: input.contentFormat,
      content: input.content,
      revisionId: "revision-post-1-2",
      updatedAt: "2026-06-08T00:02:00Z"
    }));
    render(<App apiClient={adminApiClient({ updatePost })} />);

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");

    const summaryField = screen.getByLabelText("Draft summary");
    await user.clear(summaryField);
    await user.click(screen.getByRole("button", { name: "Save draft changes" }));

    expect(updatePost).toHaveBeenCalledWith(
      "post-1",
      expect.objectContaining({ summary: null })
    );
  });

  it("normalizes a cleared draft category ID to null before update", async () => {
    const user = userEvent.setup();
    const updatePost = vi.fn(async (_postId: string, input: AdminPostUpdateInput): Promise<AdminPostDetail> => ({
      id: "post-1",
      title: input.title,
      slug: input.slug,
      summary: input.summary,
      categoryId: input.categoryId,
      seriesId: input.seriesId,
      tags: input.tags,
      status: "draft",
      contentFormat: input.contentFormat,
      content: input.content,
      revisionId: "revision-post-1-2",
      updatedAt: "2026-06-08T00:02:00Z"
    }));
    render(<App apiClient={adminApiClient({ updatePost })} />);

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");

    const categoryField = screen.getByLabelText("Draft category ID");
    await user.clear(categoryField);
    await user.type(categoryField, "   ");
    await user.click(screen.getByRole("button", { name: "Save draft changes" }));

    expect(updatePost).toHaveBeenCalledWith(
      "post-1",
      expect.objectContaining({ categoryId: null })
    );
  });

  it("normalizes a cleared draft series ID to null before update", async () => {
    const user = userEvent.setup();
    const updatePost = vi.fn(async (_postId: string, input: AdminPostUpdateInput): Promise<AdminPostDetail> => ({
      id: "post-1",
      title: input.title,
      slug: input.slug,
      summary: input.summary,
      categoryId: input.categoryId,
      seriesId: input.seriesId,
      tags: input.tags,
      status: "draft",
      contentFormat: input.contentFormat,
      content: input.content,
      revisionId: "revision-post-1-2",
      updatedAt: "2026-06-08T00:02:00Z"
    }));
    render(<App apiClient={adminApiClient({ updatePost })} />);

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");

    const seriesField = screen.getByLabelText("Draft series ID");
    await user.clear(seriesField);
    await user.type(seriesField, "   ");
    await user.click(screen.getByRole("button", { name: "Save draft changes" }));

    expect(updatePost).toHaveBeenCalledWith(
      "post-1",
      expect.objectContaining({ seriesId: null })
    );
  });

  it("normalizes cleared draft tags to an empty array before update", async () => {
    const user = userEvent.setup();
    const updatePost = vi.fn(async (_postId: string, input: AdminPostUpdateInput): Promise<AdminPostDetail> => ({
      id: "post-1",
      title: input.title,
      slug: input.slug,
      summary: input.summary,
      categoryId: input.categoryId,
      seriesId: input.seriesId,
      tags: input.tags,
      status: "draft",
      contentFormat: input.contentFormat,
      content: input.content,
      revisionId: "revision-post-1-2",
      updatedAt: "2026-06-08T00:02:00Z"
    }));
    render(<App apiClient={adminApiClient({ updatePost })} />);

    await user.click(await screen.findByRole("button", { name: /First draft/ }));
    await screen.findByText("revision-post-1-1");

    const tagsField = screen.getByLabelText("Draft tags");
    await user.clear(tagsField);
    await user.type(tagsField, "   ,  , ");
    await user.click(screen.getByRole("button", { name: "Save draft changes" }));

    expect(updatePost).toHaveBeenCalledWith(
      "post-1",
      expect.objectContaining({ tags: [] })
    );
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
              summary: input.summary,
              categoryId: input.categoryId,
              seriesId: input.seriesId,
              tags: input.tags,
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
