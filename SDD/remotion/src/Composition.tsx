import React from "react";
import {
  AbsoluteFill,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
} from "remotion";

// ============= SCENE COMPONENTS =============

// Scene 1: Title Card (0–6s)
const Scene1TitleCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeInOpacity = interpolate(frame, [0, 30], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [150, 180], [1, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#1e1e2e" }}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          height: "100%",
          opacity: fadeInOpacity * fadeOutOpacity,
        }}
      >
        <h1 style={{ color: "#00ff00", fontSize: 72, fontWeight: "bold", margin: 0 }}>
          Overwatch Queue Notifier
        </h1>
        <p style={{ color: "#888", fontSize: 36, margin: "20px 0 0 0" }}>
          AI-Powered Game Detection
        </p>
        <p style={{ color: "#666", fontSize: 24, margin: "10px 0 0 0" }}>
          Windows Desktop App
        </p>
      </div>
    </AbsoluteFill>
  );
};

// Scene 2: Problem Statement (6–13s)
const Scene2Problem: React.FC = () => {
  const frame = useCurrentFrame();
  
  const fadeInOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [180, 210], [1, 0], { extrapolateRight: "clamp" });

  const problemOffset = interpolate(
    frame,
    [0, 5, 15],
    [0, 0, 0],
    { easing: Easing.out(Easing.ease) }
  );

  const items = [
    { icon: "❌", text: "Queue in Overwatch 2..." },
    { icon: "❌", text: "Miss notifications..." },
    { icon: "❌", text: "Game starts without you" },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: "#0d1117" }}>
      <div
        style={{
          padding: 60,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          height: "100%",
          opacity: fadeInOpacity * fadeOutOpacity,
        }}
      >
        <h2 style={{ color: "#ff4444", fontSize: 56, marginBottom: 40 }}>The Problem</h2>
        <div style={{ color: "#ccc", fontSize: 32, lineHeight: 1.8 }}>
          {items.map((item, index) => {
            const itemOpacity = interpolate(
              frame,
              [15 + index * 9, 24 + index * 9],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            return (
              <p key={index} style={{ margin: "10px 0", opacity: itemOpacity }}>
                {item.icon} {item.text}
              </p>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Scene 3: Solution Overview (13–19s)
const Scene3Solution: React.FC = () => {
  const frame = useCurrentFrame();
  
  const fadeInOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [165, 180], [1, 0], { extrapolateRight: "clamp" });

  const items = [
    { icon: "✅", text: "24/7 AI screen monitoring" },
    { icon: "✅", text: "Instant detection (<1 second)" },
    { icon: "✅", text: "Desktop & Discord notifications" },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: "#0d1117" }}>
      <div
        style={{
          padding: 60,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          height: "100%",
          opacity: fadeInOpacity * fadeOutOpacity,
        }}
      >
        <h2 style={{ color: "#00ff00", fontSize: 56, marginBottom: 40 }}>The Solution</h2>
        <div style={{ color: "#ccc", fontSize: 32, lineHeight: 1.8 }}>
          {items.map((item, index) => {
            const itemOpacity = interpolate(
              frame,
              [15 + index * 9, 24 + index * 9],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            return (
              <p key={index} style={{ margin: "10px 0", opacity: itemOpacity }}>
                {item.icon} {item.text}
              </p>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Scene 4: Architecture Diagram (19–26s)
const Scene4Architecture: React.FC = () => {
  const frame = useCurrentFrame();
  
  const fadeInOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [165, 180], [1, 0], { extrapolateRight: "clamp" });

  const components = [
    { x: 100, label: "Screen Capture", color: "#4444ff", subtitle: "Windows GDI" },
    { x: 500, label: "Gate Filter", color: "#ffff00", subtitle: "Pixel Motion Detect" },
    { x: 900, label: "AI Classifier", color: "#ff6600", subtitle: "ONNX Model (5MB)" },
    { x: 1300, label: "Notify User", color: "#ff4444", subtitle: "Desktop + Discord" },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: "#1e1e2e" }}>
      <svg width={1920} height={1080} style={{ opacity: fadeInOpacity * fadeOutOpacity }}>
        {/* Render boxes and arrows */}
        {components.map((comp, idx) => (
          <g key={idx}>
            <rect
              x={comp.x}
              y={150}
              width={300}
              height={100}
              fill={comp.color}
              stroke="#00ff00"
              strokeWidth={2}
            />
            <text
              x={comp.x + 150}
              y={210}
              textAnchor="middle"
              fill="#fff"
              fontSize={20}
              fontFamily="monospace"
            >
              {comp.label}
            </text>
            <text
              x={comp.x + 150}
              y={350}
              textAnchor="middle"
              fill="#ccc"
              fontSize={18}
              fontFamily="monospace"
            >
              {comp.subtitle}
            </text>

            {/* Arrows between boxes */}
            {idx < components.length - 1 && (
              <>
                <line
                  x1={comp.x + 300}
                  y1={200}
                  x2={components[idx + 1].x}
                  y2={200}
                  stroke="#00ff00"
                  strokeWidth={3}
                  markerEnd="url(#arrowhead)"
                />
                <text
                  x={(comp.x + components[idx + 1].x) / 2}
                  y={120}
                  textAnchor="middle"
                  fill="#00ff00"
                  fontSize={16}
                  fontFamily="monospace"
                >
                  {[50, 150, 200][idx]}ms
                </text>
              </>
            )}
          </g>
        ))}

        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
            <polygon points="0 0, 10 5, 0 10" fill="#00ff00" />
          </marker>
        </defs>
      </svg>
    </AbsoluteFill>
  );
};

// Scene 5: Tech Stack (26–32s)
const Scene5TechStack: React.FC = () => {
  const frame = useCurrentFrame();
  
  const fadeInOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [165, 180], [1, 0], { extrapolateRight: "clamp" });

  const leftSlide = interpolate(frame, [0, 30], [-200, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rightSlide = interpolate(frame, [0, 30], [200, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0d1117" }}>
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          justifyContent: "space-between",
          padding: "100px",
          opacity: fadeInOpacity * fadeOutOpacity,
        }}
      >
        <div
          style={{
            transform: `translateX(${leftSlide}px)`,
          }}
        >
          <h3 style={{ color: "#00ff00", fontSize: 36, marginBottom: 30 }}>Frontend</h3>
          <ul style={{ color: "#ccc", fontSize: 28, listStyle: "none", padding: 0 }}>
            <li>🖥️ Electron 28</li>
            <li>⚛️ React 18</li>
            <li>💾 Zustand</li>
            <li>🎨 Tailwind CSS</li>
          </ul>
        </div>

        <div
          style={{
            transform: `translateX(${rightSlide}px)`,
          }}
        >
          <h3 style={{ color: "#ff6600", fontSize: 36, marginBottom: 30 }}>Backend</h3>
          <ul style={{ color: "#ccc", fontSize: 28, listStyle: "none", padding: 0 }}>
            <li>🐍 Python 3.11</li>
            <li>🤖 ONNX Runtime</li>
            <li>💿 SQLite</li>
            <li>📡 MCP Server</li>
          </ul>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Scene 6: Real-Time Demo (32–45s)
const Scene6Demo: React.FC = () => {
  const frame = useCurrentFrame();
  
  const fadeInOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [345, 390], [1, 0], { extrapolateRight: "clamp" });

  // State changes
  const state1 = interpolate(frame, [15, 210], [1, 1], { extrapolateRight: "clamp" }); // QUEUE
  const state2 = interpolate(frame, [210, 240], [0, 1], { extrapolateLeft: "clamp" }); // LOADING
  const state3 = interpolate(frame, [240, 390], [0, 1], { extrapolateLeft: "clamp" }); // MATCH FOUND

  const getState = () => {
    if (state1 > 0.5) return { text: "QUEUE", color: "#4444ff", confidence: 95 };
    if (state2 > 0.5) return { text: "LOADING", color: "#ffff00", confidence: 70 };
    return { text: "MATCH FOUND!", color: "#00ff00", confidence: 92 };
  };

  const state = getState();

  return (
    <AbsoluteFill style={{ backgroundColor: "#0d1117" }}>
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          opacity: fadeInOpacity * fadeOutOpacity,
        }}
      >
        <div
          style={{
            backgroundColor: "#fff",
            width: 800,
            height: 600,
            borderRadius: 8,
            overflow: "hidden",
            boxShadow: "0 10px 40px rgba(0,0,0,0.5)",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div style={{ backgroundColor: "#333", padding: 12, color: "#fff", fontSize: 16 }}>
            Overwatch Queue Notifier
          </div>

          <div
            style={{
              padding: 40,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              flex: 1,
            }}
          >
            <div style={{ fontSize: 64, fontWeight: "bold", marginBottom: 30, color: state.color }}>
              {state.text}
            </div>

            <div
              style={{
                width: "60%",
                height: 30,
                backgroundColor: "#eee",
                borderRadius: 4,
                overflow: "hidden",
                marginBottom: 30,
              }}
            >
              <div
                style={{
                  width: `${state.confidence}%`,
                  height: "100%",
                  backgroundColor: "#00ff00",
                  transition: "width 0.3s",
                }}
              />
            </div>

            <p style={{ color: "#666", fontSize: 18 }}>Monitoring Overwatch 2...</p>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Scene 7: Notification Examples (45–51s)
const Scene7Notifications: React.FC = () => {
  const frame = useCurrentFrame();
  
  const fadeInOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [315, 330], [1, 0], { extrapolateRight: "clamp" });

  const desktopScale = interpolate(frame, [0, 30], [0.8, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const discordScale = interpolate(frame, [30, 60], [0.8, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0d1117" }}>
      <div
        style={{
          display: "flex",
          gap: 40,
          padding: 40,
          opacity: fadeInOpacity * fadeOutOpacity,
          width: "100%",
          height: "100%",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div style={{ flex: 1 }}>
          <p style={{ color: "#00ff00", fontSize: 28, marginBottom: 20 }}>Desktop Notification</p>
          <div
            style={{
              backgroundColor: "#333",
              padding: 20,
              borderRadius: 4,
              border: "2px solid #00ff00",
              transform: `scale(${desktopScale})`,
              transformOrigin: "center",
            }}
          >
            <p style={{ color: "#fff", fontSize: 20, margin: 0 }}>🎮 MATCH FOUND!</p>
            <p style={{ color: "#888", fontSize: 16, margin: "8px 0 0 0" }}>Confidence: 92%</p>
          </div>
        </div>

        <div style={{ flex: 1 }}>
          <p style={{ color: "#5865f2", fontSize: 28, marginBottom: 20 }}>Discord Webhook</p>
          <div
            style={{
              backgroundColor: "#2c2f33",
              padding: 20,
              borderLeft: "4px solid #5865f2",
              borderRadius: 4,
              transform: `scale(${discordScale})`,
              transformOrigin: "center",
            }}
          >
            <p style={{ color: "#fff", fontSize: 18, margin: 0 }}>Overwatch Queue</p>
            <p style={{ color: "#dcddde", fontSize: 14, margin: "8px 0 0 0" }}>
              🎮 MATCH FOUND! (92%)
            </p>
            <p style={{ color: "#888", fontSize: 12, margin: "4px 0 0 0" }}>
              Detection time: 450ms
            </p>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Scene 8: Performance Metrics (51–57s)
const MetricBox: React.FC<{ title: string; value: string; unit: string; color: string }> = ({
  title,
  value,
  unit,
  color,
}) => {
  return (
    <div
      style={{
        border: `2px solid ${color}`,
        padding: 30,
        borderRadius: 8,
        textAlign: "center",
      }}
    >
      <p style={{ color: "#888", fontSize: 16, margin: 0 }}>{title}</p>
      <p style={{ color, fontSize: 48, fontWeight: "bold", margin: "10px 0" }}>{value}</p>
      <p style={{ color: "#666", fontSize: 14, margin: 0 }}>{unit}</p>
    </div>
  );
};

const Scene8Metrics: React.FC = () => {
  const frame = useCurrentFrame();
  
  const fadeInOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [315, 330], [1, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0d1117" }}>
      <div
        style={{
          padding: 60,
          display: "grid",
          gridTemplateColumns: "1fr 1fr 1fr",
          gap: 40,
          opacity: fadeInOpacity * fadeOutOpacity,
          width: "100%",
          height: "100%",
          alignContent: "center",
        }}
      >
        <MetricBox title="Latency" value="<1s" unit="end-to-end" color="#00ff00" />
        <MetricBox title="Accuracy" value="92%" unit="match detection" color="#00ff00" />
        <MetricBox title="Inference" value="<150ms" unit="AI per-frame" color="#00ff00" />
        <MetricBox title="Memory" value="45MB" unit="total footprint" color="#00ff00" />
        <MetricBox title="CPU" value="<5%" unit="idle load" color="#00ff00" />
        <MetricBox title="FPS" value="500ms" unit="perception cycle" color="#00ff00" />
      </div>
    </AbsoluteFill>
  );
};

// Scene 9: Database Overview (57–63s)
const Scene9Database: React.FC = () => {
  const frame = useCurrentFrame();
  
  const fadeInOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [315, 330], [1, 0], { extrapolateRight: "clamp" });

  const rows = [
    { icon: "📊", label: "Detection History", value: "100K+ records" },
    { icon: "🎯", label: "Calibration Profiles", value: "Multi-monitor support" },
    { icon: "📢", label: "Notification Log", value: "Sent/Failed tracking" },
    { icon: "⚙️", label: "Settings", value: "User preferences" },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: "#1e1e2e" }}>
      <div
        style={{
          padding: 40,
          opacity: fadeInOpacity * fadeOutOpacity,
          width: "100%",
          height: "100%",
        }}
      >
        <h2 style={{ color: "#00ff00", fontSize: 48, marginBottom: 40 }}>Local SQLite Database</h2>
        <table style={{ color: "#ccc", fontSize: 20, borderCollapse: "collapse", width: "100%" }}>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={idx}>
                <td style={{ border: "1px solid #00ff00", padding: 15 }}>
                  {row.icon} {row.label}
                </td>
                <td style={{ border: "1px solid #00ff00", padding: 15 }}>{row.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p style={{ color: "#666", marginTop: 30, fontSize: 18 }}>
          Zero cloud dependency • Fully offline capable
        </p>
      </div>
    </AbsoluteFill>
  );
};

// Scene 10: Deployment (63–69s)
const StepComponent: React.FC<{ num: number; text: string }> = ({ num, text }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
    <div
      style={{
        width: 40,
        height: 40,
        borderRadius: "50%",
        backgroundColor: "#00ff00",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#000",
        fontWeight: "bold",
        fontSize: 20,
      }}
    >
      {num}
    </div>
    <p style={{ color: "#ccc", fontSize: 24, margin: 0 }}>{text}</p>
  </div>
);

const Scene10Deployment: React.FC = () => {
  const frame = useCurrentFrame();
  
  const fadeInOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [315, 330], [1, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0d1117" }}>
      <div
        style={{
          padding: 60,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 40,
          opacity: fadeInOpacity * fadeOutOpacity,
          width: "100%",
          height: "100%",
          justifyContent: "center",
        }}
      >
        <h2 style={{ color: "#00ff00", fontSize: 48 }}>One-Click Installation</h2>

        <div style={{ display: "flex", gap: 40, alignItems: "center" }}>
          <div style={{ fontSize: 80 }}>📥</div>

          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <StepComponent num={1} text="Download .msi" />
            <StepComponent num={2} text="Run installer" />
            <StepComponent num={3} text="Launch app" />
            <StepComponent num={4} text="Calibrate region" />
            <StepComponent num={5} text="Enable notifications" />
          </div>
        </div>

        <p style={{ color: "#666", fontSize: 20, marginTop: 40 }}>~5 minutes total setup time</p>
      </div>
    </AbsoluteFill>
  );
};

// Scene 11: Development (69–75s)
const Scene11Development: React.FC = () => {
  const frame = useCurrentFrame();
  
  const fadeInOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [315, 330], [1, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#1e1e2e" }}>
      <div style={{ padding: 60, opacity: fadeInOpacity * fadeOutOpacity }}>
        <h2 style={{ color: "#ff6600", fontSize: 48, marginBottom: 40 }}>Open Source Development</h2>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 40,
            fontSize: 20,
            color: "#ccc",
          }}
        >
          <div>
            <p style={{ color: "#00ff00", fontWeight: "bold", fontSize: 24 }}>🔧 Built With</p>
            <ul style={{ paddingLeft: 20 }}>
              <li>Electron + React (Frontend)</li>
              <li>Python 3.11 (Backend)</li>
              <li>ONNX Runtime (AI)</li>
              <li>GitHub Actions (CI/CD)</li>
            </ul>
          </div>

          <div>
            <p style={{ color: "#00ff00", fontWeight: "bold", fontSize: 24 }}>📚 Well-Documented</p>
            <ul style={{ paddingLeft: 20 }}>
              <li>Full architecture specs</li>
              <li>API reference</li>
              <li>Development workflows</li>
              <li>Test strategies</li>
            </ul>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Scene 12: Call-to-Action (75–85s)
const Scene12CTA: React.FC = () => {
  const frame = useCurrentFrame();
  
  const fadeInOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [435, 480], [1, 0], { extrapolateRight: "clamp" });

  const glowOpacity = Math.abs(Math.sin((frame * Math.PI) / 30));

  return (
    <AbsoluteFill style={{ backgroundColor: "#0d1117" }}>
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          gap: 40,
          opacity: fadeInOpacity * fadeOutOpacity,
        }}
      >
        <h1 style={{ color: "#00ff00", fontSize: 64, textAlign: "center", margin: 0 }}>
          Get Started Today
        </h1>

        <div
          style={{
            display: "flex",
            gap: 40,
            fontSize: 24,
            color: "#ccc",
            opacity: 0.7 + glowOpacity * 0.3,
          }}
        >
          <a style={{ color: "#00ff00", textDecoration: "none", cursor: "pointer" }}>
            👉 github.com/overwatch-queue-notifier
          </a>
        </div>

        <div
          style={{
            marginTop: 40,
            fontSize: 20,
            color: "#666",
            textAlign: "center",
            maxWidth: 800,
          }}
        >
          <p>Never miss another match.</p>
          <p>AI-powered detection. Instant notifications.</p>
          <p>Free. Open source. Yours.</p>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Scene 13: End Credits (85–90s)
const Scene13Credits: React.FC = () => {
  const frame = useCurrentFrame();
  
  const fadeInOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const fadeOutOpacity = interpolate(frame, [255, 300], [1, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#1e1e2e" }}>
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          opacity: fadeInOpacity * fadeOutOpacity,
        }}
      >
        <div style={{ color: "#ccc", fontSize: 24, textAlign: "center", lineHeight: 2 }}>
          <p>Created with ❤️ using AutoSpec</p>
          <p>Remotion React Video Framework</p>
          <p style={{ marginTop: 40, color: "#888" }}>© 2024 Overwatch Queue Notifier</p>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ============= MAIN COMPOSITION =============

interface CompositionProps {
  version?: "full" | "short" | "developer";
}

export const Composition: React.FC<CompositionProps> = ({ version = "full" }) => {
  if (version === "short") {
    // Short version: 45 seconds (Scenes 1-7)
    return (
      <AbsoluteFill>
        <Sequence from={0} durationInFrames={180}>
          <Scene1TitleCard />
        </Sequence>
        <Sequence from={180} durationInFrames={210}>
          <Scene2Problem />
        </Sequence>
        <Sequence from={390} durationInFrames={180}>
          <Scene3Solution />
        </Sequence>
        <Sequence from={570} durationInFrames={210}>
          <Scene4Architecture />
        </Sequence>
        <Sequence from={780} durationInFrames={180}>
          <Scene5TechStack />
        </Sequence>
        <Sequence from={960} durationInFrames={390}>
          <Scene6Demo />
        </Sequence>
        <Sequence from={1350} durationInFrames={180}>
          <Scene7Notifications />
        </Sequence>
      </AbsoluteFill>
    );
  }

  // Full version: 90 seconds (All 13 scenes)
  return (
    <AbsoluteFill>
      {/* Scene 1: Title Card (0–6s = 0-180 frames) */}
      <Sequence from={0} durationInFrames={180}>
        <Scene1TitleCard />
      </Sequence>

      {/* Scene 2: Problem (6–13s = 180-390 frames) */}
      <Sequence from={180} durationInFrames={210}>
        <Scene2Problem />
      </Sequence>

      {/* Scene 3: Solution (13–19s = 390-570 frames) */}
      <Sequence from={390} durationInFrames={180}>
        <Scene3Solution />
      </Sequence>

      {/* Scene 4: Architecture (19–26s = 570-780 frames) */}
      <Sequence from={570} durationInFrames={210}>
        <Scene4Architecture />
      </Sequence>

      {/* Scene 5: Tech Stack (26–32s = 780-960 frames) */}
      <Sequence from={780} durationInFrames={180}>
        <Scene5TechStack />
      </Sequence>

      {/* Scene 6: Demo (32–45s = 960-1350 frames) */}
      <Sequence from={960} durationInFrames={390}>
        <Scene6Demo />
      </Sequence>

      {/* Scene 7: Notifications (45–51s = 1350-1530 frames) */}
      <Sequence from={1350} durationInFrames={180}>
        <Scene7Notifications />
      </Sequence>

      {/* Scene 8: Metrics (51–57s = 1530-1710 frames) */}
      <Sequence from={1530} durationInFrames={180}>
        <Scene8Metrics />
      </Sequence>

      {/* Scene 9: Database (57–63s = 1710-1890 frames) */}
      <Sequence from={1710} durationInFrames={180}>
        <Scene9Database />
      </Sequence>

      {/* Scene 10: Deployment (63–69s = 1890-2070 frames) */}
      <Sequence from={1890} durationInFrames={180}>
        <Scene10Deployment />
      </Sequence>

      {/* Scene 11: Development (69–75s = 2070-2250 frames) */}
      <Sequence from={2070} durationInFrames={180}>
        <Scene11Development />
      </Sequence>

      {/* Scene 12: CTA (75–85s = 2250-2550 frames) */}
      <Sequence from={2250} durationInFrames={300}>
        <Scene12CTA />
      </Sequence>

      {/* Scene 13: Credits (85–90s = 2550-2700 frames) */}
      <Sequence from={2550} durationInFrames={150}>
        <Scene13Credits />
      </Sequence>
    </AbsoluteFill>
  );
};

// Export composition with metadata
export const CompositionMeta = {
  id: "Composition",
  component: Composition,
  durationInFrames: 2700, // 90 seconds at 30fps
  fps: 30,
  width: 1920,
  height: 1080,
  defaultProps: {
    version: "full" as const,
  },
};

export default Composition;
