import type { AdminApiClient, AdminPostDetail, AdminPostSummary } from "./App";

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

type ManagementPostDetail = ManagementPostSummary & {
  contentFormat: "markdown" | "mdx";
  content: string;
  revisionId: string;
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

function mapPostDetail(post: ManagementPostDetail): AdminPostDetail {
  return {
    ...mapPostSummary(post),
    contentFormat: post.contentFormat,
    content: post.content,
    revisionId: post.revisionId
  };
}

function buildManagementUrl(apiBaseUrl: string, path: string): string {
  try {
    return buildUrl(apiBaseUrl, path);
  } catch (error) {
    if (error instanceof Error && error.message === "Admin API base URL is not configured.") {
      throw error;
    }
    throw new Error("Admin API base URL must be absolute.");
  }
}

type RuntimeAdminApiClientOptions = {
  apiBaseUrl: string;
  getAuthToken?: () => string;
  fetchImpl: FetchLike;
};

async function fetchManagementJson<T>({
  apiBaseUrl,
  getAuthToken,
  fetchImpl,
  path
}: RuntimeAdminApiClientOptions & { path: string }): Promise<T> {
  const response = await fetchImpl(buildManagementUrl(apiBaseUrl, path), {
    method: "GET",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${requireAuthToken(getAuthToken)}`
    }
  });

  if (!response.ok) {
    throw new Error("Admin API request failed.");
  }

  return (await response.json()) as T;
}

export function createAdminApiClient({
  apiBaseUrl,
  getAuthToken,
  fetchImpl = globalThis.fetch.bind(globalThis)
}: CreateAdminApiClientOptions): AdminApiClient {
  const clientOptions = { apiBaseUrl, getAuthToken, fetchImpl };

  return {
    async listPosts() {
      const payload = await fetchManagementJson<ListPostsResponse>({
        ...clientOptions,
        path: "/api/v1/posts?status=draft"
      });
      return (payload.items ?? []).map(mapPostSummary);
    },
    async getPost(postId: string) {
      const payload = await fetchManagementJson<ManagementPostDetail>({
        ...clientOptions,
        path: `/api/v1/posts/${encodeURIComponent(postId)}`
      });
      return mapPostDetail(payload);
    }
  };
}
