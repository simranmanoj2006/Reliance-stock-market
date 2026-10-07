import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Reliance Stock Analytics", page_icon="📈",
                   layout="wide", initial_sidebar_state="expanded")

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\simra\Downloads\reliance report.csv")
    date_col = None
    for col in df.columns:
        if "date" in col.lower():
            date_col = col
            df[col] = pd.to_datetime(df[col], errors="coerce")
            df = df.sort_values(col).reset_index(drop=True)
            break
    return df, date_col

try:
    df, date_col = load_data()
except Exception as e:
    st.error(f"Could not load CSV: {e}")
    st.stop()

def find_col(kws):
    for kw in kws:
        for c in df.columns:
            if kw.lower() in c.lower():
                return c
    return None

open_col  = find_col(["open"])
high_col  = find_col(["high"])
low_col   = find_col(["low"])
close_col = find_col(["close"])
vol_col   = find_col(["volume","vol"])

if "chart_type" not in st.session_state:
    st.session_state.chart_type = "Candlestick"

# ── ENHANCED CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
  --cream: #fdf8f0;
  --gold: #c8872a;
  --gold-light: #f0b860;
  --gold-pale: #fdf0d8;
  --navy: #1a2340;
  --navy-mid: #243056;
  --rose: #c0392b;
  --emerald: #1a7a4a;
  --muted: #6b7280;
  --border: #e8dcc8;
  --shadow-xs: 0 1px 4px rgba(200,135,42,.08);
  --shadow-sm: 0 2px 12px rgba(200,135,42,.12);
  --shadow-md: 0 8px 32px rgba(200,135,42,.18);
  --shadow-lg: 0 20px 60px rgba(26,35,64,.16);
  --glow-gold: 0 0 20px rgba(240,184,96,.35), 0 0 40px rgba(200,135,42,.15);
  --glow-green: 0 0 16px rgba(26,122,74,.4);
  --glow-red: 0 0 16px rgba(192,57,43,.4);
}

/* ── BASE ── */
.stApp { background: var(--cream) !important; font-family: 'DM Sans', sans-serif; }
.main .block-container { padding: 0 2.5rem 5rem !important; max-width: 1800px; }

