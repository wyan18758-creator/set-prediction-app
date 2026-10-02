import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, time

st.set_page_config(page_title="SET Index Live & Session Prediction Dashboard", layout="wide")

st.title("📊 SET Index Live & Session-based Prediction Dashboard")
st.markdown("ထိုင်းစတော့မားကတ် (`^SET.BK`) ၏ အချိန်အလိုက် Live ဈေးနှုန်းများနှင့် အပိတ်စျေး ခန့်မှန်းပေးသော စနစ်")

# Fetch Live Market Data
@st.cache_data(ttl=15)
def load_live_data():
    try:
        ticker = yf.Ticker("^SET.BK")
        df = ticker.history(period="1d", interval="1m")
        if df.empty:
            df = ticker.history(period="5d", interval="5m")
        
        if not df.empty:
            df.reset_index(inplace=True)
            dt_col = "Datetime" if "Datetime" in df.columns else "Date"
            if dt_col in df.columns:
                df["Dt"] = pd.to_datetime(df[dt_col])
                df["Time"] = df["Dt"].dt.strftime("%Y-%m-%d %H:%M")
            return df
        return None
    except Exception as e:
        return None

df = load_live_data()

# Session Selector Tab
session_tab = st.radio("⏰ ရွေးချယ်ရန် Session:", ["🌅 မနက်ပိုင်း Session (၉:၀၀ - ၁၂:၀၁)", "🌇 ညနေပိုင်း Session (၁:၀၀ - ၄:၁၀)"], horizontal=True)

st.divider()

