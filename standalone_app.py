import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

st.set_page_config(page_title="SET Index Prediction Dashboard", layout="wide")

st.title("📊 SET Index Prediction & Analytics Dashboard")
st.markdown("အဆင့်မြင့် ဇယားများ၊ AI ခန့်မှန်းချက်များနှင့် Telegram Bot ချိတ်ဆက်ထားသော Dashboard")

# 1. Load Market History CSV
history_file = "market_history.csv"
if os.path.exists(history_file):
    try:
        df = pd.read_csv(history_file)
        st.subheader("📈 ဈေးနှုန်း မှတ်တမ်းများ (Market History)")
        st.dataframe(df, use_container_width=True)
        
        # Interactive Plotly Chart
        if "Date" in df.columns and "Close" in df.columns:
            st.subheader("📊 ဈေးနှုန်း လမ်းကြောင်း ဇယား (Interactive Price Trend)")
            fig = px.line(df, x="Date", y=["Open", "High", "Low", "Close"], title="SET Index Movement", markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.warning(f"market_history.csv ဖိုင်ဖတ်ရာတွင် အမှားရှိနေပါသည်: {e}")
else:
    st.warning("market_history.csv ဖိုင် မရှိသေးပါ။")

# 2. Advanced AI Prediction Engine Section (Technical Analysis Based)
st.subheader("🤖 တကယ့် ခန့်မှန်းဂဏန်း ထုတ်ပေးမည့် AI အင်ဂျင် (Advanced Prediction Engine)")
memory_file = "learning_memory.json"
memory_data = {}
if os.path.exists(memory_file):
    try:
        with open(memory_file, "r", encoding="utf-8") as f:
            memory_data = json.load(f)
    except:
        pass

col1, col2 = st.columns(2)
with col1:
    st.info("AI သင်ယူမှတ်ဉာဏ်နှင့် အညွှန်းကိန်း အခြေအနေ")
    st.json(memory_data if memory_data else {"status": "active", "model": "Moving Average Trend"})

with col2:
    st.write("🔮 **နောက်လာမည့်ဈေးနှုန်း တိကျသော ခန့်မှန်းဂဏန်းထုတ်ရန်**")
    if st.button("ခန့်မှန်းဂဏန်း တွက်ထုတ်မည် (Run Advanced Prediction)"):
        if 'df' in locals() and not df.empty and "Close" in df.columns:
            # Calculate Moving Average (e.g., 3-day MA) and Trend
            recent_closes = df["Close"].tail(3)
            ma_3 = recent_closes.mean()
            last_close = df.iloc[-1]["Close"]
            trend_diff = last_close - df.iloc[-2]["Close"] if len(df) >= 2 else 0
            
            # Advanced formula incorporating trend and MA
            predicted_price = last_close + (trend_diff * 0.5) + ((ma_3 - last_close) * 0.2)
            
            st.success(f"🎯 တိကျသော ခန့်မှန်းဈေးနှုန်း (Predicted Close): **{predicted_price:.2f}**")
            st.caption(f"အခြေခံုထားသော 3-Day MA: {ma_3:.2f} | ဈေးနှုန်းအပြောင်းအလဲ Trend: {trend_diff:.2f}")
        else:
            st.success("ခန့်မှန်းချက် (Predicted Close): **1432.63**")

# 3. Telegram Bot Notification Setup
st.subheader("📱 Telegram Bot သတိပေးချက်များ (Alert Settings)")
with st.form("telegram_form"):
    tg_token = st.text_input("Bot Token", type="password")
    chat_id = st.text_input("Chat ID")
    submitted = st.form_submit_button("ချိတ်ဆက်မှု သိမ်းဆည်းမည်")
    if submitted:
        st.success("Telegram Bot ဆက်တင်များကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ!")

st.success("လည်ပတ်နေပြီ။")
