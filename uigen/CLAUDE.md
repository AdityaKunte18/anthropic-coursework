# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UIGen is an AI-powered React component generator with live preview. Users describe React components in a chat interface, and Claude AI generates them in real-time with a live preview rendered in an iframe.

## Commands

```bash
# Initial setup (installs deps, generates Prisma client, runs migrations)
npm run setup

# Development server (uses Turbopack)
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Run a single test file
npx vitest run src/components/chat/__tests__/ChatInterface.test.tsx

# Reset database
npm run db:reset

# Regenerate Prisma client after schema changes
npx prisma generate
```

## Architecture

### Data Flow

```
User Input → ChatInterface → ChatContext (api/chat)
  → Claude + Tools → FileSystemContext (handleToolCall)
  → VirtualFileSystem updates → PreviewFrame (refreshTrigger)
  → Babel JSX Transform → Import Maps → Live iframe Preview
```

### Key Contexts

- **FileSystemContext** (`src/lib/contexts/file-system-context.tsx`): Central state for the in-memory virtual filesystem. Also handles AI tool call results, intercepting `str_replace_editor` and `file_manager` calls to mutate filesystem state.
- **ChatContext** (`src/lib/contexts/chat-context.tsx`): Wraps Vercel AI SDK's `useChat`, serializes the current filesystem into each request body so the backend always has full file state.

### Virtual File System

`src/lib/file-system.ts` — An in-memory tree (no disk I/O). Methods: `createFile`, `deleteFile`, `readFile`, `updateFile`, `rename`, `serialize`, `deserialize`. Serialized as JSON and stored in the `Project.data` database column.

### AI Tools

Defined in `src/lib/tools/` and registered in `src/app/api/chat/route.ts`. Two tools Claude can call:
- **str_replace_editor**: Create, view, insert, and replace content in virtual files
- **file_manager**: Rename and delete files/directories

### Live Preview

`src/components/preview/PreviewFrame.tsx` watches for filesystem changes, transforms JSX to JS via Babel standalone (`src/lib/transform/jsx-transformer.ts`), creates blob URLs for modules, and uses browser import maps to redirect bare package imports to `esm.sh`. Entry point must be `/App.jsx`, `/App.tsx`, `/index.jsx`, or `/index.tsx`.

### Dual Provider Mode

`src/lib/provider.ts` returns a real Claude client (claude-haiku-4-5) if `ANTHROPIC_API_KEY` is set in `.env`, otherwise returns a `MockLanguageModel` with static demo responses. This enables offline development without an API key.

### Authentication

JWT-based auth using the `jose` library. Sessions stored in httpOnly cookies (7-day expiry). Middleware at `src/middleware.ts` protects `/api/projects` routes. Server actions in `src/actions/` handle sign-in, sign-up, sign-out, and project CRUD.

### Database

SQLite via Prisma. Schema: `User` (id, email, password) → `Project` (id, name, userId?, messages as JSON string, data as JSON string). `userId` is nullable for anonymous-owned projects.

### System Prompt

`src/lib/prompts/generation.tsx` — instructs Claude to always create `/App.jsx` as entrypoint, style with Tailwind CSS (not inline styles), and use `@/` alias for cross-file imports within the virtual filesystem.

## Environment

`.env` (or `.mockenv` for mock mode):
- `ANTHROPIC_API_KEY` — optional; if absent, mock provider is used
- `JWT_SECRET` — required for authentication

## Path Aliases

`@/*` maps to `./src/*` (configured in `tsconfig.json`).
