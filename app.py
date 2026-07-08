import streamlit as st
import cv2
import numpy as np
import google.generativeai as genai
import json
from PIL import Image

# Set up clean mobile-responsive web layout
st.set_page_config(page_title="AI Multi-Directional Chart Analyzer", layout="centered")

st.title("📊 AI Bi-Directional Chart Analyzer")
st.subheader("Automated Long/Short 2:1 Risk Framework")

# 1. File Uploader
uploaded_file = st.file_uploader("Drop your chart screenshot here...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Convert file to image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    st.image(uploaded_file, caption="Uploaded Chart Canvas", use_container_width=True)
    
    with st.spinner("Analyzing market bias and direction..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            model = genai.GenerativeModel(
                'gemini-2.5-flash', 
                generation_config={
                    "temperature": 0.0,
                    "response_mime_type": "application/json"
                }
            )
            
            # Convert image to format expected by Gemini
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            prompt = """
            You are a precise technical analysis engine. Look at the provided trading platform screenshot.
            
            STRICT EXTRACT RULES:
            1. DIRECTION BIAS: Determine if the recent market structure or immediate price action indicates a "LONG" (bullish/buying) or "SHORT" (bearish/shorting) setup.
            2. CURRENT PRICE: Find the massive, main current index price displayed in bold white text at the top left of the screen. This is the 'current_price'. Do NOT guess this from the graph lines.
            3. DYNAMIC STOP LOSS: 
               - If the setup is LONG: Identify a logical support low level below the current price for the 'stop_loss'.
               - If the setup is SHORT: Identify a logical resistance high level above the current price for the 'stop_loss'.
            
            Return ONLY a raw JSON object matching this structure:
            {
                "direction": "LONG" or "SHORT",
                "current_price": float,
                "stop_loss": float
            }
            """
            
            response = model.generate_content([prompt, pil_image])
            data = json.loads(response.text.strip())
            
            direction = data.get('direction', 'LONG').upper()
            entry_price = float(data.get('current_price', 0.0))
            stop_loss = float(data.get('stop_loss', 0.0))
            
            # BI-DIRECTIONAL MATHEMATICAL 2:1 RATIO CALCULATION
            if direction == "LONG":
                # For Longs: Stop Loss is below entry
                if stop_loss >= entry_price or stop_loss == 0:
                    stop_loss = entry_price - 50.0  # Default 50pt buffer
                risk = entry_price - stop_loss
                take_profit = entry_price + (risk * 2)
                
            else:  # SHORT
                # For Shorts: Stop Loss is above entry
                if stop_loss <= entry_price or stop_loss == 0:
                    stop_loss = entry_price + 50.0  # Default 50pt buffer
                risk = stop_loss - entry_price
                take_profit = entry_price - (risk * 2)
            
            st.success("Analysis & Math Complete!")
            
            # Visual indicator badge for trade direction
            if direction == "LONG":
                st.markdown("### 🟢 Direction: **LONG (Buy/Call)**")
            else:
                st.markdown("### 🔴 Direction: **SHORT (Sell/Put)**")
                
            st.markdown("### 🎯 Strict 2:1 Execution Parameters")
            
            # Display values clearly
            st.metric(label="Current Market Price (Entry)", value=f"${entry_price:,.2f}")
            st.metric(label="Stop Loss (Invalidation)", value=f"${stop_loss:,.2f}")
            st.metric(label="Take Profit (Automated 2:1 Target)", value=f"${take_profit:,.2f}")
            
            st.warning(f"**Total Risk:** {risk:,.2f} points | **Target Reward:** {(risk * 2):,.2f} points (Strict 2:1)")
            
        except Exception as e:
            st.error(f"Analysis failed. Details: {e}")
