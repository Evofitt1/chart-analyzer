import streamlit as st
import cv2
import numpy as np
import google.generativeai as genai
import json
from PIL import Image

# Responsive trading cockpit layout
st.set_page_config(page_title="AI Autonomous Order Flow Engine", layout="centered")

st.title("🤖 Autonomous Order Flow Engine")
st.subheader("Unbiased Price Action, Liquidity, & Interactive Interrogator")

st.markdown("""
---
### 📸 Drop Your Charts Here
Upload up to two screenshot canvases. You can also type a specific question below to grill the AI on the current setup.
""")

# --- NEW INTERACTIVE QUESTION FIELD ---
st.markdown("### 💬 Ask the AI a Question")
user_question = st.text_input(
    "Type a specific question about these charts (Optional):",
    placeholder="e.g., Is that an order block exhaustion? Where is the next major supply zone?",
    help="Leave blank for standard autonomous breakdown, or type a custom question to override the text analysis."
)

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
        
    with st.spinner("🤖 Processing data blocks and answering queries..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel(
                'gemini-2.5-flash', 
                generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
            
            # Formulate the target question injection block
            question_context = f"The user has a specific live question you must prioritize and answer in 'market_logic': '{user_question}'" if user_question else "Perform a standard unbiased structural breakdown."
            
            prompt = f"""
            You are an autonomous institutional execution router analyzing the provided market screens with absolute, unbiased precision.
            Inspect the raw text values, volume profile shelves, depth of market bars, and price action layouts to extract a precise trade setup.
            
            USER CUSTOM QUERY/QUESTION CONTEXT:
            {question_context}
            
            CORE ALGORITHMIC OBJECTIVES:
            1. CURRENT PRICE: Locate the bold, active index price level displayed on the chart/DOM. Use this as your reference point.
            2. INSTITUTIONAL IMBALANCE: Scan for high-volume nodes, heavy bid/ask order blocks, and clear supply/demand zones.
            3. DIRECTION BIAS: Determine the high-probability path ("LONG" or "SHORT").
            4. EXECUTION BRACKETS:
               - Entry Price: Determine the optimal fill level right at or near the current market price text context.
               - Stop Loss: Place it cleanly behind the nearest heavy visual volume shelf or structural invalidation level.
               - Take Profit: Project a mathematical target balancing market structures and major liquidity barriers.
            
            Return ONLY a raw JSON object with this exact schema:
            {{
                "direction": "LONG" or "SHORT",
                "entry_price": float,
                "stop_loss": float,
                "take_profit": float,
                "market_logic": "If the user provided a specific question, answer it thoroughly here based on what you see in the images. If no question was asked, provide a crisp reason why you chose these exact structural levels."
            }}
            """
            
            response = model.generate_content([prompt] + pil_images)
            data = json.loads(response.text.strip())
            
            direction = data.get('direction', 'LONG').upper()
            entry = float(data.get('entry_price', 0.0))
            stop = float(data.get('stop_loss', 0.0))
            tp = float(data.get('take_profit', 0.0))
            logic = data.get('market_logic', '')
            
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
            st.success("📐 Analysis & Query Processing Complete!")
            
            if direction == "LONG":
                st.markdown("### 🟢 Unbiased Bias: **LONG**")
            else:
                st.markdown("### 🔴 Unbiased Bias: **SHORT**")
                
            # This section now clearly calls out the answers to your specific text questions
            if user_question:
                st.markdown(f"#### 💬 AI Answer to Your Question:")
                st.info(logic)
            else:
                st.markdown(f"#### 📊 Structural Rationale:")
                st.info(logic)
            
            st.markdown("### 🎯 Machine-Calculated Execution Targets")
            st.metric(label="🟢 TARGET TAKE PROFIT", value=f"{tp:,.2f}")
            st.metric(label="⚪ AUTOMATED ENTRY", value=f"{entry:,.2f}")
            st.metric(label="🔴 STRUCTURAL STOP LOSS", value=f"{stop:,.2f}")
            
            st.warning(f"**Calculated Specs:** Risking {points_risk:.2f} pts (${cash_risk:.2f}) to bank {points_reward:.2f} pts (${cash_reward:.2f}) per contract.")
            
        except Exception as e:
            st.error(f"Autonomous scan encountered an error. Details: {e}")
