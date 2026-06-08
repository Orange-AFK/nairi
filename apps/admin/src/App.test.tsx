import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { App, type AdminApiClient, type AdminPostDetail } from "./App";

function adminApiClient(overrides: Partial<AdminApiClient> = {}): AdminApiClient {
  return {
    async listPosts() {
      return [
        {
          id: "post-1",
          title: "First draft",
          status: "draft",
          updatedAt: "2026-06-08T00:00:00Z"
        }
      ];
    },
    async getPost(postId: string) {
      return {
        id: postId,
        title: "First draft",
        status: "draft",
        contentFormat: "markdown",
        content: "# First draft\n\nDraft body from the management API.",
        revisionId: "revision-post-1-1",
        updatedAt: "2026-06-08T00:00:00Z"
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

    expect(await screen.findByRole("button", { name: /First draft/ })).toBeInTheDocument();
    expect(screen.getAllByText("draft").length).toBeGreaterThan(0);
  });

  it("selects a post and reads draft detail through the injected API boundary", async () => {
    const user = userEvent.setup();
    const getPost = vi.fn(async (postId: string): Promise<AdminPostDetail> => ({
      id: postId,
      title: "First draft",
      status: "draft",
      contentFormat: "markdown",
      content: "# First draft\n\nDraft body from the management API.",
      revisionId: "revision-post-1-1",
      updatedAt: "2026-06-08T00:00:00Z"
    }));
    render(<App apiClient={adminApiClient({ getPost })} />);

    await user.click(await screen.findByRole("button", { name: /First draft/ }));

    expect(getPost).toHaveBeenCalledWith("post-1");
    expect(await screen.findByRole("heading", { name: "First draft" })).toBeInTheDocument();
    expect(screen.getByText("API-backed draft detail"));
    expect(screen.getByText(/Draft body from the management API\./)).toBeInTheDocument();
    expect(screen.getByText("revision-post-1-1")).toBeInTheDocument();
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
                status: "draft",
                updatedAt: "2026-06-08T00:00:00Z"
              },
              {
                id: "post-2",
                title: "Second draft",
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
