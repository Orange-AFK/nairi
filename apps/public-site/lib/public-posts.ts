export type PublicPostDetail = {
  postId: string;
  title: string;
  slug: string;
  status: "published";
  contentFormat: "markdown" | "mdx";
  content: string;
  bodyHtml: string;
  summary: string | null;
  tags: string[];
  categoryId: string | null;
  seriesId: string | null;
  publishedAt: string;
};

export type PublicPostSummary = {
  postId: string;
  title: string;
  slug: string;
  status: "published";
  contentFormat: "markdown" | "mdx";
  summary: string | null;
  tags: string[];
  categoryId: string | null;
  seriesId: string | null;
  publishedAt: string;
};

type ListPublicPostsResponse = {
  items: PublicPostSummary[];
  nextCursor: string | null;
};

type FetchPublicPostOptions = {
  apiBaseUrl?: string;
};

const DEFAULT_API_BASE_URL = "http://localhost:8000";

function publicApiBaseUrl(apiBaseUrl?: string): string {
  return (apiBaseUrl ?? process.env.NEXT_PUBLIC_NAIRI_API_BASE_URL ?? DEFAULT_API_BASE_URL).replace(/\/$/, "");
}

export async function fetchPublicPostBySlug(
  slug: string,
  options: FetchPublicPostOptions = {},
): Promise<PublicPostDetail | null> {
  const response = await fetch(`${publicApiBaseUrl(options.apiBaseUrl)}/api/v1/public/posts/${encodeURIComponent(slug)}`, {
    cache: "no-store",
  });

  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`Failed to fetch public post ${slug}: ${response.status}`);
  }

  return (await response.json()) as PublicPostDetail;
}

export async function fetchPublicPosts(options: FetchPublicPostOptions = {}): Promise<PublicPostSummary[]> {
  const response = await fetch(`${publicApiBaseUrl(options.apiBaseUrl)}/api/v1/public/posts`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch public posts: ${response.status}`);
  }

  const payload = (await response.json()) as ListPublicPostsResponse;
  return payload.items;
}
