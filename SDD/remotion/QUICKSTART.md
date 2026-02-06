# Remotion Video Rendering

This project uses Remotion to generate a professional 90-second video showcasing the Overwatch Queue Notifier.

## Quick Start

1. **Install dependencies**
   ```bash
   cd remotion
   npm install
   ```

2. **Preview in development**
   ```bash
   npm start
   # Opens http://localhost:3000
   ```

3. **Render video**
   ```bash
   npm run build
   # Creates output.mp4
   ```

## Available Scripts

- `npm start` - Development preview server
- `npm run build` - Full 90-second video
- `npm run build:short` - 45-second promotional version
- `npm run build:dev` - 120-second developer version

## Video Scenes (90 seconds)

| Time | Scene | Duration |
|------|-------|----------|
| 0–6s | Title Card | 6s |
| 6–13s | Problem Statement | 7s |
| 13–19s | Solution Overview | 6s |
| 19–26s | Architecture Diagram | 7s |
| 26–32s | Tech Stack | 6s |
| 32–45s | Real-Time Demo | 13s |
| 45–51s | Notifications | 6s |
| 51–57s | Metrics | 6s |
| 57–63s | Database | 6s |
| 63–69s | Deployment | 6s |
| 69–75s | Development | 6s |
| 75–85s | Call-to-Action | 10s |
| 85–90s | Credits | 5s |

## Output

The rendered video will be:
- **File**: `remotion/output.mp4`
- **Format**: H.264 video, AAC audio
- **Size**: 1920×1080 @ 30fps
- **File Size**: ~30–50MB
- **Duration**: 90 seconds

## Technology

- **Remotion 4.0+** - React-based video framework
- **TypeScript 5.0+** - Type-safe composition code
- **React 18** - Component-based animation

## Project Structure

```
remotion/
├── src/
│   ├── Composition.tsx    # Main 13-scene video composition
│   └── index.ts           # Entry point
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── remotion.config.ts     # Remotion settings
├── README.md              # Full documentation
└── .gitignore            # Git exclusions
```

## Customization

Edit `src/Composition.tsx` to:
- Change text content
- Adjust timing and animations
- Modify colors (current theme: terminal green #00ff00)
- Update company/project information

## Rendering Options

### Local (Single Machine)
```bash
npm run build
```

### Cloud (AWS Lambda)
```bash
remotion render --org [org-name] src/Composition.tsx output.mp4
```

### Docker
```bash
docker run --rm -v $(pwd):/work remotion-renderer npm run build
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Slow preview | Reduce complexity, disable debug |
| Render errors | Check Node.js version (16+) |
| Missing fonts | Install system fonts or use web fonts |
| Large file size | Reduce bitrate or codec settings |

## Next Steps

1. Preview the video locally: `npm start`
2. Customize scenes as needed in `Composition.tsx`
3. Render final video: `npm run build`
4. Upload to GitHub Releases or YouTube
5. Embed in project documentation

## Resources

- [Remotion Documentation](https://www.remotion.dev/docs)
- [Video Configuration](https://www.remotion.dev/docs/config)
- [Animation Techniques](https://www.remotion.dev/docs/spring)
- [Deployment Guide](https://www.remotion.dev/docs/deploy)

---

**Last Updated**: February 2026 | **Status**: Ready for production
