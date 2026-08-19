"""Application configuration and Streamlit session defaults."""

import os
import time


BAR_MINUTES = 5
BARS_PER_DAY = 75
SIM_DAYS = 5
TICK_SECONDS_BASE = 5.0
DEFAULT_OPEN_PRICE = 24000.0
VOL_MIN, VOL_MAX = 0.12, 0.18
TOTAL_EXPIRY_DAYS = 25
PERSIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oms_session_state.json")
HOLD_DAYS = 22


def initialize_session_state(session_state):
    """Populate the simulator's state once, without overwriting an active session."""
    defaults = {
        'simulated_data': None, 'current_index': 0, 'playing': False,
        'speed': 1.0, 'last_update': time.time(), 'basket': [],
        'positions': [], 'tradebook': [], 'pending_limits': [],
        'realized_pnl': 0.0, 'max_reached_index': 0, 'data_loaded': False,
        'selected_date': None, 'prev_day_close': None, 'start_time': None,
        'session_end': None, 'expiry_dt': None, 'scale_factor': 1.0,
        'lot_size': 65, 'target_nifty_level': DEFAULT_OPEN_PRICE,
        'prev_scaled_close': None, 'trading_locked': False,
        'session_finished': False, 'report_generated': False,
        'report_path': None, 'df_raw': None, 'df_day_scaled': None,
        'current_price': DEFAULT_OPEN_PRICE, 'T_current': TOTAL_EXPIRY_DAYS / 365,
        'chain_df': None, 'starting_capital': 10000000.0,
        'peak_margin_used': 0.0, 'session_start_wall': None,
        'data_source_choice': None, 'day_close_map': {}, 'theme_mode': 'dark',
    }
    for key, value in defaults.items():
        if key not in session_state:
            session_state[key] = value
