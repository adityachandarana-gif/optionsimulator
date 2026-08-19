"""Black-Scholes pricing and the simulator's implied-volatility surface."""

import math
import pandas as pd
from scipy.stats import norm

BASE_ATM_IV = 13.5
TERM_COEFF = 2.5
SKEW_SLOPE = 0.9
SKEW_CURV = 0.06


def get_iv_surface(strike, spot, T):
    days_left = max(T * 365, 0.1)
    moneyness_pct = (strike - spot) / max(spot, 1) * 100
    term_scale = 1.0 / math.sqrt(days_left + 1)
    atm_iv = BASE_ATM_IV + TERM_COEFF * term_scale
    skew = (-SKEW_SLOPE * moneyness_pct + SKEW_CURV * moneyness_pct ** 2) * term_scale
    iv = atm_iv + skew
    return round(min(max(iv, 8.0), 60.0), 2)


def calculate_option_price(S, K, T, r, q, sigma, option_type='call'):
    MIN_PRICE = 0.05
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


def generate_option_chain(spot_price, prev_spot, T):
    base_strike = round(spot_price / 100) * 100
    strikes = list(range(int(base_strike) - 500, int(base_strike) + 600, 100))
    chain_data = []
    for strike in strikes:
        # Moneyness is a display classification only; pricing remains unchanged.
        ce_moneyness = 'ATM' if strike == base_strike else ('ITM' if strike < spot_price else 'OTM')
        pe_moneyness = 'ATM' if strike == base_strike else ('ITM' if strike > spot_price else 'OTM')
        iv = get_iv_surface(strike, spot_price, T) / 100
        call_price, call_delta, call_gamma, _, _ = calculate_option_price(spot_price, strike, T, 0.068, 0.014, iv, 'call')
        put_price, put_delta, put_gamma, _, _ = calculate_option_price(spot_price, strike, T, 0.068, 0.014, iv, 'put')
        prev_call, _, _, _, _ = calculate_option_price(prev_spot, strike, T + 1/365, 0.068, 0.014, iv, 'call')
        prev_put, _, _, _, _ = calculate_option_price(prev_spot, strike, T + 1/365, 0.068, 0.014, iv, 'put')
        call_pct = ((call_price - prev_call) / prev_call * 100) if prev_call > 0.1 else 0
        put_pct = ((put_price - prev_put) / prev_put * 100) if prev_put > 0.1 else 0
        chain_data.append({'Strike': strike, 'CE Price': round(call_price, 2), 'CE Moneyness': ce_moneyness, 'CE %': f"{call_pct:+.1f}%", 'CE Δ': round(call_delta, 3), 'CE Γ': round(call_gamma, 4), 'PE Price': round(put_price, 2), 'PE Moneyness': pe_moneyness, 'PE %': f"{put_pct:+.1f}%", 'PE Δ': round(put_delta, 3), 'PE Γ': round(put_gamma, 4), 'IV %': round(iv * 100, 1)})
    return pd.DataFrame(chain_data)
