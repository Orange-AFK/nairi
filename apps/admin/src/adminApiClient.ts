import type {
  AdminApiClient,
  AdminCategory,
  AdminPostMetadata,
  AdminPostDetail,
  AdminPostPublishInput,
  AdminPostPublishResult,
  AdminPostSummary,
  AdminPostUpdateInput,
  AdminPublishReviewRequestInput,
  AdminPublishReviewRequestResult
} from "./App";

type FetchLike = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

type CreateAdminApiClientOptions = {
  apiBaseUrl: string;
  getAuthToken?: () => string;
  fetchImpl?: FetchLike;
};

type ManagementPostSummary = {
  postId: string;
  title: string;
  slug: string;
  summary: string | null;
  categoryId: string | null;
  seriesId: string | null;
  tags: string[];
  metadata: AdminPostMetadata;
  status: string;
  updatedAt?: string;
  publishedAt?: string;
};

type ManagementPostDetail = ManagementPostSummary & {
  contentFormat: "markdown" | "mdx";
  content: string;
  revisionId: string;
};

type ManagementPostUpdateResponse = {
  postId: string;
  status: string;
  revisionId: string;
  updatedAt: string;
};

type ManagementPostPublishResponse = {
  postId: string;
  status: string;
  publishedAt: string;
  jobId: string;
  publicInvalidation: AdminPostPublishResult["publicInvalidation"];
};

type ManagementPublishReviewRequestResponse = {
  requestId: string;
  postId: string;
  revisionId: string;
  status: "pending";
  requestedAt: string;
};

type ListPostsResponse = {
  items?: ManagementPostSummary[];
};

type ManagementCategory = {
  categoryId: string;
  name: string;
  slug: string;
  createdAt: string;
  updatedAt: string;
};

type ListCategoriesResponse = {
  items?: ManagementCategory[];
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
    slug: post.slug,
    summary: post.summary,
    categoryId: post.categoryId,
    seriesId: post.seriesId,
    tags: post.tags,
    metadata: post.metadata,
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

function mapPostPublishResult(payload: ManagementPostPublishResponse): AdminPostPublishResult {
  return {
    id: payload.postId,
    status: payload.status,
    publishedAt: payload.publishedAt,
    jobId: payload.jobId,
    publicInvalidation: payload.publicInvalidation
  };
}

function mapPublishReviewRequestResult(
  payload: ManagementPublishReviewRequestResponse
): AdminPublishReviewRequestResult {
  return {
    requestId: payload.requestId,
    postId: payload.postId,
    revisionId: payload.revisionId,
    status: payload.status,
    requestedAt: payload.requestedAt
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
  path,
  method = "GET",
  body
}: RuntimeAdminApiClientOptions & { path: string; method?: "GET" | "PATCH" | "POST"; body?: unknown }): Promise<T> {
  const url = buildManagementUrl(apiBaseUrl, path);
  const headers: Record<string, string> = {
    Accept: "application/json",
    Authorization: `Bearer ${requireAuthToken(getAuthToken)}`
  };
  const init: RequestInit = { method, headers };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(body);
  }

  const response = await fetchImpl(url, init);

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
    async listPublishedPosts() {
      const payload = await fetchManagementJson<ListPostsResponse>({
        ...clientOptions,
        path: "/api/v1/posts?status=published"
      });
      return (payload.items ?? []).map(mapPostSummary);
    },
    async getPost(postId: string) {
      const payload = await fetchManagementJson<ManagementPostDetail>({
        ...clientOptions,
        path: `/api/v1/posts/${encodeURIComponent(postId)}`
      });
      return mapPostDetail(payload);
    },
    async updatePost(postId: string, input: AdminPostUpdateInput) {
      const payload = await fetchManagementJson<ManagementPostUpdateResponse>({
        ...clientOptions,
        path: `/api/v1/posts/${encodeURIComponent(postId)}`,
        method: "PATCH",
        body: {
          title: input.title,
          slug: input.slug,
          summary: input.summary,
          categoryId: input.categoryId,
          seriesId: input.seriesId,
          tags: input.tags,
          metadata: input.metadata,
          contentFormat: input.contentFormat,
          content: input.content,
          expectedRevisionId: input.expectedRevisionId
        }
      });
      return {
        id: payload.postId,
        title: input.title,
        slug: input.slug,
        summary: input.summary,
        categoryId: input.categoryId,
        seriesId: input.seriesId,
        tags: input.tags,
        metadata: input.metadata,
        status: payload.status,
        contentFormat: input.contentFormat,
        content: input.content,
        revisionId: payload.revisionId,
        updatedAt: payload.updatedAt
      };
    },
    async requestPublishReview(postId: string, input: AdminPublishReviewRequestInput) {
      const payload = await fetchManagementJson<ManagementPublishReviewRequestResponse>({
        ...clientOptions,
        path: `/api/v1/posts/${encodeURIComponent(postId)}/publish-requests`,
        method: "POST",
        body: {
          revisionId: input.revisionId
        }
      });
      return mapPublishReviewRequestResult(payload);
    },
    async publishPost(postId: string, input: AdminPostPublishInput) {
      const payload = await fetchManagementJson<ManagementPostPublishResponse>({
        ...clientOptions,
        path: `/api/v1/posts/${encodeURIComponent(postId)}/publish`,
        method: "POST",
        body: {
          revisionId: input.revisionId,
          publishMode: input.publishMode,
          scheduledAt: input.scheduledAt
        }
      });
      return mapPostPublishResult(payload);
    },
    async listCategories() {
      const payload = await fetchManagementJson<ListCategoriesResponse>({
        ...clientOptions,
        path: "/api/v1/categories"
      });
      return (payload.items ?? []) as AdminCategory[];
    }
  };
}
