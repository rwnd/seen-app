# Embedding the demo video in README

GitHub **does not** render local repo paths or release URLs as inline video players in `README.md`. The `<video>` tag is stripped unless `src` points at a GitHub-hosted CDN URL.

## What works on github.com

1. Open the README editor on GitHub (not locally):
   ```bash
   gh browse --branch main -- README.md
   ```
2. In the web editor, drag `docs/assets/demo.mp4` into the text area (must be **under 10 MB**).
3. GitHub uploads the file and inserts a URL like:
   - `https://user-images.githubusercontent.com/.../demo.mp4`, or
   - `https://github.com/user-attachments/assets/...`
4. Wrap that URL in a video tag in the Demo section:
   ```html
   <div align="center">
     <video src="PASTE_CDN_URL_HERE" controls width="720"></video>
   </div>
   ```
5. Commit from the web UI (or copy the URL back into your local README and push).

## What works locally

When you run the app, the same file is served at:

http://localhost:8000/docs-assets/demo.mp4

## Fallback (no CDN upload)

Use the poster image + link to the [demo release](https://github.com/rwnd/seen-app/releases/tag/demo-v1) — visitors click to watch/download the MP4.
