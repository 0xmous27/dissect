#!/usr/bin/env python3
"""dissect - Auto-generate detailed HTB writeups from YouTube walkthroughs."""

import argparse
import json
import os
import re
import sys
import threading
import time

from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

CONFIG_DIR = os.path.expanduser("~/.config/dissect")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

PROMPT = '''You are a senior penetration tester writing a detailed HTB machine writeup in HTML.

Analyze this transcript and generate a COMPLETE, DETAILED HTML writeup page.

Use EXACTLY this HTML structure and CSS style (copy the style block exactly):

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MACHINE_NAME | dissect</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0d1117;color:#c9d1d9;font-family:'Inter',sans-serif;display:flex;min-height:100vh}}
a{{color:#58a6ff;text-decoration:none}}
#sidebar{{width:250px;min-width:250px;background:#161b22;border-right:1px solid #30363d;position:fixed;top:0;left:0;height:100vh;overflow-y:auto;display:flex;flex-direction:column}}
#sidebar .logo{{padding:20px 16px;border-bottom:1px solid #30363d;font-size:18px;font-weight:700;color:#fff}}
#sidebar .logo span{{color:#58a6ff}}
#sidebar nav{{padding:12px 0;flex:1}}
#sidebar nav a{{display:block;padding:9px 20px;color:#8b949e;font-size:13px;font-weight:500;transition:all .15s;border-left:3px solid transparent}}
#sidebar nav a:hover{{color:#c9d1d9;background:#1c2128}}
#sidebar nav a.active{{color:#58a6ff;border-left-color:#58a6ff;background:#1c2128}}
#sidebar .meta{{padding:16px;border-top:1px solid #30363d;font-size:11px;color:#484f58}}
#main{{margin-left:250px;flex:1;padding:40px 48px;max-width:960px}}
h1{{font-size:28px;font-weight:700;color:#fff;margin-bottom:6px}}
h2{{font-size:20px;font-weight:600;color:#fff;margin:40px 0 20px;padding-bottom:8px;border-bottom:1px solid #30363d}}
p{{line-height:1.7;color:#8b949e;font-size:14px;margin-bottom:10px}}
section{{margin-bottom:60px}}
.machine-card{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:20px 24px;display:flex;gap:32px;align-items:center;margin-bottom:28px;flex-wrap:wrap}}
.machine-card .field{{display:flex;flex-direction:column;gap:4px}}
.machine-card .label{{font-size:11px;color:#484f58;text-transform:uppercase;letter-spacing:.05em}}
.machine-card .value{{font-size:15px;font-weight:600;color:#c9d1d9}}
.badge{{display:inline-block;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600}}
.badge.hard{{background:#3d0f0f;color:#f85149;border:1px solid #f85149}}
.badge.medium{{background:#1c1a0a;color:#d29922;border:1px solid #d29922}}
.badge.easy{{background:#0a1f0e;color:#3fb950;border:1px solid #3fb950}}
.badge.insane{{background:#1a0a2e;color:#a371f7;border:1px solid #a371f7}}
.badge.linux{{background:#0d1f33;color:#58a6ff;border:1px solid #58a6ff}}
.badge.windows{{background:#1a0d2e;color:#a371f7;border:1px solid #a371f7}}
.attack-path{{display:flex;align-items:center;flex-wrap:wrap;gap:4px;margin-bottom:28px}}
.ap-box{{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:8px 14px;font-size:13px;font-weight:600;color:#c9d1d9;white-space:nowrap}}
.ap-arrow{{color:#484f58;font-size:18px;padding:0 2px}}
.box{{border-radius:6px;padding:14px 16px;margin:16px 0;font-size:13px;line-height:1.7}}
.box .box-label{{font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px}}
.box-why{{background:#0d1f33;border-left:3px solid #58a6ff}}
.box-why .box-label{{color:#58a6ff}}
.box-tells{{background:#0a1f0e;border-left:3px solid #3fb950}}
.box-tells .box-label{{color:#3fb950}}
.box-warn{{background:#1c1a0a;border-left:3px solid #d29922}}
.box-warn .box-label{{color:#d29922}}
.box-concept{{background:#161b22;border:1px solid #30363d;border-left:3px solid #58a6ff}}
.box-concept .box-label{{color:#58a6ff}}
.box-summary{{background:#0d1f33;border:1px solid #58a6ff;border-radius:8px;padding:20px 24px;margin:24px 0}}
.box-summary .box-label{{color:#58a6ff;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px}}
.box ul{{padding-left:18px;margin-top:4px}}
.box li{{margin-bottom:4px;color:#8b949e}}
.box strong{{color:#c9d1d9}}
.code-wrap{{margin:12px 0;border-radius:6px;overflow:hidden;border:1px solid #30363d}}
.code-header{{background:#161b22;padding:6px 12px;display:flex;justify-content:space-between;align-items:center}}
.code-header span{{font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#484f58}}
.copy-btn{{background:none;border:1px solid #30363d;color:#8b949e;font-size:11px;padding:2px 10px;border-radius:4px;cursor:pointer;font-family:'Inter',sans-serif;transition:all .15s}}
.copy-btn:hover{{border-color:#58a6ff;color:#58a6ff}}
pre{{background:#010409;padding:14px 16px;overflow-x:auto;font-family:'JetBrains Mono',monospace;font-size:12.5px;line-height:1.6}}
pre.cmd{{color:#3fb950}}
pre.out{{color:#8b949e}}
.hl{{color:#f0e68c;font-weight:700}}
.cmd-explain{{font-size:13px;color:#8b949e;margin:8px 0 4px;line-height:1.6}}
.timeline{{background:#010409;border:1px solid #30363d;border-radius:6px;padding:16px 20px;margin-top:16px}}
.timeline .tl-title{{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#484f58;margin-bottom:12px}}
.tl-row{{display:flex;gap:16px;font-family:'JetBrains Mono',monospace;font-size:12px;margin-bottom:6px}}
.tl-time{{color:#58a6ff;min-width:50px}}
.tl-text{{color:#8b949e}}
.flag-text{{color:#3fb950;font-weight:700}}
hr{{border:none;border-top:1px solid #30363d;margin:28px 0}}
</style>
</head>
<body>
... (full page content)
</body>
</html>

CRITICAL RULES for the writeup:
1. Every step must have a "Why" box explaining WHY this step is done
2. Every command must have a .cmd-explain paragraph explaining each flag/option
3. Every command must have its actual output in a <pre class="out"> block
4. Every output must have a "What This Tells Us" box
5. Include "Concept" boxes for any tool, protocol, or technique
6. Include ALL techniques mentioned: names, how they work, why used
7. Include ALL exact commands spoken or shown
8. Attack path boxes at the top showing the full chain
9. End with a summary box of lessons learned and a timeline
10. Sidebar nav links must match all sections
11. Include copy buttons on all command blocks
12. Be EXTREMELY detailed — this is a learning resource

Generate the COMPLETE HTML page now for this transcript:

{transcript}'''


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def get_api_key(args):
    if args.api_key:
        save_config({"api_key": args.api_key})
        return args.api_key
    cfg = load_config()
    if cfg.get("api_key"):
        return cfg["api_key"]
    print("\033[33m⚠  No Gemini API key found.\033[0m")
    print()
    print("  Get a free key at: \033[36mhttps://aistudio.google.com/app/apikey\033[0m")
    print("  (Free tier: 500 requests/day, no credit card needed)")
    print()
    print("  Then run:")
    print("    \033[32mdissect --api-key YOUR_KEY_HERE <url>\033[0m")
    print()
    print("  Or set it once:")
    print("    \033[32mdissect --api-key YOUR_KEY_HERE\033[0m")
    sys.exit(1)


