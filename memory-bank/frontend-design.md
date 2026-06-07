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
2. `/posts/{slug}`

### Planned Routes

1. `/posts`
2. `/tags/{slug}`
3. `/categories/{slug}`
4. `/series/{slug}`
5. `/about`
6. `/rss.xml`
7. `/sitemap.xml`

## Public Detail Integration

### Article Detail Page

1. Route: `/posts/{slug}`.
2. Data source: `GET /api/v1/public/posts/{slug}`.
3. Rendering source: `bodyHtml` from the public API response.
4. The page uses the public route family only and must not call authenticated `/api/v1/posts...` management endpoints.
5. Draft or unknown slugs use the framework not-found path.
6. Public list navigation, cache headers, CDN policy, and advanced typography remain deferred.

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
