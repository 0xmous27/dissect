from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import re

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class VideoRequest(BaseModel):
    url: str
    api_key: str

class ValidateRequest(BaseModel):
    api_key: str

def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    return match.group(1)

@app.post("/validate-key")
async def validate_key(req: ValidateRequest):
    try:
        genai.configure(api_key=req.api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        model.generate_content("Say OK")
        return {"valid": True}
    except Exception as e:
        msg = str(e)
        if "quota" in msg.lower() or "resource_exhausted" in msg.lower() or "429" in msg:
            # Key is valid, just quota exhausted
            return {"valid": True, "warning": "quota"}
        raise HTTPException(status_code=401, detail="Invalid API key")

PROMPT = '''You are a senior penetration tester writing a detailed HTB machine writeup in HTML.

Analyze this transcript and generate a COMPLETE, DETAILED HTML writeup page.

Use EXACTLY this HTML structure and CSS style (copy the style block exactly):

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MACHINE_NAME | HTB-LAB</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0d1117;color:#c9d1d9;font-family:\'Inter\',sans-serif;display:flex;min-height:100vh}}
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
.copy-btn{{background:none;border:1px solid #30363d;color:#8b949e;font-size:11px;padding:2px 10px;border-radius:4px;cursor:pointer;font-family:\'Inter\',sans-serif;transition:all .15s}}
.copy-btn:hover{{border-color:#58a6ff;color:#58a6ff}}
pre{{background:#010409;padding:14px 16px;overflow-x:auto;font-family:\'JetBrains Mono\',monospace;font-size:12.5px;line-height:1.6}}
pre.cmd{{color:#3fb950}}
pre.out{{color:#8b949e}}
.hl{{color:#f0e68c;font-weight:700}}
.cmd-explain{{font-size:13px;color:#8b949e;margin:8px 0 4px;line-height:1.6}}
.timeline{{background:#010409;border:1px solid #30363d;border-radius:6px;padding:16px 20px;margin-top:16px}}
.timeline .tl-title{{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#484f58;margin-bottom:12px}}
.tl-row{{display:flex;gap:16px;font-family:\'JetBrains Mono\',monospace;font-size:12px;margin-bottom:6px}}
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
1. Every step must have a "Why" box explaining WHY this step is done, what the attacker is thinking
2. Every command must have a .cmd-explain paragraph explaining each flag/option used
3. Every command must have its actual output in a <pre class="out"> block
4. Every output must have a "What This Tells Us" box explaining what the output means
5. Include "Concept" boxes for any tool, protocol, or technique that needs explanation (e.g. what is Kerberoasting, what is SMB null session, what is a linked server)
6. Include ALL techniques mentioned: their names, how they work, why they are used
7. Include ALL exact commands spoken or shown
8. The attack path boxes at the top must show the full chain
9. End with a summary box of lessons learned and a timeline
10. Sidebar nav links must match all sections
11. Include copy buttons on all command blocks
12. Be EXTREMELY detailed — this is a learning resource, not a summary

Generate the COMPLETE HTML page now for this transcript:

{transcript}'''

@app.post("/analyze")
async def analyze(req: VideoRequest):
    if not req.api_key:
        raise HTTPException(status_code=401, detail="No API key provided")
    genai.configure(api_key=req.api_key)
    video_id = extract_video_id(req.url)

    # Fetch transcript
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)
        text = " ".join(s.text for s in transcript)[:30000]
    except Exception as e:
        msg = str(e)
        if "no element" in msg.lower() or "parse" in msg.lower():
            raise HTTPException(status_code=422, detail="Could not fetch transcript. The video may have captions disabled or be age-restricted.")
        raise HTTPException(status_code=422, detail=f"Transcript error: {msg}")

    # Call Gemini
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(PROMPT.format(transcript=text))
        try:
            html = response.text.strip()
        except ValueError:
            html = "".join(part.text for part in response.parts if hasattr(part, "text")).strip()
    except HTTPException:
        raise
    except Exception as e:
        msg = str(e)
        if "quota" in msg.lower() or "429" in msg or "resource_exhausted" in msg.lower():
            raise HTTPException(status_code=429, detail="Gemini free tier daily quota exceeded. Wait until midnight Pacific Time (UTC-8) for it to reset, or add billing at https://aistudio.google.com")
        if "api_key" in msg.lower() or "invalid" in msg.lower():
            raise HTTPException(status_code=401, detail="Invalid Gemini API key. Check your .env file.")
        raise HTTPException(status_code=500, detail=f"Gemini error: {msg}")
    html = re.sub(r'^```html\s*', '', html)
    html = re.sub(r'\s*```$', '', html)

    if not html.startswith("<!DOCTYPE") and not html.startswith("<html"):
        raise HTTPException(status_code=500, detail="Gemini returned unexpected output. Try again.")

    # Fix anchor links inside iframe — intercept clicks and scroll instead of navigating
    scroll_fix = """<script>
document.addEventListener('click', function(e) {
  const a = e.target.closest('a[href^="#"]');
  if (!a) return;
  e.preventDefault();
  const el = document.querySelector(a.getAttribute('href'));
  if (el) el.scrollIntoView({behavior: 'smooth'});
});
</script>"""
    html = html.replace('</body>', scroll_fix + '</body>')

    return HTMLResponse(content=html)