/* ── ANIMATED BACKGROUND TEXTURE ── */
.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image: 
    radial-gradient(circle at 15% 15%, rgba(200,135,42,.04) 0%, transparent 40%),
    radial-gradient(circle at 85% 80%, rgba(26,35,64,.04) 0%, transparent 40%),
    url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23c8872a' fill-opacity='0.018'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: linear-gradient(175deg, #0f1628 0%, #1a2340 35%, #1e2d4a 65%, #162535 100%) !important;
  box-shadow: 6px 0 32px rgba(0,0,0,.25) !important;
  border-right: 1px solid rgba(200,135,42,.15) !important;
}
[data-testid="stSidebar"] * { color: #e8dcc8 !important; }
[data-testid="stSidebar"] h3 {
  color: #f0b860 !important;
  font-family: 'Playfair Display', serif !important;
  font-size: 1.1rem !important;
  letter-spacing: .02em !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(240,184,96,.15) !important; }
[data-testid="stSidebar"] label {
  color: rgba(240,184,96,.75) !important;
  font-size: .68rem !important;
  letter-spacing: .18em !important;
  text-transform: uppercase !important;
  font-family: 'DM Mono', monospace !important;
  font-weight: 500 !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] div[data-baseweb="input"] input {
  background: rgba(255,255,255,.06) !important;
  border: 1px solid rgba(240,184,96,.35) !important;
  border-radius: 10px !important;
  color: #fdf8f0 !important;
  -webkit-text-fill-color: #fdf8f0 !important;
  font-family: 'DM Mono', monospace !important;
}
[data-testid="stSidebar"] div[data-baseweb="input"],
[data-testid="stSidebar"] div[data-baseweb="base-input"] {
  background: rgba(255,255,255,.05) !important;
  border: 1px solid rgba(240,184,96,.25) !important;
  border-radius: 10px !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  background: rgba(255,255,255,.05) !important;
  border: 1px solid rgba(240,184,96,.25) !important;
  border-radius: 10px !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] span { color: #fdf8f0 !important; }
[data-testid="stSidebar"] .stMultiSelect > div > div {
  background: rgba(255,255,255,.05) !important;
  border: 1px solid rgba(240,184,96,.25) !important;
  border-radius: 10px !important;
}
[data-testid="stSidebar"] span[data-baseweb="tag"] {
  background: rgba(200,135,42,.3) !important;
  border: 1px solid rgba(240,184,96,.5) !important;
  border-radius: 6px !important;
}
[data-testid="stSidebar"] .stCheckbox label {
  color: #b8c8d8 !important;
  font-size: .78rem !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
}
/* Sidebar accent line */
[data-testid="stSidebar"]::after {
  content: '';
  position: absolute;
  top: 0; right: 0; bottom: 0;
  width: 1px;
  background: linear-gradient(180deg, transparent, rgba(200,135,42,.3), rgba(240,184,96,.5), rgba(200,135,42,.3), transparent);
}

/* ── SIDEBAR LOGO SECTION ── */
.sidebar-brand {
  text-align: center;
  padding: 24px 12px 20px;
  position: relative;
}
.sidebar-logo-outer {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, #c8872a, #f0b860, #c8872a, #a06020, #c8872a);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 12px;
  box-shadow: 0 0 0 3px rgba(200,135,42,.2), 0 0 24px rgba(200,135,42,.4), 0 0 48px rgba(200,135,42,.15);
  animation: spin-ring 12s linear infinite, pulse-glow 3s ease-in-out infinite alternate;
}
@keyframes spin-ring { to { transform: rotate(360deg); } }
@keyframes pulse-glow {
  from { box-shadow: 0 0 0 3px rgba(200,135,42,.2), 0 0 24px rgba(200,135,42,.4), 0 0 48px rgba(200,135,42,.15); }
  to   { box-shadow: 0 0 0 6px rgba(200,135,42,.1), 0 0 32px rgba(200,135,42,.6), 0 0 64px rgba(200,135,42,.25); }
}
.sidebar-logo-inner {
  width: 60px; height: 60px;
  border-radius: 50%;
  background: linear-gradient(145deg, #0f1628, #1a2340);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Playfair Display', serif;
  font-weight: 900; font-size: 1.1rem; color: #f0b860;
  letter-spacing: .05em;
}
.sidebar-name {
  font-family: 'Playfair Display', serif;
  font-size: .95rem; font-weight: 700;
  color: #fdf8f0 !important;
  letter-spacing: .04em;
}
.sidebar-ticker {
  font-family: 'DM Mono', monospace;
  font-size: .65rem; color: rgba(240,184,96,.7) !important;
  letter-spacing: .2em; text-transform: uppercase;
  margin-top: 2px;
}
.sidebar-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(200,135,42,.4), transparent);
  margin: 16px 0;
}

/* ── HERO ── */
.hero-wrap {
  background: linear-gradient(135deg, #0f1628 0%, #1a2340 30%, #1a2f3a 60%, #1a2820 100%);
  border-radius: 0 0 40px 40px;
  padding: 44px 52px 48px;
  margin: 0 -2.5rem 44px;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}
/* Animated gradient orbs */
.hero-wrap::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 600px 400px at 5% 50%, rgba(200,135,42,.12) 0%, transparent 60%),
    radial-gradient(ellipse 500px 300px at 95% 20%, rgba(13,115,119,.1) 0%, transparent 50%),
    radial-gradient(ellipse 300px 300px at 50% 100%, rgba(26,86,219,.08) 0%, transparent 50%);
  animation: orb-drift 8s ease-in-out infinite alternate;
}
@keyframes orb-drift {
  from { opacity: 1; transform: translateX(0); }
  to   { opacity: .7; transform: translateX(20px); }
}
/* Gold shimmer bottom line */
.hero-wrap::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent 0%, #c8872a 20%, #f0b860 50%, #c8872a 80%, transparent 100%);
  animation: shimmer-line 3s ease-in-out infinite;
}
@keyframes shimmer-line {
  0%, 100% { opacity: .6; }
  50% { opacity: 1; box-shadow: 0 0 12px rgba(240,184,96,.6); }
}
.hero-inner {
  position: relative;
  display: flex;
  align-items: center;
  gap: 32px;
}
.hero-logo-outer {
  width: 90px; height: 90px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, #c8872a 0%, #f0b860 25%, #c8872a 50%, #a06020 75%, #c8872a 100%);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  box-shadow: var(--glow-gold), 0 8px 32px rgba(200,135,42,.5);
  animation: hero-spin 16s linear infinite;
  position: relative;
}
@keyframes hero-spin { to { transform: rotate(360deg); } }
.hero-logo-inner {
  width: 76px; height: 76px;
  border-radius: 50%;
  background: linear-gradient(145deg, #0f1628, #1a2340);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Playfair Display', serif;
  font-weight: 900; font-size: 1.45rem; color: #f0b860;
  letter-spacing: .06em;
  text-shadow: 0 0 20px rgba(240,184,96,.5);
}
.hero-title {
  font-family: 'Playfair Display', serif;
  font-size: 3rem; font-weight: 900; color: #fdf8f0;
  margin: 0; line-height: 1.1;
  text-shadow: 0 2px 20px rgba(0,0,0,.3);
}
.hero-sub {
  font-family: 'DM Mono', monospace;
  font-size: .78rem;
  color: rgba(240,184,96,.75);
  margin: 8px 0 0;
  letter-spacing: .12em;
}
.hero-tags { margin-top: 14px; display: flex; flex-wrap: wrap; gap: 6px; }
.htag {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(240,184,96,.25);
  color: rgba(240,184,96,.85);
  padding: 4px 14px; border-radius: 20px;
  font-family: 'DM Mono', monospace; font-size: .68rem;
  letter-spacing: .08em;
  backdrop-filter: blur(4px);
  transition: all .2s;
}
.htag:hover {
  background: rgba(200,135,42,.2);
  border-color: rgba(240,184,96,.6);
  box-shadow: 0 0 12px rgba(200,135,42,.25);
}
.hero-right { margin-left: auto; text-align: right; flex-shrink: 0; }
.hero-price {
  font-family: 'Playfair Display', serif;
  font-size: 3.2rem; font-weight: 900; color: #fdf8f0;
  text-shadow: 0 0 30px rgba(255,255,255,.1);
  line-height: 1;
}
.hero-badge-up {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(26,122,74,.2);
  border: 1px solid rgba(74,222,128,.35);
  color: #4ade80;
  padding: 6px 18px; border-radius: 24px;
  font-family: 'DM Mono', monospace; font-size: .85rem;
  margin-top: 8px;
  box-shadow: var(--glow-green);
  animation: badge-pulse 2s ease-in-out infinite alternate;
}
.hero-badge-dn {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(192,57,43,.18);
  border: 1px solid rgba(248,113,113,.35);
  color: #f87171;
  padding: 6px 18px; border-radius: 24px;
  font-family: 'DM Mono', monospace; font-size: .85rem;
  margin-top: 8px;
  box-shadow: var(--glow-red);
  animation: badge-pulse 2s ease-in-out infinite alternate;
}
@keyframes badge-pulse {
  from { opacity: .9; }
  to   { opacity: 1; transform: scale(1.01); }
}
.filter-badge {
  display: inline-flex; align-items: center; gap: 8px;
  background: rgba(200,135,42,.15);
  border: 1px solid rgba(240,184,96,.35);
  color: rgba(240,184,96,.9);
  padding: 5px 16px; border-radius: 20px;
  font-family: 'DM Mono', monospace; font-size: .7rem;
  margin-top: 12px;
}
.fb-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #f0b860;
  box-shadow: 0 0 8px rgba(240,184,96,.8);
  animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: .2; } }

