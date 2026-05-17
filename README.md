# 🔴 dissect

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python) ![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-AI-orange?logo=google) ![License](https://img.shields.io/badge/License-MIT-green)

Auto-generate detailed HTB machine writeups from YouTube walkthrough videos.

Paste a YouTube URL → get a full pentest writeup with exact commands, reasoning, techniques, and attack flow.

```
  ╔══════════════════════════════════════════╗
  ║                                          ║
  ║          🔴  d i s s e c t              ║
  ║       HTB Writeup Auto-Generator         ║
  ║                                          ║
  ║       crafted by 0xmous27                ║
  ║       https://github.com/0xmous27        ║
  ║                                          ║
  ╚══════════════════════════════════════════╝
```

## Features

- ⚡ **Auto-extract** — Fetches transcript from any YouTube HTB walkthrough
- 📝 **Deep writeups** — Why boxes, Concept boxes, exact commands with output, attack timeline
- 🎯 **Techniques** — Every technique named, explained, and contextualized
- 📂 **Save anywhere** — Specify output directory
- 📄 **PDF support** — Export as PDF with `--format pdf`
- 🎬 **Playlist mode** — Process entire YouTube playlists in batch
- 🌐 **Auto-open** — Open writeup in browser after generation
- 📋 **List reports** — View all generated writeups
- 🔐 **API key management** — Set once, saved locally

## Installation

```bash
git clone https://github.com/0xmous27/dissect.git
cd dissect/cli
pip install youtube-transcript-api google-generativeai
sudo ln -sf $(pwd)/dissect /usr/local/bin/dissect
```

## Quick Start

```bash
# Set your Gemini API key (free, one time)
dissect --api-key YOUR_KEY_HERE

# Generate a writeup
dissect https://youtu.be/zOK_EzOyMN0

# With options
dissect -u https://youtu.be/zOK_EzOyMN0 -o ./reports/ --open
```

> 🆓 **No API key?** Get one free at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) — 500 requests/day, no credit card.

## Usage

```
dissect [-h] [-u URL] [-o OUTPUT] [-f {html,pdf}] [--open] [--playlist] [--list] [--api-key KEY]
```

| Flag | Description |
|------|-------------|
| `-u`, `--youtube` | YouTube video URL |
| `-o`, `--output` | Output directory (default: current) |
| `-f`, `--format` | Output format: `html` (default) or `pdf` |
| `--open` | Open writeup in browser after generation |
| `--playlist` | Process all videos in a YouTube playlist |
| `--list` | List previously generated writeups |
| `--api-key` | Set/save Gemini API key |
| `-h`, `--help` | Show help |

## Examples

```bash
# Single video
dissect https://youtu.be/zOK_EzOyMN0

# Save to reports folder as PDF
dissect -u https://youtu.be/zOK_EzOyMN0 -o ./reports/ -f pdf

# Process entire playlist
dissect -u "https://youtube.com/playlist?list=PLidcsTyj..." --playlist -o ./reports/

# List all generated writeups
dissect --list -o ./reports/

# Open in browser after generating
dissect -u https://youtu.be/zOK_EzOyMN0 --open
```

## How It Works

```
YouTube URL
    │
    ▼
Fetch Transcript (youtube-transcript-api)
    │
    ▼
AI Analysis (Gemini 2.5 Flash)
    │
    ▼
Rich HTML Writeup
├── Sidebar navigation
├── Why boxes (attacker reasoning)
├── Concept boxes (technique explanations)
├── Exact commands + output
├── Attack path visualization
└── Timeline + summary
```

## Output Example

The generated writeup includes:
- **Machine info** — Name, OS, difficulty
- **Attack path** — Visual chain of steps
- **Step-by-step** — Every command with flags explained
- **Why boxes** — Why each step is taken
- **Concept boxes** — What each tool/technique is
- **What This Tells Us** — Analysis of every output
- **Summary** — Lessons learned + attack timeline

## Web UI

A web interface is also included in the `frontend/` and `backend/` directories:

```bash
# Terminal 1
cd backend && pip install -r requirements.txt && uvicorn main:app --port 8000

# Terminal 2
cd frontend && npm install && npm run dev
```

Open http://localhost:5173

## Requirements

- Python 3.10+
- Free Gemini API key
- `weasyprint` (optional, for PDF export)

## License

MIT

## Author

**0xmous27** — [github.com/0xmous27](https://github.com/0xmous27)