def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if not match:
        print(f"\033[31m✗ Invalid YouTube URL: {url}\033[0m")
        sys.exit(1)
    return match.group(1)


def extract_playlist_videos(url):
    """Extract video IDs from a YouTube playlist page."""
    import urllib.request
    match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
    if not match:
        print("\033[31m✗ No playlist ID found in URL\033[0m")
        sys.exit(1)
    playlist_id = match.group(1)
    api_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req).read().decode()
        ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', resp)
        unique = list(dict.fromkeys(ids))  # dedupe preserving order
        return unique
    except Exception as e:
        print(f"\033[31m✗ Failed to fetch playlist: {e}\033[0m")
        sys.exit(1)


def fetch_transcript(video_id):
    print("  \033[36m→\033[0m Fetching transcript...", end="", flush=True)
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)
        text = " ".join(s.text for s in transcript)[:30000]
        print(f" \033[32m✓\033[0m ({len(text)} chars)")
        return text
    except Exception as e:
        print(f" \033[31m✗\033[0m")
        print(f"\033[31m  Error: {e}\033[0m")
        print("  The video may have captions disabled or be age-restricted.")
        sys.exit(1)


def generate_writeup(api_key, transcript):
    genai.configure(api_key=api_key)
    stop_spinner = threading.Event()

    def spin():
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while not stop_spinner.is_set():
            print(f"\r  {frames[i % len(frames)]} Generating writeup...", end="", flush=True)
            i += 1
            time.sleep(0.1)

    t = threading.Thread(target=spin, daemon=True)
    t.start()

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(PROMPT.format(transcript=transcript))
        try:
            html = response.text.strip()
        except ValueError:
            html = "".join(p.text for p in response.parts if hasattr(p, "text")).strip()
        stop_spinner.set()
        print(f"\r  \033[32m✓\033[0m Generating writeup... done   ")
    except Exception as e:
        stop_spinner.set()
        print(f"\r  \033[31m✗\033[0m Generating writeup... failed   ")
        msg = str(e)
        if "quota" in msg.lower() or "429" in msg:
            print("\033[33m  ⚠ Daily API limit reached. Resets at midnight Pacific Time (UTC-8).\033[0m")
            print("\033[33m    Check usage: https://ai.dev/rate-limit\033[0m")
        else:
            print(f"\033[31m  Gemini error: {msg[:150]}\033[0m")
        sys.exit(1)

    html = re.sub(r'^```html\s*', '', html)
    html = re.sub(r'\s*```$', '', html)

    if not html.startswith("<!DOCTYPE") and not html.startswith("<html"):
        print("\033[31m  ✗ Gemini returned unexpected output. Try again.\033[0m")
        sys.exit(1)

    return html


