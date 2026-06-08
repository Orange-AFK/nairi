import { describe, expect, it, vi } from "vitest";

import { createAdminApiClient } from "./adminApiClient";

describe("createAdminApiClient", () => {
  it("lists draft posts through the authenticated management API with an injected token provider", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      expect(String(input)).toBe("https://api.example.test/api/v1/posts?status=draft");
      expect(init?.method).toBe("GET");
      expect(init?.headers).toEqual({
        Accept: "application/json",
        Authorization: "Bearer tkn"
      });

      return new Response(
        JSON.stringify({
          items: [
            {
              postId: "post-1",
              title: "First draft",
              slug: "first-draft",
              status: "draft",
              updatedAt: "2026-06-08T00:00:00Z"
            }
          ],
          nextCursor: null
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    });

    const client = createAdminApiClient({
      apiBaseUrl: "https://api.example.test/",
      getAuthToken: () => "tkn",
      fetchImpl: fetchMock
    });

    await expect(client.listPosts()).resolves.toEqual([
      {
        id: "post-1",
        title: "First draft",
        slug: "first-draft",
        status: "draft",
        updatedAt: "2026-06-08T00:00:00Z"
      }
    ]);
    expect(fetchMock).toHaveBeenCalledOnce();
  });

  it("fails closed when no admin API credentials are configured", async () => {
    const fetchMock = vi.fn();
    const client = createAdminApiClient({
      apiBaseUrl: "https://api.example.test",
      fetchImpl: fetchMock
    });

    await expect(client.listPosts()).rejects.toThrow("Admin API credentials are not configured.");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("fails closed when no API base URL is configured", async () => {
    const fetchMock = vi.fn();
    const client = createAdminApiClient({
      apiBaseUrl: "",
      fetchImpl: fetchMock
    });

    await expect(client.listPosts()).rejects.toThrow("Admin API base URL is not configured.");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("rejects relative API base URLs instead of guessing a browser-local target", async () => {
    const fetchMock = vi.fn();
    const client = createAdminApiClient({
      apiBaseUrl: "/api",
      fetchImpl: fetchMock
    });

    await expect(client.listPosts()).rejects.toThrow("Admin API base URL must be absolute.");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("reports a safe generic error when the management API rejects the request", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ error: "denied" }), { status: 403 }));
    const client = createAdminApiClient({
      apiBaseUrl: "https://api.example.test",
      getAuthToken: () => "tkn",
      fetchImpl: fetchMock
    });

    await expect(client.listPosts()).rejects.toThrow("Admin API request failed.");
  });

  it("updates a draft through the authenticated management API with optimistic detail mapping", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      expect(String(input)).toBe("https://api.example.test/api/v1/posts/post%2F1");
      expect(init?.method).toBe("PATCH");
      expect(init?.headers).toEqual({
        Accept: "application/json",
        "Content-Type": "application/json",
        Authorization: "Bearer tkn"
      });
      expect(JSON.parse(String(init?.body))).toEqual({
        title: "Updated draft",
        slug: "updated-draft",
        contentFormat: "markdown",
        content: "Updated draft body.",
        expectedRevisionId: "revision-post-1-1"
      });

      return new Response(
        JSON.stringify({
          postId: "post/1",
          status: "draft",
          revisionId: "revision-post-1-2",
          updatedAt: "2026-06-08T00:05:00Z"
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    });
    const client = createAdminApiClient({
      apiBaseUrl: "https://api.example.test/",
      getAuthToken: () => "tkn",
      fetchImpl: fetchMock
    });

    await expect(
      client.updatePost("post/1", {
        title: "Updated draft",
        slug: "updated-draft",
        contentFormat: "markdown",
        content: "Updated draft body.",
        expectedRevisionId: "revision-post-1-1"
      })
    ).resolves.toEqual({
      id: "post/1",
      title: "Updated draft",
      slug: "updated-draft",
      status: "draft",
      contentFormat: "markdown",
      content: "Updated draft body.",
      revisionId: "revision-post-1-2",
      updatedAt: "2026-06-08T00:05:00Z"
    });
    expect(fetchMock).toHaveBeenCalledOnce();
  });

  it("fails closed before PATCH when update credentials are missing", async () => {
    const fetchMock = vi.fn();
    const client = createAdminApiClient({
      apiBaseUrl: "https://api.example.test",
      fetchImpl: fetchMock
    });

    await expect(
      client.updatePost("post-1", {
        title: "Updated draft",
        slug: "updated-draft",
        contentFormat: "markdown",
        content: "Updated draft body.",
        expectedRevisionId: "revision-post-1-1"
      })
    ).rejects.toThrow("Admin API credentials are not configured.");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("reports a safe generic error when the management API rejects an update", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ error: "conflict" }), { status: 409 }));
    const client = createAdminApiClient({
      apiBaseUrl: "https://api.example.test",
      getAuthToken: () => "tkn",
      fetchImpl: fetchMock
    });

    await expect(
      client.updatePost("post-1", {
        title: "Updated draft",
        slug: "updated-draft",
        contentFormat: "markdown",
        content: "Updated draft body.",
        expectedRevisionId: "revision-post-1-1"
      })
    ).rejects.toThrow("Admin API request failed.");
  });

  it("reads a draft detail through the authenticated management API", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      expect(String(input)).toBe("https://api.example.test/api/v1/posts/post-1");
      expect(init?.method).toBe("GET");
      expect(init?.headers).toEqual({
        Accept: "application/json",
        Authorization: "Bearer tkn"
      });

      return new Response(
        JSON.stringify({
          postId: "post-1",
          title: "First draft",
          status: "draft",
          contentFormat: "markdown",
          content: "# First draft\n\nDraft body from the management API.",
          revisionId: "revision-post-1-1",
          updatedAt: "2026-06-08T00:00:00Z"
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    });
    const client = createAdminApiClient({
      apiBaseUrl: "https://api.example.test/",
      getAuthToken: () => "tkn",
      fetchImpl: fetchMock
    });

    await expect(client.getPost("post-1")).resolves.toEqual({
      id: "post-1",
      title: "First draft",
      status: "draft",
      contentFormat: "markdown",
      content: "# First draft\n\nDraft body from the management API.",
      revisionId: "revision-post-1-1",
      updatedAt: "2026-06-08T00:00:00Z"
    });
  });
});
