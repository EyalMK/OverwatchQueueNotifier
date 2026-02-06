import React, { useState } from 'react';
import { ChevronDown, Menu, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Mock data structure for specs and backlog
const PROJECT_DATA = {
  name: 'Overwatch AI Queue Detection & Notification App',
  version: '1.0',
  generatedDate: 'February 6, 2026',
  specs: [
    { id: 1, title: 'Product Manager', owner: 'PM', color: 'blue', points: 400 },
    { id: 2, title: 'Backend Lead', owner: 'Backend', color: 'green', points: 500 },
    { id: 3, title: 'Frontend Lead', owner: 'Frontend', color: 'purple', points: 450 },
    { id: 4, title: 'DB Architect', owner: 'DB', color: 'red', points: 450 },
    { id: 5, title: 'QA Lead', owner: 'QA', color: 'yellow', points: 500 },
    { id: 6, title: 'DevOps Lead', owner: 'DevOps', color: 'pink', points: 550 },
    { id: 7, title: 'Marketing Lead', owner: 'Marketing', color: 'indigo', points: 550 },
    { id: 8, title: 'Finance Lead', owner: 'Finance', color: 'cyan', points: 500 },
    { id: 9, title: 'Business Lead', owner: 'Business', color: 'lime', points: 550 },
    { id: 10, title: 'UI Designer', owner: 'Design', color: 'rose', points: 450 },
  ],
  sprints: [
    {
      id: 0,
      name: 'Sprint 0',
      title: 'Project Foundation',
      points: 26,
      tickets: 10,
      duration: 'Weeks 1-2',
      goal: 'Achieve working development environment, architecture decisions locked',
    },
    {
      id: 1,
      name: 'Sprint 1',
      title: 'Backend Core + Architecture',
      points: 38,
      tickets: 12,
      duration: 'Weeks 3-5',
      goal: 'AI perception layer complete, API contracts implemented',
    },
    {
      id: 2,
      name: 'Sprint 2',
      title: 'Frontend Scaffold + Calibration',
      points: 31,
      tickets: 11,
      duration: 'Weeks 6-8',
      goal: 'Electron app boots, Settings modal complete',
    },
    {
      id: 3,
      name: 'Sprint 3',
      title: 'Backend-Frontend Integration',
      points: 28,
      tickets: 12,
      duration: 'Weeks 9-11',
      goal: 'Notifications flow end-to-end, Discord integration tested',
    },
    {
      id: 4,
      name: 'Sprint 4',
      title: 'Testing, Optimization + Beta Prep',
      points: 27,
      tickets: 10,
      duration: 'Weeks 12-14',
      goal: '75%+ test coverage, sub-50ms latency validated',
    },
    {
      id: 5,
      name: 'Sprint 5',
      title: 'Beta Launch + Community',
      points: 24,
      tickets: 9,
      duration: 'Weeks 15-17',
      goal: 'Beta version shipped to 50-100 users',
    },
    {
      id: 6,
      name: 'Sprint 6',
      title: 'General Release',
      points: 26,
      tickets: 10,
      duration: 'Weeks 18-22',
      goal: 'v1.0 stable release, public announcement',
    },
  ],
  documentation: [
    { title: 'System Architecture Overview', path: 'docs/architecture/01_system_overview.md', category: 'Architecture' },
    { title: 'Backend Architecture', path: 'docs/architecture/02_backend.md', category: 'Architecture' },
    { title: 'Frontend Architecture', path: 'docs/architecture/03_frontend.md', category: 'Architecture' },
    { title: 'Sprint Execution Workflow', path: 'docs/workflows/01_sprint_execution.md', category: 'Workflows' },
  ],
};

// Components
function Sidebar({ activeView, onViewChange, isOpen, onToggle }: any) {
  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={onToggle}
        className="lg:hidden fixed top-4 left-4 z-40 p-2 bg-slate-800 rounded text-white"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      <aside
        className={`fixed lg:relative w-64 h-screen bg-slate-900 border-r border-slate-700 p-6 overflow-y-auto transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="mb-8">
          <h1 className="text-xl font-bold text-white truncate">OW Queue</h1>
          <p className="text-xs text-slate-400 mt-1">v1.0 Specification</p>
        </div>

        <nav className="space-y-2">
          {[
            { id: 'overview', label: '📋 Overview', icon: '📋' },
            { id: 'specs', label: '📄 10 Role Specs', icon: '📄' },
            { id: 'backlog', label: '📊 Backlog (175pts)', icon: '📊' },
            { id: 'architecture', label: '🏗️ Architecture', icon: '🏗️' },
            { id: 'workflows', label: '🔄 Workflows', icon: '🔄' },
            { id: 'documentation', label: '📚 Documentation', icon: '📚' },
            { id: 'metrics', label: '📈 Metrics', icon: '📈' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => {
                onViewChange(item.id);
                onToggle();
              }}
              className={`w-full text-left px-4 py-2 rounded transition-colors ${
                activeView === item.id
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <span className="mr-2">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="mt-8 pt-6 border-t border-slate-700">
          <p className="text-xs text-slate-500">Generated: {PROJECT_DATA.generatedDate}</p>
          <p className="text-xs text-slate-500 mt-1">Total: 175 story points across 6 sprints</p>
        </div>
      </aside>
    </>
  );
}

function Overview() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">
          {PROJECT_DATA.name}
        </h2>
        <p className="text-slate-400">Complete specification-driven development framework</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Specifications"
          value="10"
          subtitle="Role-based specs"
          icon="📄"
        />
        <StatCard
          title="Total Story Points"
          value="175"
          subtitle="6 sprints planned"
          icon="📊"
        />
        <StatCard
          title="Sprints"
          value="6"
          subtitle="~18 weeks duration"
          icon="🎯"
        />
        <StatCard
          title="Team Roles"
          value="10"
          subtitle="Full-stack coverage"
          icon="👥"
        />
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Key Characteristics</h3>
        <ul className="space-y-2 text-slate-300">
          <li>✅ Windows 10/11 desktop app (Electron + React)</li>
          <li>✅ AI-powered Overwatch queue detection (&lt;50ms latency)</li>
          <li>✅ Desktop + Discord notifications</li>
          <li>✅ Local-first, privacy-preserving (no screenshots stored)</li>
          <li>✅ Single-user, calibration-based region detection</li>
          <li>✅ Complete CI/CD pipeline (GitHub Actions → MSI)</li>
          <li>✅ Freemium model (v1.0 free, v2.0 optional premium)</li>
          <li>✅ Community-driven development (open feedback loops)</li>
        </ul>
      </div>
    </div>
  );
}

