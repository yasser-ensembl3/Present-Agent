# MiniVault Template

Reusable project management dashboard boilerplate. Clone, run the setup script, and get a fully configured single-project dashboard backed by Notion, Google Drive, Gmail, GitHub, and AI — all wired via environment variables.

**Architecture**: One repo = one project. Each clone/fork is dedicated to a single project. No multi-project switching — all configuration lives in `.env.local`.

## Quick Start

```bash
# 1. Clone or copy
git clone git@github.com:yasser-ensembl3/Present-Agent.git my-project
cd my-project

# 2. Auto-create Notion databases + generate .env.local
python3 setup-project.py "My Project"

# 3. Install and run
npm install
npm run dev
# Open http://localhost:3000
```

The setup script (`setup-project.py`) creates everything in Notion automatically:
- A parent page named after your project
- 6 databases: Tasks, Goals, Metrics, Milestones, Documents, Feedback
- A `.env.local` file pre-filled with all database IDs and credentials

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| UI | shadcn/ui + Tailwind CSS (dark mode locked) |
| Auth | NextAuth.js (Google + GitHub OAuth) |
| Data | Notion API (raw fetch, not SDK) |
| AI | OpenAI (gpt-4-turbo-preview) + Anthropic (claude-3-5-sonnet) |
| Google APIs | Gmail + Drive via service account JWT + OAuth |
| Charts | Recharts |
| Calendar | react-day-picker + date-fns |
| Deployment | Vercel (iad1 region) |

## Dashboard Sections

7 collapsible sections rendered in priority order:

| # | Section | Description | Default |
|---|---------|-------------|---------|
| 1 | Goals | Output metrics (sales, subscribers, reviews) — green theme, clickable cards + Recharts line charts | Collapsed |
| 2 | Metrics | Input metrics (posts, interactions, spend) — blue theme, same interactive pattern | Collapsed |
| 3 | Guides & Docs | Documentation links — CRUD with auto-sync from Google Drive + GitHub (deduplicates by URL) | Open |
| 4 | Overview | Project description + vision (from Notion page blocks) and milestones CRUD with percentage tracking | Open |
| 5 | Projects & Tasks | 5-column Kanban (To Do / In Progress / Review / Done / Completed) with priority colors and calendar picker | Open |
| 6 | Weekly Reports | AI-generated reports from Notion tasks — stored in localStorage, not persisted | Compact when empty |
| 7 | User Feedback | Feedback CRUD with stats (total, this week, this month) | Compact when empty |

3 additional components exist but are **not mounted** in the dashboard:
- **DriveSection** — Google Drive file browser (OAuth)
- **GitHubSection** — repo viewer (commits, PRs, issues)
- **KnowledgeSection** — static placeholder

## Architecture

```
app/
├── api/
│   ├── auth/[...nextauth]/route.ts    # NextAuth handler
│   ├── ai/chat/route.ts              # Dual AI (OpenAI + Anthropic)
│   ├── notion/
│   │   ├── tasks/route.ts            # GET/POST — schema-adaptive
│   │   ├── metrics/route.ts          # GET/POST — shared by goals + metrics sections
│   │   ├── goals/route.ts            # GET/POST — output goals
│   │   ├── documents/route.ts        # GET/POST/PATCH/DELETE
│   │   ├── feedback/route.ts         # GET/POST/PATCH/DELETE
│   │   ├── milestones/route.ts       # GET/POST/PATCH/DELETE
│   │   └── project-overview/route.ts # GET/POST — page block content
│   ├── drive/files/route.ts          # Google Drive (OAuth session token)
│   ├── github/repo/route.ts          # GitHub repo + commits + PRs + issues
│   ├── google/
│   │   ├── drive/route.ts            # Google Drive (service account JWT)
│   │   └── gmail/route.ts            # Gmail (service account JWT)
│   └── feedback/save/route.ts        # Save feedback as .txt files to disk
├── auth/signin/page.tsx               # OAuth sign-in page
├── layout.tsx                         # Root layout (dark mode, Inter font, AuthProvider)
├── page.tsx                           # Renders MainDashboard
└── globals.css                        # Tailwind v3 + CSS custom properties

components/
├── auth/session-provider.tsx          # NextAuth SessionProvider wrapper
├── dashboard/
│   ├── main-dashboard.tsx            # Orchestrator — session check + 7 sections
│   ├── header.tsx                    # Project name + user info + sign out
│   ├── dashboard-section.tsx         # Reusable collapsible card (Radix Collapsible)
│   ├── goals-metrics-section.tsx     # 470 lines — green output metrics + charts
│   ├── metrics-section.tsx           # 470 lines — blue input metrics + charts
│   ├── guides-docs-section.tsx       # 635 lines — 13 link types + auto-sync
│   ├── overview-section.tsx          # 662 lines — description/vision + milestones
│   ├── project-tracking-section.tsx  # 455 lines — Kanban board
│   ├── reports-section.tsx           # 267 lines — AI weekly reports
│   ├── user-feedback-section.tsx     # 465 lines — feedback CRUD
│   ├── drive-section.tsx             # 220 lines — not mounted
│   ├── github-section.tsx            # 302 lines — not mounted
│   └── knowledge-section.tsx         # 73 lines — not mounted
└── ui/                                # 11 shadcn/ui primitives

lib/
├── auth.ts                            # NextAuth config (Google + GitHub)
├── project-config.ts                  # Env-based ProjectConfig with useProjectConfig() hook
└── utils.ts                           # cn() utility (clsx + tailwind-merge)

types/next-auth.d.ts                   # Session extension (accessToken, refreshToken, provider)
setup-project.py                       # Automated Notion setup + .env.local generator
```

