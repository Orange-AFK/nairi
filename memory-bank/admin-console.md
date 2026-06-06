# Nairi

## Admin Console Positioning

### Human Control Plane

The CMS admin console is the human-facing control plane for content, media, MDX governance, agent tasks, permissions, audit logs, and settings.

## Technology Stack

### Selected Stack

1. React
2. Vite
3. TypeScript
4. TanStack Router
5. TanStack Query
6. React Hook Form
7. Zod
8. Tailwind CSS
9. shadcn/ui

## Admin Modules

### Content Management

1. Post list
2. Post editor
3. Draft review
4. Revision history
5. Publication controls
6. Tags, categories, and series

### Media Library

1. Upload assets
2. Manage alt text
3. Track references
4. Select cover images

### MDX Governance

1. Component registry
2. Risk level configuration
3. Role and agent scope policy
4. Review requirement policy

### Agent Operations

1. Agent task list
2. Draft generation results
3. Risk explanations
4. Audit trail for agent actions

### System Settings

1. Site metadata
2. SEO defaults
3. API tokens
4. Webhooks
5. MCP configuration

## API Coupling Rule

### Admin API Access

The admin console must use documented API endpoints only. It must not perform direct database writes or bypass permission checks.