function SpecsView() {
  const [expandedSpec, setExpandedSpec] = useState<number | null>(null);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-white">10 Role-Based Specifications</h2>
      <p className="text-slate-400">
        Each role writes their specification in their own expertise domain. Total: ~4,500 lines of project-specific documentation.
      </p>

      <div className="space-y-3">
        {PROJECT_DATA.specs.map((spec) => (
          <div
            key={spec.id}
            className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden hover:border-slate-600 transition-colors"
          >
            <button
              onClick={() =>
                setExpandedSpec(expandedSpec === spec.id ? null : spec.id)
              }
              className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-750"
            >
              <div className="flex-1 text-left">
                <p className="font-semibold text-white">
                  {String(spec.id).padStart(2, '0')}. {spec.title}
                </p>
                <p className="text-sm text-slate-400">{spec.owner}</p>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm text-slate-400 hidden sm:inline">
                  {spec.points} lines
                </span>
                <ChevronDown
                  size={20}
                  className={`text-slate-400 transition-transform ${
                    expandedSpec === spec.id ? 'rotate-180' : ''
                  }`}
                />
              </div>
            </button>

            {expandedSpec === spec.id && (
              <div className="px-6 py-4 bg-slate-750 border-t border-slate-700 text-slate-300 text-sm space-y-2">
                <p>
                  Comprehensive {spec.points}-line specification covering all aspects of {spec.title.toLowerCase()} responsibilities, deliverables, and technical requirements.
                </p>
                <p className="text-xs text-slate-500 pt-2">
                  📄 specs/{String(spec.id).padStart(2, '0')}_*.md
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function BacklogView() {
  const totalPoints = PROJECT_DATA.sprints.reduce(
    (sum, sprint) => sum + sprint.points,
    0
  );

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Project Backlog</h2>
        <p className="text-slate-400">
          {totalPoints} story points organized across {PROJECT_DATA.sprints.length} sprints
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {PROJECT_DATA.sprints.map((sprint) => (
          <div
            key={sprint.id}
            className="bg-slate-800 border border-slate-700 rounded-lg p-4 text-center hover:border-slate-600 transition-colors"
          >
            <p className="text-xs text-slate-400 font-semibold mb-1">S{sprint.id}</p>
            <p className="text-2xl font-bold text-blue-400">{sprint.points}</p>
            <p className="text-xs text-slate-400">{sprint.tickets} tickets</p>
          </div>
        ))}
      </div>

      {/* Detailed Sprints */}
      <div className="space-y-4">
        {PROJECT_DATA.sprints.map((sprint) => (
          <div
            key={sprint.id}
            className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <div>
                <h3 className="text-lg font-semibold text-white">{sprint.name}</h3>
                <p className="text-slate-400">{sprint.title}</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-blue-400">{sprint.points}</p>
                <p className="text-xs text-slate-400">pts</p>
              </div>
            </div>
            <p className="text-sm text-slate-300 mb-3">{sprint.goal}</p>
            <div className="flex gap-4 text-xs text-slate-400">
              <span>📅 {sprint.duration}</span>
              <span>🎫 {sprint.tickets} tickets</span>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-blue-900 border border-blue-700 rounded-lg p-4">
        <p className="text-sm text-blue-100">
          📊 <strong>Velocity Target:</strong> 25-30 story points per sprint (1 FTE)
        </p>
      </div>
    </div>
  );
}

function ArchitectureView() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Architecture Documentation</h2>
        <p className="text-slate-400">
          Comprehensive technical architecture and design documentation
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          {
            title: '🏗️ System Overview',
            description: 'Three-tier architecture, component interactions, data flow',
            icon: '🏗️',
            items: ['AI Perception Engine', 'State Machine', 'IPC Bridge', 'Database Schema'],
          },
          {
            title: '🔧 Backend Deep Dive',
            description: 'Python backend, MCP tools, service layer design',
            icon: '🔧',
            items: ['ONNX Inference', 'Gate + Classifier', 'SQLite Repositories', 'Error Handling'],
          },
          {
            title: '⚛️ Frontend Architecture',
            description: 'Electron + React, Zustand state, component hierarchy',
            icon: '⚛️',
            items: ['Electron IPC', 'React Components', 'API Client', 'Form Handling'],
          },
          {
            title: '🗄️ Database Design',
            description: 'SQLite schema, migrations, query patterns',
            icon: '🗄️',
            items: ['Tables & Indices', 'Migrations', 'Query Optimization', 'Backup Strategy'],
          },
        ].map((doc, idx) => (
          <div
            key={idx}
            className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition-colors"
          >
            <p className="text-3xl mb-2">{doc.icon}</p>
            <h3 className="font-semibold text-white mb-2">{doc.title}</h3>
            <p className="text-sm text-slate-400 mb-4">{doc.description}</p>
            <ul className="space-y-1">
              {doc.items.map((item, i) => (
                <li key={i} className="text-xs text-slate-300 flex items-center gap-2">
                  <span className="w-1 h-1 bg-blue-400 rounded-full"></span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

function WorkflowsView() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Development Workflows</h2>
        <p className="text-slate-400">
          Team processes, sprint execution, and delivery workflows
        </p>
      </div>

      <div className="space-y-4">
        {[
          {
            title: '🎯 Sprint Execution',
            description: '2-week sprint cadence with daily standups, code review, testing',
            sections: [
              { label: 'Sprint Planning', desc: 'Monday 9am, 2 hours' },
              { label: 'Daily Standup', desc: 'Tue-Thu 10am, 15 min' },
              { label: 'Code Review', desc: 'Continuous + Friday sync' },
              { label: 'Review & Retro', desc: 'Friday 3pm, 2 hours' },
            ],
          },
          {
            title: '✅ Definition of Ready',
            description: 'Criteria for picking up a ticket from the backlog',
            sections: [
              { label: 'Clear Description', desc: 'What needs to be done?' },
              { label: 'Acceptance Criteria', desc: 'Specific, testable outcomes' },
              { label: 'Story Points', desc: '1-13 scale estimation' },
              { label: 'Dependencies', desc: 'Related tickets listed' },
            ],
          },
          {
            title: '✔️ Definition of Done',
            description: 'Criteria for marking a ticket complete',
            sections: [
              { label: 'Code Complete', desc: 'Per acceptance criteria' },
              { label: 'Tests Written', desc: '≥75% coverage' },
              { label: 'Code Review', desc: '≥1 approval required' },
              { label: 'Merged to Main', desc: 'All CI/CD checks pass' },
            ],
          },
        ].map((workflow, idx) => (
          <div
            key={idx}
            className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden hover:border-slate-600 transition-colors"
          >
            <div className="px-6 py-4 bg-slate-750">
              <h3 className="text-lg font-semibold text-white">{workflow.title}</h3>
              <p className="text-sm text-slate-400">{workflow.description}</p>
            </div>
            <div className="px-6 py-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {workflow.sections.map((section, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <span className="text-xs font-semibold text-blue-400 whitespace-nowrap">
                      {section.label}
                    </span>
                    <p className="text-xs text-slate-400">{section.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MetricsView() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Project Metrics & KPIs</h2>
        <p className="text-slate-400">
          Success criteria and tracking metrics across all dimensions
        </p>
      </div>

      {/* Performance Targets */}
      <div className="space-y-4">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">⚡ Performance Targets</h3>
          <div className="space-y-3">
            {[
              { metric: 'Detection Latency (p95)', target: '<100ms', current: '48ms ✅' },
              { metric: 'CPU Usage Sustained', target: '<10%', current: '~8%' },
              { metric: 'Memory Peak', target: '<150MB', current: '120-125MB' },
              { metric: 'Startup Time', target: '<2s', current: 'TBD (Sprint 2)' },
              { metric: 'False Positives', target: '<5%', current: 'TBD (Beta)' },
            ].map((item, idx) => (
              <div key={idx} className="flex justify-between items-center pb-2 border-b border-slate-700">
                <span className="text-slate-300">{item.metric}</span>
                <div className="text-right">
                  <p className="text-sm font-semibold text-blue-400">{item.target}</p>
                  <p className="text-xs text-slate-500">{item.current}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quality Metrics */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">🧪 Quality Metrics</h3>
          <div className="space-y-3">
            {[
              { metric: 'Test Coverage', target: '≥75%', sprint: 'Sprint 4' },
              { metric: 'Critical Bugs', target: '0', sprint: 'Always' },
              { metric: 'Code Review Time', target: '<24h', sprint: 'Every sprint' },
              { metric: 'Accessibility (WCAG)', target: 'AA', sprint: 'Sprint 4' },
            ].map((item, idx) => (
              <div key={idx} className="flex justify-between items-center pb-2 border-b border-slate-700">
                <span className="text-slate-300">{item.metric}</span>
                <div className="text-right">
                  <p className="text-sm font-semibold text-green-400">{item.target}</p>
                  <p className="text-xs text-slate-500">Due: {item.sprint}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Business Metrics */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">📊 Launch Metrics</h3>
          <div className="space-y-3">
            {[
              { metric: 'Beta Users (v0.1)', target: '50-100', phase: 'Sprint 5' },
              { metric: 'False Positive Rate', target: '<5%', phase: 'Sprint 5' },
              { metric: 'Crash-Free Hours', target: '>99%', phase: 'Beta' },
              { metric: 'v1.0 Release', target: 'Week 18', phase: 'Sprint 6' },
            ].map((item, idx) => (
              <div key={idx} className="flex justify-between items-center pb-2 border-b border-slate-700">
                <span className="text-slate-300">{item.metric}</span>
                <div className="text-right">
                  <p className="text-sm font-semibold text-yellow-400">{item.target}</p>
                  <p className="text-xs text-slate-500">{item.phase}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function DocumentationView() {
  const [selectedDoc, setSelectedDoc] = useState(PROJECT_DATA.documentation[0]);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    const loadMarkdown = async () => {
      try {
        setLoading(true);
        setError(null);
        // Try loading from the public directory first
        const response = await fetch(`/${selectedDoc.path}`);
        if (!response.ok) {
          throw new Error(`Failed to load: ${selectedDoc.title}`);
        }
        const text = await response.text();
        setContent(text);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load documentation');
        setContent('');
      } finally {
        setLoading(false);
      }
    };

    loadMarkdown();
  }, [selectedDoc]);

  const categories = Array.from(new Set(PROJECT_DATA.documentation.map(doc => doc.category)));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">📚 Documentation</h1>
        <p className="text-slate-400">Browse architecture, workflows, and implementation guides</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar - Documentation List */}
        <div className="lg:col-span-1">
          <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden sticky top-6">
            <div className="bg-slate-900 px-4 py-3 border-b border-slate-700">
              <h3 className="text-sm font-semibold text-white">Documentation</h3>
            </div>
            <div className="p-2 max-h-96 overflow-y-auto">
              {categories.map((category) => (
                <div key={category}>
                  <p className="text-xs font-semibold text-slate-400 uppercase px-3 py-2 mt-2">{category}</p>
                  {PROJECT_DATA.documentation
                    .filter(doc => doc.category === category)
                    .map((doc, idx) => (
                      <button
                        key={idx}
                        onClick={() => setSelectedDoc(doc)}
                        className={`w-full text-left text-sm px-3 py-2 rounded transition-colors ${
                          selectedDoc.title === doc.title
                            ? 'bg-blue-600 text-white'
                            : 'text-slate-300 hover:bg-slate-700'
                        }`}
                      >
                        {doc.title}
                      </button>
                    ))}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content - Markdown Viewer */}
        <div className="lg:col-span-3">
          <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
            <div className="bg-slate-900 px-6 py-4 border-b border-slate-700">
              <h2 className="text-lg font-semibold text-white">{selectedDoc.title}</h2>
              <p className="text-xs text-slate-400 mt-1">{selectedDoc.path}</p>
            </div>
            <div className="p-6 max-h-96 overflow-y-auto prose prose-invert max-w-none">
              {loading && (
                <div className="text-center py-8">
                  <p className="text-slate-400">Loading...</p>
                </div>
              )}
              {error && (
                <div className="bg-red-900 border border-red-700 rounded-lg p-4 text-red-100">
                  <p className="font-semibold">Error loading documentation</p>
                  <p className="text-sm mt-1">{error}</p>
                  <p className="text-xs text-red-300 mt-2">
                    Make sure the markdown files are copied to the public/ directory.
                  </p>
                </div>
              )}
              {!loading && !error && content && (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({ children }) => <h1 className="text-2xl font-bold text-white mt-6 mb-4">{children}</h1>,
                    h2: ({ children }) => <h2 className="text-xl font-bold text-white mt-5 mb-3">{children}</h2>,
                    h3: ({ children }) => <h3 className="text-lg font-bold text-white mt-4 mb-2">{children}</h3>,
                    p: ({ children }) => <p className="text-slate-300 mb-4 leading-relaxed">{children}</p>,
                    ul: ({ children }) => <ul className="list-disc list-inside text-slate-300 mb-4 space-y-1">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-inside text-slate-300 mb-4 space-y-1">{children}</ol>,
                    li: ({ children }) => <li className="text-slate-300">{children}</li>,
                    code: ({ inline, children }: any) =>
                      inline ? (
                        <code className="bg-slate-900 text-amber-300 px-2 py-1 rounded text-sm">{children}</code>
                      ) : (
                        <pre className="bg-slate-900 rounded-lg p-4 overflow-x-auto mb-4">
                          <code className="text-amber-300 text-sm">{children}</code>
                        </pre>
                      ),
                    table: ({ children }) => <table className="border-collapse border border-slate-600 mb-4">{children}</table>,
                    th: ({ children }) => <th className="border border-slate-600 px-4 py-2 bg-slate-900 text-white">{children}</th>,
                    td: ({ children }) => <td className="border border-slate-600 px-4 py-2 text-slate-300">{children}</td>,
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-4 border-blue-500 pl-4 py-2 text-slate-400 italic mb-4">{children}</blockquote>
                    ),
                    a: ({ href, children }) => (
                      <a href={href} className="text-blue-400 hover:text-blue-300 underline">{children}</a>
                    ),
                  }}
                >
                  {content}
                </ReactMarkdown>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, subtitle, icon }: any) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition-colors">
      <p className="text-3xl mb-2">{icon}</p>
      <p className="text-sm text-slate-400 mb-1">{title}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-xs text-slate-500 mt-1">{subtitle}</p>
    </div>
  );
}

// Main App
export default function App() {
  const [activeView, setActiveView] = useState('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const renderView = () => {
    switch (activeView) {
      case 'overview':
        return <Overview />;
      case 'specs':
        return <SpecsView />;
      case 'backlog':
        return <BacklogView />;
      case 'architecture':
        return <ArchitectureView />;
      case 'workflows':
        return <WorkflowsView />;
      case 'documentation':
        return <DocumentationView />;
      case 'metrics':
        return <MetricsView />;
      default:
        return <Overview />;
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-white overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto p-6 lg:p-8">
          <div className="mt-12 lg:mt-0">
            {renderView()}
          </div>
        </div>
      </main>

      {/* Background Pattern */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-950 to-slate-950"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-900 rounded-full opacity-5 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-purple-900 rounded-full opacity-5 blur-3xl"></div>
      </div>
    </div>
  );
}