def extract_title(html):
    match = re.search(r"<title>([^|<]+)", html)
    return match.group(1).strip() if match else "writeup"


def html_to_pdf(html, output_path):
    try:
        import weasyprint
        print(f"  \033[36m→\033[0m Converting to PDF...", end="", flush=True)
        weasyprint.HTML(string=html).write_pdf(output_path)
        print(" \033[32m✓\033[0m")
    except ImportError:
        print("\033[33m  weasyprint not installed. Install with:\033[0m")
        print("    \033[32mpip install weasyprint\033[0m")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="dissect",
        description="Auto-generate detailed HTB writeups from YouTube walkthroughs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  dissect https://youtu.be/zOK_EzOyMN0
  dissect -u https://youtu.be/zOK_EzOyMN0 -o ./reports/
  dissect -u https://youtu.be/zOK_EzOyMN0 -f pdf --open
  dissect -u "https://youtube.com/playlist?list=PLid..." --playlist -o ./reports/
  dissect --list -o ./reports/
  dissect --api-key AIzaSy..."""
    )
    parser.add_argument("url", nargs="?", help="YouTube video URL")
    parser.add_argument("-u", "--youtube", help="YouTube video URL")
    parser.add_argument("-o", "--output", default=".", help="Output directory (default: current)")
    parser.add_argument("-f", "--format", choices=["html", "pdf"], default="html", help="Output format (default: html)")
    parser.add_argument("--open", action="store_true", help="Open the writeup in browser after generation")
    parser.add_argument("--playlist", action="store_true", help="Treat URL as a playlist and generate all writeups")
    parser.add_argument("--list", action="store_true", help="List previously generated writeups in output directory")
    parser.add_argument("--api-key", help="Set Gemini API key (saved for future use)")

    args = parser.parse_args()

    # Resolve URL from either positional or -u flag
    url = args.youtube or args.url

    # Handle --list
    if args.list:
        files = [f for f in os.listdir(args.output) if f.endswith(('.html', '.pdf'))]
        if not files:
            print(f"\033[33mNo writeups found in {args.output}\033[0m")
        else:
            print(f"\n\033[1m🔴 dissect\033[0m — writeups in {args.output}\n")
            for f in sorted(files):
                path = os.path.join(args.output, f)
                size = os.path.getsize(path)
                print(f"  \033[36m•\033[0m {f}  \033[90m({size // 1024}KB)\033[0m")
            print(f"\n  Total: {len(files)} writeups\n")
        sys.exit(0)

    # Handle --api-key without URL (just saving the key)
    if args.api_key and not url:
        save_config({"api_key": args.api_key})
        print(f"\033[32m✓ API key saved to {CONFIG_FILE}\033[0m")
        sys.exit(0)

    if not url:
        parser.print_help()
        sys.exit(1)

    api_key = get_api_key(args)

    print("")
    print("  \033[32m╔══════════════════════════════════════════╗")
    print("  ║                                          ║")
    print("  ║          \033[1m🔴  d i s s e c t\033[0m\033[32m               ║")
    print("  ║       HTB Writeup Auto-Generator         ║")
    print("  ║                                          ║")
    print("  ║       crafted by 0xmous27                ║")
    print("  ║       https://github.com/0xmous27        ║")
    print("  ║                                          ║")
    print("  ╚══════════════════════════════════════════╝\033[0m")
    print("")

    if args.playlist:
        video_ids = extract_playlist_videos(url)
        print(f"  Found \033[36m{len(video_ids)}\033[0m videos in playlist\n")
        os.makedirs(args.output, exist_ok=True)
        for i, vid in enumerate(video_ids, 1):
            print(f"\033[1m[{i}/{len(video_ids)}]\033[0m https://youtu.be/{vid}")
            try:
                transcript = fetch_transcript(vid)
                html = generate_writeup(api_key, transcript)
                title = extract_title(html)
                filename = f"{title.replace(' ', '-')}.{args.format}"
                output_path = os.path.join(args.output, filename)
                if args.format == "pdf":
                    html_to_pdf(html, output_path)
                else:
                    with open(output_path, "w") as f:
                        f.write(html)
                print(f"  \033[32m✓ Saved: {output_path}\033[0m\n")
            except SystemExit:
                print(f"  \033[33m⚠ Skipped\033[0m\n")
                continue
        print(f"\033[32m✓ Done! {len(video_ids)} videos processed.\033[0m\n")
    else:
        video_id = extract_video_id(url)
        transcript = fetch_transcript(video_id)
        html = generate_writeup(api_key, transcript)
        title = extract_title(html)

        os.makedirs(args.output, exist_ok=True)
        filename = f"{title.replace(' ', '-')}.{args.format}"
        output_path = os.path.join(args.output, filename)

        if args.format == "pdf":
            html_to_pdf(html, output_path)
        else:
            with open(output_path, "w") as f:
                f.write(html)

        print(f"\n\033[32m✓ Saved: {output_path}\033[0m\n")

        if args.open:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()