/* ── HERO STATS BAR ── */
.hero-stats-bar {
  display: flex;
  gap: 0;
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid rgba(240,184,96,.12);
  position: relative;
}
.hs-item {
  flex: 1;
  padding: 0 24px 0 0;
  position: relative;
}
.hs-item:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 12px; top: 10%; bottom: 10%;
  width: 1px;
  background: linear-gradient(180deg, transparent, rgba(240,184,96,.2), transparent);
}
.hs-label {
  font-family: 'DM Mono', monospace;
  font-size: .6rem; color: rgba(200,160,80,.6);
  text-transform: uppercase; letter-spacing: .16em;
  margin-bottom: 5px;
}
.hs-value {
  font-family: 'DM Sans', sans-serif;
  font-size: 1.05rem; font-weight: 600; color: #fdf8f0;
}
.hs-sub {
  font-family: 'DM Mono', monospace;
  font-size: .65rem; color: rgba(240,184,96,.5);
  margin-top: 2px;
}

/* ── SECTION TITLE ── */
.sec-title {
  display: flex; align-items: center; gap: 14px;
  margin: 40px 0 22px;
}
.sec-title-text {
  font-family: 'Playfair Display', serif;
  font-size: 1.3rem; font-weight: 700; color: var(--navy);
  white-space: nowrap;
}
.sec-title-accent {
  width: 6px; height: 24px; border-radius: 3px;
  background: linear-gradient(180deg, #f0b860, #c8872a);
  box-shadow: 0 0 8px rgba(200,135,42,.4);
  flex-shrink: 0;
}
.sec-title-line {
  flex: 1; height: 1px;
  background: linear-gradient(90deg, rgba(200,135,42,.25), transparent);
}
.sec-title-badge {
  font-family: 'DM Mono', monospace; font-size: .65rem;
  color: rgba(200,135,42,.7);
  background: rgba(200,135,42,.08);
  border: 1px solid rgba(200,135,42,.2);
  padding: 2px 10px; border-radius: 10px;
  letter-spacing: .1em;
  white-space: nowrap;
}

/* ── KPI CARDS ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 8px;
}
@media (max-width: 1200px) { .kpi-grid { grid-template-columns: repeat(3, 1fr); } }

.kpi-card {
  background: white;
  border-radius: 20px;
  padding: 24px 22px 20px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
  transition: transform .3s cubic-bezier(.34,1.56,.64,1), box-shadow .3s;
  position: relative; overflow: hidden;
  cursor: default;
}
.kpi-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--gold), var(--gold-light));
  opacity: 0;
  transition: opacity .3s;
}
.kpi-card::after {
  content: '';
  position: absolute;
  bottom: -60px; right: -30px;
  width: 120px; height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(200,135,42,.06), transparent 70%);
  transition: transform .4s, opacity .4s;
}
.kpi-card:hover { transform: translateY(-6px); box-shadow: var(--shadow-md); }
.kpi-card:hover::before { opacity: 1; }
.kpi-card:hover::after { transform: scale(1.5); opacity: .7; }

/* Card accent colors */
.kpi-card.accent-gold::before  { background: linear-gradient(90deg, #c8872a, #f0b860); }
.kpi-card.accent-green::before { background: linear-gradient(90deg, #1a7a4a, #4ade80); }
.kpi-card.accent-blue::before  { background: linear-gradient(90deg, #1a56db, #60a5fa); }
.kpi-card.accent-purple::before{ background: linear-gradient(90deg, #7c3aed, #c084fc); }
.kpi-card.accent-rose::before  { background: linear-gradient(90deg, #c0392b, #f87171); }
.kpi-card.accent-teal::before  { background: linear-gradient(90deg, #0d7377, #2dd4bf); }

.kpi-icon-wrap {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; margin-bottom: 14px;
  background: var(--gold-pale);
}
.kpi-label {
  font-family: 'DM Mono', monospace;
  font-size: .62rem; color: var(--muted);
  text-transform: uppercase; letter-spacing: .15em;
  margin-bottom: 7px;
}
.kpi-value {
  font-family: 'Playfair Display', serif;
  font-size: 1.65rem; font-weight: 700; color: var(--navy);
  line-height: 1.1;
}
.kpi-delta-up {
  color: var(--emerald);
  font-size: .78rem; font-family: 'DM Mono', monospace;
  margin-top: 7px; display: flex; align-items: center; gap: 4px;
}
.kpi-delta-dn {
  color: var(--rose);
  font-size: .78rem; font-family: 'DM Mono', monospace;
  margin-top: 7px; display: flex; align-items: center; gap: 4px;
}
.kpi-delta-nt {
  color: var(--muted);
  font-size: .75rem; font-family: 'DM Mono', monospace;
  margin-top: 7px;
}
.kpi-spark {
  position: absolute; bottom: 14px; right: 14px;
  font-size: .65rem; font-family: 'DM Mono', monospace;
  color: rgba(200,135,42,.4);
  letter-spacing: .08em;
}

/* ── CHART CARD ── */
.chart-card {
  background: white;
  border-radius: 24px;
  padding: 10px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  margin-bottom: 24px;
  transition: box-shadow .3s;
}
.chart-card:hover { box-shadow: var(--shadow-md); }

/* ── INSIGHT BOXES ── */
.insight-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-bottom: 28px;
}
.insight-box {
  background: white;
  border-radius: 16px;
  padding: 18px 20px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
  position: relative; overflow: hidden;
  transition: transform .2s, box-shadow .2s;
}
.insight-box:hover { transform: translateY(-3px); box-shadow: var(--shadow-sm); }
.insight-box-icon {
  font-size: 1.4rem; margin-bottom: 8px;
}
.insight-box-title {
  font-family: 'DM Mono', monospace;
  font-size: .65rem; color: var(--muted);
  text-transform: uppercase; letter-spacing: .14em;
  margin-bottom: 4px;
}
.insight-box-val {
  font-family: 'Playfair Display', serif;
  font-size: 1.25rem; font-weight: 700; color: var(--navy);
}
.insight-box-sub {
  font-family: 'DM Mono', monospace;
  font-size: .7rem; color: var(--muted);
  margin-top: 4px;
}
.insight-box-bar {
  position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--gold-light); border-radius: 3px; }

/* ── MISC ── */
div[data-testid="metric-container"] { display: none !important; }
[data-testid="stDataFrame"] { border-radius: 16px !important; overflow: hidden; }
[data-testid="stExpander"] {
  background: white !important;
  border: 1px solid var(--border) !important;
  border-radius: 18px !important;
}
hr { border-color: var(--border) !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── CHART TYPE RADIO ENHANCEMENT ── */
[data-testid="stSidebar"] .stRadio > div {
  display: flex; flex-direction: column; gap: 4px;
}
[data-testid="stSidebar"] .stRadio label {
  background: rgba(255,255,255,.04) !important;
  border: 1px solid rgba(240,184,96,.15) !important;
  border-radius: 8px !important;
  padding: 6px 12px !important;
  transition: all .2s !important;
  font-size: .75rem !important;
  text-transform: none !important;
  letter-spacing: .04em !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
  background: rgba(200,135,42,.1) !important;
  border-color: rgba(240,184,96,.4) !important;
}

/* ── DATA TABLE ENHANCEMENT ── */
.stDataFrame thead tr th {
  background: var(--navy) !important;
  color: #f0b860 !important;
  font-family: 'DM Mono', monospace !important;
  font-size: .68rem !important;
  letter-spacing: .12em !important;
  text-transform: uppercase !important;
}
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ──────────────────────────────────────────────────────────────
CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#fdfaf5",
    font=dict(family="DM Mono, monospace", color="#1a1a2e", size=11),
    xaxis=dict(gridcolor="#f0e8d8", showgrid=True, zeroline=False,
               tickfont=dict(size=10), linecolor="#e8dcc8",
               rangeslider=dict(visible=False)),
    yaxis=dict(gridcolor="#f0e8d8", showgrid=True, zeroline=False,
               tickfont=dict(size=10), linecolor="#e8dcc8"),
    margin=dict(l=60, r=35, t=55, b=45),
    legend=dict(bgcolor="rgba(255,255,255,.95)", bordercolor="#e8dcc8",
                borderwidth=1, font=dict(size=11),
                orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#1a2340", font_color="#fdf8f0",
                    font_family="DM Mono, monospace", font_size=12,
                    bordercolor="#c8872a", namelength=-1),
    transition=dict(duration=400, easing="cubic-in-out"),
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand logo section
    st.markdown("""
    <div class="sidebar-brand">
      <div class="sidebar-logo-outer">
        <div class="sidebar-logo-inner">RIL</div>
      </div>
      <div class="sidebar-name">Reliance Industries</div>
      <div class="sidebar-ticker">NSE · BSE: 500325</div>
    </div>
    <div class="sidebar-divider"></div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙ Controls")
    st.markdown("---")

    if date_col:
        tz    = df[date_col].dt.tz
        min_d = df[date_col].min()
        max_d = df[date_col].max()

        st.markdown("<p style='font-family:DM Mono,monospace;font-size:.65rem;color:rgba(240,184,96,.75);"
                    "letter-spacing:.16em;text-transform:uppercase;margin-bottom:6px;'>📅 Date Range</p>",
                    unsafe_allow_html=True)
        ca, cb = st.columns(2)
        with ca:
            start_date = st.date_input("From", value=min_d.date(),
                min_value=min_d.date(), max_value=max_d.date(), key="sd")
        with cb:
            end_date = st.date_input("To", value=max_d.date(),
                min_value=min_d.date(), max_value=max_d.date(), key="ed")

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        s = pd.Timestamp(start_date).tz_localize(tz) if tz else pd.Timestamp(start_date)
        e = pd.Timestamp(end_date).tz_localize(tz)   if tz else pd.Timestamp(end_date)
        df_f = df.loc[(df[date_col] >= s) & (df[date_col] <= e)].copy().reset_index(drop=True)
    else:
        df_f = df.copy()
        s = e = None

    rc = "#4ade80" if len(df_f) > 0 else "#f87171"
    st.markdown(f"""
    <div style='background:rgba(255,255,255,.04);border:1px solid rgba(240,184,96,.15);
    border-radius:10px;padding:8px 14px;margin:-4px 0 16px;display:flex;
    align-items:center;gap:8px;'>
      <span style='width:7px;height:7px;border-radius:50%;background:{rc};
      box-shadow:0 0 8px {rc};display:inline-block;flex-shrink:0;'></span>
      <span style='font-family:DM Mono,monospace;font-size:.68rem;color:{rc};'>
        {len(df_f):,} sessions loaded</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("<p style='font-family:DM Mono,monospace;font-size:.65rem;color:rgba(240,184,96,.75);"
                "letter-spacing:.16em;text-transform:uppercase;margin-bottom:6px;'>📊 Chart Style</p>",
                unsafe_allow_html=True)
    chart_type = st.radio(
        "Chart Style",
        ["Candlestick", "OHLC", "Line", "Area", "Scatter"],
        index=["Candlestick","OHLC","Line","Area","Scatter"].index(st.session_state.chart_type),
        key="chart_radio",
        label_visibility="collapsed"
    )
    st.session_state.chart_type = chart_type

    pill_clr = {"Candlestick":"#c8872a","OHLC":"#0d7377","Line":"#1a56db",
                "Area":"#7c3aed","Scatter":"#e11d48"}[chart_type]
    st.markdown(
        f"<div style='margin:6px 0 18px;'>"
        f"<span style='background:{pill_clr}22;border:1.5px solid {pill_clr};color:{pill_clr};"
        f"padding:4px 16px;border-radius:20px;font-family:DM Mono,monospace;"
        f"font-size:.67rem;font-weight:700;letter-spacing:.12em;"
        f"box-shadow:0 0 12px {pill_clr}33;display:inline-block;'>"
        f"● {chart_type.upper()} ACTIVE</span></div>",
        unsafe_allow_html=True
    )

    ma_options  = st.multiselect("📉 Moving Averages", ["MA 20","MA 50","MA 200"],
                                  default=["MA 20","MA 50"])
    show_volume = st.checkbox("📦 Volume Panel",    value=True)
    show_bb     = st.checkbox("〰 Bollinger Bands", value=False)
    show_rsi    = st.checkbox("📡 RSI Panel",       value=False)

    if ma_options:
        mc = {"MA 20":"#c8872a","MA 50":"#7c3aed","MA 200":"#0d7377"}
        st.markdown("<div style='margin:8px 0 4px;'>" + "".join(
            f"<span style='background:{mc[m]}18;border:1px solid {mc[m]}66;color:{mc[m]};"
            f"padding:3px 12px;border-radius:12px;font-family:DM Mono,monospace;"
            f"font-size:.64rem;margin:2px 3px 0 0;display:inline-block;"
            f"box-shadow:0 0 8px {mc[m]}22;'>◈ {m}</span>"
            for m in ma_options) + "</div>", unsafe_allow_html=True)

    st.markdown("---")
    # Info panel
    st.markdown("""
    <div style='background:rgba(255,255,255,.03);border:1px solid rgba(240,184,96,.12);
    border-radius:14px;padding:16px;'>
      <div style='font-family:DM Mono,monospace;font-size:.65rem;color:#c8b898;
      line-height:2.4;'>
        <div>🏦 <span style='color:#f0b860;'>Market Cap</span> ~₹19L Cr</div>
        <div>🌐 <span style='color:#f0b860;'>Sector</span> Conglomerates</div>
        <div>📍 <span style='color:#f0b860;'>HQ</span> Mumbai, India</div>
        <div>📅 <span style='color:#f0b860;'>Listed</span> 1977</div>
        <div>🏆 <span style='color:#f0b860;'>Index</span> NIFTY 50</div>
      </div>
    </div>""", unsafe_allow_html=True)

# ── Guard ─────────────────────────────────────────────────────────────────────
if df_f.empty:
    st.warning("⚠ No data for this date range — please widen the filter.")
    st.stop()

# ── Derived stats ─────────────────────────────────────────────────────────────
lc   = float(df_f[close_col].iloc[-1]) if close_col else 0
pc   = float(df_f[close_col].iloc[-2]) if (close_col and len(df_f) > 1) else None
dpct = ((lc - pc) / pc * 100) if pc else 0
dabs = (lc - pc) if pc else 0
arr  = "▲" if dpct >= 0 else "▼"
hh   = float(df_f[close_col].max()) if close_col else 0
hl   = float(df_f[close_col].min()) if close_col else 0
av   = df_f[vol_col].mean()/1e6 if vol_col else 0
num_cols = df_f.select_dtypes(include=[np.number]).columns.tolist()

# Price change over full period
period_chg = ((df_f[close_col].iloc[-1] - df_f[close_col].iloc[0]) / df_f[close_col].iloc[0] * 100) if close_col and len(df_f) > 1 else 0
# Volatility (annualised)
daily_std = df_f[close_col].pct_change().std() * 100 if close_col else 0
annl_vol = daily_std * np.sqrt(252)

db = ""
if s and e:
    db = (f"<span class='filter-badge'><span class='fb-dot'></span>"
          f"{pd.Timestamp(s).strftime('%d %b %Y')} → {pd.Timestamp(e).strftime('%d %b %Y')}"
          f" &nbsp;·&nbsp; {len(df_f):,} sessions</span>")

badge_cls = "hero-badge-up" if dpct >= 0 else "hero-badge-dn"

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-inner">
    <div class="hero-logo-outer">
      <div class="hero-logo-inner">RIL</div>
    </div>
    <div>
      <div class="hero-title">Reliance Industries</div>
      <div class="hero-sub">NSE: RELIANCE &nbsp;·&nbsp; BSE: 500325 &nbsp;·&nbsp; NIFTY 50 Component</div>
      <div class="hero-tags">
        <span class="htag">⚡ Energy</span>
        <span class="htag">🛒 Retail</span>
        <span class="htag">📡 Telecom</span>
        <span class="htag">⚗ Petrochem</span>
        <span class="htag">💻 Digital</span>
      </div>
      {db}
    </div>
    <div class="hero-right">
      <div class="hero-price">₹{lc:,.2f}</div>
      <div>
        <span class="{badge_cls}">
          {arr} ₹{abs(dabs):.2f} &nbsp; {arr} {abs(dpct):.2f}%
        </span>
      </div>
    </div>
  </div>

  <div class="hero-stats-bar">
    <div class="hs-item">
      <div class="hs-label">Period High</div>
      <div class="hs-value">₹{hh:,.2f}</div>
      <div class="hs-sub">52W High</div>
    </div>
    <div class="hs-item">
      <div class="hs-label">Period Low</div>
      <div class="hs-value">₹{hl:,.2f}</div>
      <div class="hs-sub">52W Low</div>
    </div>
    <div class="hs-item">
      <div class="hs-label">Avg Volume</div>
      <div class="hs-value">{av:.2f}M</div>
      <div class="hs-sub">Shares / Day</div>
    </div>
    <div class="hs-item">
      <div class="hs-label">Sessions</div>
      <div class="hs-value">{len(df_f):,}</div>
      <div class="hs-sub">Trading Days</div>
    </div>
    <div class="hs-item">
      <div class="hs-label">Period Return</div>
      <div class="hs-value" style="color:{'#4ade80' if period_chg>=0 else '#f87171'};">
        {'▲' if period_chg>=0 else '▼'} {abs(period_chg):.1f}%
      </div>
      <div class="hs-sub">vs Open</div>
    </div>
    <div class="hs-item">
      <div class="hs-label">Ann. Volatility</div>
      <div class="hs-value">{annl_vol:.1f}%</div>
      <div class="hs-sub">Std Dev ×√252</div>
    </div>
    <div class="hs-item">
      <div class="hs-label">Founded</div>
      <div class="hs-value">1973</div>
      <div class="hs-sub">51 yrs public</div>
    </div>
    <div class="hs-item">
      <div class="hs-label">Chairman</div>
      <div class="hs-value">M. Ambani</div>
      <div class="hs-sub">Reliance Group</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ── INSIGHT ROW (new!) ────────────────────────────────────────────────────────
if close_col and len(df_f) > 20:
    dr = df_f[close_col].pct_change() * 100
    best_day  = dr.max()
    worst_day = dr.min()
    pos_days  = (dr > 0).sum()
    neg_days  = (dr < 0).sum()
    win_rate  = pos_days / (pos_days + neg_days) * 100 if (pos_days + neg_days) > 0 else 0
    hl_spread = ((hh - hl) / hl * 100) if hl > 0 else 0

    st.markdown(f"""
    <div class="insight-row">
      <div class="insight-box">
        <div class="insight-box-icon">🏆</div>
        <div class="insight-box-title">Best Single Day</div>
        <div class="insight-box-val" style="color:#1a7a4a;">+{best_day:.2f}%</div>
        <div class="insight-box-sub">Largest 1-day gain in period</div>
        <div class="insight-box-bar" style="background:linear-gradient(90deg,#1a7a4a,#4ade80);"></div>
      </div>
      <div class="insight-box">
        <div class="insight-box-icon">📉</div>
        <div class="insight-box-title">Worst Single Day</div>
        <div class="insight-box-val" style="color:#c0392b;">{worst_day:.2f}%</div>
        <div class="insight-box-sub">Largest 1-day loss in period</div>
        <div class="insight-box-bar" style="background:linear-gradient(90deg,#c0392b,#f87171);"></div>
      </div>
      <div class="insight-box">
        <div class="insight-box-icon">🎯</div>
        <div class="insight-box-title">Win Rate</div>
        <div class="insight-box-val" style="color:{'#1a7a4a' if win_rate>=50 else '#c0392b'};">{win_rate:.1f}%</div>
        <div class="insight-box-sub">{pos_days} up days · {neg_days} down days</div>
        <div class="insight-box-bar" style="background:linear-gradient(90deg,#c8872a,#f0b860);"></div>
      </div>
    </div>""", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sec-title">
  <div class="sec-title-accent"></div>
  <div class="sec-title-text">Key Performance Indicators</div>
  <div class="sec-title-line"></div>
  <div class="sec-title-badge">LIVE VIEW</div>
</div>""", unsafe_allow_html=True)

kpis = []
if close_col:
    kpis += [
        ("📈", "Latest Close",  f"₹{df_f[close_col].iloc[-1]:,.2f}", f"{arr} {abs(dpct):.2f}% today", dpct>=0, "accent-gold",   "vs prev close"),
        ("🏔", "Period High",   f"₹{df_f[close_col].max():,.2f}",    None,                            True,    "accent-green",  f"in {len(df_f):,} sessions"),
        ("📉", "Period Low",    f"₹{df_f[close_col].min():,.2f}",    None,                            False,   "accent-rose",   f"in {len(df_f):,} sessions"),
        ("〰", "Average Close", f"₹{df_f[close_col].mean():,.2f}",   None,                            True,    "accent-blue",   "mean price"),
        ("📊", "Std Deviation", f"₹{df_f[close_col].std():,.2f}",    None,                            True,    "accent-purple", "daily dispersion"),
    ]
if vol_col:
    kpis.append(("📦","Avg Volume",f"{df_f[vol_col].mean()/1e6:.2f}M", None, True, "accent-teal", "shares per day"))

card_html = '<div class="kpi-grid">'
for icon, label, val, delta, up, accent, sub in kpis:
    if delta:
        dclass = "kpi-delta-up" if up else "kpi-delta-dn"
        darrow = "▲" if up else "▼"
        dhtml  = f'<div class="{dclass}">{darrow} {delta}</div>'
    else:
        dhtml  = f'<div class="kpi-delta-nt">{sub}</div>'

    card_html += f"""
    <div class="kpi-card {accent}">
      <div class="kpi-icon-wrap">{icon}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{val}</div>
      {dhtml}
    </div>"""
card_html += '</div>'
st.markdown(card_html, unsafe_allow_html=True)

# ── MAIN PRICE CHART ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="sec-title">
  <div class="sec-title-accent"></div>
  <div class="sec-title-text">Price Chart</div>
  <div class="sec-title-line"></div>
  <div class="sec-title-badge">{chart_type.upper()}</div>
</div>""", unsafe_allow_html=True)

nrows = 1 + (1 if show_volume and vol_col else 0) + (1 if show_rsi else 0)
rh    = [0.72] + ([0.14] if show_volume and vol_col else []) + ([0.14] if show_rsi else [])

fig = make_subplots(rows=nrows, cols=1, shared_xaxes=True,
                    vertical_spacing=0.02, row_heights=rh,
                    specs=[[{"secondary_y": False}]] * nrows)

if chart_type == "Candlestick":
    fig.add_trace(go.Candlestick(
        x=df_f[date_col], open=df_f[open_col], high=df_f[high_col],
        low=df_f[low_col], close=df_f[close_col], name="RELIANCE",
        increasing=dict(fillcolor="#1a7a4a", line=dict(color="#1a7a4a", width=1.3)),
        decreasing=dict(fillcolor="#c0392b", line=dict(color="#c0392b", width=1.3)),
        whiskerwidth=0.5,
    ), row=1, col=1)
elif chart_type == "OHLC":
    fig.add_trace(go.Ohlc(
        x=df_f[date_col], open=df_f[open_col], high=df_f[high_col],
        low=df_f[low_col], close=df_f[close_col], name="RELIANCE",
        increasing_line_color="#1a7a4a", decreasing_line_color="#c0392b"
    ), row=1, col=1)
elif chart_type == "Area":
    fig.add_trace(go.Scatter(
        x=df_f[date_col], y=df_f[close_col], name="Close", mode="lines",
        line=dict(color="#1a56db", width=2.8),
        fill="tozeroy", fillcolor="rgba(26,86,219,0.08)"
    ), row=1, col=1)
elif chart_type == "Scatter":
    colors = ["#1a7a4a" if c >= o else "#c0392b"
              for c, o in zip(df_f[close_col], df_f[open_col])]
    fig.add_trace(go.Scatter(
        x=df_f[date_col], y=df_f[close_col], name="Close", mode="markers",
        marker=dict(color=colors, size=5, opacity=0.75,
                    line=dict(width=0.5, color="rgba(255,255,255,.5)"))
    ), row=1, col=1)
else:  # Line
    fig.add_trace(go.Scatter(
        x=df_f[date_col], y=df_f[close_col], name="Close", mode="lines",
        line=dict(color="#1a56db", width=2.8)
    ), row=1, col=1)

# MAs
ma_clr = {"MA 20":"#c8872a","MA 50":"#7c3aed","MA 200":"#0d7377"}
for ma in ma_options:
    n = int(ma.split()[1])
    df_f[ma] = df_f[close_col].rolling(n).mean()
    fig.add_trace(go.Scatter(
        x=df_f[date_col], y=df_f[ma], name=ma, mode="lines",
        line=dict(color=ma_clr[ma], width=1.8, dash="dot")
    ), row=1, col=1)

# Bollinger
if show_bb:
    r = df_f[close_col].rolling(20); m2, sd = r.mean(), r.std()
    fig.add_trace(go.Scatter(x=df_f[date_col], y=m2+2*sd,
        line=dict(color="rgba(109,40,217,.5)", width=1.2, dash="dash"),
        name="BB Upper", showlegend=True), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_f[date_col], y=m2,
        line=dict(color="rgba(109,40,217,.4)", width=1, dash="dot"),
        name="BB Mid", showlegend=True), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_f[date_col], y=m2-2*sd,
        line=dict(color="rgba(109,40,217,.5)", width=1.2, dash="dash"),
        fill="tonexty", fillcolor="rgba(109,40,217,.04)",
        name="BB Lower", showlegend=True), row=1, col=1)

cur = 2
if show_volume and vol_col:
    vc = ["#1a7a4a" if c >= o else "#c0392b"
          for c, o in zip(df_f[close_col], df_f[open_col])]
    fig.add_trace(go.Bar(
        x=df_f[date_col], y=df_f[vol_col], name="Volume",
        marker_color=vc, opacity=0.65
    ), row=cur, col=1)
    fig.update_yaxes(title_text="Vol", row=cur, col=1,
                     gridcolor="#f0e8d8", tickfont=dict(size=9))
    cur += 1

if show_rsi:
    d_  = df_f[close_col].diff()
    g   = d_.clip(lower=0).rolling(14).mean()
    l_  = (-d_.clip(upper=0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + g / l_.replace(0, np.nan)))
    fig.add_trace(go.Scatter(x=df_f[date_col], y=rsi, name="RSI(14)",
        line=dict(color="#1a56db", width=2),
        fill="tozeroy", fillcolor="rgba(26,86,219,.04)"), row=cur, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#c0392b", line_width=1.2, row=cur, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#1a7a4a", line_width=1.2, row=cur, col=1)
    # Overbought/oversold zones
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(192,57,43,.03)",
                  line_width=0, row=cur, col=1)
    fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(26,122,74,.03)",
                  line_width=0, row=cur, col=1)
    fig.update_yaxes(title_text="RSI", range=[0,100], row=cur, col=1,
                     gridcolor="#f0e8d8", tickfont=dict(size=9))

h = 640 + (160 if show_volume and vol_col else 0) + (160 if show_rsi else 0)
fig.update_layout(
    **CHART, height=h, showlegend=True,
    xaxis_rangeslider_visible=False,
    title=dict(
        text=f"<b>RELIANCE INDUSTRIES</b>  <span style='font-size:13px;color:#c8872a;'>{chart_type} · {len(df_f):,} sessions</span>",
        font=dict(size=15, color="#1a2340", family="Playfair Display, serif"), x=0.01
    )
)
# Subtle background bands (weekend/off hours visual texture)
fig.update_xaxes(showspikes=True, spikecolor="#c8872a", spikethickness=1,
                 spikedash="dot", spikemode="across")
fig.update_yaxes(showspikes=True, spikecolor="rgba(200,135,42,.3)", spikethickness=1,
                 spikedash="dot")

st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── OPEN vs CLOSE + DAILY RETURNS ─────────────────────────────────────────────
st.markdown("""
<div class="sec-title">
  <div class="sec-title-accent"></div>
  <div class="sec-title-text">Open vs Close &amp; Daily Returns</div>
  <div class="sec-title-line"></div>
</div>""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    f2 = go.Figure()
    f2.add_trace(go.Scatter(
        x=df_f[date_col], y=df_f[open_col], name="Open",
        mode="lines", line=dict(color="#c8872a", width=2.2),
        fill="tonexty", fillcolor="rgba(200,135,42,.05)"
    ))
    f2.add_trace(go.Scatter(
        x=df_f[date_col], y=df_f[close_col], name="Close",
        mode="lines", line=dict(color="#1a56db", width=2.2),
    ))
    f2.update_layout(**CHART, height=330,
        title=dict(text="<b>Open vs Close</b>", font=dict(size=13, color="#1a2340",
        family="Playfair Display, serif"), x=0.02))
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(f2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    df_f["DR%"] = df_f[close_col].pct_change() * 100
    cr = ["#1a7a4a" if v >= 0 else "#c0392b" for v in df_f["DR%"].fillna(0)]
    f3 = go.Figure()
    f3.add_trace(go.Bar(
        x=df_f[date_col], y=df_f["DR%"], name="Daily Return %",
        marker=dict(color=cr, opacity=0.85,
                    line=dict(width=0.3, color="rgba(255,255,255,.4)"))
    ))
    # Add rolling avg line
    dr_roll = df_f["DR%"].rolling(10).mean()
    f3.add_trace(go.Scatter(
        x=df_f[date_col], y=dr_roll, name="10-Day Avg",
        mode="lines", line=dict(color="#c8872a", width=1.8, dash="dot")
    ))
    f3.update_layout(**CHART, height=330,
        title=dict(text="<b>Daily Return %</b>", font=dict(size=13, color="#1a2340",
        family="Playfair Display, serif"), x=0.02))
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(f3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── STATISTICAL ANALYSIS ──────────────────────────────────────────────────────
st.markdown("""
<div class="sec-title">
  <div class="sec-title-accent"></div>
  <div class="sec-title-text">Statistical Analysis</div>
  <div class="sec-title-line"></div>
</div>""", unsafe_allow_html=True)

c3, c4 = st.columns(2)
with c3:
    f4 = go.Figure()
    f4.add_trace(go.Histogram(
        x=df_f[close_col], nbinsx=40, name="Price Distribution",
        marker=dict(
            color=df_f[close_col].values,
            colorscale=[[0,"#c0392b"],[0.5,"#c8872a"],[1,"#1a56db"]],
            opacity=0.82,
            line=dict(color="white", width=0.5)
        ),
        hovertemplate="Price: ₹%{x:,.0f}<br>Count: %{y}<extra></extra>"
    ))
    # Add mean line
    mean_price = df_f[close_col].mean()
    f4.add_vline(x=mean_price, line_dash="dash", line_color="#c8872a", line_width=2,
                 annotation_text=f"Mean ₹{mean_price:,.0f}",
                 annotation_font=dict(color="#c8872a", size=10))
    f4.update_layout(**CHART, height=330,
        title=dict(text="<b>Close Price Distribution</b>",
        font=dict(size=13, color="#1a2340", family="Playfair Display, serif"), x=0.02))
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(f4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    if len(num_cols) >= 2:
        corr = df_f[num_cols].corr()
        f5 = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale=[
                [0.0, "#c0392b"], [0.3, "#f87171"], [0.45, "#fdf0d8"],
                [0.55, "#fdf8f0"], [0.7, "#93c5fd"], [1.0, "#1e3a6e"]
            ],
            text=np.round(corr.values, 2),
            texttemplate="<b>%{text}</b>",
            textfont=dict(size=11),
            showscale=True, zmin=-1, zmax=1,
            hoverongaps=False
        ))
        f5.update_layout(**CHART, height=330,
            title=dict(text="<b>Correlation Heatmap</b>",
            font=dict(size=13, color="#1a2340", family="Playfair Display, serif"), x=0.02))
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(f5, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── HIGH–LOW BAND ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="sec-title">
  <div class="sec-title-accent"></div>
  <div class="sec-title-text">High–Low Volatility Band</div>
  <div class="sec-title-line"></div>
</div>""", unsafe_allow_html=True)

f6 = go.Figure()
f6.add_trace(go.Scatter(
    x=df_f[date_col], y=df_f[high_col], name="High",
    mode="lines", line=dict(color="#1a7a4a", width=2),
    hovertemplate="High: ₹%{y:,.2f}<extra></extra>"
))
f6.add_trace(go.Scatter(
    x=df_f[date_col], y=df_f[low_col], name="Low", mode="lines",
    fill="tonexty", fillcolor="rgba(200,135,42,.07)",
    line=dict(color="#c0392b", width=2),
    hovertemplate="Low: ₹%{y:,.2f}<extra></extra>"
))
# Add close line on top
f6.add_trace(go.Scatter(
    x=df_f[date_col], y=df_f[close_col], name="Close",
    mode="lines", line=dict(color="#1a56db", width=1.5, dash="dot"),
    hovertemplate="Close: ₹%{y:,.2f}<extra></extra>"
))
f6.update_layout(**CHART, height=300,
    title=dict(text="<b>Daily High / Low Band</b>",
    font=dict(size=13, color="#1a2340", family="Playfair Display, serif"), x=0.02))
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.plotly_chart(f6, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── CUMULATIVE RETURN (new!) ──────────────────────────────────────────────────
if close_col and len(df_f) > 5:
    st.markdown("""
    <div class="sec-title">
      <div class="sec-title-accent"></div>
      <div class="sec-title-text">Cumulative Return</div>
      <div class="sec-title-line"></div>
      <div class="sec-title-badge">NEW</div>
    </div>""", unsafe_allow_html=True)

    cum_ret = ((df_f[close_col] / df_f[close_col].iloc[0]) - 1) * 100
    cum_color = "#1a7a4a" if cum_ret.iloc[-1] >= 0 else "#c0392b"
    fill_color = "rgba(26,122,74,.1)" if cum_ret.iloc[-1] >= 0 else "rgba(192,57,43,.08)"

    f7 = go.Figure()
    f7.add_hline(y=0, line_color="rgba(200,135,42,.4)", line_width=1.5, line_dash="dash")
    f7.add_trace(go.Scatter(
        x=df_f[date_col], y=cum_ret, name="Cumulative Return %",
        mode="lines", line=dict(color=cum_color, width=2.8),
        fill="tozeroy", fillcolor=fill_color,
        hovertemplate="Date: %{x}<br>Return: %{y:.2f}%<extra></extra>"
    ))
    f7.update_layout(**CHART, height=280,
        title=dict(
            text=f"<b>Cumulative Return</b>  "
                 f"<span style='color:{'#1a7a4a' if cum_ret.iloc[-1]>=0 else '#c0392b'};font-size:13px;'>"
                 f"{'▲' if cum_ret.iloc[-1]>=0 else '▼'} {abs(cum_ret.iloc[-1]):.1f}% total</span>",
            font=dict(size=13, color="#1a2340", family="Playfair Display, serif"), x=0.02
        ))
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(f7, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── RAW DATA ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sec-title">
  <div class="sec-title-accent"></div>
  <div class="sec-title-text">Raw Data</div>
  <div class="sec-title-line"></div>
</div>""", unsafe_allow_html=True)

with st.expander("📋 View Full Dataset", expanded=True):
    safe = [c for c in num_cols[:min(4, len(num_cols))] if df_f[c].notna().any()]
    try:
        styled = (df_f.style
                  .background_gradient(cmap="YlOrBr", subset=safe)
                  .format({c: "₹{:,.2f}" for c in safe if "vol" not in c.lower()})
                  ) if safe else df_f.style
        st.dataframe(styled, use_container_width=True, height=440)
    except Exception:
        st.dataframe(df_f, use_container_width=True, height=440)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.caption(f"📊 {len(df_f):,} rows × {df_f.shape[1]} columns")
    with col_b:
        st.caption(f"📅 {pd.Timestamp(s).strftime('%d %b %Y') if s else ''} → {pd.Timestamp(e).strftime('%d %b %Y') if e else ''}")
    with col_c:
        st.download_button("⬇ Export CSV", df_f.to_csv(index=False).encode(),
                           file_name="reliance_filtered.csv", mime="text/csv",
                           use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-top:60px;padding:28px 0 16px;
  border-top:1px solid rgba(200,135,42,.15);
  text-align:center;'>
  <div style='font-family:Playfair Display,serif;font-size:1.1rem;
    color:#1a2340;font-weight:700;margin-bottom:8px;letter-spacing:.04em;'>
    Reliance Stock Analytics
  </div>
  <div style='font-family:DM Mono,monospace;font-size:.68rem;color:#9ca3af;
    letter-spacing:.1em;'>
    Built with Python · Streamlit · Plotly &nbsp;◆&nbsp; Educational Use Only
  </div>
</div>""", unsafe_allow_html=True)