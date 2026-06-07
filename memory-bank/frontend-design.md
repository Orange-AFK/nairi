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

### Planned Routes

1. `/`
2. `/posts`
3. `/posts/{slug}`
4. `/tags/{slug}`
5. `/categories/{slug}`
6. `/series/{slug}`
7. `/about`
8. `/rss.xml`
9. `/sitemap.xml`

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
