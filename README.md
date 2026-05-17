# 🔴 dissect

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python) ![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-AI-orange?logo=google) ![License](https://img.shields.io/badge/License-MIT-green)

Auto-generate detailed HTB machine writeups from YouTube walkthrough videos using AI.

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

## What It Does

Paste a YouTube HTB walkthrough URL → get a complete writeup with:
- Exact commands and their output
- **Why** boxes explaining attacker reasoning
- **Concept** boxes explaining techniques and tools
- **What This Tells Us** analysis for every output
- Attack path visualization
- Timeline and summary of lessons learned

## Install

```bash
git clone https://github.com/0xmous27/dissect.git
cd dissect
pip install -r requirements.txt
sudo ln -sf $(pwd)/dissect.py /usr/local/bin/dissect
```

## Setup

Get a free Gemini API key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) (no credit card needed), then:

```bash
dissect --api-key YOUR_KEY_HERE
```

Key is saved locally at `~/.config/dissect/config.json`. You only need to do this once.

## Usage

```bash
# Generate writeup (saves as MachineName.html)
dissect https://youtu.be/zOK_EzOyMN0

# Using -u flag
dissect -u https://youtu.be/zOK_EzOyMN0

# Save to specific folder
dissect -u https://youtu.be/zOK_EzOyMN0 -o ./reports/

# Export as PDF
dissect -u https://youtu.be/zOK_EzOyMN0 -f pdf

# Open in browser after generating
dissect -u https://youtu.be/zOK_EzOyMN0 --open

# Process entire YouTube playlist
dissect -u "https://youtube.com/playlist?list=PLid..." --playlist -o ./reports/

# List all generated writeups in a folder
dissect --list -o ./reports/
```

## Flags

| Flag | Description |
|------|-------------|
| `-u`, `--youtube` | YouTube video URL |
| `-o`, `--output` | Output directory (default: current) |
| `-f`, `--format` | `html` (default) or `pdf` |
| `--open` | Open in browser after generation |
| `--playlist` | Process all videos in a playlist |
| `--list` | List generated writeups in output dir |
| `--api-key` | Set Gemini API key (saved for future use) |
| `-h`, `--help` | Show help |

## Sample Output

Check [`samples/Outbound.html`](samples/Outbound.html) — generated from [this video](https://youtu.be/bDql3eTHgZ8).

## Requirements

- Python 3.10+
- Free Gemini API key
- `weasyprint` (optional, only needed for `--format pdf`)

## License

MIT

## Author

**0xmous27** — [github.com/0xmous27](https://github.com/0xmous27)
