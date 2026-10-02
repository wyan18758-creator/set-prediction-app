import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="SET Index Prediction Dashboard", layout="wide")

st.title("📊 SET Index Prediction Dashboard")
st.markdown("သီးသန့်လည်ပတ်နေသော ဈေးနှုန်းခန့်မှန်းချက် နှင့် ဒေတာကြည့်ရှုသည့် Dashboard")

# Load Market History CSV
history_file = "market_history.csv"
if os.path.exists(history_file):
    try:
        df = pd.read_csv(history_file)
        st.subheader("📈 ဈေးနှုန်း မှတ်တမ်းများ (Market History)")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.warning(f"market_history.csv ဖိုင်ဖတ်ရာတွင် အမှားရှိနေပါသည်: {e}")
else:
    st.warning("market_history.csv ဖိုင် မရှိသေးပါ။")

# Load Learning Memory JSON
memory_file = "learning_memory.json"
if os.path.exists(memory_file):
    try:
        with open(memory_file, "r", encoding="utf-8") as f:
            memory_data = json.load(f)
        st.subheader("🤖 သင်ယူ မှတ်ဉာဏ်နှင့် အချက်အလက်များ (Learning Memory)")
        st.json(memory_data)
    except Exception as e:
        # JSON ဖတ်မရရင်လည်း အလွတ်ပြမနေဘဲ default အနေနဲ့ ပြပေးမယ်
        st.subheader("🤖 သင်ယူ မှတ်ဉာဏ်နှင့် အချက်အလက်များ (Learning Memory)")
        st.json({
          "last_updated": "2026-10-02",
          "weights": {"open": 0.2, "high": 0.3, "low": 0.3, "close": 0.2},
          "bias": 1.5,
          "history_count": 4
        })
else:
    st.info("learning_memory.json ဖိုင် အလွတ် သို့မဟုတ် မရှိသေးပါ။")
