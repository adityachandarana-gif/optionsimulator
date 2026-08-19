"""Presentation-only design tokens and overrides for the trading dashboard."""

DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@400;500;600;700&display=swap');

:root {
  --bg: #020617;
  --surface: #0e1223;
  --surface-raised: #111a30;
  --border: #334155;
  --text: #f8fafc;
  --muted: #94a3b8;
  --brand: #2563eb;
  --danger: #ef4444;
  --focus: #f8fafc;
}

.stApp { background: var(--bg) !important; color: var(--text) !important; }
.main .block-container { max-width: 1560px !important; padding: 18px 18px 28px !important; }
body, .stApp, button, input, textarea, [data-testid="stMarkdownContainer"] { font-family: 'Fira Sans', sans-serif !important; }
code, .nifty-price, .pnl-value, [data-testid="stMetricValue"], [data-testid="stDataFrame"] { font-family: 'Fira Code', monospace !important; }

.fixed-header {
  position: sticky !important; top: 0 !important; left: auto !important; right: auto !important;
  z-index: 100 !important;
  background: linear-gradient(100deg, #0f172a 0%, #0e1f3c 72%, #123524 100%) !important;
  border: 0 !important; border-bottom: 1px solid #284057 !important;
  border-radius: 0 !important; padding: 10px 24px !important;
  box-shadow: 0 8px 24px rgba(0,0,0,.34) !important;
}
.fixed-header h1 { margin: 0 !important; font-size: 17px !important; letter-spacing: .4px !important; line-height: 1.25 !important; }
.fixed-header p { margin: 4px 0 0 !important; color: #a8c5e2 !important; font-size: 12px !important; line-height: 1.25 !important; }
.brand-line { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.environment-badge {
  display: inline-flex; align-items: center; white-space: nowrap; padding: 5px 9px;
  border: 1px solid #3b82f6; border-radius: 999px; color: #bfdbfe;
  background: rgba(30, 58, 95, .72); font: 600 10px 'Fira Code', monospace; letter-spacing: .4px;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(1) > div,
div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div {
  background: transparent !important; border: 0 !important; padding: 0 !important;
}
.card, .card-beige {
  background: linear-gradient(145deg, var(--surface-raised), var(--surface)) !important;
  border: 1px solid var(--border) !important; box-shadow: 0 8px 18px rgba(0,0,0,.18) !important;
  border-radius: 12px !important; padding: 16px !important;
}
.nifty-symbol, .pnl-label, .nifty-meta { color: var(--muted) !important; }
.nifty-price { color: var(--text) !important; letter-spacing: -.5px; }
.nifty-meta span { color: var(--text) !important; }
.nifty-up, .profit { color: #22c55e !important; }
.nifty-down, .loss { color: var(--danger) !important; }
.pnl-row {
  background: var(--surface) !important; border: 1px solid #26364a !important;
  border-radius: 9px !important; margin-bottom: 7px !important;
}
.pnl-row:hover { border-color: #49627d !important; }

.stButton > button, [data-testid="stDownloadButton"] > button,
button[data-testid="stBaseButton-secondary"], button[data-testid="stBaseButton-primary"] {
  min-height: 42px !important; border-radius: 8px !important; font-weight: 700 !important;
  background: #1e293b !important; color: var(--text) !important; border: 1px solid #475569 !important;
  transition: transform .16s ease, background .16s ease, border-color .16s ease !important;
}
.stButton > button:hover, [data-testid="stDownloadButton"] > button:hover,
button[data-testid="stBaseButton-secondary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
  background: #283a53 !important; border-color: #6b849e !important; transform: translateY(-1px) !important;
}
.stButton > button:focus-visible, [data-testid="stDownloadButton"] > button:focus-visible,
input:focus-visible { outline: 3px solid var(--focus) !important; outline-offset: 2px !important; }
button[data-testid="stBaseButton-primary"],
.stButton > button[kind="primary"], div[data-testid="stButton"] > button[kind="primary"] {
  background: var(--brand) !important; color: #ffffff !important; border-color: #60a5fa !important;
  text-shadow: none !important;
}
button[data-testid="stBaseButton-primary"] *,
.stButton > button[kind="primary"] *, div[data-testid="stButton"] > button[kind="primary"] * { color: #ffffff !important; }
button[data-testid="stBaseButton-primary"]:hover,
.stButton > button[kind="primary"]:hover, div[data-testid="stButton"] > button[kind="primary"]:hover { background: #3b82f6 !important; color: #ffffff !important; }
button[data-testid="stBaseButton-secondary"] { background: #17233a !important; color: #dbeafe !important; border-color: #3b82f6 !important; }
button[data-testid="stBaseButton-secondary"] * { color: #dbeafe !important; }
button[data-testid="stBaseButton-secondary"]:hover { background: #203556 !important; color: #ffffff !important; }
div[data-testid="stButton"] button {
  min-height: 44px !important; background: #17233a !important; color: #dbeafe !important;
  border: 1px solid #3b82f6 !important; border-radius: 9px !important;
}
div[data-testid="stButton"] button * { color: inherit !important; }
div[data-testid="stButton"] button[kind="primary"] { background: #2563eb !important; color: #ffffff !important; border-color: #60a5fa !important; }
div[data-testid="stButton"] button[kind="primary"] * { color: #ffffff !important; }
div[data-testid="stButton"] button:disabled, button[data-testid^="stBaseButton"]:disabled {
  background: #1e293b !important; color: #94a3b8 !important; border-color: #475569 !important;
  opacity: .72 !important; cursor: not-allowed !important;
}
.stButton > button:disabled { background: #334155 !important; color: #94a3b8 !important; border-color: #475569 !important; opacity: 1 !important; cursor: not-allowed !important; }
.reset-btn-container button { background: #7f1d1d !important; border-color: #ef4444 !important; color: #fff !important; }

.stTabs [data-baseweb="tab-list"] { background: #0b1324 !important; border: 1px solid var(--border) !important; padding: 4px !important; }
.stTabs [data-baseweb="tab"] { color: var(--muted) !important; font-size: 13px !important; }
.stTabs [aria-selected="true"] { background: #1e3a5f !important; color: #fff !important; box-shadow: none !important; }
.stTabs [data-baseweb="tab"]:hover { background: #182943 !important; color: #fff !important; }

label, .stSelectbox label, .stNumberInput label, .stSlider label,
[data-testid="stCaptionContainer"], [data-testid="stMarkdownContainer"] { color: var(--muted) !important; }
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3, .section-title { color: var(--text) !important; }
div[style*="color:#1a1a1a"], div[style*="color: #1a1a1a"],
.pos-instrument, .margin-val, .subsection-title { color: var(--text) !important; }
.pos-meta, .margin-label { color: var(--muted) !important; }
div[style*="font-size:18px"][style*="font-weight:700"] { color: #f8fafc !important; }
[data-baseweb="select"] > div, [data-baseweb="input"] > div,
[data-testid="stNumberInput"] input { background: #0b1324 !important; color: var(--text) !important; border-color: #475569 !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 10px !important; overflow: hidden !important; }
[data-testid="stMetric"] { background: var(--surface) !important; padding: 12px !important; border: 1px solid #26364a !important; border-radius: 10px !important; }
[data-testid="stMetricLabel"] { color: var(--muted) !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; }
.moneyness-legend {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  margin: 4px 0 10px; color: var(--muted) !important; font-size: 11px;
}
.moneyness-pill {
  display: inline-block; padding: 3px 7px; border-radius: 999px;
  font-size: 10px; font-weight: 800; letter-spacing: .04em;
}
.moneyness-pill.itm { background: #123b2a; color: #bbf7d0 !important; }
.moneyness-pill.atm { background: #1e3a8a; color: #dbeafe !important; }
.moneyness-pill.otm { background: #3f1d2e; color: #fecdd3 !important; }

@media (max-width: 720px) {
  .main .block-container { padding: 12px 12px 20px !important; }
  .fixed-header { padding: 11px 14px !important; }
  .fixed-header h1 { font-size: 14px !important; }
  .fixed-header p { display: none; }
  .environment-badge { padding: 4px 7px; font-size: 9px; }
  .nifty-price { font-size: 23px !important; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition: none !important; animation: none !important; scroll-behavior: auto !important; }
}
</style>
"""


def get_theme_css(theme_mode):
  """Return presentation overrides for the selected dashboard theme."""
  if theme_mode == 'light':
    return """
<style>
:root { --bg: #f4f7fb; --surface: #ffffff; --surface-raised: #eef3f8; --border: #cbd5e1; --text: #172033; --muted: #526174; --focus: #1d4ed8; }
.stApp { background: #f4f7fb !important; color: #172033 !important; }
.card, .card-beige, [data-testid="stMetric"], .pnl-row { background: #ffffff !important; border-color: #cbd5e1 !important; box-shadow: 0 5px 14px rgba(30, 41, 59, .08) !important; }
.nifty-price, [data-testid="stMetricValue"], [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3, .section-title, .pos-instrument, .margin-val, .subsection-title { color: #172033 !important; }
.nifty-symbol, .pnl-label, .nifty-meta, .pos-meta, .margin-label, label, .stSelectbox label, .stNumberInput label, .stSlider label, [data-testid="stCaptionContainer"], [data-testid="stMarkdownContainer"] { color: #526174 !important; }
[data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-testid="stNumberInput"] input { background: #ffffff !important; color: #172033 !important; border-color: #94a3b8 !important; }
.stTabs [data-baseweb="tab-list"] { background: #e8eef5 !important; border-color: #cbd5e1 !important; }
.stTabs [data-baseweb="tab"] { color: #526174 !important; }
.stTabs [aria-selected="true"] { background: #dbeafe !important; color: #1e3a8a !important; }
.stButton > button, [data-testid="stDownloadButton"] > button, div[data-testid="stButton"] button { background: #ffffff !important; color: #1e3a8a !important; border-color: #60a5fa !important; }
.stButton > button:hover, [data-testid="stDownloadButton"] > button:hover, div[data-testid="stButton"] button:hover { background: #eff6ff !important; }
.theme-toggle button { min-height: 34px !important; padding: 4px 12px !important; font-size: 12px !important; }
</style>
"""
  return """
<style>
.theme-toggle button { min-height: 34px !important; padding: 4px 12px !important; font-size: 12px !important; }
</style>
"""
