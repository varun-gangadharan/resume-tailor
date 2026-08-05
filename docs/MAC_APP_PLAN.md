# Mac Clickable App Plan

## Current runnable local app

```bash
cd ~/resume-tailor
python3 -m resume_tailor.ui
```

This starts a local-only browser app at `http://127.0.0.1:8765`.

## Option 1 — Finder/Dock shortcut, least code

Create a double-clickable command file:

```bash
chmod +x bin/resume-tailor-ui.command
open bin/resume-tailor-ui.command
```

You can keep it on Desktop or drag it to the Dock. This opens Terminal and launches the browser UI.

## Option 2 — Real `.app` wrapper, better Mac feel

Implemented with:

```bash
python3 scripts/build_mac_app.py
open "$HOME/Applications/Resume Tailor.app"
```

The builder writes both:

- `dist/Resume Tailor.app`
- `$HOME/Applications/Resume Tailor.app`

Drag `$HOME/Applications/Resume Tailor.app` to the Dock. This is still local; it just launches the same Python server.

## Option 3 — Menu bar/native app, defer

Build with SwiftUI or Tauri only if the browser UI feels annoying. More code, same core workflow.

## Recommendation

Ship Option 1 now. Add Option 2 next if you want a proper app icon in Applications/Dock.
