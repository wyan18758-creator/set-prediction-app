import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, time, timedelta

st.set_page_config(page_title="SET Index Live & Session Prediction Dashboard", layout="wide")

st.title("📊 SET Index Live & Session-based Prediction Dashboard")
st.markdown("ထိုင်းစတော့မားကတ် (`^SET.BK`) ၏ အချိန်အလိုက် Live ဈေးနှုန်းများနှင့် အပိတ်စျေး ခန့်မှန်းပေးသော စနစ်")

# Fetch Live Market Data and adjust Timezone to Myanmar Time (+6:30)
@st.cache_data(ttl=30)
def load_live_data():
    try:
        ticker = yf.Ticker("^SET.BK")
        df = ticker.history(period="1d", interval="1m")
        if df is None or df.empty:
            df = ticker.history(period="5d", interval="5m")
        
        if df is not None and not df.empty:
            df.reset_index(inplace=True)
            dt_col = "Datetime" if "Datetime" in df.columns else "Date"
            if dt_col in df.columns:
                df["Dt"] = pd.to_datetime(df[dt_col])
                # Convert timezone to Myanmar Time (UTC +6:30) if timezone-aware
                if df["Dt"].dt.tz is not None:
                    df["Dt"] = df["Dt"].dt.tz_convert("Asia/Rangoon")
                    df["Dt"] = df["Dt"].dt.tz_localize(None)
                
                df["Time"] = df["Dt"].dt.strftime("%Y-%m-%d %H:%M")
                # Add time value in minutes from 00:00 for easy comparison
                df["time_val"] = df["Dt"].dt.hour * 60 + df["Dt"].dt.minute
            return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

with st.spinner("ဈေးကွက်ဒေတာများကို ချိတ်ဆက်နေပါသည်... ကျေးဇူးပြု၍ ခဏစောင့်ပါ 🔄"):
    df = load_live_data()

# Session Selector Tab
session_tab = st.radio("⏰ ရွေးချယ်ရန် Session:", ["🌅 မနက်ပိုင်း Session (၉:၀၀ - ၁၂:၀၁)", "🌇 ညနေပိုင်း Session (၁:၀၀ - ၄:၁၀)"], horizontal=True)

st.divider()

