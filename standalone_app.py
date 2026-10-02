import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="SET Index Prediction Dashboard", page_icon="📈", layout="wide")

st.title("📈 SET Index Prediction Dashboard")
st.markdown("သီးသန့်လည်ပတ်နေသော ဈေးနှုန်းခန့်မှန်းချက်နှင့် ဒေတာကြည့်ရှုသည့် Dashboard")

# Load Market History CSV
history_file = "market_history.csv"
if os.path.exists(history_file):
    df = pd.read_csv(history_file)
    st.subheader("📊 ဈေးနှုန်း မှတ်တမ်းများ (Market History)")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("market_history.csv ဖိုင် မတွေ့ရသေးပါ။")

# Load Learning Memory JSON
memory_file = "learning_memory.json"
if os.path.exists(memory_file):
    with open(memory_file, "r") as f:
        memory_data = json.load(f)
    st.subheader("🧠 စနစ်၏ မှတ်ဉာဏ်နှင့် အချက်အလက်များ (Learning Memory)")
    st.json(memory_data)
else:
    st.info("learning_memory.json ဖိုင် အလွတ် သို့မဟုတ် မရှိသေးပါ။")
