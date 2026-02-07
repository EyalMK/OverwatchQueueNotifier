const { spawn } = require("node:child_process");
const path = require("node:path");

const electronBin = require("electron");
const env = { ...process.env };
delete env.ELECTRON_RUN_AS_NODE;

const child = spawn(electronBin, ["."], {
  cwd: path.join(__dirname, ".."),
  env,
  windowsHide: true,
});

let stdout = "";
let stderr = "";
let done = false;
const startedAt = Date.now();

const timeout = setTimeout(() => {
  if (done) return;
  done = true;
  child.kill();
  console.error("Startup measurement timed out after 15s.");
  if (stderr.trim()) console.error(stderr.trim());
  process.exit(1);
}, 15000);

function finish(code = 0) {
  if (done) return;
  done = true;
  clearTimeout(timeout);
  child.kill();
  if (code !== 0 && stderr.trim()) {
    console.error(stderr.trim());
  }
  process.exit(code);
}

child.stdout.on("data", (buf) => {
  const text = buf.toString();
  stdout += text;
  const match = stdout.match(/\[startup\] window ready in (\d+)ms/);
  if (match) {
    const appReportedMs = Number(match[1]);
    const wallClockMs = Date.now() - startedAt;
    console.log(
      JSON.stringify(
        {
          startup_ms_app: appReportedMs,
          startup_ms_wall_clock: wallClockMs,
          measured_at: new Date().toISOString(),
        },
        null,
        2
      )
    );
    finish(0);
  }
});

child.stderr.on("data", (buf) => {
  stderr += buf.toString();
});

child.on("exit", (code) => {
  if (done) return;
  done = true;
  clearTimeout(timeout);
  if (code === 0) {
    console.error("Electron exited before startup marker was captured.");
  } else {
    console.error(`Electron exited with code ${code} before startup marker was captured.`);
    if (stderr.trim()) console.error(stderr.trim());
  }
  process.exit(1);
});
