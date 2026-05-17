import React, { useState, useEffect, useRef } from 'react'
import './index.css'

function ApiKeySetup({ onSave }) {
  const [key, setKey] = useState('')
  const [checking, setChecking] = useState(false)
  const [err, setErr] = useState('')

  async function submit() {
    if (!key.trim()) return
    setChecking(true); setErr('')
    try {
      const res = await fetch('/validate-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key.trim() })
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || 'Invalid API key')
      }
      const data = await res.json()
      localStorage.setItem('gemini_api_key', key.trim())
      onSave(key.trim())
    } catch (e) {
      setErr(e.message)
    } finally {
      setChecking(false)
    }
  }

  return (
    <div className="setup-screen">
      <div className="setup-card">
        <div className="setup-logo">🔴 HTB<span>-LAB</span></div>
        <h2>Enter your Gemini API Key</h2>
        <p>Your key is stored locally in your browser and never sent to any server other than Google.</p>
        <div className="get-key-box">
          <span>🆓 Don't have a key?</span>
          <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer">
            Get a free key at aistudio.google.com →
          </a>
          <span className="get-key-note">Free tier: 500 requests/day · No credit card needed</span>
        </div>
        <input
          type="password"
          value={key}
          onChange={e => setKey(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && submit()}
          placeholder="AIzaSy..."
          autoFocus
        />
        {err && <div className="setup-err">❌ {err}</div>}
        <button onClick={submit} disabled={checking || !key.trim()}>
          {checking ? 'Validating...' : 'Save & Continue'}
        </button>
      </div>
    </div>
  )
}