## API Routes

### Notion Routes

All routes use raw `fetch()` against Notion REST API v2022-06-28. Every POST route dynamically queries the database schema first to discover property names and types, supporting multiple naming variants (English and French).

| Route | Methods | Key Details |
|-------|---------|-------------|
| `/api/notion/tasks` | GET, POST | Status reads: `status.name` → `select.name` → `rich_text`. Priority and tags written as `rich_text`. Schema-adaptive property discovery for 5 field variants. |
| `/api/notion/metrics` | GET, POST | Shared by goals and metrics sections (different database IDs). Number property adapts to type: `number`, `multi_select`, or `rich_text`. Date from "Last Updated" or "Date". |
| `/api/notion/goals` | GET, POST | Properties: Name, Category, Current Progress, Deadline, Status, Target. POST checks schema for each property's existence. |
| `/api/notion/documents` | GET, POST, PATCH, DELETE | Type detection from `select` or `rich_text`. URL from "URL" or "Link". DELETE archives (not hard delete). PATCH fetches page to discover parent database schema. |
| `/api/notion/feedback` | GET, POST, PATCH, DELETE | PATCH uses page-level property introspection to find correct property keys. POST requires title + feedback + userName. |
| `/api/notion/milestones` | GET, POST, PATCH, DELETE | Percentage field discovery: 11 name variants searched via case-insensitive exact match, then partial match. Sorted by "Due Date" ascending. |
| `/api/notion/project-overview` | GET, POST | Reads/writes Notion page blocks (not database). Finds "Description" and "Vision" headings (h2/h3), reads/updates the paragraph block after each. Creates heading + paragraph if missing. |

### Other Routes

| Route | Auth | Details |
|-------|------|---------|
| `/api/ai/chat` | None | POST with `{ message, provider, model }`. OpenAI default: `gpt-4-turbo-preview`. Anthropic default: `claude-3-5-sonnet-20241022`. Max tokens: 1024 (Anthropic). |
| `/api/auth/[...nextauth]` | — | NextAuth handler. Logs env var presence on startup. |
| `/api/drive/files` | OAuth session | Google Drive folder listing. Returns folder metadata + files with type detection (folder/doc/sheet/slides). 50 results, sorted by modifiedTime desc. |
| `/api/github/repo` | OAuth session | Fetches repo info + 5 latest commits + 10 open issues + 10 open PRs. All via GitHub REST API v3. |
| `/api/google/drive` | Service account JWT | Alternative Drive access via `googleapis` library. Supports query parameter. |
| `/api/google/gmail` | Service account JWT | Lists messages via Gmail API. Fetches full message details (subject, from, date, snippet). |
| `/api/feedback/save` | None | Saves feedback as `.txt` files to `data/feedbacks/` directory. Filename: `YYYY-MM-DD_sanitized_title.txt`. |

## Authentication

NextAuth.js with JWT strategy:

```
User → /auth/signin → Google or GitHub
  → OAuth redirect → authorization code
  → JWT callback stores access_token + refresh_token + provider
  → Session callback exposes tokens to client
  → MainDashboard checks session → redirect if absent
```

**Google scopes**: openid, email, profile, gmail.readonly, drive.readonly, documents.readonly
**GitHub scopes**: read:user, user:email, repo

Session type extended with `accessToken`, `refreshToken`, `provider` fields.

## Setup Script

`setup-project.py` automates project bootstrapping:

