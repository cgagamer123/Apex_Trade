
import joblib
import requests
import os
import yfinance as yf
import pandas as pd

MODEL_URL = "https://slinycjjbrgxjnyqspzp.supabase.co/storage/v1/object/public/models//model.pkl"
MODEL_PATH = "model.pkl"

def download_model():
    if not os.path.exists(MODEL_PATH):
        response = requests.get(MODEL_URL)
        with open(MODEL_PATH, "wb") as f:
            f.write(response.content)

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_features(ticker):
    df = yf.Ticker(ticker).history(period="60d")
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["RSI"] = compute_rsi(df["Close"])
    df["Return"] = df["Close"].pct_change()
    df.dropna(inplace=True)
    return df[["SMA20", "SMA50", "RSI", "Return"]].iloc[-1:]

def predict(ticker):
    try:
        download_model()
        model = joblib.load(MODEL_PATH)
        features = get_features(ticker)
        if features.empty:
            return "Not enough data to compute features."

        prediction = model.predict(features)[0]
        proba = model.predict_proba(features)[0][prediction]

        direction = "↑" if prediction == 1 else "↓"
        action = "Buy Call" if prediction == 1 else "Buy Put"
        current_price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]

        entry = round(current_price, 2)
        target = round(entry * (1.02 if prediction == 1 else 0.98), 2)
        stop = round(entry * (0.98 if prediction == 1 else 1.02), 2)

        return {
            "PredictionID": f"{ticker}_PRED_123456",
            "Direction": direction,
            "Confidence": round(proba, 2),
            "Action": action,
            "Entry": entry,
            "Target": target,
            "StopLoss": stop,
            "TradeOptions": [{
                "ExecutionDate": pd.Timestamp.today().date(),
                "Strike": round(entry),
                "Type": "Call" if prediction == 1 else "Put",
                "Premium": round(abs(target - entry) * 0.2, 2),
                "EstimatedProfit": abs(target - entry) * 1.0,
                "EstimatedLoss": abs(entry - stop)
            }]
        }

    except Exception as e:
        return str(e)
