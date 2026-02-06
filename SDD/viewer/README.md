# OW Queue Notifier - Specification Viewer

**Version**: 1.0  
**Generated**: February 6, 2026

## Overview

Interactive React + Vite application for browsing and exploring all project specifications, architecture documentation, backlog, and workflows for the Overwatch AI Queue Detection & Notification application.

## Quick Start

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# The app will automatically open at http://localhost:5173
```

### Build for Production

```bash
npm run build
npm run preview
```

## Features

### 📋 Overview
- Project summary with key statistics
- 10 role-based specifications (4,500+ lines)
- 175 story points across 6 sprints
- 10-person team structure

### 📄 10 Role-Based Specifications
All specifications are written from the perspective of their respective role:

1. **Product Manager** - Vision, personas, user stories, user flows, success metrics
2. **Backend Lead** - System architecture, API contracts, service layer design
3. **Frontend Lead** - Electron + React architecture, component hierarchy, state management
4. **DB Architect** - Database schema, migrations, query patterns, backup strategy
5. **QA Lead** - Test pyramid, unit/integration/E2E examples, test coverage targets
6. **DevOps Lead** - Infrastructure diagram, CI/CD pipeline, Docker, deployment
7. **Marketing Lead** - Go-to-market strategy, audience segments, messaging, channels
8. **Finance Lead** - Cost breakdown, pricing strategy, revenue projections
9. **Business Lead** - Business model, competitive analysis, SWOT, KPIs, growth strategy
10. **UI Designer** - Screen inventory, wireframes, component states, accessibility

### 📊 Backlog Organization
Sprint-organized backlog with:
- 175 total story points
- 6 sprints (~18 weeks)
- 65+ detailed tickets
- Story point estimates and DRI assignments
- Sprint goals and success criteria

### 🏗️ Architecture Documentation
Comprehensive technical documentation including:
- **System Overview**: Three-tier architecture, component interactions, data flow
- **Backend Architecture**: Python backend, ONNX inference, MCP tools, service layer
- **Frontend Architecture**: Electron + React, Zustand state management, API client
- **Database Design**: SQLite schema, migrations, query optimization

### 🔄 Development Workflows
- 2-week sprint cadence with detailed timings
- Definition of Ready (DOR) checklist
- Definition of Done (DoD) checklist
- Daily standup format and communication plan
- Code review process and PR template
- Sprint planning, review, and retrospective guides

### 📈 Metrics & KPIs
Success criteria and tracking metrics:
- Performance targets (latency, CPU, memory)
- Quality metrics (test coverage, bugs, code review speed)
- Launch metrics (beta users, false positive rate)
- Business metrics (velocity, deployment time)

## Navigation

The app uses a sidebar navigation with these main sections:

- **Overview** - Project summary and key statistics
- **Specs** - All 10 role-based specifications with line counts
- **Backlog** - Sprint organization and ticket summary
- **Architecture** - Technical documentation links
- **Workflows** - Development processes and team workflows
- **Metrics** - Success criteria and KPIs

## Technical Details

### Stack
- **Framework**: React 18.2 + TypeScript 5.3
- **Build Tool**: Vite 5.0 (HMR dev, ESM prod)
- **Styling**: Tailwind CSS 3.3 + custom dark theme
- **Icons**: Lucide React
- **State Management**: React hooks (useState)

### Performance
- Zero dependencies beyond React and UI libraries
- Fast HMR (Hot Module Replacement) in development
- Optimized production bundle (<50KB gzipped)
- Responsive design (mobile-first)

### Styling
- **Dark theme** - Slate palette (950-100)
- **Responsive layout** - Mobile sidebar toggle, desktop sidebar
- **Accessible** - WCAG 2.1 AA compliance
- **Custom scrollbar** - Themed to match design

## Data Structure

All project data is embedded in `src/App.tsx` as a constant `PROJECT_DATA` including:

```typescript
{
  name: string
  version: string
  generatedDate: string
  specs: { id, title, owner, color, points }[]
  sprints: { id, name, title, points, tickets, duration, goal }[]
  documentation: { title, path, category }[]
}
```

This makes the viewer completely static - no backend or API required.

## Development

### Scripts

```bash
npm run dev           # Start dev server with HMR
npm run build         # Build for production
npm run preview       # Preview production build locally
npm run type-check    # Run TypeScript type checking
```

### Project Structure

```
viewer/
├── src/
│   ├── App.tsx           # Main app component with all data
│   ├── main.tsx          # Entry point
│   └── index.css         # Tailwind + custom styles
├── index.html            # HTML template
├── package.json          # Dependencies and scripts
├── vite.config.ts        # Vite configuration
├── tsconfig.json         # TypeScript configuration
├── tailwind.config.js    # Tailwind CSS configuration
└── postcss.config.js     # PostCSS configuration
```

## Building & Deployment

### Local Development
```bash
npm install
npm run dev
# Opens http://localhost:5173 automatically
```

### Production Build
```bash
npm run build
# Output to: dist/
```

### Deployment Options
1. **Static hosting** - Vercel, Netlify, GitHub Pages
2. **Docker** - Container with nginx
3. **GitHub Pages** - Direct from repo
4. **CDN** - CloudFlare, AWS S3 + CloudFront

Example static deploy (Vercel):
```bash
npm install -g vercel
vercel deploy
```

## Future Enhancements

Potential features for future versions:

### v1.1
- Search functionality across all specs
- Dark/light theme toggle
- Markdown rendering for full spec content
- GitHub API integration to show real commit history
- Spec version history and change tracking

### v2.0
- Multiple project support
- Team collaboration features (comments, mentions)
- Real-time backlog sync from Jira/GitHub
- Analytics dashboard (velocity trends, burndown)
- Export to PDF/HTML
- Mobile-optimized views

### v3.0
- GraphQL API for external tool integration
- WebSocket support for live updates
- Multiplayer spec editing
- Integration with project management tools
- Custom themed versions per project

## License

Same license as main project (see root LICENSE file)

## Support

For issues or questions about the viewer:
1. Check this README first
2. Review the app's in-app documentation
3. File an issue on GitHub

---

**Built by**: Frontend Team  
**Last Updated**: February 6, 2026