1. Takes project name as argument
2. Uses `urllib.request` to call Notion API (no external dependencies)
3. Creates a parent page in the configured workspace
4. Creates 6 databases as children of that page with predefined schemas:
   - **Tasks**: Name (title), Status (select: To Do/In Progress/Review/Done/Completed), Priority (select: Low/Medium/High/Urgent), Assignee (rich_text), Due Date (date), Tags (multi_select)
   - **Goals**: Name (title), Category (select), Current Progress (number), Target (number), Deadline (date), Status (select)
   - **Metrics**: Metric Name (title), Number (number), Last Updated (date)
   - **Milestones**: Name (title), Due Date (date), Description (rich_text), Percentage (number)
   - **Documents**: Name (title), URL (url), Description (rich_text), Type (select)
   - **Feedback**: Title (title), Date (date), Feedback (rich_text), User Name (rich_text)
5. Generates `.env.local` with all database IDs + OAuth credentials

## Dual Metrics System

Two separate tracking dimensions sharing the same API endpoint but querying different Notion databases:

| Dimension | Theme | Database Config Key | Purpose |
|-----------|-------|-------------------|---------|
| Goals (outputs) | Green | `NEXT_PUBLIC_NOTION_DB_GOALS` | Results achieved (sales, subscribers, reviews) |
| Metrics (inputs) | Blue | `NEXT_PUBLIC_NOTION_DB_METRICS` | Actions taken (posts, interactions, spend) |

Both feature: clickable metric cards with ring highlight, Recharts line charts, `normalizeMetricType()` (lowercase, accents removed), add dialog.

## Environment Variables

```env
# Authentication
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=

# OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_ID=
GITHUB_SECRET=

# APIs
NOTION_TOKEN=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_SERVICE_ACCOUNT_KEY=  # single-line JSON

# Project (NEXT_PUBLIC_ = client-accessible)
NEXT_PUBLIC_PROJECT_NAME=
NEXT_PUBLIC_NOTION_DB_TASKS=
NEXT_PUBLIC_NOTION_DB_GOALS=
NEXT_PUBLIC_NOTION_DB_METRICS=
NEXT_PUBLIC_NOTION_DB_MILESTONES=
NEXT_PUBLIC_NOTION_DB_DOCUMENTS=
NEXT_PUBLIC_NOTION_DB_FEEDBACK=
NEXT_PUBLIC_NOTION_DB_SALES=
NEXT_PUBLIC_NOTION_DB_CUSTOM_METRICS=
NEXT_PUBLIC_NOTION_PROJECT_PAGE_ID=
NEXT_PUBLIC_GITHUB_OWNER=
NEXT_PUBLIC_GITHUB_REPO=
NEXT_PUBLIC_GOOGLE_DRIVE_FOLDER_ID=
```

## Design Decisions

1. **One repo = one project** — no multi-project support, no project switching. Each deployment serves one project.
2. **Schema-adaptive Notion** — every POST route queries database schema first, handles multiple property name variants (English + French), adapts write format to actual property type.
3. **Raw fetch over SDK** — `@notionhq/client` is installed but unused. All Notion calls use raw `fetch()`.
4. **Dark mode locked** — `<html className="dark">` in layout, no toggle.
5. **No database** — all persistent data in Notion or localStorage (reports). No SQL/Prisma.
6. **Dual Google Drive** — OAuth (user token via session) and service account (JWT) implementations coexist.
7. **Console logging stripped in prod** — `next.config.js` `removeConsole: true`. Debug logs prefixed with `[ComponentName]`.
8. **Template-first** — designed to be cloned, with `setup-project.py` handling all Notion bootstrapping.

## Deployment (Vercel)

1. Push to GitHub
2. Import in Vercel
3. Add all environment variables
4. Update `NEXTAUTH_URL` to production URL
5. Update OAuth callback URLs: `https://your-domain/api/auth/callback/google` and `/github`

`vercel.json` sets region to `iad1` (US East).

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No access token" | Sign in with the correct provider (Google for Drive/Gmail, GitHub for repos) |
| Notion API 401 | Check `NOTION_TOKEN`, ensure integration has database access |
| Empty sections | Verify the corresponding `NEXT_PUBLIC_NOTION_DB_*` env var is set |
| OAuth callback error | Check callback URLs match exactly in OAuth app settings |
| Milestones % missing | Percentage property name may not match any of the 11 searched variants |
| AI reports fail | Check `OPENAI_API_KEY` is set and has credits |
| GOOGLE_SERVICE_ACCOUNT_KEY error | Must be single-line JSON (no unescaped newlines) |
| Slow first compilation | `optimizePackageImports` in next.config.js handles this (lucide-react + @radix-ui/react-icons tree-shaking) |
