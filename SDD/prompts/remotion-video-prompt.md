# Remotion Video Prompt
## 90-Second Project Overview Video

---

## Overview

Generate a 90-second (30fps, ~2700 frames) animated video using **Remotion** (React video framework) showing the Overwatch Queue Notifier project.

**Output**: `.mp4` video, 1920×1080, 30fps, <50MB

---

## Scene-by-Scene Breakdown (13 scenes, 6–8 seconds each)

### Scene 1: Title Card (0–6s)

```tsx
<div style={{ backgroundColor: '#1e1e2e', width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
  <h1 style={{ color: '#00ff00', fontSize: 72, fontWeight: 'bold' }}>Overwatch Queue Notifier</h1>
  <p style={{ color: '#888', fontSize: 36 }}>AI-Powered Game Detection</p>
  <p style={{ color: '#666', fontSize: 24 }}>Windows Desktop App</p>
</div>
```

**Animation**: Fade in (0–1s), hold text (1–5.5s), fade out (5.5–6s)
**Background**: Dark terminal theme (#1e1e2e)
**Font**: Monospace green (#00ff00)

---

### Scene 2: Problem Statement (6–13s)

```tsx
<div style={{ backgroundColor: '#0d1117', padding: 60, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
  <h2 style={{ color: '#ff4444', fontSize: 56, marginBottom: 40 }}>The Problem</h2>
  <div style={{ color: '#ccc', fontSize: 32, lineHeight: 1.8 }}>
    <p>❌ Queue in Overwatch 2...</p>
    <p>❌ Miss notifications...</p>
    <p>❌ Game starts without you</p>
  </div>
</div>
```

**Animation**: Fade in (6–6.5s), hold (6.5–12.5s), fade out (12.5–13s)
**Elements appear sequentially**: 
- Title "The Problem" (100ms stagger)
- "❌ Queue..." (300ms)
- "❌ Miss..." (600ms)
- "❌ Game..." (900ms)

---

### Scene 3: Solution Overview (13–19s)

```tsx
<div style={{ backgroundColor: '#0d1117', padding: 60, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
  <h2 style={{ color: '#00ff00', fontSize: 56, marginBottom: 40 }}>The Solution</h2>
  <div style={{ color: '#ccc', fontSize: 32, lineHeight: 1.8 }}>
    <p>✅ 24/7 AI screen monitoring</p>
    <p>✅ Instant detection (<1 second)</p>
    <p>✅ Desktop & Discord notifications</p>
  </div>
</div>
```

**Animation**: Similar to Scene 2, but green checkmarks

---

### Scene 4: Architecture Diagram (19–26s)

**Visual**: ASCII-style boxes and arrows (render as SVG)

```tsx
<svg width={1920} height={1080} style={{ backgroundColor: '#1e1e2e' }}>
  {/* Screen Capture Box */}
  <rect x={100} y={150} width={300} height={100} fill="#4444ff" stroke="#00ff00" strokeWidth={2} />
  <text x={250} y={210} textAnchor="middle" fill="#fff" fontSize={20}>Screen Capture</text>

  {/* Arrow */}
  <line x1={400} y1={200} x2={500} y2={200} stroke="#00ff00" strokeWidth={3} markerEnd="url(#arrowhead)" />

  {/* Gate Filter */}
  <rect x={500} y={150} width={300} height={100} fill="#ffff00" stroke="#00ff00" strokeWidth={2} />
  <text x={650} y={210} textAnchor="middle" fill="#000" fontSize={20}>Gate Filter</text>

  {/* Arrow */}
  <line x1={800} y1={200} x2={900} y2={200} stroke="#00ff00" strokeWidth={3} />

  {/* AI Classifier */}
  <rect x={900} y={150} width={300} height={100} fill="#ff6600" stroke="#00ff00" strokeWidth={2} />
  <text x={1050} y={210} textAnchor="middle" fill="#fff" fontSize={20}>AI Classifier</text>

  {/* Arrow */}
  <line x1={1200} y1={200} x2={1300} y2={200} stroke="#00ff00" strokeWidth={3} />

  {/* Notification */}
  <rect x={1300} y={150} width={300} height={100} fill="#ff4444" stroke="#00ff00" strokeWidth={2} />
  <text x={1450} y={210} textAnchor="middle" fill="#fff" fontSize={20}>Notify User</text>

  {/* Bottom labels */}
  <text x={250} y={350} textAnchor="middle" fill="#ccc" fontSize={18}>Windows GDI</text>
  <text x={650} y={350} textAnchor="middle" fill="#ccc" fontSize={18}>Pixel Motion Detect</text>
  <text x={1050} y={350} textAnchor="middle" fill="#ccc" fontSize={18}>ONNX Model (5MB)</text>
  <text x={1450} y={350} textAnchor="middle" fill="#ccc" fontSize={18}>Desktop + Discord</text>

  {/* Latency labels */}
  <text x={450} y={120} fill="#00ff00" fontSize={16}>50ms</text>
  <text x={850} y={120} fill="#00ff00" fontSize={16}>150ms</text>
  <text x={1250} y={120} fill="#00ff00" fontSize={16}>200ms</text>

  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
      <polygon points="0 0, 10 5, 0 10" fill="#00ff00" />
    </marker>
  </defs>
</svg>
```

**Animation**: 
- Fade in entire diagram (19–19.5s)
- Highlight each box sequentially (19.5–22s): blue → yellow → orange → red
- Arrows animate left-to-right with latency labels
- Hold full diagram (22–25.5s)
- Fade out (25.5–26s)

---

### Scene 5: Tech Stack (26–32s)

**Left column: Frontend**
```tsx
<div style={{ position: 'absolute', left: 100, top: 100 }}>
  <h3 style={{ color: '#00ff00', fontSize: 36 }}>Frontend</h3>
  <ul style={{ color: '#ccc', fontSize: 28 }}>
    <li>🖥️ Electron 28</li>
    <li>⚛️ React 18</li>
    <li>💾 Zustand</li>
    <li>🎨 Tailwind CSS</li>
  </ul>
</div>
```

**Right column: Backend**
```tsx
<div style={{ position: 'absolute', right: 100, top: 100 }}>
  <h3 style={{ color: '#ff6600', fontSize: 36 }}>Backend</h3>
  <ul style={{ color: '#ccc', fontSize: 28 }}>
    <li>🐍 Python 3.11</li>
    <li>🤖 ONNX Runtime</li>
    <li>💿 SQLite</li>
    <li>📡 MCP Server</li>
  </ul>
</div>
```

**Animation**: Fade in (26–26.5s), hold (26.5–31.5s), fade out (31.5–32s)
**Left side**: Slide in from left (26–27s)
**Right side**: Slide in from right (26–27s)

---

### Scene 6: Real-Time Demo (32–45s)

**Show mock desktop interface**

```tsx
<div style={{ backgroundColor: '#fff', width: 800, height: 600, margin: '60px auto', borderRadius: 8, overflow: 'hidden', boxShadow: '0 10px 40px rgba(0,0,0,0.5)' }}>
  {/* Desktop window title bar */}
  <div style={{ backgroundColor: '#333', padding: 12, color: '#fff', fontSize: 16 }}>
    Overwatch Queue Notifier
  </div>

  {/* Main content */}
  <div style={{ padding: 40, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 'calc(100% - 50px)' }}>
    {/* State indicator */}
    <div style={{ fontSize: 64, fontWeight: 'bold', marginBottom: 30, color: stateColor }}>
      QUEUE
    </div>

    {/* Confidence bar */}
    <div style={{ width: '60%', height: 30, backgroundColor: '#eee', borderRadius: 4, overflow: 'hidden', marginBottom: 30 }}>
      <div style={{ width: confidenceWidth, height: '100%', backgroundColor: '#00ff00', transition: 'width 0.3s' }} />
    </div>

    {/* Status text */}
    <p style={{ color: '#666', fontSize: 18 }}>Monitoring Overwatch 2...</p>
  </div>
</div>
```

**Animation sequence**:
- Window appears (32–32.5s)
- State shows "QUEUE" (32.5–37s)
- Confidence bar at 95% (green)
- Text: "Monitoring Overwatch 2..."
- At 37s: State changes to "LOADING" (yellow), confidence drops to 70%
- At 40s: State changes to "MATCH FOUND!" (red/green), confidence 92%
- Toast notification appears in corner (animated slide-in)
- Hold final state (40–44.5s)
- Fade out (44.5–45s)

---

### Scene 7: Notification Examples (45–51s)

**Split screen: Desktop + Discord**

```tsx
<div style={{ display: 'flex', gap: 40, padding: 40 }}>
  {/* Desktop Toast */}
  <div style={{ flex: 1 }}>
    <p style={{ color: '#00ff00', fontSize: 28, marginBottom: 20 }}>Desktop Notification</p>
    <div style={{ backgroundColor: '#333', padding: 20, borderRadius: 4, border: '2px solid #00ff00' }}>
      <p style={{ color: '#fff', fontSize: 20, margin: 0 }}>🎮 MATCH FOUND!</p>
      <p style={{ color: '#888', fontSize: 16, margin: '8px 0 0 0' }}>Confidence: 92%</p>
    </div>
  </div>

  {/* Discord Embed */}
  <div style={{ flex: 1 }}>
    <p style={{ color: '#5865f2', fontSize: 28, marginBottom: 20 }}>Discord Webhook</p>
    <div style={{ backgroundColor: '#2c2f33', padding: 20, borderLeft: '4px solid #5865f2', borderRadius: 4 }}>
      <p style={{ color: '#fff', fontSize: 18, margin: 0 }}>Overwatch Queue</p>
      <p style={{ color: '#dcddde', fontSize: 14, margin: '8px 0 0 0' }}>🎮 MATCH FOUND! (92%)</p>
      <p style={{ color: '#888', fontSize: 12, margin: '4px 0 0 0' }}>Detection time: 450ms</p>
    </div>
  </div>
</div>
```

**Animation**:
- Fade in (45–45.5s)
- Desktop toast: Slide down (45.5–46s)
- Discord embed: Pulse animation (46–48s)
- Hold both (48–50.5s)
- Fade out (50.5–51s)

---

### Scene 8: Performance Metrics (51–57s)

**Display key metrics on a dashboard-style layout**

```tsx
<div style={{ backgroundColor: '#0d1117', padding: 60, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 40 }}>
  <Metric title="Latency" value="<1s" unit="end-to-end" color="#00ff00" />
  <Metric title="Accuracy" value="92%" unit="match detection" color="#00ff00" />
  <Metric title="Inference" value="<150ms" unit="AI per-frame" color="#00ff00" />
  <Metric title="Memory" value="45MB" unit="total footprint" color="#00ff00" />
  <Metric title="CPU" value="<5%" unit="idle load" color="#00ff00" />
  <Metric title="FPS" value="500ms" unit="perception cycle" color="#00ff00" />
</div>
```

**Metric component**:
```tsx
function Metric({ title, value, unit, color }) {
  return (
    <div style={{ border: `2px solid ${color}`, padding: 30, borderRadius: 8, textAlign: 'center' }}>
      <p style={{ color: '#888', fontSize: 16, margin: 0 }}>{title}</p>
      <p style={{ color, fontSize: 48, fontWeight: 'bold', margin: '10px 0' }}>{value}</p>
      <p style={{ color: '#666', fontSize: 14, margin: 0 }}>{unit}</p>
    </div>
  );
}
```

**Animation**:
- Fade in (51–51.5s)
- Metric cards: Slide up from bottom with stagger (51.5–54s, 200ms delay between cards)
- Number counters: Animate from 0% to final value (51.5–54.5s)
- Hold all (54.5–56.5s)
- Fade out (56.5–57s)

---

### Scene 9: Database Overview (57–63s)

```tsx
<div style={{ backgroundColor: '#1e1e2e', padding: 40 }}>
  <h2 style={{ color: '#00ff00', fontSize: 48, marginBottom: 40 }}>Local SQLite Database</h2>
  <table style={{ color: '#ccc', fontSize: 20, borderCollapse: 'collapse', width: '100%' }}>
    <tr>
      <td style={{ border: '1px solid #00ff00', padding: 15 }}>📊 Detection History</td>
      <td style={{ border: '1px solid #00ff00', padding: 15 }}>100K+ records</td>
    </tr>
    <tr>
      <td style={{ border: '1px solid #00ff00', padding: 15 }}>🎯 Calibration Profiles</td>
      <td style={{ border: '1px solid #00ff00', padding: 15 }}>Multi-monitor support</td>
    </tr>
    <tr>
      <td style={{ border: '1px solid #00ff00', padding: 15 }}>📢 Notification Log</td>
      <td style={{ border: '1px solid #00ff00', padding: 15 }}>Sent/Failed tracking</td>
    </tr>
    <tr>
      <td style={{ border: '1px solid #00ff00', padding: 15 }}>⚙️ Settings</td>
      <td style={{ border: '1px solid #00ff00', padding: 15 }}>User preferences</td>
    </tr>
  </table>
  <p style={{ color: '#666', marginTop: 30, fontSize: 18 }}>Zero cloud dependency • Fully offline capable</p>
</div>
```

**Animation**:
- Fade in table header (57–57.5s)
- Rows animate in (row-by-row, 57.5–60s with 500ms stagger)
- Highlight gradient sweep across table (60–62s)
- Hold (62–62.5s)
- Fade out (62.5–63s)

---

### Scene 10: Deployment (63–69s)

```tsx
<div style={{ backgroundColor: '#0d1117', padding: 60, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 40 }}>
  <h2 style={{ color: '#00ff00', fontSize: 48 }}>One-Click Installation</h2>
  
  <div style={{ display: 'flex', gap: 40, alignItems: 'center' }}>
    {/* Download icon */}
    <div style={{ fontSize: 80 }}>📥</div>
    
    {/* Installer flow */}
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <Step num={1} text="Download .msi" />
      <Step num={2} text="Run installer" />
      <Step num={3} text="Launch app" />
      <Step num={4} text="Calibrate region" />
      <Step num={5} text="Enable notifications" />
    </div>
  </div>

  <p style={{ color: '#666', fontSize: 20, marginTop: 40 }}>~5 minutes total setup time</p>
</div>
```

**Step component**:
```tsx
function Step({ num, text }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
      <div style={{ width: 40, height: 40, borderRadius: '50%', backgroundColor: '#00ff00', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#000', fontWeight: 'bold', fontSize: 20 }}>{num}</div>
      <p style={{ color: '#ccc', fontSize: 24, margin: 0 }}>{text}</p>
    </div>
  );
}
```

**Animation**:
- Fade in title (63–63.5s)
- Download icon: Rotate (63.5–64s)
- Steps: Slide in from left with stagger (64–66s, 300ms delay)
- Setup time text: Fade in (66–66.5s)
- Hold all (66.5–68.5s)
- Fade out (68.5–69s)

---

### Scene 11: Development (69–75s)

```tsx
<div style={{ backgroundColor: '#1e1e2e', padding: 60 }}>
  <h2 style={{ color: '#ff6600', fontSize: 48, marginBottom: 40 }}>Open Source Development</h2>
  
  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 40, fontSize: 20, color: '#ccc' }}>
    <div>
      <p style={{ color: '#00ff00', fontWeight: 'bold' }}>🔧 Built With</p>
      <ul>
        <li>Electron + React (Frontend)</li>
        <li>Python 3.11 (Backend)</li>
        <li>ONNX Runtime (AI)</li>
        <li>GitHub Actions (CI/CD)</li>
      </ul>
    </div>
    
    <div>
      <p style={{ color: '#00ff00', fontWeight: 'bold' }}>📚 Well-Documented</p>
      <ul>
        <li>Full architecture specs</li>
        <li>API reference</li>
        <li>Development workflows</li>
        <li>Test strategies</li>
      </ul>
    </div>
  </div>
</div>
```

**Animation**:
- Fade in title (69–69.5s)
- Left column: Fade & slide up (69.5–71s)
- Right column: Fade & slide up (71–72.5s)
- Hold both (72.5–74.5s)
- Fade out (74.5–75s)

---

### Scene 12: Call-to-Action (75–85s)

```tsx
<div style={{ backgroundColor: '#0d1117', width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: 40 }}>
  <h1 style={{ color: '#00ff00', fontSize: 64, textAlign: 'center' }}>Get Started Today</h1>
  
  <div style={{ display: 'flex', gap: 40, fontSize: 24, color: '#ccc' }}>
    <a style={{ color: '#00ff00', textDecoration: 'none', cursor: 'pointer' }}>👉 github.com/overwatch-queue-notifier</a>
  </div>

  <div style={{ marginTop: 40, fontSize: 20, color: '#666', textAlign: 'center', maxWidth: 800 }}>
    <p>Never miss another match.</p>
    <p>AI-powered detection. Instant notifications.</p>
    <p>Free. Open source. Yours.</p>
  </div>
</div>
```

**Animation**:
- Fade in main heading (75–75.5s)
- GitHub link: Pulse & glow effect (75.5–78s)
- Bottom text: Fade in line-by-line (78–82s, 1s per line)
- Pulse entire call-to-action (82–84.5s)
- Hold (84.5–85s)

---

### Scene 13: End Credits (85–90s)

```tsx
<div style={{ backgroundColor: '#1e1e2e', width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
  <div style={{ color: '#ccc', fontSize: 24, textAlign: 'center', lineHeight: 2 }}>
    <p>Created with ❤️ using AutoSpec</p>
    <p>Remotion React Video Framework</p>
    <p style={{ marginTop: 40, color: '#888' }}>© 2024 Overwatch Queue Notifier</p>
  </div>
</div>
```

**Animation**:
- Fade in credits (85–85.5s)
- Hold (85.5–89.5s)
- Final fade to black (89.5–90s)

---

## Technical Specs

**Remotion Configuration**:

```tsx
// remotion/config.ts
import { Config } from "remotion";

Config.setVideoImageFormat("png");
Config.setFramerate(30);
Config.setDurationInFrames(2700); // 90 seconds at 30fps
Config.setHeight(1080);
Config.setWidth(1920);
```

**Color Palette** (From design tokens):

```
- Primary: #00ff00 (terminal green)
- Secondary: #ff6600 (orange)
- Error: #ff4444 (red)
- Background: #0d1117 (dark)
- Text: #ccc (light gray)
- Accent: #4444ff (blue)
- Alert: #ffff00 (yellow)
```

**Fonts**:
- Heading: Courier New, monospace, bold
- Body: system-ui, monospace

---

## Compilation Command

```bash
npx remotion render path/to/Composition.tsx output.mp4 --props '{"fps": 30}'
```

**Output**: `output.mp4` (1920×1080, H.264, 30fps, ~30–50MB)

---

## Optional: Branching Versions

1. **Short version** (45s): Scenes 1–7 (Problem → Solution → Demo)
2. **Full version** (90s): All 13 scenes (above)
3. **Developer version** (120s): Add Scene 11 expanded (code walkthroughs)

---

## Usage

1. Create `remotion/` folder in project root
2. Copy scene components above into `remotion/Composition.tsx`
3. Run: `npx remotion serve` (preview)
4. Export: `npx remotion render Composition.tsx output.mp4`
5. Upload to YouTube / GitHub Releases

Result: Professional, polished project overview video that showcases the entire product in 90 seconds.
