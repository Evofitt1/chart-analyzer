import streamlit as st
import cv2
import numpy as np
import google.generativeai as genai
import json
from PIL import Image

# 1. Page Configuration
st.set_page_config(
    page_title="Alpha Flow | Order Flow Engine", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Bulletproof Banner Loader
banner_url = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80"
try:
    st.image(banner_url, use_container_width=True)
except Exception:
    pass  # Safety net: If the image network fails, skip it completely to prevent an app crash

# Styled Title and Motivational Subtitle Block
st.markdown("""
<div style="text-align: center; margin-top: -10px; margin-bottom: 25px;">
    <h1 style="color: #00ffcc; font-family: 'Arial Black', sans-serif; letter-spacing: 2px; margin-bottom: 0; text-shadow: 2px 2px #000000;">ALPHA FLOW ENGINE</h1>
    <p style="font-style: italic; color: #a1b0c0; font-size: 1.1rem; font-weight: bold; margin-top: 5px;">
        <span style="color: #00ff88;">⚡ BULLISH MOMENTUM</span> vs <span style="color: #ff3355;">BEARISH DISTRIBUTION 📉</span>
    </p>
    <p style="font-style: italic; color: #6c7a89; font-size: 0.95rem;">"Plan the trade. Trade the plan. Emotion is noise; execution is everything."</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# 3. Interactive Interrogator Block
st.markdown("### 💬 Live Order Flow Query")
user_question = st.text_input(
    "Ask a strategic question about this execution layer (Optional):",
    placeholder="e.g., Is this breakout exhausted? Where is the hidden institutional supply block?",
    help="Leave blank for a completely autonomous baseline structure scan."
)

# 4. Visual Interface Feeds
st.markdown("### 📸 Visual Interface Feeds")
uploaded_files = st.file_uploader(
    "Drop your live trading chart screenshots or DOM profiles here...", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    pil_images = []
    
    # Display layouts cleanly
    for i, file in enumerate(uploaded_files[:2]):
        file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        st.image(file, caption=f"Canvas {i+1}: {file.name}", use_container_width=True)
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_images.append(Image.fromarray(rgb_image))
        
    with st.spinner("🤖 Mapping order blocks, reading liquidity depth, and calculating risk curves..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel(
                'gemini-2.5-flash', 
                generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
            
            question_context = f"The user has a specific live question you must prioritize and answer in 'market_logic': '{user_question}'" if user_question else "Perform a standard unbiased structural breakdown."
            
            # Reprogrammed prompt targeting candle patterns, wicks, and micro structure gaps
            prompt = f"""
            You are a hyper-stringent risk-management AI router executing intraday scalps on Micro Nasdaq futures.
            Your primary goal is capital protection; you must filter out choppy, low-probability environments and only execute on clean momentum displacement.
            
            USER CUSTOM QUERY/QUESTION CONTEXT:
            {question_context}
            
            EXAMINATION & PATTERN ALGORITHM:
            1. CANDLE ANATOMY: Look closely at the wicks and bodies of the most recent 3 to 5 candles. 
               - Did a long wick just sweep a visible prior high or low? (Look for liquidity grabs).
               - Is there a "Displacement" candle? (A large, energetic body closing strongly in one direction).
            2. MARKET STRUCTURE BREAK: Identify if the displacement candle broke past a recent swing high or swing low. If it did not, assume the market is ranging/choppy.
            3. IMBALANCE DEPLOYMENT: Locate any Fair Value Gaps (FVGs) or order blocks created by that sudden fast move. 
               - For a LONG setup: The entry must be right at the top of the bullish FVG or mitigated order block. The STOP must be tucked cleanly below the candle that started the move.
               - For a SHORT setup: The entry must be right at the bottom of the bearish FVG. The STOP must be placed strictly above the swing high wick that grabbed liquidity.
            
            EXECUTION RULE: If the candles look choppy, overlapping, or do not show a clear, aggressive breakout wick, you must significantly tighten the target profit to a micro-scalp, or widen the stop behind a major volume shelf.
            
            Return ONLY a raw JSON object with this exact schema:
            {{
                "direction": "LONG" or "SHORT",
                "entry_price": float,
                "stop_loss": float,
                "take_profit": float,
                "market_logic": "Explain which specific candle wicks, high-volume nodes, or gaps validated this exact bracket choice."
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
                st.error("Engine vision failed to read core price values. Ensure text is sharp and unwarped.")
                st.stop()
                
            # Point differential calculus
            points_risk = abs(entry - stop)
            points_reward = abs(tp - entry)
            
            # Compute exact risk metrics for MNQ spec ($2.00/point)
            cash_risk = points_risk * 2.0
            cash_reward = points_reward * 2.0
            
            # --- OUTPUT INTERFACE ---
            st.markdown("---")
            st.success("📐 Structural Matrix Alignment Complete")
            
            if direction == "LONG":
                st.markdown("### 🟢 Flow Bias: **LONG (Bullish Liquidity Build)**")
            else:
                st.markdown("### 🔴 Flow Bias: **SHORT (Bearish Distribution)**")
                
            if user_question:
                st.markdown(f"#### 💬 AI Intelligence Report:")
                st.info(logic)
            else:
                st.markdown(f"#### 📊 Structural Rationale:")
                st.info(logic)
            
            # --- AUTOMATED GUARDRAIL ENGINE ---
            r_to_r = points_reward / points_risk if points_risk > 0 else 0
            
            if r_to_r < 1.5:
                st.error(f"⚠️ RISK WARNING: The AI is suggesting an inefficient Risk-to-Reward ratio of 1:{r_to_r:.1f}. The risk is too wide for a fast scalp setup. Proceed with extreme caution.")
            elif points_risk > 18.0:
                st.warning(f"🚨 WIDE ACCURACY ALERT: The structural stop loss is quite wide ({points_risk:.1f} pts). This indicates a highly chaotic or volatile candle pattern.")
            
            st.markdown("### 🎯 Machine-Calculated Execution Brackets")
            st.metric(label="🟢 TARGET TAKE PROFIT", value=f"{tp:,.2f}")
            st.metric(label="⚪ RECONSTRUCTED ENTRY", value=f"{entry:,.2f}")
            st.metric(label="🔴 PROTECTION STOP LOSS", value=f"{stop:,.2f}")
            
            st.warning(f"**Specs:** Risk: {points_risk:.2f} pts (${cash_risk:.2f}) | Target: {points_reward:.2f} pts (${cash_reward:.2f}) per contract.")
            
        except Exception as e:
            st.error(f"Autonomous scan encountered an error. Details: {e}")