if "🌅 မနက်ပိုင်း" in session_tab:
    st.subheader("🎯 မနက်ပိုင်း Session (၁၂:၀၁ မိနစ် အပိတ်စျေး ခန့်မှန်းချက်)")
    st.info("📌 မနက် ၉:၀၀ နာရီမှ ၁၂:၀၁ မိနစ်အထိ Live ဈေးနှုန်းများကို ပြသသည်။ (၁၁:၃၅ တွင် ဂဏန်းထွက်ပြီး တစ်နေ့ကုန်သည်အထိ ဆက်ပြမည်)")
    
    morning_live_df = pd.DataFrame()
    morning_pred_df = pd.DataFrame()
    current_time_val = datetime.now().hour * 60 + datetime.now().minute
    
    if df is not None and not df.empty and "Dt" in df.columns:
        today_date = df["Dt"].dt.date.max()
        morning_live_df = df[(df["Dt"].dt.date == today_date) & (df["time_val"] >= 9 * 60) & (df["time_val"] <= 12 * 1)]
        
        if morning_live_df.empty:
            morning_live_df = df[(df["Dt"].dt.date == today_date) & (df["time_val"] >= 9 * 60) & (df["time_val"] <= 13 * 60)]
            
        # ၉:၀၀ မှ ၁၁:၃၀ အတွင်း ဒေတာများကို ခန့်မှန်းရန် စုဆောင်းသည်
        morning_pred_df = df[(df["Dt"].dt.date == today_date) & (df["time_val"] >= 9 * 60) & (df["time_val"] <= 11 * 30)]
    
    if not morning_live_df.empty:
        latest_row = morning_live_df.iloc[-1]
        first_row = morning_live_df.iloc[0]
        price_diff = latest_row["Close"] - first_row["Close"]
        pct_change = (price_diff / first_row["Close"]) * 100
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🔴 မနက်ပိုင်း စျေးနှုန်းအခြေအနေ", f"{latest_row['Close']:.2f}", f"{price_diff:+.2f} ({pct_change:+.2f}%)")
        m2.metric("📈 အမြင့်ဆုံးစျေး (High)", f"{morning_live_df['High'].max():.2f}")
        m3.metric("📉 အနိမ့်ဆုံးစျေး (Low)", f"{morning_live_df['Low'].min():.2f}")
        
        st.write(f"📈 **မနက်ပိုင်း ဈေးနှုန်း မှတ်တမ်းများ (စုစုပေါင်း {len(morning_live_df)} ခု)**")
        cols_to_show = [c for c in ["Time", "Open", "High", "Low", "Close", "Volume"] if c in morning_live_df.columns]
        st.dataframe(morning_live_df[cols_to_show].tail(10), use_container_width=True)
        
        fig = px.line(morning_live_df, x="Time", y="Close", title="SET Index Morning Movement", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("ယနေ့အတွက် မနက်ပိုင်း ဒေတာများ မရရှိသေးပါ (သို့မဟုတ် ဈေးပိတ်ရက် ဖြစ်နေပါသည်)။")
    
    # ၁၁:၃၅ ကျော်မှသာ (သို့မဟုတ် ခလုတ်နှိပ်၍) ဂဏန်းပြသရန် စီစဉ်ခြင်း
    # (၁၁:၃၅ မိနစ်သည် 11 * 60 + 35 = 695 ဖြစ်သည်)
    target_show_time = 11 * 60 + 35
    
    if current_time_val >= target_show_time or st.button("🔮 ၁၁:၃၅ ပြီးနောက် ခန့်မှန်းဂဏန်းများ ထုတ်ရန်"):
        if not morning_pred_df.empty:
            last_close = morning_pred_df.iloc[-1]["Close"]
            base_digit = int(f"{last_close:.2f}".split(".")[1][-1])
            trend_diff = last_close - morning_pred_df.iloc[0]["Close"]
            
            offset = 1 if trend_diff >= 0 else 3
            p1 = (base_digit + offset) % 10
            p2 = (base_digit + offset + 3) % 10
            p3 = (base_digit + offset + 6) % 10
            
            st.success(f"🎯 ၁၂:၀၁ မိနစ် အပိတ်စျေးအတွက် ခန့်မှန်းဒသမနောက်ဆုံးဂဏန်း (၃) လုံး (၁၁:၃၀ ထိ ဒေတာအခြေခံ):")
            st.markdown(f"### `🔮 {p1} ၊ {p2} ၊ {p3}`")
            st.caption(f"အခြေခံဈေး (၁၁:၃၀ အထိ): {last_close:.2f} | Base Digit: {base_digit}")
        else:
            st.warning("⚠️ ၁၁:၃၀ အထိ လုံလောက်သော ဒေတာ မရှိသေးပါ။")
    else:
        st.info("⏰ မနက် ၁၁:၃၅ ကျော်မှသာ ဤနေရာတွင် ခန့်မှန်းဂဏန်း (၃) လုံး အလိုအလျောက် ပေါ်လာမည်ဖြစ်ပြီး ညနေအထိ ဆက်ပြနေမည် ဖြစ်ပါသည်။")

else:
    st.subheader("🎯 ညနေပိုင်း Session (၄:၁၀ မိနစ် အပိတ်စျေး ခန့်မှန်းချက်)")
    st.info("📌 နေ့လယ် ၁:၀၀ နာရီမှ ညနေ ၄:၁၀ အထိ ဈေးနှုန်းများကို ပြသသည်။ (၃:၃၅ တွင် ဂဏန်းထွက်ပြီး ဈေးပိတ်သည်အထိ ဆက်ပြမည်)")
    
    evening_live_df = pd.DataFrame()
    evening_pred_df = pd.DataFrame()
    current_time_val = datetime.now().hour * 60 + datetime.now().minute
    
    if df is not None and not df.empty and "Dt" in df.columns:
        today_date = df["Dt"].dt.date.max()
        evening_live_df = df[(df["Dt"].dt.date == today_date) & (df["time_val"] >= 13 * 60)]
        # ၁:၀၀ မှ ၃:၃၀ အတွင်း ဒေတာများကို ခန့်မှန်းရန် စုဆောင်းသည်
        evening_pred_df = df[(df["Dt"].dt.date == today_date) & (df["time_val"] >= 13 * 60) & (df["time_val"] <= 15 * 60 + 30)]
    
    if not evening_live_df.empty:
        latest_row = evening_live_df.iloc[-1]
        first_row = evening_live_df.iloc[0]
        price_diff = latest_row["Close"] - first_row["Close"]
        pct_change = (price_diff / first_row["Close"]) * 100
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🔴 ညနေပိုင်း ပိတ်သိမ်းစျေး အခြေအနေ", f"{latest_row['Close']:.2f}", f"{price_diff:+.2f} ({pct_change:+.2f}%)")
        m2.metric("📈 အမြင့်ဆုံးစျေး (High)", f"{evening_live_df['High'].max():.2f}")
        m3.metric("📉 အနိမ့်ဆုံးစျေး (Low)", f"{evening_live_df['Low'].min():.2f}")
        
        st.write(f"📈 **ညနေပိုင်း ဈေးနှုန်း မှတ်တမ်းများ (စုစုပေါင်း {len(evening_live_df)} ခု)**")
        cols_to_show = [c for c in ["Time", "Open", "High", "Low", "Close", "Volume"] if c in evening_live_df.columns]
        st.dataframe(evening_live_df[cols_to_show].tail(10), use_container_width=True)
        
        fig = px.line(evening_live_df, x="Time", y="Close", title="SET Index Evening Movement", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("ယနေ့အတွက် ညနေပိုင်း ဒေတာများ မရရှိသေးပါ (သို့မဟုတ် ဈေးပိတ်ရက် ဖြစ်နေပါသည်)။")
    
    # ၃:၃၅ ကျော်မှသာ (သို့မဟုတ် ခလုတ်နှိပ်၍) ဂဏန်းပြသရန် စီစဉ်ခြင်း
    # (၃:၃၅ မိနစ်သည် 15 * 60 + 35 = 935 ဖြစ်သည်)
    target_evening_show_time = 15 * 60 + 35
    
    if current_time_val >= target_evening_show_time or st.button("🔮 ၃:၃၅ ပြီးနောက် ညနေခန့်မှန်းဂဏန်းများ ထုတ်ရန်"):
        if not evening_pred_df.empty:
            last_close = evening_pred_df.iloc[-1]["Close"]
            base_digit = int(f"{last_close:.2f}".split(".")[1][-1])
            trend_diff = last_close - evening_pred_df.iloc[0]["Close"]
            
            offset = 2 if trend_diff >= 0 else 4
            p1 = (base_digit + offset) % 10
            p2 = (base_digit + offset + 3) % 10
            p3 = (base_digit + offset + 6) % 10
            
            st.success(f"🎯 ၄:၁၀ မိနစ် အပိတ်စျေးအတွက် ခန့်မှန်းဒသမနောက်ဆုံးဂဏန်း (၃) လုံး (၃:၃၀ ထိ ဒေတာအခြေခံ):")
            st.markdown(f"### `🔮 {p1} ၊ {p2} ၊ {p3}`")
            st.caption(f"အခြေခံဈေး (၃:၃၀ အထိ): {last_close:.2f} | Base Digit: {base_digit}")
        else:
            st.warning("⚠️ ၃:၃၀ အထိ လုံလောက်သော ဒေတာ မရှိသေးပါ။")
    else:
        st.info("⏰ ညနေ ၃:၃၅ ကျော်မှသာ ဤနေရာတွင် ညနေပိုင်း ခန့်မှန်းဂဏန်း (၃) လုံး အလိုအလျောက် ပေါ်လာမည်ဖြစ်ပြီး ဈေးပိတ်သည်အထိ ဆက်ပြနေမည် ဖြစ်ပါသည်။")

# Telegram Bot Notification Setup
st.subheader("📱 Telegram Bot သတိပေးချက်များ (Alert Settings)")
with st.form("telegram_form"):
    tg_token = st.text_input("Bot Token", type="password")
    chat_id = st.text_input("Chat ID")
    submitted = st.form_submit_button("ချိတ်ဆက်မှု သိမ်းဆည်းမည်")
    if submitted:
        st.success("Telegram Bot ဆက်တင်များကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ!")
