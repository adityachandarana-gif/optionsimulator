import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta, date, time as dtime
import math
import json
from scipy.stats import norm
import os
import random
import io
from fpdf import FPDF
import base64
import streamlit.components.v1 as components
from app_config import (
    BAR_MINUTES, BARS_PER_DAY, DEFAULT_OPEN_PRICE, HOLD_DAYS, PERSIST_PATH,
    SIM_DAYS, TICK_SECONDS_BASE, TOTAL_EXPIRY_DAYS, VOL_MAX, VOL_MIN,
    initialize_session_state,
)
from options_pricing import calculate_option_price, generate_option_chain, get_iv_surface
from trading_risk import calculate_realistic_margin, compute_position_greeks, consolidate_positions
from ui_styles import DASHBOARD_CSS, get_theme_css

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Option Market Simulator (Live Trading Simulator)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ GLOBAL CSS ============
APP_CSS = """
<style>
/* Hide default Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
.stApp > header { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }

/* Light professional background */
.stApp { background: #f4f6f9 !important; }
section.main > div { padding-top: 0 !important; }
div[data-testid="stAppViewContainer"] > div:first-child { padding-top: 0 !important; }

.main .block-container {
    padding-top: 52px !important;
    max-width: 100% !important;
    padding-left: 10px !important;
    padding-right: 10px !important;
}

/* Fixed header */
.fixed-header {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 999999;
    background: #0a2540;
    color: white;
    padding: 8px 18px;
    border-radius: 0 0 10px 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    text-align: left;
}
.fixed-header h1 {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.3px;
    color: #ffffff;
    line-height: 1.2;
}
.fixed-header p {
    margin: 2px 0 0 0;
    font-size: 11px;
    color: #a8c5e2;
    font-weight: 500;
    line-height: 1.2;
}

/* Two-column panels - light */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) > div {
    background: #f7f3eb;
    border-radius: 12px;
    padding: 12px 10px !important;
    border: 1px solid #e8e0d0;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div {
    background: #ffffff;
    border-radius: 12px;
    padding: 12px 14px !important;
    border: 1px solid #eaeaea;
}

/* Cards */
.card {
    background: #ffffff;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 12px;
    border: 1px solid #ebe5d8;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.card-beige {
    background: #faf7f0;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 12px;
    border: 1px solid #e8e0d0;
}

/* NIFTY */
.nifty-symbol {
    font-size: 12px;
    font-weight: 600;
    color: #666;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
    text-transform: uppercase;
}
.nifty-price {
    font-size: 26px;
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: 2px;
    font-variant-numeric: tabular-nums;
}
.nifty-up { color: #00a86b; }
.nifty-down { color: #e74c3c; }
.nifty-change {
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 4px;
    font-variant-numeric: tabular-nums;
}
.nifty-meta {
    font-size: 12px;
    color: #555;
    margin-top: 8px;
    line-height: 1.55;
}
.nifty-meta span {
    font-weight: 600;
    color: #222;
}

/* P&L rows */
.pnl-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 12px;
    border-radius: 10px;
    margin-bottom: 6px;
    background: #ffffff;
    border: 1px solid #ebe5d8;
}
.pnl-label {
    font-size: 12px;
    font-weight: 600;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
.pnl-value {
    font-size: 15px;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
}
.profit { color: #00a86b !important; }
.loss { color: #e74c3c !important; }

/* Buttons */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    border: none !important;
    transition: all 0.12s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(0,0,0,0.12);
}

.reset-btn-container button {
    background: #c0392b !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    padding: 8px 0 !important;
}

/* Tabs - Zerodha style light */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #ebf0f5;
    padding: 5px;
    border-radius: 8px;
    border: 1px solid #d6dee8;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    padding: 9px 16px;
    font-weight: 700;
    font-size: 13px;
    color: #444 !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #387ed1 !important;
    color: #ffffff !important;
    box-shadow: 0 2px 6px rgba(56,126,209,0.35);
}
.stTabs [data-baseweb="tab"]:hover {
    background: #dce6f5 !important;
    color: #1a1a1a !important;
}

/* Margin box */
.margin-box {
    background: #f8f9fb;
    border-radius: 10px;
    padding: 12px;
    margin: 10px 0;
    border: 1px solid #e8ecf0;
}
.margin-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    text-align: center;
}
.margin-label {
    font-size: 10px;
    color: #777;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
.margin-val {
    font-size: 14px;
    font-weight: 700;
    color: #222;
    margin-top: 2px;
    font-variant-numeric: tabular-nums;
}

/* Positions */
.pos-instrument {
    font-weight: 600;
    font-size: 14px;
    color: #1a1a1a;
}
.pos-meta {
    font-size: 12px;
    color: #777;
    margin-top: 2px;
}
.pos-side-buy { color: #00a86b; font-weight: 700; }
.pos-side-sell { color: #e74c3c; font-weight: 700; }

/* Section titles */
.section-title {
    font-size: 14px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 12px 0 8px 0;
    letter-spacing: 0.2px;
}
.subsection-title {
    font-size: 13px;
    font-weight: 700;
    color: #333;
    margin: 8px 0 6px 0;
}

/* Greek boxes */
.greek-box {
    display: inline-block;
    background: #f0f4f8;
    border-radius: 6px;
    padding: 5px 10px;
    margin: 3px 4px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid #e0e6ed;
}
.greek-label {
    color: #777;
    font-size: 10px;
    text-transform: uppercase;
    margin-right: 4px;
}

.status-banner {
    background: #fff8e6;
    border-left: 4px solid #f0b429;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 10px;
    font-size: 13px;
    font-weight: 600;
    color: #7a5c00;
}

.stSelectbox label, .stNumberInput label, .stSlider label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #444 !important;
}
div[data-testid="stMetricValue"] {
    font-size: 17px;
}
</style>
"""

st.markdown(APP_CSS, unsafe_allow_html=True)
st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)


# ============ SESSION STATE INIT ============
# ============ SIMULATION CONSTANTS ============
initialize_session_state(st.session_state)
st.markdown(get_theme_css(st.session_state.theme_mode), unsafe_allow_html=True)

# ============ HELPER / CACHED FUNCTIONS ============

def _add_day_num(df):
    """Tag each bar with a 1-based sequential trading-day number (Day-1, Day-2, ...)."""
    if df is None or len(df) == 0:
        return df
    df = df.copy()
    df['day_num'] = pd.factorize(df['datetime'].dt.date)[0] + 1
    return df


def _parse_raw_lines(lines):
    """Parse whitespace/tab-delimited OHLCV lines: SYMBOL DATE TIME O H L C VOL."""
    records = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t') if '\t' in line else line.split()
        if len(parts) >= 8:
            try:
                dt = datetime.strptime(f"{parts[1]} {parts[2]}", "%Y%m%d %H:%M")
                records.append({
                    'symbol': parts[0], 'datetime': dt,
                    'open': float(parts[3]), 'high': float(parts[4]),
                    'low': float(parts[5]), 'close': float(parts[6]),
                    'volume': int(parts[7]) if str(parts[7]).isdigit() else 0
                })
            except Exception:
                continue
    return pd.DataFrame(records) if records else None


