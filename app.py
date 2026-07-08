import streamlit as st
import cv2
import numpy as np
import google.generativeai as genai
import json
from PIL import Image

# Responsive trading cockpit layout
st.set_page_config(page_title="AI Autonomous Order Flow Engine", layout="centered")

st.title("🤖 Autonomous Order Flow Engine")
st.subheader("Unbiased Price Action, Liquidity, & Bracket Extractor")

st.markdown("""
---
### 📸 Drop Your Charts Here
Upload up to two screenshot canvases (e.g., execution view, order book depth, or a wider timeframe setup). The engine will cross-examine them without any manual price inputs.
""")

# Multiple file uploader layout
uploaded_files = st.file_uploader(
    "Upload trading screen captures...", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    pil_images = []
    
    # Render visuals on screen
    for i, file in enumerate(uploaded_files[:2]): # Cap at two canvases for performance
        file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        st.image(file, caption=f"Canvas {i+1}: {file.name}", use_container_width=True)
        
        # Prepare for API transmission
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_images.append(Image.fromarray(rgb_image))
        
    with st.spinner("🤖 Extracting raw order blocks, scanning volume depth, and mapping execution brackets..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel(
                'gemini-2.5-flash', 
                generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
            
            # The prompt is now strictly instructed to generate its own entry based on raw market structure
            prompt = """
            You are an autonomous institutional execution router. Your function is to analyze the provided market screens with absolute, unbiased precision.
            Do not rely on any user inputs. Inspect the raw text values, volume profile shelves, depth of market bars, and price action layouts to extract a precise trade setup.
            
            CORE ALGORITHMIC OBJECTIVES:
            1. CURRENT PRICE: Locate the bold, active index price level displayed on the chart/DOM. Use this as your reference point.
            2. INSTITUTIONAL IMBALANCE: Scan for high-volume nodes, heavy bid/ask order blocks, and clear supply/demand zones.
            3. DIRECTION BIAS: Determine the high-probability path ("LONG" or "SHORT") by checking if current price is bouncing off demand/bids or failing at an overhead supply block. Look closely for fakeouts or exhaustion.
            4. EXECUTION BRACKETS:
               - Entry Price: Determine the optimal fill level right at or near the current market price text context.
               - Stop Loss: Place it cleanly behind the nearest heavy visual volume shelf or structural invalidation level.
               - Take Profit: Project a mathematical target balancing market structures and major liquidity barriers.
            
            Return ONLY a raw JSON object with this exact schema:
            {
                "direction": "LONG" or "SHORT",
                "entry_price": float,
                "stop_loss": float,
                "take_profit": float,
                "market_logic": "A crisp, concise reason why the AI chose these exact structural levels based on order blocks and volume."
            }
            """
            
            response = model.generate_content([prompt] + pil_images)
            data = json.loads(response.text.strip())
            
            direction = data.get('direction', 'LONG').upper()
            entry = float(data.get('entry_price', 0.0))
            stop = float(data.get('stop_loss', 0.0))
            tp = float(data.get('take_profit', 0.0))
            logic = data.get('market_logic', '')
            
            # Defensive validation check if vision fails to extract clean parameters
            if entry == 0.0:
                st.error("Engine failed to extract clear numbers from image text. Ensure screenshots are high-resolution.")
                st.stop()
                
            # Compute exact risk metrics for MNQ spec ($2.00/point)
            points_risk = abs(entry - stop)
            points_reward = abs(tp - entry)
            cash_risk = points_risk * 2.0
            cash_reward = points_reward * 2.0
            
            # --- DASHBOARD DISPLAY ---
            st.markdown("---")
            st.success("📐 Autonomous Structural Matrix Mapped!")
            
            # Display Directional Badge
            if direction == "LONG":
                st.markdown("### 🟢 Unbiased Bias: **LONG**")
            else:
                st.markdown("### 🔴 Unbiased Bias: **SHORT**")
                
            st.info(f"**Structural Rationale:** {logic}")
            
            st.markdown("### 🎯 Machine-Calculated Execution Targets")
            st.metric(label="🟢 TARGET TAKE PROFIT", value=f"{tp:,.2f}")
            st.metric(label="⚪ AUTOMATED ENTRY ENTRY", value=f"{entry:,.2f}")
            st.metric(label="🔴 STRUCTURAL STOP LOSS", value=f"{stop:,.2f}")
            
            # Dynamic cash value footer based on the AI's actual calculated parameters
            st.warning(f"**Calculated Specs:** Risking {points_risk:.2f} pts (${cash_risk:.2f}) to bank {points_reward:.2f} pts (${cash_reward:.2f}) per contract.")
            
        except Exception as e:
            st.error(f"Autonomous scan encountered an error. Details: {e}")
