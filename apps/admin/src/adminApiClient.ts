import type { AdminApiClient, AdminPostSummary } from "./App";

type FetchLike = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

type CreateAdminApiClientOptions = {
  apiBaseUrl: string;
  getAuthToken?: () => string;
  fetchImpl?: FetchLike;
};

type ManagementPostSummary = {
  postId: string;
  title: string;
  status: string;
  updatedAt?: string;
  publishedAt?: string;
};

type ListPostsResponse = {
  items?: ManagementPostSummary[];
};

function requireAbsoluteApiBaseUrl(apiBaseUrl: string): string {
  const trimmedBaseUrl = apiBaseUrl.trim();
  if (!trimmedBaseUrl) {
    throw new Error("Admin API base URL is not configured.");
  }

  const parsedBaseUrl = new URL(trimmedBaseUrl);
  if (parsedBaseUrl.protocol !== "http:" && parsedBaseUrl.protocol !== "https:") {
    throw new Error("Admin API base URL must be absolute.");
  }

  return parsedBaseUrl.toString();
}

function buildUrl(apiBaseUrl: string, path: string): string {
  const baseUrl = requireAbsoluteApiBaseUrl(apiBaseUrl);
  return new URL(path.replace(/^\//, ""), baseUrl).toString();
}

function requireAuthToken(getAuthToken?: () => string): string {
  const token = getAuthToken?.().trim();
  if (!token) {
    throw new Error("Admin API credentials are not configured.");
  }
  return token;
}

function mapPostSummary(post: ManagementPostSummary): AdminPostSummary {
  return {
    id: post.postId,
    title: post.title,
    status: post.status,
    updatedAt: post.updatedAt ?? post.publishedAt ?? ""
  };
}

export function createAdminApiClient({
  apiBaseUrl,
  getAuthToken,
  fetchImpl = globalThis.fetch.bind(globalThis)
}: CreateAdminApiClientOptions): AdminApiClient {
  return {
    async listPosts() {
      let url: string;
      try {
        url = buildUrl(apiBaseUrl, "/api/v1/posts?status=draft");
      } catch (error) {
        if (error instanceof Error && error.message === "Admin API base URL is not configured.") {
          throw error;
        }
        throw new Error("Admin API base URL must be absolute.");
      }

      const response = await fetchImpl(url, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${requireAuthToken(getAuthToken)}`
        }
      });

      if (!response.ok) {
        throw new Error("Admin API request failed.");
      }

      const payload = (await response.json()) as ListPostsResponse;
      return (payload.items ?? []).map(mapPostSummary);
    }
  };
}
