# Option Market Simulator

A Streamlit-based live trading simulator for exploring option pricing, implied volatility, Greeks, portfolio risk, margin, and simulated market paths.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run AppCL4.2.py
```

Then open the local URL shown by Streamlit, usually `http://localhost:8501`.

## Deploy with Streamlit Community Cloud

1. Open [share.streamlit.io](https://share.streamlit.io/).
2. Sign in with GitHub.
3. Select `adityachandarana-gif/optionsimulator` and the `main` branch.
4. Set the main file to `AppCL4.2.py`.
5. Deploy.

The app stores session state locally when the environment permits it. This repository intentionally excludes the local `oms_session_state.json` file and Python cache files.

## Project structure

- `AppCL4.2.py`: Streamlit UI and application entry point
- `options_pricing.py`: option pricing, implied volatility, and option-chain calculations
- `trading_risk.py`: positions, Greeks, and margin calculations
- `app_config.py`: application constants and session initialization
- `ui_styles.py`: dashboard presentation styles
- `requirements.txt`: Python dependencies