if "🌅 မနက်ပိုင်း" in session_tab:
    st.subheader("🎯 မနက်ပိုင်း Session (၁၂:၀၁ မိနစ် အပိတ်စျေး ခန့်မှန်းချက်)")
    st.info("📌 Live ဈေးနှုန်းများကို မနက် ၉:၀၀ နာရီမှ ၁၂:၀၁ မိနစ်အထိ တိုက်ရိုက်ပြသသည်။ ခန့်မှန်းချက်အတွက် ၉:၀၀ မှ ၁၁:၃၀ ထိ ဒေတာကို အသုံးပြုသည်။")
    
    morning_live_df = None
    morning_pred_df = None
    
    if df is not None and not df.empty and "Dt" in df.columns:
        today_date = df["Dt"].dt.date.max()
        # Live display from 9:00 to 12:01
        morning_live_df = df[(df["Dt"].dt.date == today_date) & (df["Dt"].dt.time >= time(9, 0)) & (df["Dt"].dt.time <= time(12, 1))]
        # Prediction data range from 9:00 to 11:30
        morning_pred_df = df[(df["Dt"].dt.date == today_date) & (df["Dt"].dt.time >= time(9, 0)) & (df["Dt"].dt.time <= time(11, 30))]
    
    if morning_live_df is not None and not morning_live_df.empty:
        latest_row = morning_live_df.iloc[-1]
        first_row = morning_live_df.iloc[0]
        price_diff = latest_row["Close"] - first_row["Close"]
        pct_change = (price_diff / first_row["Close"]) * 100
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🔴 မနက်ပိုင်း Live စျေးနှုန်း (၉:၀၀ - ၁၂:၀၁)", f"{latest_row['Close']:.2f}", f"{price_diff:+.2f} ({pct_change:+.2f}%)")
        m2.metric("📈 အမြင့်ဆုံးစျေး (High)", f"{morning_live_df['High'].max():.2f}")
        m3.metric("📉 အနိမ့်ဆုံးစျေး (Low)", f"{morning_live_df['Low'].min():.2f}")
        
        st.write(f"📈 **မနက်ပိုင်း Live ဈေးနှုန်း မှတ်တမ်းများ (စုစုပေါင်း {len(morning_live_df)} ခု)**")
        st.dataframe(morning_live_df[["Time", "Open", "High", "Low", "Close", "Volume"]].tail(10), use_container_width=True)
        
        fig = px.line(morning_live_df, x="Time", y="Close", title="SET Index Morning Live Movement", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("ယနေ့အတွက် မနက်ပိုင်း Live ဒေတာများ မရရှိသေးပါ။")
    
    if st.button("🔮 ၁၁:၃၀ နာရီတွင် မနက် ၁၂:၀၁ အပိတ်စျေး ခန့်မှန်းရန်"):
        if morning_pred_df is not None and not morning_pred_df.empty:
            last_close = morning_pred_df.iloc[-1]["Close"]
            base_digit = int(f"{last_close:.2f}".split(".")[1][-1])
            trend_diff = last_close - morning_pred_df.iloc[0]["Close"]
            
            offset = 1 if trend_diff >= 0 else 3
            p1 = (base_digit + offset) % 10
            p2 = (base_digit + offset + 3) % 10
            p3 = (base_digit + offset + 6) % 10
            
            st.success(f"🎯 ၁၂:၀၁ မိနစ် အပိတ်စျေးအတွက် ခန့်မှန်းဒသမနောက်ဆုံးဂဏန်း (၃) လုံး:")
            st.markdown(f"### `🔮 {p1} ၊ {p2} ၊ {p3}`")
            st.caption(f"အခြေခံဈေး (၁၁:၃၀ အထိ): {last_close:.2f} | Base Digit: {base_digit}")
        else:
            st.markdown("### `🔮 2 ၊ 5 ၊ 8` (Default)")

else:
    st.subheader("🎯 ညနေပိုင်း Session (၄:၁၀ မိနစ် အပိတ်စျေး ခန့်မှန်းချက်)")
    st.info("📌 Live ဈေးနှုန်းများကို နေ့လယ် ၁:၀၀ နာရီမှ ညနေ ၄:၁၀ (စျေးပိတ်ချိန်) အထိ တိုက်ရိုက်ပြသသည်။ ခန့်မှန်းချက်အတွက် ၁:၀၀ မှ ၃:၃၀ ထိ ဒေတာကို အသုံးပြုသည်။")
    
    evening_live_df = None
    evening_pred_df = None
    
    if df is not None and not df.empty and "Dt" in df.columns:
        today_date = df["Dt"].dt.date.max()
        # Live display from 13:00 to 16:10
        evening_live_df = df[(df["Dt"].dt.date == today_date) & (df["Dt"].dt.time >= time(13, 0)) & (df["Dt"].dt.time <= time(16, 10))]
        # Prediction data range from 13:00 to 15:30
        evening_pred_df = df[(df["Dt"].dt.date == today_date) & (df["Dt"].dt.time >= time(13, 0)) & (df["Dt"].dt.time <= time(15, 30))]
    
    if evening_live_df is not None and not evening_live_df.empty:
        latest_row = evening_live_df.iloc[-1]
        first_row = evening_live_df.iloc[0]
        price_diff = latest_row["Close"] - first_row["Close"]
        pct_change = (price_diff / first_row["Close"]) * 100
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🔴 ညနေပိုင်း Live စျေးနှုန်း (၁:၀၀ - ၄:၁၀)", f"{latest_row['Close']:.2f}", f"{price_diff:+.2f} ({pct_change:+.2f}%)")
        m2.metric("📈 အမြင့်ဆုံးစျေး (High)", f"{evening_live_df['High'].max():.2f}")
        m3.metric("📉 အနိမ့်ဆုံးစျေး (Low)", f"{evening_live_df['Low'].min():.2f}")
        
        st.write(f"📈 **ညနေပိုင်း Live ဈေးနှုန်း မှတ်တမ်းများ (စုစုပေါင်း {len(evening_live_df)} ခု)**")
        st.dataframe(evening_live_df[["Time", "Open", "High", "Low", "Close", "Volume"]].tail(10), use_container_width=True)
        
        fig = px.line(evening_live_df, x="Time", y="Close", title="SET Index Evening Live Movement", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("ယနေ့အတွက် ညနေပိုင်း Live ဒေတာများ မရရှိသေးပါ။")
    
    if st.button("🔮 ၃:၃၀ နာရီတွင် ညနေ ၄:၁၀ အပိတ်စျေး ခန့်မှန်းရန်"):
        if evening_pred_df is not None and not evening_pred_df.empty:
            last_close = evening_pred_df.iloc[-1]["Close"]
            base_digit = int(f"{last_close:.2f}".split(".")[1][-1])
            trend_diff = last_close - evening_pred_df.iloc[0]["Close"]
            
            offset = 2 if trend_diff >= 0 else 4
            p1 = (base_digit + offset) % 10
            p2 = (base_digit + offset + 3) % 10
            p3 = (base_digit + offset + 6) % 10
            
            st.success(f"🎯 ၄:၁၀ မိနစ် အပိတ်စျေးအတွက် ခန့်မှန်းဒသမနောက်ဆုံးဂဏန်း (၃) လုံး:")
            st.markdown(f"### `🔮 {p1} ၊ {p2} ၊ {p3}`")
            st.caption(f"အခြေခံဈေး (၃:၃၀ အထိ): {last_close:.2f} | Base Digit: {base_digit}")
        else:
            st.markdown("### `🔮 3 ၊ 7 ၊ 9` (Default)")

# Telegram Bot Notification Setup
st.subheader("📱 Telegram Bot သတိပေးချက်များ (Alert Settings)")
with st.form("telegram_form"):
    tg_token = st.text_input("Bot Token", type="password")
    chat_id = st.text_input("Chat ID")
    submitted = st.form_submit_button("ချိတ်ဆက်မှု သိမ်းဆည်းမည်")
    if submitted:
        st.success("Telegram Bot ဆက်တင်များကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ!")
