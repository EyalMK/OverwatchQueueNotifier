You are executing the AutoSpec Spec-Driven Development methodology.

Read ALL documents in the input folder. Use them as the single source of truth.

## Input

Read every file in: SRS/
These are the project's SRS, PRD, and/or requirements documents.

Extract from them:
  - Project name and description
  - Target users / personas
  - All functional and non-functional requirements
  - Technical stack (frontend, backend, database, language, hosting)
  - Constraints, assumptions, and out-of-scope items
  - User flows and business rules

If any of the above are missing from the input documents, state your assumptions
explicitly at the top of 01_product_manager.md and continue generating.

══════════════════════════════════════════════════════════════
GENERATION PLAN — WHAT YOU MUST PRODUCE
══════════════════════════════════════════════════════════════

Generate the COMPLETE output structure below.
Every file must be specific to THIS project — no generic placeholders.

project/
│
├── specs/                              # 10 role-based specifications
│   ├── 01_product_manager.md
│   ├── 02_backend_lead.md
│   ├── 03_frontend_lead.md
│   ├── 04_db_architect.md
│   ├── 05_qa_lead.md
│   ├── 06_devops_lead.md
│   ├── 07_marketing_lead.md
│   ├── 08_finance_lead.md
│   ├── 09_business_lead.md
│   ├── 10_ui_designer.md
│   └── backlog.md                      # Sprint-organized ticket backlog
│
├── docs/                               # Comprehensive project documentation
│   ├── architecture/
│   │   ├── overview.md                 # High-level system architecture
│   │   ├── backend.md                  # Backend layers, patterns, structure
│   │   ├── frontend.md                 # Component architecture, state, routing
│   │   ├── database.md                 # ERD, schemas, migrations, queries
│   │   ├── security.md                 # Auth flow, encryption, OWASP checklist
│   │   ├── cloud.md                    # Cloud provider architecture (AWS/GCP/Azure)
│   │   └── deep-dive.md               # Detailed technical decisions and trade-offs
│   │
│   ├── workflows/
│   │   ├── development.md              # Feature development step-by-step
│   │   ├── sprint-execution.md         # How to run a sprint (single + multi-agent)
│   │   ├── git-workflow.md             # Branching strategy, commit conventions, PR flow
│   │   ├── ci-cd-pipeline.md           # Pipeline stages, triggers, artifacts
│   │   ├── bug-fix.md                  # Triage → reproduce → fix → verify flow
│   │   ├── deployment.md               # Dev → staging → production deployment
│   │   ├── multi-agent.md              # Parallel agent execution rules
│   │   └── qa-review.md               # QA checklist and review process
│   │
│   ├── environments/
│   │   ├── development.md              # Local setup guide with prerequisites
│   │   ├── docker.md                   # docker-compose, Dockerfiles, commands
│   │   ├── staging.md                  # Staging environment config
│   │   ├── production.md               # Production environment + checklist
│   │   └── environment-variables.md    # Complete .env reference with every variable
│   │
│   ├── api/
│   │   ├── reference.md                # Full REST API reference (all endpoints)
│   │   ├── authentication.md           # Auth endpoints, token flow, refresh
│   │   ├── error-codes.md              # Error code catalog with HTTP mappings
│   │   └── rate-limiting.md            # Rate limit rules per endpoint
│   │
│   ├── testing/
│   │   ├── strategy.md                 # Test pyramid, coverage targets
│   │   ├── unit-tests.md               # Unit test patterns with examples
│   │   ├── integration-tests.md        # API integration test patterns
│   │   ├── e2e-tests.md                # End-to-end test scenarios
│   │   └── test-data.md                # Seed data, fixtures, factories
│   │
│   ├── ui-design-system/
│   │   ├── tokens.md                   # Colors, typography, spacing, radii, shadows
│   │   ├── components.md               # Component inventory with states
│   │   ├── layouts.md                  # Page layouts, grid system, breakpoints
│   │   ├── accessibility.md            # WCAG 2.1 AA checklist, screen reader notes
│   │   └── icons-assets.md             # Icon set, image guidelines, loading strategy
│   │
│   └── project/
│       ├── setup.md                    # Repo structure, configs, IDE setup
│       ├── coding-standards.md         # Naming, patterns, linting rules
│       └── glossary.md                 # Project-specific terms defined
│
├── sprint_prompts/                     # Ready-to-paste sprint execution prompts
│   ├── sprint-0-foundation.md          # Foundation sprint with phase breakdown
│   ├── sprint-N-template.md            # Feature sprint template (replace N)
│   ├── multi-agent.md                  # Agent A (backend) + Agent B (frontend) prompts
│   ├── qa-review.md                    # QA review checklist prompt
│   └── finops.md                       # Model selection optimizer (haiku/sonnet/opus)
│
├── prompts/                            # Additional generation prompts
│   ├── gemini-diagram-prompts.md       # Prompts for Gemini to generate architecture diagrams
│   └── remotion-video-prompt.md        # Prompt for Remotion video generation
│
└── viewer/                             # Project monitor website (React app)
    └── (see Section 7 for full spec)

══════════════════════════════════════════════════════════════
SECTION 1 — SPECS (10 Role-Based Specifications)
══════════════════════════════════════════════════════════════

Generate 10 specification files in specs/. Each must be 300–800 lines,
specific to THIS project, with concrete examples — never generic placeholders.
Cross-reference other specs by filename where relevant.

