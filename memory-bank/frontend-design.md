# Nairi

## Public Frontend Positioning

### Reader Experience

The public frontend presents articles, pages, project retrospectives, tags, categories, series, RSS, sitemap, and SEO metadata.

## Technology Stack

### Selected Stack

1. Next.js
2. React
3. TypeScript
4. Tailwind CSS
5. shadcn/ui
6. Markdown and governed MDX rendering

## Public Routes

### Implemented Routes

1. `/`
2. `/posts`
3. `/posts/{slug}`

### Planned Routes

1. `/tags/{slug}`
2. `/categories/{slug}`
3. `/series/{slug}`
4. `/about`
5. `/rss.xml`
6. `/sitemap.xml`

## Public List Integration

### Article List Page

1. Route: `/posts`.
2. Data source: `GET /api/v1/public/posts`.
3. Display fields: `title`, `summary`, `publishedAt`, and `tags`.
4. Each item links to `/posts/{slug}`.
5. The page uses the public route family only and must not call authenticated `/api/v1/posts...` management endpoints.
6. Empty public lists render a stable empty-state message.
7. Public list fetch failures render a controlled error boundary message.
8. The page requests a small first page with `limit`, accepts an item-id `cursor` query parameter, and renders a stable `Load more articles` link when `page.hasNextPage` is true and `nextCursor` is present.
9. Displaying page metadata, filtering UI, infinite scroll, RSS/sitemap pagination expansion, and cache/CDN policy remain deferred.

## Public Detail Integration

### Article Detail Page

1. Route: `/posts/{slug}`.
2. Data source: `GET /api/v1/public/posts/{slug}`.
3. Rendering source: `bodyHtml` from the public API response.
4. The page uses the public route family only and must not call authenticated `/api/v1/posts...` management endpoints.
5. Draft or unknown slugs use the framework not-found path.
6. Public list navigation, cache headers, CDN policy, and advanced typography remain deferred.

## Public Site Styling Boundary

### Shared Surface Rhythm

1. `/`, `/posts`, `/posts/{slug}`, and `/posts` error state share the `article-header` rhythm.
2. Home action, post cards, article body, empty state, and error state share the `surface-card` boundary.
3. CSS custom properties define the current small styling surface: `--nairi-surface`, `--nairi-border`, `--nairi-muted`, and `--nairi-shadow-soft`.
4. This is a narrow styling boundary only; Tailwind, shadcn/ui, a full design system, cache/CDN policy, SEO, RSS, and sitemap remain deferred.

## Rendering Rules

### Content Rendering

1. Public content should be read through dedicated public API capabilities.
2. The public site must not call authenticated `/api/v1/posts...` management endpoints directly.
3. Markdown is rendered by default.
4. MDX rendering uses registered components and published policies.
5. The public site must not expose admin or agent-only data, including revision identifiers, internal metadata, audit/job state, and agent traces.
6. `/posts` renders published date with a machine-readable `time` element, always shows a summary fallback when `summary` is null, renders tags when present, and links each item to `/posts/{slug}`.
7. `/posts/{slug}` renders public-safe `bodyHtml`, uses the framework not-found path for unknown slugs, renders published date with a machine-readable `time` element, always shows a summary fallback when `summary` is null, and renders tags when present.

### Public Cache Policy

1. Public list fetches use Next.js revalidation through `PUBLIC_POST_LIST_REVALIDATE_SECONDS`, currently 60 seconds.
2. Public detail fetches use Next.js revalidation through `PUBLIC_POST_DETAIL_REVALIDATE_SECONDS`, currently 300 seconds.
3. `/posts` and `/posts/{slug}` opt out of build-time API prerendering with `dynamic = "force-dynamic"` so local and CI builds do not require a live API.
4. Public frontend fetches must not use `cache: "no-store"` after this boundary unless a later explicit cache-policy task changes the contract.
5. Public frontend cache policy is explicitly Next.js revalidation only: no CDN headers, no publish-triggered invalidation, and no tag-based revalidation in this boundary.
6. `/rss.xml` uses route-level Next.js revalidation through `PUBLIC_FEED_REVALIDATE_SECONDS`, currently 300 seconds.
7. `/sitemap.xml` uses route-level Next.js revalidation through `PUBLIC_SITEMAP_REVALIDATE_SECONDS`, currently 300 seconds.
8. RSS and sitemap cache policy is explicitly Next.js route revalidation only: no CDN headers, no purge, and no publish-triggered invalidation execution in this boundary.
9. Real CDN purge wiring, revalidation webhooks, pagination cache policy, and tag/path invalidation execution remain deferred.

## SEO

### Public Metadata

1. `/` defines route metadata with title `Nairi | Project Experience Publishing` and a stable public-site description.
2. `/posts` defines route metadata with title `Articles | Nairi` and a stable published-list description.
3. `/posts/{slug}` generates metadata from `GET /api/v1/public/posts/{slug}` using the public title and summary.
4. Unknown public detail slugs return `Post not found | Nairi` metadata.
5. `/sitemap.xml` returns a sitemap index that points to `/sitemap-posts.xml`.
6. `/sitemap-posts.xml` returns XML with `/`, `/posts`, and published post detail URLs from bounded full-history public-list pagination; detail entries use `publishedAt` as `lastmod`.
7. `/rss.xml` returns RSS 2.0 XML with items from bounded full-history public-list pagination; items include title, link, guid, `pubDate` from `publishedAt`, and summary as description, and must not include full `bodyHtml`.
8. RSS and posts-sitemap full-history traversal uses anonymous public list pages only, with explicit `PUBLIC_POSTS_PAGE_SIZE` and `PUBLIC_POSTS_MAX_PAGES` bounds to avoid unbounded crawling. `/sitemap.xml` is a sitemap index, `/sitemap-static.xml` lists stable public landing routes, and `/sitemap-posts.xml` lists post detail URLs.
9. The public site URL defaults to localhost for local builds and is overridable through `NEXT_PUBLIC_NAIRI_PUBLIC_SITE_URL`.
10. Open Graph image generation, Atom, richer SEO schema, search-engine sitemap splitting beyond static/posts shards, and CDN invalidation remain deferred.
