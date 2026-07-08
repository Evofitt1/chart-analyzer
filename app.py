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
    
    with st.spinner("Analyzing price action structure..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # Lock temperature to 0.0 for strict OCR reading
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
            You are a technical analysis OCR engine. Your sole task is to identify the current price structure.
            
            DYNAMIC RULES:
            1. Look at the right-hand side Y-axis price scale. Determine the exact current multi-digit range (e.g., 29,xxx, 31,xxx, etc.).
            2. Locate the prominent support/resistance level or recent order block to determine a "Suggested Entry".
            3. Locate the logical invalidation level just below structure to determine a "Stop Loss".
            
            Return ONLY a raw JSON object matching this structure:
            {
                "entry": float,
                "stop_loss": float
            }
            """
            
            # Pass the PIL image format instead of the numpy array
            response = model.generate_content([prompt, pil_image])
            data = json.loads(response.text.strip())
            
            # Extract the raw prices read by the AI
            entry_price = float(data.get('entry', 0.0))
            stop_loss = float(data.get('stop_loss', 0.0))
            
            # HARDCODED MATHEMATICAL 2:1 RATIO CALCULATION
            risk = entry_price - stop_loss
            
            if risk > 0:
                take_profit = entry_price + (risk * 2)
            else:
                take_profit = entry_price * 1.01 
            
            st.success("Analysis & Math Complete!")
            st.markdown("### 🎯 Strict 2:1 Execution Parameters")
            
            # Display values clearly
            st.metric(label="Suggested Entry (Structure)", value=f"${entry_price:,.2f}")
            st.metric(label="Stop Loss (Invalidation)", value=f"${stop_loss:,.2f}")
            st.metric(label="Take Profit (Automated 2:1 Target)", value=f"${take_profit:,.2f}")
            
            st.warning(f"**Total Risk:** ${risk:,.2f} points | **Target Reward:** ${(risk * 2):,.2f} points (Strict 2:1)")
            
        except Exception as e:
            st.error(f"Analysis failed. Details: {e}")


