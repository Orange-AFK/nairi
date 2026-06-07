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
8. Pagination, filtering UI, RSS, sitemap, and cache/CDN policy remain deferred.

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

## SEO

### Public Metadata

1. Title
2. Description
3. Canonical URL
4. Open Graph image
5. Structured metadata where appropriate.
