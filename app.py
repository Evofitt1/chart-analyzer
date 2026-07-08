import streamlit as st
import cv2
import numpy as np
import google.generativeai as genai
import json
from PIL import Image

# Set up clean mobile-responsive web layout
st.set_page_config(page_title="AI 2:1 Chart Analyzer", layout="centered")

st.title("📊 AI 2:1 Chart Analyzer")
st.subheader("Automated Risk-to-Reward Framework")

# 1. File Uploader
uploaded_file = st.file_uploader("Drop your chart screenshot here...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Convert file to image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    st.image(uploaded_file, caption="Uploaded Chart Canvas", use_container_width=True)
    
    with st.spinner("Analyzing current market price..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # Lock temperature to 0.0 for strict OCR accuracy
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
            You are a precise data extraction engine. Look at the provided trading platform screenshot.
            
            STRICT EXTRACT RULES:
            1. Find the massive, main current index price displayed in bold white text at the top left of the screen (e.g., 29,440.25). This is the absolute 'current_price'. Do NOT guess or pull from the graph lines for this.
            2. Look at the chart structure below it. Find the nearest logical support or invalidation low level shown in the recent price swing to determine a 'stop_loss'. 
               - Ensure the stop_loss is dynamically scaled to match the 5-digit range of the current price (e.g., if current is 29,440, the stop loss should be a logical number below it like 29,350 or 29,400 depending on the chart visual).
            
            Return ONLY a raw JSON object matching this structure:
            {
                "current_price": float,
                "stop_loss": float
            }
            """
            
            # Pass the PIL image format instead of the numpy array
            response = model.generate_content([prompt, pil_image])
            data = json.loads(response.text.strip())
            
            # Set entry exactly to the live price found at the top
            entry_price = float(data.get('current_price', 0.0))
            stop_loss = float(data.get('stop_loss', 0.0))
            
            # If the AI fails or places stop loss above current price, create a default 50-point risk buffer
            if stop_loss >= entry_price or stop_loss == 0:
                stop_loss = entry_price - 50.0
            
            # HARDCODED MATHEMATICAL 2:1 RATIO CALCULATION
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * 2)
            
            st.success("Analysis & Math Complete!")
            st.markdown("### 🎯 Strict 2:1 Live Execution Parameters")
            
            # Display values clearly
            st.metric(label="Current Market Price (Entry)", value=f"${entry_price:,.2f}")
            st.metric(label="Stop Loss (Invalidation)", value=f"${stop_loss:,.2f}")
            st.metric(label="Take Profit (Automated 2:1 Target)", value=f"${take_profit:,.2f}")
            
            st.warning(f"**Total Risk:** {risk:,.2f} points | **Target Reward:** {(risk * 2):,.2f} points (Strict 2:1)")
            
        except Exception as e:
            st.error(f"Analysis failed. Details: {e}")
