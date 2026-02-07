# Performance Baseline

## Electron Startup Time
- Measurement command: `npm run perf:startup`
- Latest measured result:
  - `startup_ms_app`: `453ms`
  - `startup_ms_wall_clock`: `610ms`
  - `measured_at`: `2026-02-07T16:39:20.394Z`
- Target: `<2s` (acceptable `<3s`)
- Last updated: 2026-02-07

## Notes
- Startup marker is emitted by `frontend/src/main-electron.ts` as:
  - `[startup] window ready in <ms>ms`
- Automated measurement script:
  - `frontend/scripts/measure-startup.js`
- If local result exceeds `3000ms`, profile startup and reduce main-process boot work before adding integrations.
