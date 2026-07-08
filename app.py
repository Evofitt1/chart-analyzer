import streamlit as st
import cv2
import numpy as np
import google.generativeai as genai
import json
from PIL import Image

# High-velocity compact layout
st.set_page_config(page_title="MNQ 25-Point Velocity Scalper", layout="centered")

st.title("⚡ MNQ 25-Point Velocity Engine")
st.subheader("High-Probability Momentum Bracket Framework")

st.markdown("""
> **Velocity Scalp Target Specs:**
> * **Profit Target:** 25 Points ($50.00 Gross Profit per contract)
> * **Protection Stop:** 10 Points ($20.00 Risk per contract)
> * **Risk-to-Reward Ratio:** Highly efficient **1:2.5**
""")

# --- 1. INSTANT EXECUTION PANEL ---
st.markdown("### 🕹️ Real-Time Execution Bracket")
col1, col2 = st.columns([2, 1])

with col1:
    entry_price = st.number_input("🔢 TYPE ENTRY PRICE & HIT ENTER:", value=0.0, step=0.25, format="%.2f")
with col2:
    bias = st.radio("MOMENTUM DIRECTION:", ["LONG (Buy)", "SHORT (Sell)"], horizontal=False)

# Fixed Velocity Parameters for the 25-point model
TARGET_POINTS = 25.0
STOP_POINTS = 10.0
MULTIPLIER = 2.0  # $2 per index point for MNQ

if entry_price > 0.0:
    # Mechanical Bracket Engine
    if "LONG" in bias:
        take_profit = entry_price + TARGET_POINTS
        stop_loss = entry_price - STOP_POINTS
    else:  # SHORT
        take_profit = entry_price - TARGET_POINTS
        stop_loss = entry_price + STOP_POINTS
        
    cash_risk = STOP_POINTS * MULTIPLIER
    cash_reward = TARGET_POINTS * MULTIPLIER
    
    # Instant High-Visibility Dashboard
    st.markdown("---")
    st.markdown(f"### 🎯 Active Bracket: **{bias} Setup**")
    
    st.metric(label="🟢 AUTOMATED TAKE PROFIT TARGET (+25 Pts)", value=f"{take_profit:,.2f}")
    st.metric(label="⚪ ENTRY BASELINE PRICE", value=f"{entry_price:,.2f}")
    st.metric(label="🔴 PROTECTION STOP LOSS (-10 Pts)", value=f"{stop_loss:,.2f}")
    
    # Risk Profile Metrics
    st.error(f"**Execution Summary:** Risking ${cash_risk:.2f} to bank ${cash_reward:.2f} per contract.")
    st.markdown("---")

# --- 2. BACKEND BLOCK INTEGRITY ENGINE (Optional) ---
st.markdown("### 📸 Optional: Quick Order Block Validation")
uploaded_file = st.file_uploader("Drop a 1-minute chart or DOM snippet to check underlying order blocks...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None and entry_price > 0.0:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    
    with st.spinner("Analyzing immediate liquidity blocks..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel(
                'gemini-2.5-flash', 
                generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
            
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            prompt = f"""
            You are a high-speed futures execution system. The trader is taking a 25-point velocity scalp at {entry_price} with a direction bias of {bias}.
            Analyze the immediate horizontal volume profile shelves or order book clusters in this screenshot.
            Identify if there is an institutional block or immediate wall that could trap this 25-point push.
            Return ONLY a raw JSON object matching this structure:
            {{
                "path_clear": "YES" or "NO",
                "nearest_wall": float,
                "flow_analysis": "A single sentence explaining if order flow supports a quick 25-point push."
            }}
            """
            
            response = model.generate_content([prompt, pil_image])
            data = json.loads(response.text.strip())
            
            path_clear = data.get("path_clear", "YES")
            nearest_wall = float(data.get("nearest_wall", 0.0))
            flow_analysis = data.get("flow_analysis", "")
            
            st.markdown("#### 🤖 Instant Order Flow Telemetry")
            if path_clear == "NO":
                st.error(f"🚨 IMMEDIATE RESISTANCE WALL SPOTTED AT {nearest_wall:,.2f}: {flow_analysis}")
            else:
                st.success(f"✅ MOMENTUM PATH CLEAR: {flow_analysis}")
                
        except Exception as e:
            st.caption(f"Visual check bypassed: {e}")