### specs/01_product_manager.md
- Project vision, elevator pitch (one paragraph)
- Problem statement (what pain does this solve?)
- 3–5 detailed user personas: name, role, goals, frustrations, tech comfort
- User stories with acceptance criteria (Given/When/Then)
- Complete user flows (registration, core actions, edge cases) with ASCII diagrams
- Feature prioritization (MoSCoW: Must/Should/Could/Won't for v1)
- Success metrics with numeric targets
- Assumptions stated explicitly

### specs/02_backend_lead.md
- System architecture overview with ASCII diagram
- Tech stack table (framework, ORM, validation, auth, testing)
- Project directory structure
- Complete API contracts table: Method | Path | Auth | Request Body | Response | Status Codes
- Request/response JSON examples for EVERY endpoint
- Authentication flow (JWT access + refresh tokens, or sessions)
- Service layer design with responsibility boundaries
- Error handling: custom error classes, error code enum, HTTP mapping
- Rate limiting rules per endpoint category
- Middleware chain order

### specs/03_frontend_lead.md
- Tech stack (framework, build tool, CSS approach, state management)
- Component hierarchy: atoms → molecules → organisms → pages
- State management: what is global (auth, theme) vs local (form, modal)
- Complete routing table with auth guards and lazy loading
- Design system tokens: colors (hex), spacing scale (px), typography (font, sizes, weights)
- Form handling pattern (library, validation, error display)
- API client abstraction (base URL, interceptors, error handling)
- Performance targets (LCP < 2.5s, FID < 100ms, CLS < 0.1)

### specs/04_db_architect.md
- Database technology and ORM/query builder
- Entity-Relationship diagram (ASCII)
- Complete CREATE TABLE SQL for every table: columns, types, constraints, defaults
- Index definitions with purpose (what query each index optimises)
- Migration strategy: naming convention (YYYYMMDDHHMMSS_desc), tooling
- Common query patterns (list with pagination, search, joins)
- Seed data plan: what tables, how many rows, realistic data
- Soft delete vs hard delete policy

### specs/05_qa_lead.md
- Test pyramid: unit (70%) / integration (20%) / e2e (10%)
- Coverage target: 70%+ lines, 80%+ for critical services
- Test file naming and location conventions
- Unit test examples for services (with mock setup)
- Integration test examples for API endpoints (with test DB)
- E2E critical path scenarios (list every flow to test)
- Performance benchmarks: p50 < 100ms, p95 < 300ms, p99 < 1s
- Security testing checklist (OWASP top 10 mapped to this project)
- QA process: when to test, who reviews, definition of done

### specs/06_devops_lead.md
- Infrastructure diagram (ASCII)
- CI/CD pipeline: stages (lint → typecheck → test → build → deploy), triggers
- Docker setup: base images, multi-stage builds, compose services
- Environment matrix: dev | staging | production differences
- Deployment strategy (blue-green, rolling, or canary)
- Monitoring: what metrics, what alerts, what thresholds
- Logging: structured JSON, log levels, retention policy
- Backup: database backup schedule, recovery procedure, RTO/RPO

### specs/07_marketing_lead.md
- Go-to-market strategy (phased: beta → launch → growth)
- Target audience segments with estimated sizes
- Messaging framework: value props, taglines, elevator pitch
- Launch timeline with milestones
- Channel strategy: which channels, why, expected CAC per channel
- Content plan: blog posts, social, email sequences
- Success metrics: signups, activation rate, retention targets

### specs/08_finance_lead.md
- Infrastructure cost estimate (monthly: compute, DB, storage, CDN, monitoring)
- AI/LLM cost estimate (tokens per sprint, model tier breakdown)
- Pricing strategy (if SaaS: free tier, paid tiers with limits)
- Revenue projections (3, 6, 12 month)
- Unit economics: CAC, LTV, LTV:CAC ratio, payback period
- Budget allocation by phase
- Break-even analysis

### specs/09_business_lead.md
- Business model overview (how it makes money or delivers value)
- Competitive analysis: 3–5 competitors with strengths/weaknesses table
- SWOT analysis
- Value proposition canvas (jobs, pains, gains)
- KPIs with targets and measurement method
- Risk assessment: 5+ risks with likelihood, impact, mitigation
- Growth strategy: phases with triggers to advance

### specs/10_ui_designer.md
- Complete screen inventory: every page, modal, drawer, toast
- Wireframe descriptions for each screen (layout, elements, interactions)
- Component states: default, hover, active, disabled, error, loading, empty
- Responsive breakpoints: mobile (< 640), tablet (640–1024), desktop (> 1024)
- Design tokens repeated from frontend spec for self-containment
- Interaction patterns: navigation, forms, tables, cards, drag-and-drop
- Accessibility: WCAG 2.1 AA compliance, color contrast ratios, focus management
- Animation principles: micro-interactions, transitions, loading states

══════════════════════════════════════════════════════════════
SECTION 2 — BACKLOG
══════════════════════════════════════════════════════════════

Generate specs/backlog.md.

Format:

# [Project Name] Backlog

Generated: [date]
Total Tickets: [count]
Total Story Points: [sum]

## Sprint 0: Foundation
Goal: Project setup, infrastructure, walking skeleton.

| ID | Title | Description | Points | Status | Owner | Model | Dependencies |
|----|-------|-------------|--------|--------|-------|-------|-------------|

## Sprint 1: [Theme]
Goal: [description]

| ID | Title | Description | Points | Status | Owner | Model | Dependencies |
|----|-------|-------------|--------|--------|-------|-------|-------------|

[Continue for all sprints]

## Bug Backlog
| ID | Title | Severity | Status | Sprint | Notes |
|----|-------|----------|--------|--------|-------|

Rules:
- Extract EVERY actionable item from all 10 specs.
- Sprint 0: 15–25 points (setup + skeleton).
- Feature sprints: 25–40 points each.
- Each ticket: 1–5 points (split anything > 5).
- Story points: 1 = ~30 min, 2 = ~1–2h, 3 = ~2–4h, 5 = ~4–8h.
- Model column: haiku (40%), sonnet (45%), opus (15%).
- Owner: DB, Backend, Frontend, DevOps, QA.
- All statuses start as "todo".
- Include dependencies (e.g., "1.3" means ticket 1.3 must complete first).

══════════════════════════════════════════════════════════════
SECTION 3 — DOCS: ARCHITECTURE
══════════════════════════════════════════════════════════════

Generate every file in docs/architecture/.

### docs/architecture/overview.md
- High-level system diagram (ASCII): client → API → DB → cache → queue
- Tech stack summary table
- Request lifecycle from browser to database and back
- Non-functional requirements summary (latency, throughput, availability)
- Key architectural decisions with rationale

### docs/architecture/backend.md
- Layered architecture: Routes → Middleware → Controllers → Services → Repositories
- Directory structure with file purposes
- Dependency injection approach
- Error propagation through layers
- Logging at each layer

### docs/architecture/frontend.md
- Component tree from App root to leaf components
- State flow: global store → context → local state → derived
- Data fetching strategy (React Query / SWR / fetch)
- Code splitting and lazy loading plan
- Asset pipeline (images, fonts, icons)

### docs/architecture/database.md
- Full ERD with all relationships (ASCII)
- Table catalog: every table with column list and purpose
- Query performance expectations
- Connection pooling configuration
- Partitioning or sharding strategy (if applicable, else state "not needed at this scale")

### docs/architecture/security.md
- Authentication flow diagram (ASCII): register → login → token → refresh → logout
- Authorization model (RBAC/ABAC) with role definitions
- Input validation layer (where, how, which library)
- SQL injection, XSS, CSRF prevention
- Secret management (env vars, vault, rotation policy)
- HTTPS, CORS, CSP, rate limiting
- Data encryption: at rest (DB) and in transit (TLS)

### docs/architecture/cloud.md
- Target cloud provider architecture
- Service mapping: which cloud service for each component
- Networking: VPC, subnets, security groups
- Scaling strategy: horizontal auto-scaling rules
- Cost optimisation notes
- If cloud provider is unknown, generate for AWS with notes on GCP/Azure equivalents

### docs/architecture/deep-dive.md
- Technical decisions log: decision, options considered, chosen option, rationale
- Trade-offs acknowledged
- Known limitations and future migration paths
- Performance bottleneck analysis
- Caching strategy (what, where, TTL, invalidation)

══════════════════════════════════════════════════════════════
SECTION 4 — DOCS: WORKFLOWS, ENVIRONMENTS, API, TESTING,
             UI DESIGN SYSTEM, PROJECT
══════════════════════════════════════════════════════════════

Generate every file in docs/workflows/, docs/environments/, docs/api/,
docs/testing/, docs/ui-design-system/, and docs/project/.

Each file should be 100–300 lines, specific to THIS project.

### docs/workflows/
- development.md: Feature development flow from ticket to done (step-by-step)
- sprint-execution.md: How to run a sprint with AutoSpec (read specs, execute tickets, update backlog)
- git-workflow.md: Branch naming, commit format (type(scope): desc), PR template, merge strategy
- ci-cd-pipeline.md: Pipeline diagram, stage details, failure handling, artifact outputs
- bug-fix.md: Triage → reproduce → failing test → fix → verify → update backlog
- deployment.md: Dev auto-deploy, staging on merge to develop, production on release tag
- multi-agent.md: Agent A (backend) + Agent B (frontend) rules, shared backlog, integration phase
- qa-review.md: Code quality, test coverage, security, functional, performance, accessibility checklists

### docs/environments/
- development.md: Prerequisites, clone, install, env vars, start services, verify health
- docker.md: docker-compose.yml content, Dockerfiles, common commands, troubleshooting
- staging.md: Staging URL, deployment, data seeding, access control
- production.md: Production URL, deployment, checklist, rollback procedure
- environment-variables.md: Every env var with name, description, example value, required/optional

### docs/api/
- reference.md: Full endpoint catalog with Method | Path | Auth | Body | Response | Codes
- authentication.md: Register, login, refresh, logout flows with curl examples
- error-codes.md: Every error code, HTTP status, user message, developer message
- rate-limiting.md: Rules table, headers returned, retry-after handling

### docs/testing/
- strategy.md: Test pyramid, tooling, coverage targets, CI integration
- unit-tests.md: Service test pattern (arrange/act/assert), mocking guide, examples
- integration-tests.md: API test pattern (supertest), test DB setup/teardown, examples
- e2e-tests.md: Critical user journeys as test scenarios, Playwright/Cypress patterns
- test-data.md: Seed script, factory functions, fixture files

### docs/ui-design-system/
- tokens.md: Full token table: colors (hex + semantic name), spacing (scale), font sizes, weights, line heights, border radii, shadows, z-index scale
- components.md: Every UI component: name, props, variants, states (default/hover/active/disabled/error/loading)
- layouts.md: Page layout templates, grid system (12-col), sidebar width, header height, breakpoints
- accessibility.md: WCAG 2.1 AA checklist applied to this project, focus management, aria attributes, skip links
- icons-assets.md: Icon library (Lucide/Heroicons), image optimisation (WebP, lazy loading), favicon, OG image

### docs/project/
- setup.md: Full repo structure tree, config files explained (tsconfig, eslint, prettier, vite)
- coding-standards.md: Naming conventions (camelCase vars, PascalCase types, snake_case DB), patterns, import order
- glossary.md: Every project-specific term defined (domain language)

══════════════════════════════════════════════════════════════
SECTION 5 — SPRINT PROMPTS
══════════════════════════════════════════════════════════════

Generate every file in sprint_prompts/. Each prompt must be COMPLETE and
READY TO PASTE into an AI assistant — the user should not need to add context.

CRITICAL: Every sprint prompt must begin with an instruction block that tells
the AI to read ALL relevant project files before executing. This is how the AI
gets full context. Each prompt must list the exact files to read.

### sprint_prompts/sprint-0-foundation.md

A complete, ready-to-paste prompt for executing Sprint 0. Structure:

Context — Read These Files First
Read the following files to understand the full project:

SPECS (read all): specs/01_product_manager.md — requirements, personas, user flows specs/02_backend_lead.md — API design, service layer, error handling specs/03_frontend_lead.md — components, state, routing, design tokens specs/04_db_architect.md — database schema, migrations, queries specs/05_qa_lead.md — test strategy, coverage targets specs/06_devops_lead.md — infrastructure, CI/CD, Docker specs/10_ui_designer.md — screens, wireframes, responsive design

BACKLOG: specs/backlog.md — Sprint 0 tickets (your work items)

DOCS (read all relevant): docs/architecture/overview.md — system architecture docs/architecture/backend.md — backend layer design docs/architecture/frontend.md — frontend component architecture docs/architecture/database.md — ERD, tables, relationships docs/architecture/security.md — auth flow, security rules docs/environments/development.md — local setup prerequisites docs/environments/docker.md — Docker setup docs/environments/environment-variables.md — all env vars docs/project/setup.md — repo structure, config files docs/project/coding-standards.md — naming conventions, patterns docs/workflows/development.md — development workflow docs/workflows/git-workflow.md — branching, commit format docs/testing/strategy.md — test pyramid, tooling docs/ui-design-system/tokens.md — design tokens


Then:
- Phase breakdown: Infrastructure → Database → Backend setup → Frontend setup → Quality gates
- Per-ticket instructions referencing the exact spec file and section
- Definition of done checklist per ticket
- Commands to verify each phase (health check, lint, typecheck, test)
- Backlog update: mark each ticket "done" in specs/backlog.md after completion

### sprint_prompts/sprint-N-template.md

A template prompt for any feature sprint with [N] placeholder. Structure:

Context — Read These Files First
Read the following files: specs/backlog.md — find Sprint [N] tickets specs/01_product_manager.md — requirements for this sprint's features specs/02_backend_lead.md — API contracts for endpoints in this sprint specs/03_frontend_lead.md — component specs for UI in this sprint specs/04_db_architect.md — database changes needed specs/05_qa_lead.md — test requirements docs/architecture/overview.md — ensure changes fit architecture docs/architecture/backend.md — follow backend patterns docs/architecture/frontend.md — follow frontend patterns docs/architecture/database.md — follow DB conventions docs/api/reference.md — endpoint contracts docs/api/authentication.md — auth patterns (if auth-related) docs/api/error-codes.md — error handling patterns docs/testing/unit-tests.md — unit test patterns docs/testing/integration-tests.md — integration test patterns docs/workflows/development.md — development workflow to follow docs/workflows/git-workflow.md — branch + commit conventions docs/ui-design-system/tokens.md — design tokens for UI work docs/ui-design-system/components.md — component patterns docs/project/coding-standards.md — naming + patterns


Then:
- Backend ticket pattern: migration → schema → repo → service → controller → routes → tests
- Frontend ticket pattern: types → API service → components → page → routes → tests
- After EVERY ticket: update specs/backlog.md (status → "done", add notes)
- Sprint completion checklist: all tests pass, lint clean, typecheck clean

### sprint_prompts/multi-agent.md

Two separate prompts (Agent A and Agent B) that can be pasted into parallel AI sessions:

Agent A (Backend) prompt must start with:
Read these files: specs/02_backend_lead.md, specs/04_db_architect.md, specs/05_qa_lead.md specs/backlog.md (your tickets: Owner = "Backend" or "DB") docs/architecture/backend.md, docs/architecture/database.md, docs/architecture/security.md docs/api/reference.md, docs/api/authentication.md, docs/api/error-codes.md docs/environments/environment-variables.md docs/testing/unit-tests.md, docs/testing/integration-tests.md docs/project/coding-standards.md


Agent B (Frontend) prompt must start with:
Read these files: specs/03_frontend_lead.md, specs/10_ui_designer.md, specs/05_qa_lead.md specs/backlog.md (your tickets: Owner = "Frontend") docs/architecture/frontend.md docs/ui-design-system/tokens.md, docs/ui-design-system/components.md, docs/ui-design-system/layouts.md, docs/ui-design-system/accessibility.md docs/testing/unit-tests.md, docs/testing/e2e-tests.md docs/project/coding-standards.md


Integration phase prompt: merge branches, connect APIs, run full test suite, fix issues
Rules: no cross-directory work, shared backlog, dependency order respected

### sprint_prompts/qa-review.md

Prompt for QA review after a sprint. Must start with:
Read ALL specs and docs to understand the full project: specs/* (all 10 specs + backlog.md) docs/testing/* (strategy, unit, integration, e2e, test-data) docs/architecture/security.md docs/api/reference.md, docs/api/error-codes.md docs/ui-design-system/accessibility.md docs/workflows/qa-review.md


Then:
- Checklist sections: code quality, test coverage, security, functional, performance, accessibility
- Per-ticket output format: status (PASS/FAIL), issues found, verdict
- Final actions: mark tickets done in backlog, add bugs to Bug Backlog

### sprint_prompts/finops.md
- Model selection guide: haiku (40%), sonnet (45%), opus (15%)
- Per-task-type recommendations (haiku: boilerplate/CRUD, sonnet: features/tests, opus: architecture/complex)
- Cost comparison table
- Sprint cost forecast template

══════════════════════════════════════════════════════════════
SECTION 6 — GENERATION PROMPTS (GEMINI DIAGRAMS + REMOTION VIDEO)
══════════════════════════════════════════════════════════════

Generate the following prompt files in prompts/.

### prompts/gemini-diagram-prompts.md

A ready-to-paste prompt for Google Gemini (or any image-capable AI) to generate
architecture and workflow diagrams. The prompt must instruct the AI to:

- Read ALL generated files to understand the full project
- Generate these diagrams:
  1. System Architecture Diagram — from docs/architecture/overview.md
     (client → API → services → DB → cache → queue → external)
  2. Database ERD — from specs/04_db_architect.md and docs/architecture/database.md
     (all tables, relationships, cardinality, key columns)
  3. Frontend Component Tree — from specs/03_frontend_lead.md and docs/architecture/frontend.md
     (App → layouts → pages → organisms → molecules → atoms)
  4. CI/CD Pipeline — from specs/06_devops_lead.md and docs/workflows/ci-cd-pipeline.md
     (stages with parallel branches, triggers, artifacts)
  5. Authentication Flow — from docs/architecture/security.md and docs/api/authentication.md
     (register → login → JWT → refresh → logout, with token storage)
  6. Cloud Infrastructure — from docs/architecture/cloud.md
     (VPC, subnets, services, load balancer, CDN, monitoring)
  7. User Journey Map — from specs/01_product_manager.md
     (persona → entry point → core actions → completion → edge cases)
  8. Sprint Workflow — from docs/workflows/sprint-execution.md
     (ticket pickup → implement → test → review → merge → deploy)

- Style: clean, professional, consistent colour palette, legible at 1x zoom
- Format: SVG or high-res PNG (300 DPI)
- Include a legend on each diagram

### prompts/remotion-video-prompt.md

A ready-to-paste prompt for generating a Remotion (React video framework)
project that creates an animated project overview video.

The prompt must instruct the AI to:

1. READ ALL GENERATED PROJECT FILES to understand every aspect:
   - All 10 specs in specs/ (01_product_manager.md through 10_ui_designer.md)
   - The complete backlog in specs/backlog.md (all sprints, tickets, story points)
   - All 37 docs across docs/architecture/, docs/workflows/, docs/environments/,
     docs/api/, docs/testing/, docs/ui-design-system/, docs/project/
   - The sprint prompts in sprint_prompts/

2. GENERATE A REMOTION PROJECT with these scenes (in order):

   Scene 1 — Title Card (3s):
     Project name, tagline from 01_product_manager.md, tech stack badges

   Scene 2 — Problem & Solution (8s):
     Problem statement from 01_product_manager.md
     Animated bullet points of key pain points → solution value props

   Scene 3 — Architecture Overview (10s):
     Animate the system architecture from docs/architecture/overview.md
     Components fly in: client → API → services → DB → cache
     Connection lines draw between components
     Tech stack labels appear on each component

   Scene 4 — Database Schema (8s):
     Animate ERD from specs/04_db_architect.md
     Tables slide in, relationships draw as lines
     Show key columns and data types per table

   Scene 5 — User Flows (10s):
     Animate 2-3 key user flows from specs/01_product_manager.md
     Show persona → screens → actions → outcomes
     Use screen mockup shapes from specs/10_ui_designer.md

   Scene 6 — API Overview (6s):
     Animate endpoint groups from docs/api/reference.md
     Show request → response flow with status codes
     Group by resource (auth, users, core features)

   Scene 7 — Frontend Architecture (8s):
     Component tree animation from docs/architecture/frontend.md
     App root → pages → layouts → components (cascade reveal)
     Show state management flow arrows

   Scene 8 — Sprint Roadmap (10s):
     Animate sprint timeline from specs/backlog.md
     Each sprint slides in as a card with:
       Sprint name, goal, ticket count, story points
     Progress bar fills for each sprint
     Total project: X sprints, Y tickets, Z story points

   Scene 9 — DevOps & Deployment (6s):
     CI/CD pipeline animation from docs/workflows/ci-cd-pipeline.md
     Pipeline stages flow: lint → test → build → deploy
     Docker + cloud infrastructure from docs/architecture/cloud.md

   Scene 10 — Security (5s):
     Auth flow animation from docs/architecture/security.md
     Show JWT token lifecycle, RBAC roles
     Security checklist items check off

   Scene 11 — Testing Strategy (5s):
     Test pyramid animation from docs/testing/strategy.md
     Unit (70%) → Integration (20%) → E2E (10%)
     Coverage targets and CI gates

   Scene 12 — Team & Roles (6s):
     Show all 10 AutoSpec roles animating in:
     Product Manager, Backend Lead, Frontend Lead, DB Architect,
     QA Lead, DevOps Lead, Marketing Lead, Finance Lead,
     Business Lead, UI Designer
     Each with an icon and one-line responsibility

   Scene 13 — Closing Card (4s):
     Project name, "Built with AutoSpec"
     Key stats: X specs, Y docs, Z sprint prompts
     GitHub URL / project URL

3. TECHNICAL REQUIREMENTS:
   - Remotion v4 + TypeScript
   - 1920x1080 (1080p), 30fps
   - Total duration: ~90 seconds
   - Use @remotion/transitions for scene transitions (slide, fade, wipe)
   - Use @remotion/paths for SVG path drawing animations
   - Use spring() for physics-based animations
   - Consistent colour palette matching the project's design tokens from
     docs/ui-design-system/tokens.md
   - Font: Inter (headings) + JetBrains Mono (code)
   - Background: dark gradient (#0f172a → #1e293b)
   - Export as MP4 (H.264) and WebM

══════════════════════════════════════════════════════════════
SECTION 7 — VIEWER / PROJECT MONITOR WEBSITE
══════════════════════════════════════════════════════════════

Generate a complete, self-contained React application in viewer/ that
provides a visual dashboard for ALL generated artefacts (specs, docs,
backlog, workflows).

### 7.1 Tech Stack

  React 18 + TypeScript + Vite + Tailwind CSS + React Router
  @xyflow/react (React Flow v12) — workflow graph visualisation
  framer-motion — panel transitions ONLY (NOT for mass edge animation)
  lucide-react — icons
  react-markdown + remark-gfm — Markdown rendering

### 7.2 Project Structure

viewer/
├── public/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css                    # Tailwind + global tokens + @keyframes
│   │
│   ├── data/                        # Static artefacts (import at build time)
│   │   ├── specs/                   # All 10 spec .md files
│   │   ├── docs/                    # All docs .md files (mirrored structure)
│   │   ├── backlog.json             # Parsed backlog (sprints + tickets)
│   │   ├── workflows.json           # Graph definitions (nodes + edges)
│   │   └── requirements.md          # Original SRS
│   │
│   ├── pages/
│   │   ├── DashboardPage.tsx        # "/"
│   │   ├── SpecsPage.tsx            # "/specs" + "/specs/:slug"
│   │   ├── DocsPage.tsx             # "/docs" + "/docs/:section/:slug"
│   │   ├── BacklogPage.tsx          # "/backlog"
│   │   ├── WorkflowsPage.tsx        # "/workflows"
│   │   ├── ArchitecturePage.tsx     # "/architecture"
│   │   └── RequirementsPage.tsx     # "/requirements"
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx          # Collapsible nav (260 px → 64 px)
│   │   │   ├── Header.tsx           # Search, breadcrumb, theme toggle
│   │   │   ├── DetailsPanel.tsx     # Right drawer (380 px, slide-in)
│   │   │   └── Layout.tsx           # Three-column shell
│   │   │
│   │   ├── specs/
│   │   │   ├── SpecViewer.tsx       # Markdown renderer + sticky TOC
│   │   │   └── SpecCard.tsx         # Grid card for spec list
│   │   │
│   │   ├── docs/
│   │   │   ├── DocViewer.tsx        # Markdown renderer for docs
│   │   │   ├── DocTree.tsx          # Nested folder tree navigation
│   │   │   └── DocCard.tsx          # Card for doc section
│   │   │
│   │   ├── backlog/
│   │   │   ├── BacklogBoard.tsx     # Tab per sprint + table
│   │   │   ├── SprintTab.tsx
│   │   │   └── TicketRow.tsx
│   │   │
│   │   ├── workflows/
│   │   │   ├── WorkflowCanvas.tsx   # React Flow wrapper
│   │   │   ├── AnimatedEdge.tsx     # SVG stroke-dashoffset animation
│   │   │   ├── WorkflowNode.tsx     # Memoised node component
│   │   │   ├── AnimationController.tsx  # Play/Pause/Speed/Focus toolbar
│   │   │   ├── WorkflowLegend.tsx   # Collapsible legend overlay
│   │   │   ├── WorkflowSearch.tsx   # Search + filter bar
│   │   │   └── PlayTour.tsx         # Auto-walk critical path
│   │   │
│   │   ├── dashboard/
│   │   │   ├── OverviewCards.tsx
│   │   │   ├── ProgressRing.tsx
│   │   │   └── RecentTickets.tsx
│   │   │
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── Badge.tsx
│   │       ├── Card.tsx
│   │       ├── Toggle.tsx
│   │       └── Tooltip.tsx
│   │
│   ├── hooks/
│   │   ├── useAnimationEngine.ts    # Central animation state
│   │   ├── useAnimationSettings.ts  # localStorage persistence
│   │   └── useReducedMotion.ts      # prefers-reduced-motion
│   │
│   └── lib/
│       ├── animation.ts             # Constants, easing, helpers
│       ├── graph.ts                 # BFS, critical path, subgraph
│       └── theme.ts                 # Design tokens
│
├── tailwind.config.js
├── vite.config.ts
├── tsconfig.json
└── package.json

### 7.3 Design System (Dark Theme)

Colours:
  --bg:           #0f172a   (slate-950)
  --surface:      #1e293b   (slate-800)
  --surface-2:    #334155   (slate-700)
  --border:       rgba(255,255,255,0.08)
  --text:         #f1f5f9   (slate-100)
  --text-muted:   #94a3b8   (slate-400)
  --primary:      #3b82f6   (blue-500)
  --secondary:    #a855f7   (purple-500)
  --success:      #10b981   (emerald-500)
  --warning:      #f59e0b   (amber-500)
  --error:        #ef4444   (red-500)
  --info:         #06b6d4   (cyan-500)

Typography: Inter (headings 600–700, body 400), JetBrains Mono (code)
Base: 16 px, scale: 1.25
Spacing: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 px
Radii: sm 6, md 10, lg 16, full 9999

### 7.4 Pages

Dashboard ("/"):
  - Project name, description, tech stack badges
  - Sprint progress ring (% done calculated from backlog.json)
  - Stat cards: total tickets, done, in-progress, blocked (from backlog.json)
  - Top 5 in-progress tickets table (from backlog.json)
  - Quick-links grid to ALL 10 specs (01_product_manager → 10_ui_designer)
  - Quick-links grid to ALL doc folders (architecture, workflows, environments, api, testing, ui-design-system, project)
  - "View Workflows" CTA
  - "View Backlog" CTA with total ticket count

Specs ("/specs"):
  - 10 spec cards in responsive grid (2 col md, 3 col lg)
  - Card: role icon, title, excerpt (first 150 chars), word count badge
  - Must render ALL 10 specs:
    01_product_manager.md  │  02_backend_lead.md    │  03_frontend_lead.md
    04_db_architect.md     │  05_qa_lead.md         │  06_devops_lead.md
    07_marketing_lead.md   │  08_finance_lead.md    │  09_business_lead.md
    10_ui_designer.md
  - Detail ("/specs/:slug"): full Markdown rendered with react-markdown + remark-gfm
  - Sticky TOC auto-generated from ## headings
  - "Back to all specs" breadcrumb

Docs ("/docs"):
  - Nested tree navigation mirroring the EXACT docs/ folder structure
  - Top-level cards per folder with file count badge:
    📁 architecture/ (7 files)  — overview, backend, frontend, database, security, cloud, deep-dive
    📁 workflows/ (8 files)     — development, sprint-execution, git-workflow, ci-cd-pipeline, bug-fix, deployment, multi-agent, qa-review
    📁 environments/ (5 files)  — development, docker, staging, production, environment-variables
    📁 api/ (4 files)           — reference, authentication, error-codes, rate-limiting
    📁 testing/ (5 files)       — strategy, unit-tests, integration-tests, e2e-tests, test-data
    📁 ui-design-system/ (5 files) — tokens, components, layouts, accessibility, icons-assets
    📁 project/ (3 files)       — setup, coding-standards, glossary
  - Clicking a folder shows all files inside as cards
  - Detail ("/docs/:section/:slug"): full Markdown with TOC
  - Breadcrumb: Docs > Architecture > Security
  - EVERY .md file from ALL 37 doc files must be accessible and rendered

Backlog ("/backlog"):
  THIS IS THE MOST CRITICAL DATA PAGE — it renders specs/backlog.md as a fully
  interactive board.

  - Parse backlog.md into structured data: sprints, tickets, stats
  - Tab per sprint (Sprint 0, 1, 2, …)
  - Per-sprint header: sprint goal, total points, progress bar (done/total)
  - Table with columns: ID | Title | Description | Points | Status | Owner | Model | Dependencies
  - Status badges colour-coded:
    todo = slate, in-progress = blue, done = emerald, blocked = red
  - Filters: status dropdown, owner dropdown, model dropdown (haiku/sonnet/opus)
  - Search: free-text across ticket titles and descriptions
  - Sprint summary stats: total tickets, total points, points completed, % done
  - Overall project stats header: total sprints, total tickets, total story points
  - Bug Backlog tab at the end with severity badges
  - Click any ticket row → DetailsPanel slides in with full description,
    dependencies (linked to their tickets), and owner info

Workflows ("/workflows"):
  - Full-screen React Flow canvas (see Section 7.5)
  - Top toolbar: animation controls + search + filters
  - Bottom-right: legend overlay (collapsible)
  - Sidebar auto-collapses on this page

Architecture ("/architecture"):
  - Renders ALL 7 docs/architecture/ files:
    overview.md | backend.md | frontend.md | database.md | security.md | cloud.md | deep-dive.md
  - Tab or accordion per file
  - ASCII diagrams rendered in styled <pre> blocks with monospace font
  - Cross-links between architecture docs (e.g., "See security.md" becomes a click)

Requirements ("/requirements"):
  - Renders original SRS/PRD as Markdown
  - Functional vs non-functional sections with colour badges
  - Highlight extracted requirements that map to spec tickets

### 7.5 Workflow Animation Engine

DATA MODEL:

  interface WorkflowGraph {
    id: string;
    name: string;
    description: string;
    nodes: WorkflowNode[];
    edges: WorkflowEdge[];
  }

  interface WorkflowNode {
    id: string;
    label: string;
    type: 'process' | 'decision' | 'start' | 'end' | 'external';
    metadata?: Record<string, string>;
    position: { x: number; y: number };
  }

  interface WorkflowEdge {
    id: string;
    source: string;
    target: string;
    label?: string;
    animated: boolean;
    animationDirection: 'forward' | 'reverse';
    priority: number;   // 0 = critical path, 1+ = secondary
  }

Generate workflows.json with at LEAST these graphs:
  1. Feature Development Flow (8–12 nodes)
  2. Sprint Execution Flow (6–10 nodes)
  3. System Request Lifecycle (8–12 nodes, from client to DB and back)
  4. CI/CD Pipeline (8–10 nodes with parallel stages)
  5. User Authentication Flow (8–10 nodes)
  6. One additional flow derived from the project's specific user flows

EDGE ANIMATION (AnimatedEdge.tsx):

  Technique: SVG stroke-dasharray + stroke-dashoffset via CSS @keyframes.
  NO JavaScript timers. Pure CSS on an SVG <path>.

  The edge draws a second <path> overlay (the "pulse"):
    - strokeDasharray = pathLength
    - strokeDashoffset animates from pathLength → 0 (forward)
    - animation-duration reads from CSS variable --edge-anim-duration
    - animationTimingFunction: ease-in-out
    - animationIterationCount: infinite

  @keyframes edgeFlow {
    0%   { stroke-dashoffset: var(--path-length); opacity: 0; }
    10%  { opacity: 1; }
    90%  { opacity: 1; }
    100% { stroke-dashoffset: 0; opacity: 0; }
  }

  Speed mapping (set as CSS custom property on wrapper):
    0.5x → --edge-anim-duration: 6s
    1.0x → --edge-anim-duration: 3s
    1.5x → --edge-anim-duration: 2s

NODE SELECTION — CAUSAL TRACE:

  Click a node →
    Step 1 (0 ms): Dim all nodes/edges to opacity 0.15.
                    Highlight clicked node (opacity 1 + ring).
    Step 2 (0–600 ms): Incoming edges animate (pulse travels TO node).
                        Source nodes fade to 0.8.
    Step 3 (600–900 ms): Pause. Clicked node pulses (scale 1.0 → 1.03 → 1.0).
    Step 4 (900–1500 ms): Outgoing edges animate (pulse travels AWAY).
                           Target nodes fade to 0.8.
                           Multiple outgoing edges stagger 150 ms each.
    Step 5 (1500 ms+): Hold. Edges loop. Click another node or canvas bg to reset.

  Implementation: CSS classes toggled by useAnimationEngine hook.
  NO per-node/per-edge React state. Only hook holds selectedNodeId.

CONTROLS (AnimationController.tsx):

  ┌──────────────────────────────────────────────────────────┐
  │ ▶ Play │ ⏸ Pause │ 0.5x  1x  1.5x │ 🔍 Focus │ ⚙ │
  └──────────────────────────────────────────────────────────┘

  - Play / Pause: toggle edge CSS animation-name.
  - Speed: set --edge-anim-duration CSS property. No React re-render.
  - Focus Mode: only selected node's subgraph (BFS depth 2) visible.
    If no node selected: auto-highlight critical path (longest path heuristic).
  - Settings gear (⚙) popover: master ON/OFF + reduced-motion override.
  - Persist to localStorage: animationsEnabled, speed, focusMode.

PLAY TOUR (PlayTour.tsx):

  1. Compute critical path (longest start→end path).
  2. fitView to start node (800 ms pan).
  3. Trigger causal trace on current node.
  4. Open DetailsPanel with node metadata.
  5. Wait 1500 ms / speed multiplier.
  6. Advance to next node.
  7. On final node: fitView to full graph (1200 ms).
  Cancel: click canvas, press Escape, or click Pause.

LEGEND (WorkflowLegend.tsx):

  Bottom-right corner, semi-transparent, collapsible.
  ──▶  Animated pulse = active data flow
  - -▶  Dashed = secondary / inactive path
  ● Blue   = process step
  ◆ Yellow = decision point
  ○ Grey   = external system
  Click a node to trace its flow. "Play Tour" auto-walks the main path.
  Hidden on viewports < 768 px.

ACCESSIBILITY:

  - Read prefers-reduced-motion on mount and on change.
  - If active: animations default OFF, edges show static dashes,
    node selection uses instant opacity (0 ms transition).
    User can still opt-in via Settings toggle.
  - All controls: keyboard-accessible (Tab, Enter, Space).
  - Animated edges: aria-hidden="true" (decorative).

PERFORMANCE (>50 nodes or >80 edges):

  1. Only animate priority-0 edges by default.
  2. Enable React Flow viewport virtualisation.
  3. React.memo on EVERY node and edge component.
  4. Memo comparator ignores: playing, speed, focusedNodeId.
  5. ONE requestAnimationFrame loop (if needed) via useAnimationEngine.
  6. Only GPU-composited properties: opacity, transform, stroke-dashoffset.
  7. Framer Motion: panels/pages ONLY. Never on canvas elements.
  8. Zero setInterval / setTimeout for animation.

### 7.6 Viewer Data Files

Generate these inside viewer/src/data/. The viewer must have access to
EVERY SINGLE generated .md file so it can render them all.

viewer/src/data/
├── specs/
│   ├── 01_product_manager.md
│   ├── 02_backend_lead.md
│   ├── 03_frontend_lead.md
│   ├── 04_db_architect.md
│   ├── 05_qa_lead.md
│   ├── 06_devops_lead.md
│   ├── 07_marketing_lead.md
│   ├── 08_finance_lead.md
│   ├── 09_business_lead.md
│   └── 10_ui_designer.md
│
├── docs/
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── backend.md
│   │   ├── frontend.md
│   │   ├── database.md
│   │   ├── security.md
│   │   ├── cloud.md
│   │   └── deep-dive.md
│   ├── workflows/
│   │   ├── development.md
│   │   ├── sprint-execution.md
│   │   ├── git-workflow.md
│   │   ├── ci-cd-pipeline.md
│   │   ├── bug-fix.md
│   │   ├── deployment.md
│   │   ├── multi-agent.md
│   │   └── qa-review.md
│   ├── environments/
│   │   ├── development.md
│   │   ├── docker.md
│   │   ├── staging.md
│   │   ├── production.md
│   │   └── environment-variables.md
│   ├── api/
│   │   ├── reference.md
│   │   ├── authentication.md
│   │   ├── error-codes.md
│   │   └── rate-limiting.md
│   ├── testing/
│   │   ├── strategy.md
│   │   ├── unit-tests.md
│   │   ├── integration-tests.md
│   │   ├── e2e-tests.md
│   │   └── test-data.md
│   ├── ui-design-system/
│   │   ├── tokens.md
│   │   ├── components.md
│   │   ├── layouts.md
│   │   ├── accessibility.md
│   │   └── icons-assets.md
│   └── project/
│       ├── setup.md
│       ├── coding-standards.md
│       └── glossary.md
│
├── backlog.json              # Parsed from specs/backlog.md into structured JSON:
│                             #   { sprints: [{ id, name, goal, tickets: [{ id, title,
│                             #     description, points, status, owner, model, deps }] }],
│                             #     bugs: [{ id, title, severity, status, sprint, notes }] }
│
├── workflows.json            # Graph definitions (per Section 7.5)
└── requirements.md           # Original SRS/PRD input documents

Import strategy: Use Vite's ?raw import for .md files so they are embedded
at build time. For .json files, use standard import.

══════════════════════════════════════════════════════════════
SECTION 8 — QUALITY GATES
══════════════════════════════════════════════════════════════

Every generated file must:

  ✓ Be SPECIFIC to this project — no "[insert here]" placeholders.
  ✓ Cross-reference other files by name (e.g., "See specs/02_backend_lead.md").
  ✓ Use consistent naming across all files.
  ✓ Contain concrete examples (real endpoint paths, real table names).

Specs: 300–800 lines each.
Docs: 100–300 lines each.
Viewer: must build with zero TypeScript errors (strict mode).

══════════════════════════════════════════════════════════════
BEGIN GENERATION
══════════════════════════════════════════════════════════════

Read all documents in SRS/.
Generate every file listed above.
Start now.