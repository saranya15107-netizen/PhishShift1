# PhishShift — Message Risk Scanner

Educational Streamlit prototype for phishing-risk cues.

## Render deployment
Push this folder to GitHub, then create a Render Blueprint using `render.yaml`. Render runs `pip install -r requirements.txt` and starts Streamlit on `$PORT`.

## Local testing (optional)
`python -m venv .venv`, activate it, run `python -m pip install -r requirements.txt`, then `python -m streamlit run app.py`.

The dataset is synthetic and only for demo use. Metrics are not real-world benchmarks. Do not enter confidential messages or personal information.
