# Overwatch Queue Notifier - Remotion Video

Professional 90-second animated video showcasing the Overwatch Queue Notifier project using Remotion (React video framework).

## Features

- **13 Scene Composition** - Full product overview from problem to CTA
- **Smooth Animations** - Fade, slide, scale, and glow effects
- **Multiple Versions** - Full (90s), Short (45s), and Developer (120s) versions
- **High Quality Output** - 1920×1080, 30fps, H.264 codec
- **AWS-Ready** - Optimized for cloud rendering

## Scenes

1. **Title Card** (0–6s) - Project introduction
2. **Problem Statement** (6–13s) - Queue notification problem
3. **Solution Overview** (13–19s) - AI-powered detection
4. **Architecture Diagram** (19–26s) - System components and latency
5. **Tech Stack** (26–32s) - Frontend & Backend technologies
6. **Real-Time Demo** (32–45s) - Live interface mockup
7. **Notification Examples** (45–51s) - Desktop + Discord notifications
8. **Performance Metrics** (51–57s) - Key performance indicators
9. **Database Overview** (57–63s) - SQLite data storage
10. **Deployment** (63–69s) - One-click installation flow
11. **Development** (69–75s) - Open source & documentation
12. **Call-to-Action** (75–85s) - Get started prompt
13. **Credits** (85–90s) - Attribution and closing

## Installation

```bash
cd remotion
npm install
```

## Development

Preview the video in real-time:

```bash
npm run preview
# or
npm start
```

Visit `http://localhost:3000` to see the interactive preview.

## Building

### Full Version (90 seconds)
```bash
npm run build
```

### Short Version (45 seconds)
```bash
npm run build:short
```

### Developer Version (120 seconds)
```bash
npm run build:dev
```

## Output

- **File**: `output.mp4` (or specified output path)
- **Format**: H.264 video codec
- **Resolution**: 1920×1080 (4K-ready)
- **Frame Rate**: 30fps
- **Size**: ~30–50MB
- **Duration**: 90 seconds

## Color Palette

Consistent with the project's design tokens:

```
- Primary: #00ff00 (Terminal Green)
- Secondary: #ff6600 (Orange)
- Error: #ff4444 (Red)
- Background: #0d1117 (Dark)
- Text: #ccc (Light Gray)
- Accent: #4444ff (Blue)
- Alert: #ffff00 (Yellow)
```

## Tech Stack

- **Framework**: Remotion 4.0+
- **Runtime**: React 18
- **Language**: TypeScript 5.0+
- **Styling**: Inline CSS
- **Animations**: Remotion spring, interpolate, Easing

## Customization

Edit `src/Composition.tsx` to:
- Modify colors and fonts
- Adjust animation timings
- Add new scenes
- Change text content

## Rendering Options

### Local Rendering
```bash
npm run build
```

### Headless Server (Docker)
```bash
docker run --rm -v $(pwd):/app remotion-headless
```

### AWS Lambda (via CLI)
```bash
remotion render --org my-org src/Composition.tsx output.mp4
```

## Deployment

### GitHub Releases
Upload the compiled `.mp4` to GitHub Releases for project distribution.

### YouTube
Upload with description:
```
Overwatch Queue Notifier - AI-Powered Game Detection
- Instant match notifications
- 24/7 screen monitoring
- Desktop & Discord alerts
- Free & Open Source

GitHub: https://github.com/overwatch-queue-notifier
```

### Web Deployment
Host the video on your project website or embedded in documentation.

## Troubleshooting

### Video Not Playing
- Ensure H.264 codec support in your player
- Try exporting with different codec: `--codec vp8`
- Check output file size and duration

### Slow Rendering
- Reduce resolution: `--props '{"width": 1280, "height": 720}'`
- Lower frame rate: `--props '{"fps": 24}'`
- Use GPU acceleration with `--concurrency 4`

### Memory Issues
- Process video in chunks
- Use cloud rendering (AWS Lambda)
- Reduce animation complexity

## References

- [Remotion Docs](https://www.remotion.dev/docs)
- [Remotion Examples](https://github.com/remotion-dev/remotion/tree/main/packages/examples)
- [Video Configuration Guide](https://www.remotion.dev/docs/config)

## License

Part of the Overwatch Queue Notifier project - licensed under the same terms as the parent project.

---

**Created**: 2024 | **Framework**: Remotion | **Status**: Production-Ready
