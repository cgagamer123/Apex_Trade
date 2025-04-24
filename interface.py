
import streamlit as st
from predictor import predict
import plotly.graph_objects as go

st.set_page_config(page_title="Aimbot Predictor", layout="wide")
st.title("📈 Aimbot Stock Predictor")

# Input
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA)", value="AAPL").upper()

if st.button("Get Prediction") and ticker:
    result = predict(ticker)

    if isinstance(result, str):
        st.error(result)
    else:
        st.success("Prediction Generated")

        st.markdown("### 📊 Prediction Overview")
        st.markdown(f'''
        - **Prediction ID**: `{result["PredictionID"]}`
        - **Direction**: `{result["Direction"]}`
        - **Confidence**: `{result["Confidence"]}`
        - **Action**: `{result["Action"]}`
        - **Entry Price**: `${result["Entry"]}`
        - **Target Price**: `${result["Target"]}`
        - **Stop Loss**: `${result["StopLoss"]}`
        ''')

        st.markdown("### 💼 Trade Option")
        option = result["TradeOptions"][0]
        st.markdown(f'''
        - **Execution Date**: {option["ExecutionDate"]}
        - **Strike Price**: ${option["Strike"]}
        - **Option Type**: {option["Type"]}
        - **Premium Estimate**: ${option["Premium"]}
        - **Est. Profit**: ${option["EstimatedProfit"]}
        - **Est. Loss**: ${option["EstimatedLoss"]}
        ''')

        st.markdown("### 📈 Chart (Sample)")
        fig = go.Figure(data=go.Candlestick(x=[1, 2, 3],
                                            open=[10, 11, 12],
                                            high=[12, 13, 14],
                                            low=[9, 10, 11],
                                            close=[11, 12, 13]))
        st.plotly_chart(fig)