export default function App() {
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('gemini_api_key') || '')
  const [tab, setTab] = useState('generate') // 'generate' | 'settings' | 'history'
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState({ msg: '', type: '' })
  const [html, setHtml] = useState('')
  const [flags, setFlags] = useState({ user: '', root: '' })
  const [machineName, setMachineName] = useState('')
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState('')
  const timerRef = useRef(null)
  const iframeRef = useRef(null)

  // Settings state
  const [newKey, setNewKey] = useState('')
  const [keyMsg, setKeyMsg] = useState('')
  const [keyChecking, setKeyChecking] = useState(false)

  // Theme state
  const [theme, setTheme] = useState(() => localStorage.getItem('htb_theme') || 'dark')

  // History state
  const [history, setHistory] = useState(() => {
    try { return JSON.parse(localStorage.getItem('htb_history')) || [] } catch { return [] }
  })

  // MITRE ATT&CK badges
  const [mitreCodes, setMitreCodes] = useState([])

  useEffect(() => { localStorage.setItem('htb_theme', theme) }, [theme])

  const STAGES = [
    { pct: 5,  label: 'Fetching transcript...' },
    { pct: 20, label: 'Parsing transcript...' },
    { pct: 35, label: 'Sending to Gemini...' },
    { pct: 55, label: 'Analyzing techniques...' },
    { pct: 70, label: 'Generating writeup...' },
    { pct: 85, label: 'Building HTML...' },
    { pct: 93, label: 'Almost done...' },
  ]

  function startProgress() {
    let i = 0; setProgress(0); setStage('')
    timerRef.current = setInterval(() => {
      if (i < STAGES.length) { setProgress(STAGES[i].pct); setStage(STAGES[i].label); i++ }
      else clearInterval(timerRef.current)
    }, 6000)
  }

  function finishProgress() { clearInterval(timerRef.current); setProgress(100); setStage('Done!') }

  function extractFlags(html) {
    const userMatch = html.match(/user[\s\S]{0,200}?([a-f0-9]{32})/i)
    const rootMatch = html.match(/root[\s\S]{0,200}?([a-f0-9]{32})/i)
    return { user: userMatch?.[1] || '', root: rootMatch?.[1] || '' }
  }

  function extractMitreCodes(html) {
    const matches = html.match(/T\d{4}/g)
    return matches ? [...new Set(matches)] : []
  }

  function saveToHistory(title, url, html) {
    const entry = { title, url, date: new Date().toISOString(), html }
    const updated = [entry, ...history].slice(0, 50)
    setHistory(updated)
    localStorage.setItem('htb_history', JSON.stringify(updated))
  }

  function deleteHistoryEntry(index) {
    const updated = history.filter((_, i) => i !== index)
    setHistory(updated)
    localStorage.setItem('htb_history', JSON.stringify(updated))
  }

  function loadHistoryEntry(entry) {
    setHtml(entry.html)
    setMachineName(entry.title)
    setFlags(extractFlags(entry.html))
    setMitreCodes(extractMitreCodes(entry.html))
    setTab('generate')
  }

  async function analyze() {
    if (!url.trim()) return
    setLoading(true); setError({ msg: '', type: '' }); setHtml(''); setFlags({ user: '', root: '' }); setMitreCodes([])
    startProgress()
    try {
      const res = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, api_key: apiKey })
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({ detail: 'Unknown error' }))
        const type = res.status === 429 ? 'quota' : res.status === 422 ? 'transcript' : 'error'
        clearInterval(timerRef.current); setProgress(0)
        setError({ msg: data.detail, type }); return
      }
      const text = await res.text()
      const titleMatch = text.match(/<title>([^|<]+)/i)
      const title = titleMatch ? titleMatch[1].trim() : 'writeup'
      setMachineName(title)
      setFlags(extractFlags(text))
      setMitreCodes(extractMitreCodes(text))
      setHtml(text)
      saveToHistory(title, url, text)
      finishProgress()
    } catch (e) {
      clearInterval(timerRef.current); setProgress(0)
      setError({ msg: 'Network error — is the backend running?', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  async function saveKey() {
    if (!newKey.trim()) return
    setKeyChecking(true); setKeyMsg('')
    try {
      const res = await fetch('/validate-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: newKey.trim() })
      })
      if (!res.ok) throw new Error('Invalid key')
      localStorage.setItem('gemini_api_key', newKey.trim())
      setApiKey(newKey.trim()); setNewKey('')
      setKeyMsg('✅ API key updated successfully')
    } catch {
      setKeyMsg('❌ Invalid API key')
    } finally {
      setKeyChecking(false)
    }
  }

  function save() {
    const filename = `${machineName.replace(/\s+/g, '-')}.html`
    if (window.showSaveFilePicker) {
      window.showSaveFilePicker({ suggestedName: filename, types: [{ description: 'HTML', accept: { 'text/html': ['.html'] } }] })
        .then(h => h.createWritable()).then(w => w.write(html).then(() => w.close()))
        .catch(e => { if (e.name !== 'AbortError') fallbackSave(filename) })
    } else fallbackSave(filename)
  }

  function fallbackSave(filename) {
    const a = document.createElement('a')
    a.href = URL.createObjectURL(new Blob([html], { type: 'text/html' }))
    a.download = filename; a.click()
  }

  function exportPdf() {
    const win = window.open('', '_blank')
    win.document.write(html)
    win.document.close()
    win.onload = () => win.print()
  }

  if (!apiKey) return <ApiKeySetup onSave={(k) => setApiKey(k)} />

  return (
    <div className={`theme-${theme}`}>
      <div className="topbar">
        <div className="logo">🔴 HTB<span>-LAB</span></div>
        {tab === 'generate' && <>
          <input value={url} onChange={e => setUrl(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !loading && analyze()}
            placeholder="Paste YouTube HTB walkthrough URL..." />
          <button className="btn-generate" onClick={analyze} disabled={loading}>
            {loading ? <><span className="btn-spinner"/>Generating...</> : '⚡ Generate Writeup'}
          </button>
          <button className="btn-save" onClick={save} disabled={!html}>💾 Save HTML</button>
          <button className="btn-save" onClick={exportPdf} disabled={!html}>🖨 PDF</button>
        </>}
        <button className="btn-theme" onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}>
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
        <div className="tab-nav">
          <button className={tab === 'generate' ? 'active' : ''} onClick={() => setTab('generate')}>Generate</button>
          <button className={tab === 'history' ? 'active' : ''} onClick={() => setTab('history')}>History</button>
          <button className={tab === 'settings' ? 'active' : ''} onClick={() => setTab('settings')}>⚙ API Key</button>
        </div>
      </div>

      {tab === 'settings' ? (
        <div className="settings-page">
          <div className="settings-card">
            <h2>Gemini API Key</h2>
            <p>Current key: <code>{apiKey.slice(0, 8)}{'•'.repeat(20)}</code></p>
            <div className="get-key-box">
              <span>🆓 Need a new key?</span>
              <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer">Get a free key at aistudio.google.com →</a>
              <span className="get-key-note">Free tier: 500 requests/day · No credit card needed</span>
            </div>
            <input type="password" value={newKey} onChange={e => setNewKey(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && saveKey()}
              placeholder="Enter new API key..." />
            {keyMsg && <div className={keyMsg.startsWith('✅') ? 'key-ok' : 'setup-err'}>{keyMsg}</div>}
            <button onClick={saveKey} disabled={keyChecking || !newKey.trim()}>
              {keyChecking ? 'Validating...' : 'Update Key'}
            </button>
          </div>
        </div>
      ) : tab === 'history' ? (
        <div className="settings-page">
          <div className="history-list">
            <h2>History ({history.length})</h2>
            {history.length === 0 && <p>No writeups generated yet.</p>}
            {history.map((entry, i) => (
              <div key={i} className="history-card">
                <div className="history-info">
                  <strong>{entry.title}</strong>
                  <span className="history-date">{new Date(entry.date).toLocaleString()}</span>
                  <a href={entry.url} target="_blank" rel="noreferrer" className="history-url">{entry.url}</a>
                </div>
                <div className="history-actions">
                  <button onClick={() => loadHistoryEntry(entry)}>📄 Load</button>
                  <button onClick={() => deleteHistoryEntry(i)}>🗑 Delete</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <>
          {(flags.user || flags.root || mitreCodes.length > 0) && (
            <div className="flagbar">
              {flags.user && <div className="flag flag-user">🚩 User: <code>{flags.user}</code></div>}
              {flags.root && <div className="flag flag-root">🏆 Root: <code>{flags.root}</code></div>}
              {mitreCodes.map(code => (
                <span key={code} className="badge-mitre">{code}</span>
              ))}
            </div>
          )}
          <div className="content">
            {html
              ? <iframe ref={iframeRef} srcDoc={html} sandbox="allow-scripts allow-same-origin" title="writeup" />
              : <div className="overlay">
                  {loading
                    ? <><div className="spinner"/>
                        <span>Generating writeup for <strong>{url.slice(0, 50)}</strong></span>
                        <div className="progress-wrap"><div className="progress-bar" style={{ width: `${progress}%` }}/></div>
                        <span className="hint">{stage} ({progress}%)</span>
                      </>
                    : error.msg
                      ? <div className={`err-box err-${error.type}`}>
                          <div className="err-title">
                            {error.type === 'quota' ? '⏳ Gemini Daily Quota Reached' : error.type === 'transcript' ? '📄 Transcript Error' : '❌ Error'}
                          </div>
                          <div className="err-msg">{error.msg}</div>
                        </div>
                      : <div className="empty-state">
                          <div className="empty-icon">🔴</div>
                          <div className="empty-title">HTB-LAB Writeup Generator</div>
                          <div className="empty-sub">Paste any HTB YouTube walkthrough URL above to generate a detailed writeup</div>
                        </div>
                  }
                </div>
            }
          </div>
        </>
      )}
    </div>
  )
}
