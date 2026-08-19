"""Portfolio aggregation, Greeks, and margin calculations."""

import streamlit as st
import pandas as pd

from options_pricing import calculate_option_price, get_iv_surface


def compute_position_greeks(positions, spot, T, r=0.068, q=0.014):
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


def consolidate_positions(positions, current_price, T_current, chain_df):
    consolidated = {}
    for pos in positions:
        key = f"{pos['strike']}_{pos['type']}"
        if key not in consolidated:
            consolidated[key] = {'strike': pos['strike'], 'type': pos['type'], 'net_qty': 0, 'total_cost': 0.0, 'entries': []}
        sign = 1 if pos['side'] == 'Buy' else -1
        qty = pos.get('quantity', st.session_state.lot_size)
        price = pos['entry_price']
        consolidated[key]['net_qty'] += sign * qty
        consolidated[key]['total_cost'] += sign * qty * price
        consolidated[key]['entries'].append({'side': pos['side'], 'qty': qty, 'price': price})
    result = []
    for data in consolidated.values():
        if data['net_qty'] != 0:
            avg_price = data['total_cost'] / data['net_qty']
            row = chain_df[chain_df['Strike'] == data['strike']] if chain_df is not None else pd.DataFrame()
            cur_px = float(row.iloc[0]['CE Price'] if data['type'] == 'CE' else row.iloc[0]['PE Price']) if len(row) > 0 else 0.0
            result.append({'strike': data['strike'], 'type': data['type'], 'net_qty': data['net_qty'], 'avg_price': avg_price, 'current_price': cur_px, 'pnl': (cur_px - avg_price) * data['net_qty'], 'side': 'Buy' if data['net_qty'] > 0 else 'Sell'})
    return result


def calculate_realistic_margin(items, spot, lot_size):
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
    total_margin, short_legs = 0.0, []
    for (strike, typ), data in legs.items():
        if data['qty'] < 0:
            short_legs.append({'strike': strike, 'type': typ, 'qty': abs(data['qty']), 'premium': data['premium']})
    used = set()
    for i, a in enumerate(short_legs):
        if i in used:
            continue
        paired = False
        for j, b in enumerate(short_legs):
            if j > i and j not in used and a['type'] == b['type'] and a['strike'] != b['strike']:
                width, qty = abs(a['strike'] - b['strike']), min(a['qty'], b['qty'])
                total_margin += width * qty * 0.15 + max(a['premium'], b['premium']) * qty
                used.update({i, j}); paired = True; break
        if not paired:
            total_margin += max(a['premium'] * a['qty'] * 3.0, a['strike'] * a['qty'] * 0.10) + spot * 0.015 * a['qty']
            used.add(i)
    remaining = [leg for index, leg in enumerate(short_legs) if index not in used]
    ce_short = sum(leg['qty'] for leg in remaining if leg['type'] == 'CE')
    pe_short = sum(leg['qty'] for leg in remaining if leg['type'] == 'PE')
    if ce_short > 0 and pe_short > 0:
        total_margin = max(0.0, total_margin - min(ce_short, pe_short) * spot * 0.005)
    return round(max(total_margin, 0), 0)