@st.cache_data(ttl=300)
def load_data_from_path(file_path):
    """Load OHLCV data from a file path on disk."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        return _parse_raw_lines(lines)
    except Exception:
        return None


def load_data_from_upload(uploaded_file):
    """Load OHLCV data from a Streamlit UploadedFile."""
    try:
        text = uploaded_file.getvalue().decode('utf-8', errors='ignore')
        return _parse_raw_lines(text.splitlines())
    except Exception:
        return None


def resample_to_bars(df, bar_minutes=BAR_MINUTES):
    """Collapse a finer-grained OHLCV frame down to fixed-width bars."""
    if df is None or len(df) == 0:
        return df
    d = df.set_index('datetime').sort_index()
    agg = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}
    if 'volume' in d.columns:
        agg['volume'] = 'sum'
    out = d.resample(f'{bar_minutes}min').agg(agg).dropna(subset=['open', 'close']).reset_index()
    return out


def calculate_scale_factor(df, target_level=DEFAULT_OPEN_PRICE):
    if df is not None and len(df) > 0:
        avg_price = df['close'].mean()
        if avg_price > 0:
            return target_level / avg_price
    return 1.0


def scale_data(df, scale_factor):
    if df is not None and scale_factor != 1.0:
        df_scaled = df.copy()
        for col in ['open', 'high', 'low', 'close']:
            if col in df_scaled.columns:
                df_scaled[col] = df_scaled[col] * scale_factor
        return df_scaled
    return df


# ---------- Default path-generation model: discrete-time GARCH(1,1) ----------
# 5-minute bars, annualized volatility band-constrained to [VOL_MIN, VOL_MAX],
# with a random overnight/day-open gap so each session doesn't open at the
# prior session's close (mimics a real market open).

def _simulate_garch_bar_returns(n_bars, bars_per_year, vol_min, vol_max, rng):
    """GARCH(1,1) variance recursion, soft-clipped so annualized vol stays in band."""
    sigma_bar_target = ((vol_min + vol_max) / 2) / np.sqrt(bars_per_year)
    sigma_min = vol_min / np.sqrt(bars_per_year)
    sigma_max = vol_max / np.sqrt(bars_per_year)
    alpha, beta = 0.10, 0.85          # persistence -> volatility clustering
    long_run_var = sigma_bar_target ** 2
    omega = long_run_var * (1 - alpha - beta)

    sigma2 = long_run_var
    prev_r = 0.0
    returns = np.empty(n_bars)
    for i in range(n_bars):
        sigma2 = omega + alpha * prev_r ** 2 + beta * sigma2
        sigma = float(np.clip(np.sqrt(sigma2), sigma_min, sigma_max))
        r = sigma * rng.standard_normal()
        returns[i] = r
        prev_r = r
    return returns


@st.cache_data(ttl=600)
def generate_garch_week_path(start_date, open_price=DEFAULT_OPEN_PRICE, bars_per_day=BARS_PER_DAY,
                              days=SIM_DAYS, vol_min=VOL_MIN, vol_max=VOL_MAX,
                              bar_minutes=BAR_MINUTES, gap_sd=0.004, seed=None):
    """Simulate a one-week 5-minute NIFTY-like path via GARCH(1,1), with gapped daily opens."""
    rng = np.random.default_rng(seed)
    bars_per_year = bars_per_day * 252

    records = []
    cur_date = start_date
    this_open = open_price
    # Implied "previous close" before day 0, so the very first bar also opens on a gap.
    first_gap = rng.normal(0, gap_sd)
    prev_close = open_price / (1 + first_gap)

    for d in range(days):
        gap = first_gap if d == 0 else rng.normal(0, gap_sd)
        this_open = prev_close * (1 + gap)

        returns = _simulate_garch_bar_returns(bars_per_day, bars_per_year, vol_min, vol_max, rng)
        closes = this_open * np.exp(np.cumsum(returns))
        opens = np.concatenate([[this_open], closes[:-1]])

        base_dt = datetime.combine(cur_date, dtime(9, 15))
        wobble = np.abs(rng.normal(0, closes * 0.0004))  # small intrabar high/low noise
        for i in range(bars_per_day):
            o, c = float(opens[i]), float(closes[i])
            hi = max(o, c) + float(wobble[i])
            lo = min(o, c) - float(wobble[i])
            records.append({
                'symbol': 'NIFTY',
                'datetime': base_dt + timedelta(minutes=bar_minutes * (i + 1)),
                'open': round(o, 2), 'high': round(hi, 2),
                'low': round(lo, 2), 'close': round(c, 2),
                'volume': int(rng.integers(500, 5000))
            })
        prev_close = float(closes[-1])
        cur_date = cur_date + timedelta(days=1)  # continuous — all 5 days are treated as trading days

    return pd.DataFrame(records), round(first_gap, 6), round(open_price / (1 + first_gap), 2)

# ---------- IV smile + term-structure surface ----------
# ATM vol rises modestly as expiry nears (front-month effect), and the
# put/call skew (higher IV for OTM puts, lower for OTM calls) steepens
# the closer we get to expiry -- both standard equity-index features.
def legacy_get_iv_surface(strike, spot, T):
    """Return IV (%) for a given strike/spot/time-to-expiry, with smile + term structure."""
    days_left = max(T * 365, 0.1)
    moneyness_pct = (strike - spot) / max(spot, 1) * 100  # + = OTM call side, - = OTM put side
    term_scale = 1.0 / math.sqrt(days_left + 1)

    atm_iv = BASE_ATM_IV + TERM_COEFF * term_scale
    skew = (-SKEW_SLOPE * moneyness_pct + SKEW_CURV * moneyness_pct ** 2) * term_scale
    iv = atm_iv + skew
    return round(min(max(iv, 8.0), 60.0), 2)

def legacy_calculate_option_price(S, K, T, r, q, sigma, option_type='call'):
    MIN_PRICE = 0.05  # exchange tick floor -- live prices never show as zero
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        intrinsic = max(S - K, 0) if option_type == 'call' else max(K - S, 0)
        return max(intrinsic, MIN_PRICE), 0.0, 0.0, 0.0, 0.0
    try:
        d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        if option_type == 'call':
            price = S * math.exp(-q * T) * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
            delta = math.exp(-q * T) * norm.cdf(d1)
        else:
            price = K * math.exp(-r * T) * norm.cdf(-d2) - S * math.exp(-q * T) * norm.cdf(-d1)
            delta = -math.exp(-q * T) * norm.cdf(-d1)
        gamma = math.exp(-q * T) * norm.pdf(d1) / (S * sigma * math.sqrt(T))
        theta = (-(S * sigma * math.exp(-q * T) * norm.pdf(d1)) / (2 * math.sqrt(T))
                 - r * K * math.exp(-r * T) * (norm.cdf(d2) if option_type == 'call' else norm.cdf(-d2))
                 + q * S * math.exp(-q * T) * (norm.cdf(d1) if option_type == 'call' else -norm.cdf(-d1)))
        vega = S * math.exp(-q * T) * math.sqrt(T) * norm.pdf(d1) / 100
        return max(price, MIN_PRICE), delta, gamma, theta / 365, vega
    except Exception:
        return MIN_PRICE, 0.0, 0.0, 0.0, 0.0

def legacy_generate_option_chain(spot_price, prev_spot, T):
    base_strike = round(spot_price / 100) * 100
    strikes = list(range(int(base_strike) - 500, int(base_strike) + 600, 100))
    chain_data = []
    for strike in strikes:
        iv = get_iv_surface(strike, spot_price, T) / 100
        call_price, call_delta, call_gamma, call_theta, call_vega = calculate_option_price(
            spot_price, strike, T, 0.068, 0.014, iv, 'call')
        put_price, put_delta, put_gamma, put_theta, put_vega = calculate_option_price(
            spot_price, strike, T, 0.068, 0.014, iv, 'put')
        prev_call, _, _, _, _ = calculate_option_price(prev_spot, strike, T + 1/365, 0.068, 0.014, iv, 'call')
        prev_put, _, _, _, _ = calculate_option_price(prev_spot, strike, T + 1/365, 0.068, 0.014, iv, 'put')
        call_pct = ((call_price - prev_call) / prev_call * 100) if prev_call > 0.1 else 0
        put_pct = ((put_price - prev_put) / prev_put * 100) if prev_put > 0.1 else 0
        chain_data.append({
            'Strike': strike,
            'CE Price': round(call_price, 2),
            'CE %': f"{call_pct:+.1f}%",
            'CE Δ': round(call_delta, 3),
            'CE Γ': round(call_gamma, 4),
            'PE Price': round(put_price, 2),
            'PE %': f"{put_pct:+.1f}%",
            'PE Δ': round(put_delta, 3),
            'PE Γ': round(put_gamma, 4),
            'IV %': round(iv * 100, 1)
        })
    return pd.DataFrame(chain_data)

def get_time_to_expiry(current_dt, expiry_dt):
    """Precise fractional year to expiry -- exact elapsed seconds, not rounded to whole days."""
    seconds_left = (expiry_dt - current_dt).total_seconds()
    min_seconds = 60  # floor at 1 minute so pricing never divides by ~0
    return max(seconds_left, min_seconds) / (365 * 24 * 3600)

def create_chart(bar_data, current_price, session_start=None):
    """Candlestick chart of the 5-minute bars revealed so far, labeled Day-1..Day-N
    on a category axis so there is never a gap/break between sessions."""
    fig = go.Figure()
    if len(bar_data) > 0:
        if 'day_num' in bar_data.columns:
            x_labels = bar_data.apply(lambda r: f"Day-{int(r['day_num'])} {r['datetime'].strftime('%H:%M')}", axis=1)
        else:
            x_labels = bar_data['datetime'].dt.strftime('%H:%M')
        fig.add_trace(go.Candlestick(
            x=x_labels,
            open=bar_data['open'], high=bar_data['high'],
            low=bar_data['low'], close=bar_data['close'],
            name="NIFTY",
            increasing_line_color='#00a86b',
            decreasing_line_color='#e74c3c',
            line_width=1, showlegend=False, whiskerwidth=0.3
        ))
    fig.add_hline(y=current_price, line_dash="dash", line_color="#0a2540", opacity=0.4, line_width=1)
    fig.update_layout(
        template='plotly_white',
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(type='category', rangeslider=dict(visible=True, thickness=0.06),
                   gridcolor='#f0f0f0', nticks=12),
        yaxis=dict(gridcolor='#f0f0f0', tickformat=',.2f'),
        font=dict(size=11),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig

def legacy_compute_position_greeks(positions, spot, T, r=0.068, q=0.014):
    net = {'delta': 0.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0}
    for pos in positions:
        iv = get_iv_surface(pos['strike'], spot, T) / 100
        opt = 'call' if pos['type'] == 'CE' else 'put'
        _, delta, gamma, theta, vega = calculate_option_price(spot, pos['strike'], T, r, q, iv, opt)
        sign = 1 if pos['side'] == 'Buy' else -1
        qty = pos.get('quantity', st.session_state.lot_size)
        net['delta'] += sign * delta * qty
        net['gamma'] += sign * gamma * qty
        net['theta'] += sign * theta * qty
        net['vega'] += sign * vega * qty
    return net

def legacy_consolidate_positions(positions, current_price, T_current, chain_df):
    consolidated = {}
    for pos in positions:
        key = f"{pos['strike']}_{pos['type']}"
        if key not in consolidated:
            consolidated[key] = {
                'strike': pos['strike'], 'type': pos['type'],
                'net_qty': 0, 'total_cost': 0.0, 'entries': []
            }
        sign = 1 if pos['side'] == 'Buy' else -1
        qty = pos.get('quantity', st.session_state.lot_size)
        price = pos['entry_price']
        consolidated[key]['net_qty'] += sign * qty
        consolidated[key]['total_cost'] += sign * qty * price
        consolidated[key]['entries'].append({'side': pos['side'], 'qty': qty, 'price': price})

    result = []
    for key, data in consolidated.items():
        if data['net_qty'] != 0:
            avg_price = data['total_cost'] / data['net_qty'] if data['net_qty'] != 0 else 0
            row = chain_df[chain_df['Strike'] == data['strike']] if chain_df is not None else pd.DataFrame()
            cur_px = 0.0
            if len(row) > 0:
                cur_px = float(row.iloc[0]['CE Price'] if data['type'] == 'CE' else row.iloc[0]['PE Price'])
            pnl = (cur_px - avg_price) * data['net_qty']
            result.append({
                'strike': data['strike'], 'type': data['type'],
                'net_qty': data['net_qty'], 'avg_price': avg_price,
                'current_price': cur_px, 'pnl': pnl,
                'side': 'Buy' if data['net_qty'] > 0 else 'Sell'
            })
    return result

def legacy_calculate_realistic_margin(items, spot, lot_size):
    """
    Broker-style margin: per-leg naked rates with spread benefit.
    - Long options: premium only (already paid) – no extra margin.
    - Short naked: higher of (premium * 3) or 10% notional + SPAN-like add-on.
    - Vertical spreads (same type, different strikes): reduced defined-risk margin.
    - Short straddle/strangle: modest offset benefit.
    """
    if not items:
        return 0.0

    legs = {}
    for item in items:
        key = (item['strike'], item['type'])
        qty = item.get('quantity', item.get('lots', 1) * lot_size)
        sign = 1 if item['side'] == 'Buy' else -1
        prem = float(item.get('price', item.get('entry_price', 0)))
        if key not in legs:
            legs[key] = {'qty': 0, 'premium': prem}
        legs[key]['qty'] += sign * qty
        legs[key]['premium'] = prem

    total_margin = 0.0
    short_legs = []
    for (strike, typ), data in legs.items():
        qty = data['qty']
        prem = data['premium']
        if qty > 0:
            pass  # long: premium already paid, no margin add
        elif qty < 0:
            short_legs.append({'strike': strike, 'type': typ, 'qty': abs(qty), 'premium': prem})

    used = set()
    for i, a in enumerate(short_legs):
        if i in used:
            continue
        paired = False
        for j, b in enumerate(short_legs):
            if j <= i or j in used:
                continue
            if a['type'] == b['type'] and a['strike'] != b['strike']:
                width = abs(a['strike'] - b['strike'])
                qty = min(a['qty'], b['qty'])
                total_margin += width * qty * 0.15 + max(a['premium'], b['premium']) * qty
                used.add(i)
                used.add(j)
                paired = True
                break
        if not paired:
            notional = a['strike'] * a['qty']
            total_margin += max(a['premium'] * a['qty'] * 3.0, notional * 0.10) + spot * 0.015 * a['qty']
            used.add(i)

    remaining = [s for idx, s in enumerate(short_legs) if idx not in used]
    ce_short = sum(s['qty'] for s in remaining if s['type'] == 'CE')
    pe_short = sum(s['qty'] for s in remaining if s['type'] == 'PE')
    if ce_short > 0 and pe_short > 0:
        offset_qty = min(ce_short, pe_short)
        total_margin = max(0.0, total_margin - offset_qty * spot * 0.005)

    return round(max(total_margin, 0), 0)


def _json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Type {type(obj)} not serializable")


def save_session_state():
    """Persist key trading state so a browser refresh does not wipe the session."""
    keys = [
        'current_index', 'playing', 'speed', 'basket', 'positions', 'tradebook',
        'pending_limits', 'realized_pnl', 'max_reached_index', 'data_loaded',
        'prev_day_close', 'start_time', 'session_end', 'expiry_dt', 'scale_factor',
        'lot_size', 'prev_scaled_close', 'trading_locked', 'session_finished',
        'report_generated', 'report_path', 'current_price', 'T_current',
        'starting_capital', 'peak_margin_used', 'session_start_wall',
        'data_source_choice', 'day_close_map', 'target_nifty_level'
    ]
    payload = {}
    for k in keys:
        if k in st.session_state:
            v = st.session_state[k]
            if isinstance(v, (datetime, date)):
                payload[k] = v.isoformat()
            else:
                try:
                    json.dumps(v, default=_json_serial)
                    payload[k] = v
                except Exception:
                    pass
    if st.session_state.get('simulated_data') is not None:
        try:
            df = st.session_state.simulated_data
            payload['_sim_records'] = df.to_dict(orient='records')
        except Exception:
            pass
    try:
        with open(PERSIST_PATH, 'w') as f:
            json.dump(payload, f, default=_json_serial)
    except Exception:
        pass


def load_session_state():
    """Restore previously saved session if available."""
    if not os.path.exists(PERSIST_PATH):
        return False
    try:
        with open(PERSIST_PATH, 'r') as f:
            payload = json.load(f)
    except Exception:
        return False
    if not payload.get('data_loaded'):
        return False
    if '_sim_records' in payload:
        try:
            recs = payload.pop('_sim_records')
            df = pd.DataFrame(recs)
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
            st.session_state.simulated_data = df
            st.session_state.df_day_scaled = df
            st.session_state.df_raw = df
        except Exception:
            return False
    for k, v in payload.items():
        if k in ('start_time', 'session_end', 'expiry_dt', 'session_start_wall'):
            try:
                st.session_state[k] = datetime.fromisoformat(v) if v else None
            except Exception:
                st.session_state[k] = v
        else:
            st.session_state[k] = v
    if 'cart' in st.session_state and not st.session_state.get('basket'):
        st.session_state.basket = st.session_state.pop('cart', [])
    return True


HOLD_DAYS = 22

def get_trading_day_offsets(n_days, anchor_date=None):
    """Calendar-day offsets (1, 2, 3, ...) that fall on a real weekday, skipping
    Sat/Sun, keeping their original offset number -- e.g. 1,2,3,4,5,8,9,10,11,12,..."""
    anchor = anchor_date or date.today()
    offsets = []
    d = 0
    while len(offsets) < n_days:
        d += 1
        if (anchor + timedelta(days=d)).weekday() < 5:
            offsets.append(d)
    return offsets

def compute_hold_to_expiry_table(spot, hold_days=HOLD_DAYS):
    """
    For every CLOSED position: reprice day-by-day as if it had been held instead
    of exited, using the current spot and the IV surface at that day's residual
    maturity. Day offsets skip real Saturdays/Sundays (provision for weekend
    market holidays) while keeping their original calendar-day numbering, e.g.
    1,2,3,4,5,8,9,10,11,12,... Last row is what the user actually realized on exit.
    """
    closed = [t for t in st.session_state.tradebook if t['status'] == 'Closed']
    if not closed:
        return None, []

    day_offsets = get_trading_day_offsets(hold_days)

    labels, columns = [], []
    for i, t in enumerate(closed):
        label = f"{i+1}. {t['strike']}{t['type']} {t['side']}"
        labels.append(label)
        opt = 'call' if t['type'] == 'CE' else 'put'
        sign = 1 if t['side'] == 'Buy' else -1
        qty = t['qty']
        col = []
        for d in day_offsets:
            T_d = d / 365
            iv_d = get_iv_surface(t['strike'], spot, T_d) / 100
            price_d, *_ = calculate_option_price(spot, t['strike'], T_d, 0.068, 0.014, iv_d, opt)
            col.append(sign * (price_d - t['entry_price']) * qty)
        col.append(t['pnl'])  # actual realized P&L, as the final row
        columns.append(col)

    index = [f"Day {d}" for d in day_offsets] + ["Actual (Exit)"]
    table = pd.DataFrame({lbl: col for lbl, col in zip(labels, columns)}, index=index)
    return table, labels

def generate_pdf_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Option Market Simulator - Performance Report", ln=True, align="C")
    pdf.ln(8)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Date: {date.today().strftime('%d-%m-%Y')}", ln=True)
    pdf.cell(0, 8, f"Total Trades: {len(st.session_state.tradebook)}", ln=True)
    pdf.ln(4)
    closed_pnl = sum(t['pnl'] for t in st.session_state.tradebook if t['status'] == 'Closed')
    open_pnl = 0.0
    if st.session_state.positions and st.session_state.chain_df is not None:
        cons = consolidate_positions(st.session_state.positions, st.session_state.current_price,
                                     st.session_state.T_current, st.session_state.chain_df)
        open_pnl = sum(p['pnl'] for p in cons)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "P&L Summary", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Realized P&L: {closed_pnl:+.2f}", ln=True)
    pdf.cell(0, 7, f"Open P&L: {open_pnl:+.2f}", ln=True)
    pdf.cell(0, 7, f"Total P&L: {closed_pnl + open_pnl:+.2f}", ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Tradebook", ln=True)
    pdf.set_font("Arial", "B", 9)
    for col, w in [("Time", 25), ("Instrument", 30), ("Side", 18), ("Qty", 18), ("Entry", 25), ("Exit", 25), ("P&L", 25)]:
        pdf.cell(w, 7, col, 1)
    pdf.ln()
    pdf.set_font("Arial", "", 8)
    for t in st.session_state.tradebook:
        pdf.cell(25, 6, t['entry_time'], 1)
        pdf.cell(30, 6, f"{t['strike']} {t['type']}", 1)
        pdf.cell(18, 6, t['side'], 1)
        pdf.cell(18, 6, str(t['qty']), 1)
        pdf.cell(25, 6, f"{t['entry_price']:.2f}", 1)
        pdf.cell(25, 6, f"{t['exit_price']:.2f}" if t['status'] == 'Closed' else "-", 1)
        pdf.cell(25, 6, f"{t['pnl']:+.2f}" if t['status'] == 'Closed' else "Open", 1)
        pdf.ln()

    # Hold-to-Day-22 hypothetical table
    hold_table, labels = compute_hold_to_expiry_table(st.session_state.current_price)
    if hold_table is not None:
        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Hypothetical P&L if Held {HOLD_DAYS} Days (vs Actual Exit)", ln=True)
        pdf.set_font("Arial", "", 8)
        pdf.multi_cell(0, 5, "Columns: " + " | ".join(labels))
        pdf.ln(1)
        n_cols = len(labels)
        col_w = min(28, max(18, 180 // max(n_cols, 1)))
        pdf.set_font("Arial", "B", 8)
        pdf.cell(22, 6, "Row", 1)
        for i in range(n_cols):
            pdf.cell(col_w, 6, f"Pos {i+1}", 1)
        pdf.ln()
        pdf.set_font("Arial", "", 7)
        for row_label, row in hold_table.iterrows():
            pdf.cell(22, 6, row_label, 1)
            for val in row:
                pdf.cell(col_w, 6, f"{val:+.1f}", 1)
            pdf.ln()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"performance_report_{timestamp}.pdf"
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    try:
        pdf.output(filepath)
    except Exception:
        filepath = os.path.join("/tmp", filename)
        pdf.output(filepath)
    return filepath, filename


def _settle_all_cash(spot, current_dt):
    """Cash-settle every open position at intrinsic value and clear the book."""
    if not st.session_state.positions:
        return
    realized_add = 0.0
    for pos in list(st.session_state.positions):
        intrinsic = max(spot - pos['strike'], 0.0) if pos['type'] == 'CE' else max(pos['strike'] - spot, 0.0)
        for t in st.session_state.tradebook:
            if (t['strike'] == pos['strike'] and t['type'] == pos['type']
                    and t['status'] == 'Open' and t['side'] == pos['side']):
                t['exit_time'] = current_dt.strftime('%H:%M:%S')
                t['exit_price'] = intrinsic
                sign = 1 if t['side'] == 'Buy' else -1
                t['pnl'] = sign * (t['exit_price'] - t['entry_price']) * t['qty']
                t['status'] = 'Closed'
                realized_add += t['pnl']
                break
    st.session_state.realized_pnl += realized_add
    st.session_state.positions = []


def match_pending_limits(current_price, current_dt, chain_df, lot_size):
    """
    Re-evaluate pending LIMIT orders against the live option chain LTP.
    Fills marketable orders (BUY if limit >= LTP, SELL if limit <= LTP).
    Fill price = limit price (standard limit fill convention).
    Returns number of fills.
    """
    if not st.session_state.pending_limits or chain_df is None or st.session_state.trading_locked:
        return 0
    still_pending = []
    filled = 0
    for item in st.session_state.pending_limits:
        row = chain_df[chain_df['Strike'] == item['strike']]
        if len(row) == 0:
            still_pending.append(item)
            continue
        ltp = float(row.iloc[0]['CE Price'] if item['type'] == 'CE' else row.iloc[0]['PE Price'])
        item['ltp'] = ltp
        marketable = (item['side'] == 'Buy' and item['price'] >= ltp) or                      (item['side'] == 'Sell' and item['price'] <= ltp)
        if not marketable:
            still_pending.append(item)
            continue
        # Margin check before fill
        trial = list(st.session_state.positions) + [item]
        req = calculate_realistic_margin(trial, current_price, lot_size)
        if req > st.session_state.starting_capital:
            still_pending.append(item)  # keep pending if margin insufficient
            continue
        # Fill at limit price
        st.session_state.positions.append({
            'strike': item['strike'],
            'type': item['type'],
            'side': item['side'],
            'entry_price': item['price'],
            'quantity': item['quantity'],
            'lots': item['lots']
        })
        st.session_state.tradebook.append({
            'entry_time': current_dt.strftime('%H:%M:%S'),
            'strike': item['strike'],
            'type': item['type'],
            'side': item['side'],
            'qty': item['quantity'],
            'entry_price': item['price'],
            'exit_time': '-',
            'exit_price': 0.0,
            'pnl': 0.0,
            'status': 'Open'
        })
        filled += 1
    st.session_state.pending_limits = still_pending
    if filled:
        margin_now = calculate_realistic_margin(st.session_state.positions, current_price, lot_size)
        if margin_now > st.session_state.peak_margin_used:
            st.session_state.peak_margin_used = margin_now
        save_session_state()
    return filled


# ============ MAIN APP ============
def main():
    # Try restore persisted session on first load
    if not st.session_state.data_loaded:
        load_session_state()

    # Fixed Header
    st.markdown("""
    <div class="fixed-header">
        <div class="brand-line">
            <h1>Option Market Simulator</h1>
            <span class="environment-badge">SIMULATED MARKET</span>
        </div>
        <p>Developed by Prof. Bhavesh (IMNU) for classroom use only</p>
    </div>
    """, unsafe_allow_html=True)

    theme_col, _ = st.columns([1, 5])
    with theme_col:
        next_theme = 'light' if st.session_state.theme_mode == 'dark' else 'dark'
        theme_label = '☀️ Light theme' if next_theme == 'light' else '🌙 Dark theme'
        st.markdown('<div class="theme-toggle">', unsafe_allow_html=True)
        if st.button(theme_label, key="btn_theme_toggle", use_container_width=True):
            st.session_state.theme_mode = next_theme
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    lot_size = st.session_state.lot_size

    # ===== DATA SOURCE SETUP =====
    if not st.session_state.data_loaded:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Session Setup")
        st.caption(
            "By default the simulator generates a one-week 5-minute price path using a "
            "GARCH(1,1) model (annualized vol 12%-18%). Optionally supply your own intraday "
            "data below -- either input overrides the default model."
        )
        c1, c2 = st.columns(2)
        with c1:
            data_path = st.text_input("Data file path (optional)", value="", key="setup_path",
                                       placeholder="/path/to/your/data.txt")
        with c2:
            uploaded = st.file_uploader("Or upload data file (optional)", type=["txt", "csv"], key="setup_upload")
        open_price_input = st.number_input("Opening price", min_value=1.0, value=DEFAULT_OPEN_PRICE, step=50.0, key="setup_open")

        if st.button("Start Session", type="primary", use_container_width=True, key="btn_start_session"):
            df = None
            source = "garch"
            if uploaded is not None:
                df = load_data_from_upload(uploaded)
                source = "upload"
            elif data_path.strip():
                if os.path.exists(data_path.strip()):
                    df = load_data_from_path(data_path.strip())
                    source = "path"
                else:
                    st.error(f"Path not found: {data_path}")

            if df is not None and len(df) > 0:
                # ---- Real uploaded/path data ----
                st.session_state.df_raw = df
                scale_factor = calculate_scale_factor(df, open_price_input)
                st.session_state.scale_factor = scale_factor
                df_scaled = scale_data(df, scale_factor)
                bars = _add_day_num(resample_to_bars(df_scaled, BAR_MINUTES))
                first_gap = np.random.normal(0, 0.004)
                implied_prev_close = round(open_price_input / (1 + first_gap), 2)

                st.session_state.df_day_scaled = bars
                st.session_state.prev_scaled_close = implied_prev_close
                st.session_state.prev_day_close = implied_prev_close
                st.session_state.start_time = bars.iloc[0]['datetime']
                st.session_state.session_end = bars.iloc[-1]['datetime']
                st.session_state.simulated_data = bars
                st.session_state.data_source_choice = source
            else:
                # ---- Default model: GARCH(1,1), one trading week, 5-min bars ----
                start_date = date.today()
                sim_data, first_gap, implied_prev_close = generate_garch_week_path(
                    start_date=start_date, open_price=open_price_input,
                    bars_per_day=BARS_PER_DAY, days=SIM_DAYS,
                    vol_min=VOL_MIN, vol_max=VOL_MAX, bar_minutes=BAR_MINUTES,
                    seed=int(time.time())
                )
                sim_data = _add_day_num(sim_data)
                st.session_state.df_raw = sim_data
                st.session_state.df_day_scaled = sim_data
                st.session_state.scale_factor = 1.0
                st.session_state.prev_scaled_close = implied_prev_close
                st.session_state.prev_day_close = implied_prev_close
                st.session_state.start_time = sim_data.iloc[0]['datetime']
                st.session_state.session_end = sim_data.iloc[-1]['datetime']
                st.session_state.simulated_data = sim_data
                st.session_state.data_source_choice = "garch"

            st.session_state.expiry_dt = (
                st.session_state.start_time.replace(hour=15, minute=30, second=0, microsecond=0)
                + timedelta(days=TOTAL_EXPIRY_DAYS)
            )
            st.session_state.current_index = 0
            st.session_state.max_reached_index = 0
            st.session_state.data_loaded = True
            st.session_state.session_start_wall = datetime.now()
            st.session_state.basket = []
            save_session_state()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ===== MAIN SIMULATION STATE =====
    sim = st.session_state.simulated_data
    n_bars = len(sim)
    if n_bars == 0:
        st.error("No simulation data.")
        return

    if st.session_state.current_index >= n_bars:
        st.session_state.current_index = n_bars - 1
    if st.session_state.current_index > st.session_state.max_reached_index:
        st.session_state.max_reached_index = st.session_state.current_index

    current_row = sim.iloc[st.session_state.current_index]
    st.session_state.current_price = float(current_row['close'])
    current_price = st.session_state.current_price
    current_dt = current_row['datetime']
    current_day_num = int(current_row['day_num']) if 'day_num' in sim.columns else (st.session_state.current_index // BARS_PER_DAY) + 1

    # Build / refresh day-close map so change is always vs previous trading day's close
    if (not st.session_state.day_close_map) and sim is not None and len(sim) > 0 and 'day_num' in sim.columns:
        day_closes = {}
        for dnum, g in sim.groupby('day_num'):
            day_closes[int(dnum)] = float(g.iloc[-1]['close'])
        st.session_state.day_close_map = day_closes

    if current_day_num <= 1:
        ref_close = st.session_state.prev_day_close or st.session_state.prev_scaled_close or current_price
    else:
        ref_close = st.session_state.day_close_map.get(
            current_day_num - 1,
            st.session_state.prev_scaled_close or current_price
        )
    prev_close = float(ref_close)
    price_change = current_price - prev_close
    price_pct = (price_change / prev_close) * 100 if prev_close > 0 else 0
    is_up = price_change >= 0

    T_current = get_time_to_expiry(current_dt, st.session_state.expiry_dt)
    st.session_state.T_current = T_current
    days_to_expiry = round(T_current * 365, 1)
    atm_strike = round(current_price / 100) * 100

    # Cash settlement when time-to-expiry is exhausted
    if T_current <= (60 / (365 * 24 * 3600)) and st.session_state.positions and not st.session_state.trading_locked:
        _settle_all_cash(current_price, current_dt)
        st.toast("Options expired — all open positions cash-settled", icon="📅")
        st.session_state.trading_locked = True
        save_session_state()

    # End of simulated week (last bar reached): settle + lock
    if st.session_state.current_index >= n_bars - 1:
        st.session_state.playing = False
        if st.session_state.positions and not st.session_state.trading_locked:
            _settle_all_cash(current_price, current_dt)
            st.toast("Session week complete — all open positions cash-settled", icon="📅")
        st.session_state.pending_limits = []  # cancel unfilled limits at week end
        st.session_state.trading_locked = True

    st.session_state.chain_df = generate_option_chain(current_price, prev_close, T_current)
    chain_df = st.session_state.chain_df

    # Continuous limit-order matching against live LTPs
    n_filled = match_pending_limits(current_price, current_dt, chain_df, lot_size)
    if n_filled:
        st.toast(f"✅ {n_filled} limit order(s) filled", icon="📋")

    # Compute open / realized + margin
    open_pnl = 0.0
    cons_pos = []
    if st.session_state.positions:
        cons_pos = consolidate_positions(st.session_state.positions, current_price, T_current, chain_df)
        open_pnl = sum(p['pnl'] for p in cons_pos)
    realized_pnl = st.session_state.realized_pnl
    used_margin = calculate_realistic_margin(st.session_state.positions, current_price, lot_size)
    if used_margin > st.session_state.peak_margin_used:
        st.session_state.peak_margin_used = used_margin
    available_margin = max(0.0, st.session_state.starting_capital - used_margin)

    # ===== LAYOUT: LEFT + RIGHT =====
    col_left, col_right = st.columns([1, 2], gap="medium")

    # ==================== LEFT SIDEBAR ====================
    with col_left:
        # Prominent trading day + lock status
        _day_extra = ""
        if st.session_state.trading_locked or st.session_state.current_index >= n_bars - 1:
            _day_extra = " &nbsp;·&nbsp; <span style='color:#ffab40'>SESSION CLOSED</span>"
        st.markdown(f"""
        <div style="background:linear-gradient(90deg,#0a1628,#12263a);color:#e8f0fe;border-radius:10px;padding:8px 14px;margin-bottom:10px;
                    text-align:center;font-weight:700;font-size:15px;letter-spacing:0.3px;border:1px solid #1e3a5f;">
            TRADING DAY &nbsp;·&nbsp; Day-{current_day_num}{_day_extra}
        </div>
        """, unsafe_allow_html=True)

        # NIFTY Card — change vs previous day's close
        price_cls = "nifty-up" if is_up else "nifty-down"
        change_sign = "+" if is_up else ""
        st.markdown(f"""
        <div class="card">
            <div class="nifty-symbol">NIFTY 50</div>
            <div class="nifty-price {price_cls}">₹{current_price:,.2f}</div>
            <div class="nifty-change {price_cls}">{change_sign}{price_change:.2f} ({change_sign}{price_pct:.2f}%)</div>
            <div class="nifty-meta">
                TIME <span>{current_dt.strftime('%H:%M:%S')}</span><br>
                DTE <span>{days_to_expiry}</span><br>
                PREV DAY CLOSE <span>₹{prev_close:,.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Open / Realized P&L + Margin
        open_cls = "profit" if open_pnl >= 0 else "loss"
        real_cls = "profit" if realized_pnl >= 0 else "loss"
        st.markdown(f"""
        <div class="pnl-row">
            <span class="pnl-label">Open P&L</span>
            <span class="pnl-value {open_cls}">₹{open_pnl:+,.2f}</span>
        </div>
        <div class="pnl-row">
            <span class="pnl-label">Realized P&L</span>
            <span class="pnl-value {real_cls}">₹{realized_pnl:+,.2f}</span>
        </div>
        <div class="pnl-row">
            <span class="pnl-label">Used Margin</span>
            <span class="pnl-value">₹{used_margin:,.0f}</span>
        </div>
        <div class="pnl-row">
            <span class="pnl-label">Available Margin</span>
            <span class="pnl-value">₹{available_margin:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ===== PROMINENT GO LIVE / PAUSE =====
        if not st.session_state.playing:
            st.markdown("""
            <style>
            div[data-testid="stButton"] > button[kind="primary"] {
                background: #2563eb !important;
                color: white !important;
                font-size: 16px !important;
                font-weight: 700 !important;
                padding: 12px 0 !important;
                border-radius: 12px !important;
                border: none !important;
                box-shadow: 0 4px 12px rgba(0,168,107,0.35);
            }
            </style>
            """, unsafe_allow_html=True)
            if st.button("▶  GO LIVE", use_container_width=True, type="primary", key="btn_golive",
                         disabled=st.session_state.trading_locked):
                st.session_state.playing = True
                st.session_state.last_update = time.time()
                st.rerun()
        else:
            if st.button("⏸  PAUSE", use_container_width=True, key="btn_pause"):
                st.session_state.playing = False
                save_session_state()
                st.rerun()
            st.caption("● LIVE")

        st.markdown("<br>", unsafe_allow_html=True)

        # Speed: 0.25x – 5x ; 1 real sec = 1 sim min → bar every 5s at 1x
        speed = st.slider("Speed", 0.25, 5.0, float(st.session_state.speed), 0.25, key="speed_slider")
        st.session_state.speed = speed
        secs_per_bar = TICK_SECONDS_BASE / speed
        st.caption(f"{speed:.2f}x  •  1 bar (5 sim-min) every {secs_per_bar:.1f}s  •  "
                   f"~{(BARS_PER_DAY * secs_per_bar) / 60:.1f} min real-time per trading day")

        # Jump forward — single dropdown; selection jumps immediately
        jump_options = {
            "— Jump forward —": None,
            "5 Minutes": 1,
            "10 Minutes": 2,
            "30 Minutes": 6,
            "1 Hour": 12,
            "2 Hours": 24,
            "+1 Day": "day",
        }
        jump_choice = st.selectbox("Jump forward", list(jump_options.keys()), key="jump_select")
        jump_val = jump_options[jump_choice]
        if jump_val is not None:
            if jump_val == "day":
                cur_day = st.session_state.current_index // BARS_PER_DAY
                new_idx = min((cur_day + 1) * BARS_PER_DAY, n_bars - 1)
            else:
                new_idx = min(st.session_state.current_index + jump_val, n_bars - 1)
            if new_idx != st.session_state.current_index:
                st.session_state.current_index = new_idx
                if new_idx > st.session_state.max_reached_index:
                    st.session_state.max_reached_index = new_idx
                st.session_state.pop("jump_select", None)
                save_session_state()
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Reset high-contrast
        st.markdown('<div class="reset-btn-container">', unsafe_allow_html=True)
        if st.button("🔄 RESET SESSION", use_container_width=True, key="btn_reset"):
            for key in list(st.session_state.keys()):
                if key not in ['data_loaded', 'df_raw', 'simulated_data', 'df_day_scaled',
                               'start_time', 'session_end', 'expiry_dt', 'scale_factor', 'prev_scaled_close',
                               'prev_day_close', 'lot_size', 'target_nifty_level', 'starting_capital',
                               'data_source_choice', 'day_close_map']:
                    del st.session_state[key]
            st.session_state.playing = False
            st.session_state.current_index = 0
            st.session_state.max_reached_index = 0
            st.session_state.basket = []
            st.session_state.positions = []
            st.session_state.tradebook = []
            st.session_state.pending_limits = []
            st.session_state.realized_pnl = 0.0
            st.session_state.peak_margin_used = 0.0
            st.session_state.trading_locked = False
            st.session_state.session_finished = False
            try:
                if os.path.exists(PERSIST_PATH):
                    os.remove(PERSIST_PATH)
            except Exception:
                pass
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ==================== RIGHT PANEL ====================
    with col_right:
        tab_place, tab_pos, tab_graph, tab_perf = st.tabs([
            "Place Order", "Positions", "View Graph", "Performance and Reports"
        ])

        # ---------- TAB 1: PLACE ORDER ----------
        with tab_place:
            if st.session_state.trading_locked:
                st.warning("Session finished — trading is locked. Generate/download report or Reset to continue.")
            st.markdown('<div class="section-title" style="color:#1a1a1a; margin-bottom:6px;">Place Order</div>', unsafe_allow_html=True)

            # Clean tight order-entry row
            c1, c2, c3, c4, c5, c6 = st.columns([1.0, 0.9, 1.2, 0.8, 1.1, 1.0])
            with c1:
                side = st.selectbox("Side", ["BUY", "SELL"], key="ord_side")
            with c2:
                otype = st.selectbox("Type", ["CE", "PE"], key="ord_type")
            with c3:
                strikes = chain_df['Strike'].tolist()
                default_idx = strikes.index(atm_strike) if atm_strike in strikes else 0
                strike = st.selectbox("Strike", strikes, index=default_idx, key="ord_strike")
            with c4:
                lots = st.number_input("Lots", min_value=1, value=1, step=1, key="ord_lots")
            with c5:
                order_type = st.selectbox("Order", ["MARKET", "LIMIT"], key="ord_order")
            with c6:
                row = chain_df[chain_df['Strike'] == strike]
                ltp = float(row.iloc[0]['CE Price'] if otype == 'CE' else row.iloc[0]['PE Price']) if len(row) else 0.0
                st.markdown(
                    f"<div style='padding-top:4px;'><div style='font-size:11px;color:#666;font-weight:600;'>LTP</div>"
                    f"<div style='font-size:18px;font-weight:700;color:#1a1a1a;'>₹{ltp:.2f}</div></div>",
                    unsafe_allow_html=True
                )

            limit_price = None
            if order_type == "LIMIT":
                limit_price = st.number_input("Limit Price", min_value=0.05, value=float(round(ltp, 2)), step=0.05, key="limit_px")

            def _build_order_item():
                qty = lots * lot_size
                px = limit_price if order_type == "LIMIT" else ltp
                return {
                    'side': side.title(),
                    'type': otype,
                    'strike': strike,
                    'lots': lots,
                    'quantity': qty,
                    'price': px,
                    'order_type': order_type,
                    'ltp': ltp
                }

            def _can_afford(extra_items):
                trial = list(st.session_state.positions) + list(extra_items)
                req = calculate_realistic_margin(trial, current_price, lot_size)
                return req <= st.session_state.starting_capital, req

            def _execute_items(items):
                """Execute marketable orders; queue non-marketable limits. Returns count executed."""
                if st.session_state.trading_locked:
                    st.error("Trading is locked for this session.")
                    return 0
                ok, req = _can_afford(items)
                if not ok:
                    st.error(f"Insufficient margin. Required ≈ ₹{req:,.0f}, available ₹{available_margin:,.0f}")
                    return 0
                executed = 0
                for item in items:
                    if item['order_type'] == "LIMIT":
                        marketable = (item['side'] == 'Buy' and item['price'] >= item['ltp']) or \
                                     (item['side'] == 'Sell' and item['price'] <= item['ltp'])
                        if not marketable:
                            st.session_state.pending_limits.append(item)
                            continue
                    st.session_state.positions.append({
                        'strike': item['strike'],
                        'type': item['type'],
                        'side': item['side'],
                        'entry_price': item['price'],
                        'quantity': item['quantity'],
                        'lots': item['lots']
                    })
                    st.session_state.tradebook.append({
                        'entry_time': current_dt.strftime('%H:%M:%S'),
                        'strike': item['strike'],
                        'type': item['type'],
                        'side': item['side'],
                        'qty': item['quantity'],
                        'entry_price': item['price'],
                        'exit_time': '-',
                        'exit_price': 0.0,
                        'pnl': 0.0,
                        'status': 'Open'
                    })
                    executed += 1
                margin_now = calculate_realistic_margin(st.session_state.positions, current_price, lot_size)
                if margin_now > st.session_state.peak_margin_used:
                    st.session_state.peak_margin_used = margin_now
                save_session_state()
                return executed

            st.markdown("""
            <style>
            div[data-testid="stButton"] > button[kind="secondary"] {
                border: 1.5px solid #387ed1 !important;
                color: #387ed1 !important;
                background: white !important;
                font-weight: 600 !important;
                border-radius: 6px !important;
                padding: 6px 18px !important;
            }
            div[data-testid="stButton"] > button[kind="secondary"]:hover {
                background: #eef4fc !important;
            }
            </style>
            """, unsafe_allow_html=True)

            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("Add to Basket", key="btn_add_basket", type="secondary", use_container_width=True,
                             disabled=st.session_state.trading_locked):
                    st.session_state.basket.append(_build_order_item())
                    st.toast(f"Added {side} {strike} {otype} x{lots} to basket", icon="✅")
                    st.rerun()
            with btn2:
                if st.button("Execute Now", key="btn_exec_now", type="primary", use_container_width=True,
                             disabled=st.session_state.trading_locked):
                    item = _build_order_item()
                    n = _execute_items([item])
                    if n:
                        st.toast(f"✅ Order executed", icon="🎉")
                        components.html("""
                        <script>
                        const ctx = new (window.AudioContext || window.webkitAudioContext)();
                        const o = ctx.createOscillator();
                        const g = ctx.createGain();
                        o.connect(g); g.connect(ctx.destination);
                        o.frequency.value = 880; o.type = 'sine';
                        g.gain.setValueAtTime(0.15, ctx.currentTime);
                        g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
                        o.start(ctx.currentTime); o.stop(ctx.currentTime + 0.3);
                        </script>
                        """, height=0)
                    st.rerun()

            # BASKET
            st.markdown('<div class="section-title">Basket</div>', unsafe_allow_html=True)
            if st.session_state.basket:
                for i, item in enumerate(st.session_state.basket):
                    cols = st.columns([5, 1])
                    with cols[0]:
                        st.markdown(
                            f"**{item['side']}** {item['type']} {item['strike']} &nbsp; "
                            f"{item['lots']} lot &nbsp; ₹{item['price']:.2f} &nbsp; "
                            f"<span style='color:#666'>{item['order_type']}</span>",
                            unsafe_allow_html=True
                        )
                    with cols[1]:
                        if st.button("✕", key=f"rm_basket_{i}"):
                            del st.session_state.basket[i]
                            st.rerun()

                margin_req = calculate_realistic_margin(
                    list(st.session_state.positions) + list(st.session_state.basket),
                    current_price, lot_size
                )
                extra = max(0, margin_req - st.session_state.starting_capital)
                st.markdown(f"""
                <div class="margin-box">
                    <div class="margin-grid">
                        <div><div class="margin-label">Margin Required</div><div class="margin-val">₹{margin_req:,.0f}</div></div>
                        <div><div class="margin-label">Extra Needed</div><div class="margin-val">₹{extra:,.0f}</div></div>
                        <div><div class="margin-label">Available</div><div class="margin-val">₹{available_margin:,.0f}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <style>
                div[data-testid="stHorizontalBlock"] button[kind="primary"] {
                    background: #dc2626 !important;
                    color: white !important;
                    font-weight: 700 !important;
                    border-radius: 6px !important;
                    border: none !important;
                }
                div[data-testid="stHorizontalBlock"] button[kind="primary"]:hover {
                    background: #c01a1a !important;
                }
                </style>
                """, unsafe_allow_html=True)
                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button("Clear Basket", use_container_width=True, key="btn_clear_basket"):
                        st.session_state.basket = []
                        st.rerun()
                with bc2:
                    if st.button("Execute Basket", use_container_width=True, type="primary", key="btn_exec_basket",
                                 disabled=st.session_state.trading_locked):
                        n = _execute_items(list(st.session_state.basket))
                        st.session_state.basket = []
                        if n:
                            st.toast(f"✅ {n} order(s) executed from basket", icon="🎉")
                        st.rerun()
            else:
                st.caption("Basket is empty — use for multi-leg / basket orders")

            # Order Book (Pending Limits)
            st.markdown('<div class="section-title">Order Book (Pending Limits)</div>', unsafe_allow_html=True)
            if st.session_state.pending_limits:
                for i, item in enumerate(list(st.session_state.pending_limits)):
                    cols = st.columns([5, 1])
                    with cols[0]:
                        st.markdown(
                            f"**{item['side']}** {item['type']} {item['strike']} &nbsp; "
                            f"x{item['lots']} @ ₹{item['price']:.2f} &nbsp; "
                            f"<span style='color:#666'>LIMIT</span> &nbsp; "
                            f"<span style='color:#888;font-size:12px'>LTP ₹{item.get('ltp', 0):.2f}</span>",
                            unsafe_allow_html=True
                        )
                    with cols[1]:
                        if st.button("Cancel", key=f"cx_lim_{i}", disabled=st.session_state.trading_locked):
                            del st.session_state.pending_limits[i]
                            save_session_state()
                            st.toast("Limit order cancelled", icon="🗑️")
                            st.rerun()
            else:
                st.caption("No pending limit orders")

            chain_container = st.container()
            with chain_container:
                st.markdown('<div class="section-title">Live Option Chain</div>', unsafe_allow_html=True)
                st.caption(f"ATM ₹{atm_strike:,} · DTE {days_to_expiry}d · Live updating")
                st.markdown(
                    '<div class="moneyness-legend">'
                    '<span class="moneyness-pill itm">ITM</span> Calls: strike below spot · Puts: strike above spot '
                    '<span class="moneyness-pill atm">ATM</span> Nearest strike '
                    '<span class="moneyness-pill otm">OTM</span> Calls: strike above spot · Puts: strike below spot'
                    '</div>',
                    unsafe_allow_html=True,
                )

                display_df = chain_df.copy()
                # Older persisted sessions may contain a chain without display-only status columns.
                base_strike = round(current_price / 100) * 100
                if 'CE Moneyness' not in display_df.columns:
                    display_df['CE Moneyness'] = display_df['Strike'].apply(
                        lambda strike: 'ATM' if strike == base_strike else ('ITM' if strike < current_price else 'OTM')
                    )
                if 'PE Moneyness' not in display_df.columns:
                    display_df['PE Moneyness'] = display_df['Strike'].apply(
                        lambda strike: 'ATM' if strike == base_strike else ('ITM' if strike > current_price else 'OTM')
                    )
                status_columns = ['Strike', 'CE Moneyness', 'PE Moneyness']
                display_df = display_df[status_columns + [column for column in display_df.columns if column not in status_columns]]
                # Display-only status colors: call and put moneyness are independent.
                def highlight_moneyness(row):
                    styles = [''] * len(row)
                    colors = {
                        'ITM': 'background-color: #123b2a; color: #bbf7d0; font-weight: 700;',
                        'ATM': 'background-color: #1e3a8a; color: #dbeafe; font-weight: 700;',
                        'OTM': 'background-color: #3f1d2e; color: #fecdd3; font-weight: 700;',
                    }
                    for column in ('CE Moneyness', 'PE Moneyness'):
                        if column in row.index:
                            styles[row.index.get_loc(column)] = colors.get(row[column], '')
                    return styles

                st.dataframe(
                    display_df.style.apply(highlight_moneyness, axis=1),
                    use_container_width=True,
                    height=340,
                    hide_index=True,
                    column_config={
                        "Strike": st.column_config.NumberColumn("Strike", format="%d"),
                        "CE Price": st.column_config.NumberColumn("CE LTP", format="%.2f"),
                        "CE Moneyness": st.column_config.TextColumn("CE Status"),
                        "CE %": st.column_config.TextColumn("CE %"),
                        "CE Δ": st.column_config.NumberColumn("CE Δ", format="%.3f"),
                        "PE Price": st.column_config.NumberColumn("PE LTP", format="%.2f"),
                        "PE Moneyness": st.column_config.TextColumn("PE Status"),
                        "PE %": st.column_config.TextColumn("PE %"),
                        "PE Δ": st.column_config.NumberColumn("PE Δ", format="%.3f"),
                        "IV %": st.column_config.NumberColumn("IV %", format="%.1f"),
                    }
                )

        # ---------- TAB 2: POSITIONS ----------
        with tab_pos:
            st.markdown('<div class="section-title">Your Positions</div>', unsafe_allow_html=True)
            if cons_pos:
                for idx, pos in enumerate(cons_pos):
                    pnl_cls = "profit" if pos['pnl'] >= 0 else "loss"
                    side_cls = "pos-side-buy" if pos['side'] == 'Buy' else "pos-side-sell"
                    cols = st.columns([6, 2, 1])
                    with cols[0]:
                        st.markdown(f"""
                        <div>
                            <div class="pos-instrument">
                                <span class="{side_cls}">{pos['side']}</span>
                                &nbsp;NIFTY {pos['strike']} {pos['type']}
                            </div>
                            <div class="pos-meta">
                                {abs(pos['net_qty'])} shares · Avg ₹{pos['avg_price']:.2f} · LTP ₹{pos['current_price']:.2f}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with cols[1]:
                        st.markdown(f"<div style='text-align:right;font-weight:700;font-size:16px;' class='{pnl_cls}'>₹{pos['pnl']:+,.2f}</div>", unsafe_allow_html=True)
                    with cols[2]:
                        if st.button("Exit", key=f"exit_{idx}", disabled=st.session_state.trading_locked):
                            st.session_state.playing = False  # pause so exit is immediate
                            to_remove = []
                            realized_add = 0.0
                            for i, orig in enumerate(st.session_state.positions):
                                if orig['strike'] == pos['strike'] and orig['type'] == pos['type']:
                                    for t in st.session_state.tradebook:
                                        if (t['strike'] == orig['strike'] and t['type'] == orig['type']
                                                and t['status'] == 'Open' and t['side'] == orig['side']):
                                            t['exit_time'] = current_dt.strftime('%H:%M:%S')
                                            t['exit_price'] = pos['current_price']
                                            sign = 1 if t['side'] == 'Buy' else -1
                                            t['pnl'] = sign * (t['exit_price'] - t['entry_price']) * t['qty']
                                            t['status'] = 'Closed'
                                            realized_add += t['pnl']
                                            break
                                    to_remove.append(i)
                            for i in sorted(to_remove, reverse=True):
                                del st.session_state.positions[i]
                            st.session_state.realized_pnl += realized_add
                            save_session_state()
                            st.toast("Position exited", icon="✅")
                            st.rerun()

                if st.button("Exit All", use_container_width=True, key="btn_exit_all",
                             disabled=st.session_state.trading_locked):
                    st.session_state.playing = False  # pause so exit is immediate
                    realized_add = 0.0
                    for pos in cons_pos:
                        for t in st.session_state.tradebook:
                            if (t['strike'] == pos['strike'] and t['type'] == pos['type'] and t['status'] == 'Open'):
                                t['exit_time'] = current_dt.strftime('%H:%M:%S')
                                t['exit_price'] = pos['current_price']
                                sign = 1 if t['side'] == 'Buy' else -1
                                t['pnl'] = sign * (t['exit_price'] - t['entry_price']) * t['qty']
                                t['status'] = 'Closed'
                                realized_add += t['pnl']
                    st.session_state.positions = []
                    st.session_state.realized_pnl += realized_add
                    save_session_state()
                    st.toast("All positions exited", icon="✅")
                    st.rerun()

                # Total Open P&L
                st.markdown(f"""
                <div class="pnl-row" style="margin-top:12px; background:#f8f9fb;">
                    <span class="pnl-label">Total Open P&L</span>
                    <span class="pnl-value {open_cls}">₹{open_pnl:+,.2f}</span>
                </div>
                """, unsafe_allow_html=True)

                # Net Greeks
                greeks = compute_position_greeks(st.session_state.positions, current_price, T_current)
                st.markdown("**Net Greeks**")
                st.markdown(f"""
                <div>
                    <span class="greek-box"><span class="greek-label">Δ</span> {greeks['delta']:+.1f}</span>
                    <span class="greek-box"><span class="greek-label">Γ</span> {greeks['gamma']:+.4f}</span>
                    <span class="greek-box"><span class="greek-label">Θ</span> {greeks['theta']:+.2f}</span>
                    <span class="greek-box"><span class="greek-label">Vega</span> {greeks['vega']:+.2f}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.caption("No open positions")

        # ---------- TAB 3: VIEW GRAPH ----------
        with tab_graph:
            arrow = "▲" if is_up else "▼"
            st.markdown(f"""
            <div style="background:#f8f9fb; padding:10px 16px; border-radius:12px; margin-bottom:10px;
                        display:flex; align-items:center; gap:18px; border:1px solid #eaeaea;">
                <span style="font-weight:700; font-size:16px;">NIFTY 50</span>
                <span style="font-size:24px; font-weight:700;" class="{price_cls}">₹{current_price:,.2f}</span>
                <span class="{price_cls}" style="font-weight:600;">{arrow} {price_pct:+.2f}%</span>
                <span style="color:#777; font-size:13px;">Prev ₹{prev_close:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)

            all_data = sim.iloc[:st.session_state.current_index + 1]
            fig = create_chart(all_data, current_price, session_start=st.session_state.start_time)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

        # ---------- TAB 4: PERFORMANCE AND REPORTS ----------
        with tab_perf:
            st.markdown('<div class="section-title">Session Summary</div>', unsafe_allow_html=True)
            total_trades = len(st.session_state.tradebook)
            closed_trades = [t for t in st.session_state.tradebook if t['status'] == 'Closed']
            wins = len([t for t in closed_trades if t['pnl'] > 0])
            win_rate = (wins / len(closed_trades) * 100) if closed_trades else 0.0

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Trading Day", f"Day-{current_day_num}")
            m2.metric("Total Trades", total_trades)
            m3.metric("Closed Trades", len(closed_trades))
            m4.metric("Win Rate", f"{win_rate:.0f}%")

            st.markdown('<div class="section-title">P&L Snapshot</div>', unsafe_allow_html=True)
            p1, p2, p3 = st.columns(3)
            p1.metric("Open P&L", f"₹{open_pnl:+,.2f}")
            p2.metric("Realized P&L", f"₹{realized_pnl:+,.2f}")
            p3.metric("Total P&L", f"₹{open_pnl + realized_pnl:+,.2f}")

            # Profit vs Funds Utilized
            peak_m = max(st.session_state.peak_margin_used, 1)
            capital_eff = ((open_pnl + realized_pnl) / peak_m) * 100
            st.markdown('<div class="section-title">Performance vs Capital</div>', unsafe_allow_html=True)
            e1, e2, e3 = st.columns(3)
            e1.metric("Peak Margin Used", f"₹{st.session_state.peak_margin_used:,.0f}")
            e2.metric("Starting Capital", f"₹{st.session_state.starting_capital:,.0f}")
            e3.metric("Return on Margin", f"{capital_eff:+.2f}%")

            # Tradebook
            st.markdown('<div class="section-title">Tradebook</div>', unsafe_allow_html=True)
            if st.session_state.tradebook:
                tb_df = pd.DataFrame(st.session_state.tradebook)
                st.dataframe(tb_df, use_container_width=True, hide_index=True, height=240)
            else:
                st.caption("No trades yet")

            # Net Greeks
            if st.session_state.positions:
                greeks = compute_position_greeks(st.session_state.positions, current_price, T_current)
                st.markdown("**Net Greeks (Open)**")
                st.markdown(f"""
                <div>
                    <span class="greek-box"><span class="greek-label">Δ</span> {greeks['delta']:+.1f}</span>
                    <span class="greek-box"><span class="greek-label">Γ</span> {greeks['gamma']:+.4f}</span>
                    <span class="greek-box"><span class="greek-label">Θ</span> {greeks['theta']:+.2f}</span>
                    <span class="greek-box"><span class="greek-label">Vega</span> {greeks['vega']:+.2f}</span>
                </div>
                """, unsafe_allow_html=True)

            # Hold-to-Day-22 hypothetical (replaces What-If)
            st.markdown(f'<div class="section-title">Hypothetical: Held {HOLD_DAYS} Days vs Actual Exit</div>', unsafe_allow_html=True)
            hold_table, hold_labels = compute_hold_to_expiry_table(current_price)
            if hold_table is not None:
                st.caption("Rows = P&L if each closed position had instead been held to that day. "
                           "Last row = what was actually realized on exit.")
                st.dataframe(
                    hold_table.style.format("{:+.2f}"),
                    use_container_width=True, height=340
                )
            else:
                st.caption("No closed positions yet — this table populates once you exit a trade.")

            # Model documentation
            st.markdown('<div class="section-title">Model Documentation</div>', unsafe_allow_html=True)
            st.caption("Mathematical specification of the GARCH path, Black–Scholes pricing, IV surface, and hold-to-expiry attribution.")
            _model_pdf_candidates = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "Model_Math.pdf"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts", "Model_Math.pdf"),
                "/home/workdir/artifacts/Model_Math.pdf",
                "/home/workdir/attachments/Model_Math.pdf",
            ]
            _model_pdf = next((p for p in _model_pdf_candidates if os.path.exists(p)), None)
            if _model_pdf:
                with open(_model_pdf, "rb") as _mf:
                    st.download_button(
                        "📄 Download Model Specification (PDF)",
                        _mf,
                        file_name="Model_Math.pdf",
                        mime="application/pdf",
                        key="btn_model_pdf",
                        use_container_width=True,
                    )
            else:
                st.caption("Model PDF not found on disk.")

            # Finish & Report
            st.markdown('<div class="section-title">Finish Session & Report</div>', unsafe_allow_html=True)
            if not st.session_state.session_finished:
                if st.button("🏁 Finish Session & Generate PDF Report", use_container_width=True, type="primary", key="btn_finish"):
                    # Close remaining
                    if st.session_state.positions:
                        for pos in cons_pos:
                            for t in st.session_state.tradebook:
                                if t['strike'] == pos['strike'] and t['type'] == pos['type'] and t['status'] == 'Open':
                                    t['exit_time'] = current_dt.strftime('%H:%M:%S')
                                    t['exit_price'] = pos['current_price']
                                    sign = 1 if t['side'] == 'Buy' else -1
                                    t['pnl'] = sign * (t['exit_price'] - t['entry_price']) * t['qty']
                                    t['status'] = 'Closed'
                                    st.session_state.realized_pnl += t['pnl']
                        st.session_state.positions = []
                    with st.spinner("Generating PDF..."):
                        path, fname = generate_pdf_report()
                        st.session_state.report_path = path
                        st.session_state.report_generated = True
                        st.session_state.session_finished = True
                        st.session_state.trading_locked = True
                        save_session_state()
                        st.success(f"Report generated: {fname}")
                        if os.path.exists(path):
                            with open(path, "rb") as f:
                                st.download_button("📥 Download PDF Report", f, file_name=fname, mime="application/pdf")
                    st.rerun()
            else:
                st.success("Session finished. Report available.")
                if st.session_state.report_path and os.path.exists(st.session_state.report_path):
                    with open(st.session_state.report_path, "rb") as f:
                        st.download_button("📥 Download PDF Report", f,
                                           file_name=os.path.basename(st.session_state.report_path),
                                           mime="application/pdf")

        # ===== AUTO-PLAY =====
        # Each bar = 5 sim-minutes. 1 real second = 1 sim minute → 5s per bar at 1x.
    if st.session_state.playing and st.session_state.current_index < n_bars - 1:
        now = time.time()
        elapsed = now - st.session_state.last_update
        delay = TICK_SECONDS_BASE / max(st.session_state.speed, 0.1)
        if elapsed >= delay:
            st.session_state.current_index += 1
            if st.session_state.current_index > st.session_state.max_reached_index:
                st.session_state.max_reached_index = st.session_state.current_index
            st.session_state.last_update = now
            if st.session_state.current_index % 5 == 0:
                save_session_state()
            st.rerun()
        else:
            remaining = max(0, delay - elapsed)
            time.sleep(min(0.3, remaining))
            st.rerun()
    elif st.session_state.current_index >= n_bars - 1:
        # Week complete: stop clock, cash-settle any open positions, lock trading
        st.session_state.playing = False
        if st.session_state.positions and not st.session_state.trading_locked:
            _settle_all_cash(current_price, current_dt)
            st.toast("Session week complete — all open positions cash-settled", icon="📅")
        st.session_state.pending_limits = []
        st.session_state.trading_locked = True
        save_session_state()

if __name__ == "__main__":
    main()
