import streamlit as st
import google.generativeai as genai
import PIL.Image
import urllib.parse
from audio_recorder_streamlit import audio_recorder

# --- 1. Secure API Setup ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except KeyError:
    st.error("API Key is missing from Streamlit secrets.")
    st.stop()

# --- 2. PREMIUM WINTER UI & CSS ANIMATIONS ---
st.set_page_config(page_title="BrokerVoice", page_icon="❄️", layout="centered")

st.markdown("""
<style>
    /* Dark Premium Night Sky */
    .stApp {
        background: linear-gradient(135deg, #0B101E 0%, #1B2838 50%, #2A4359 100%);
        color: white;
    }
    
    /* Hide Defaults */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Glassmorphism Inputs (Premium transparent look) */
    .stFileUploader>div>div, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px);
    }
    
    .stTextArea>div>div>textarea::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Premium Button */
    .stButton>button {
        border-radius: 16px !important;
        font-weight: bold !important;
        font-size: 18px !important;
        background: linear-gradient(90deg, #00C6FF 0%, #0072FF 100%) !important;
        border: none !important;
        color: white !important;
        transition: transform 0.2s ease;
    }
    .stButton>button:active {
        transform: scale(0.95);
    }

    /* 3D CSS Snowfall Animation */
    .snow-bg {
        position: fixed;
        top: -100vh; left: 0; width: 100vw; height: 200vh;
        pointer-events: none; z-index: 0;
        background-image: 
        radial-gradient(4px 4px at 20px 30px, #ffffff, transparent),
        radial-gradient(5px 5px at 150px 90px, rgba(255,255,255,0.8), transparent),
        radial-gradient(3px 3px at 280px 150px, #ffffff, transparent),
        radial-gradient(6px 6px at 390px 40px, rgba(255,255,255,0.9), transparent),
        radial-gradient(4px 4px at 80px 240px, #ffffff, transparent);
        background-size: 400px 400px;
        animation: snow-drop 15s linear infinite;
    }
    @keyframes snow-drop {
        0% { transform: translateY(0); }
        100% { transform: translateY(100vh); }
    }

    /* Snowman Flat Footer */
    .snowman-footer {
        position: fixed;
        bottom: 0; left: 0; width: 100%; height: 60px;
        background: white;
        display: flex; justify-content: space-around; align-items: flex-start;
        font-size: 35px; z-index: 100;
        border-top-left-radius: 30px; border-top-right-radius: 30px;
        box-shadow: 0px -10px 30px rgba(0, 114, 255, 0.2);
        padding-top: 5px;
    }
    
    /* Ensure content is above snow */
    .block-container {
        z-index: 10; position: relative; padding-bottom: 90px;
    }
</style>
<div class="snow-bg"></div>
<div class="snowman-footer">☃️ ⛄ ☃️ ⛄ ☃️ ⛄</div>
""", unsafe_allow_html=True)

# --- 3. App Content ---
st.markdown("<h2 style='text-align: center; color: white;'>❄️ BrokerVoice PRO</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A0C4FF;'>Apni awaaz ya photo ko professional listing mein badlein.</p>", unsafe_allow_html=True)
st.divider()

# --- 4. Inputs (Live Mic Included) ---
st.markdown("#### 🎙️ Record Live Audio")
audio_bytes = audio_recorder(text="Tap to Record 🔴", recording_color="#FF4B4B", neutral_color="#ffffff", icon_size="2x")

if audio_bytes:
    st.success("✅ Awaaz record ho gayi!")

st.markdown("#### 📁 Ya File Upload Karein")
audio_file = st.file_uploader("🎵 Voice Note upload karein", type=["mp3", "m4a", "wav"])
image_file = st.file_uploader("📸 Property ki photo", type=["jpg", "jpeg", "png"])
text_input = st.text_area("📝 (Optional) Koi aur details likhni hain?", height=80, placeholder="Example: Highway se 2km door...")

# --- 5. Processing Engine ---
if st.button("✨ Generate Listing"):
    if not audio_bytes and not audio_file and not image_file and not text_input:
        st.warning("⚠️ Kripya live record karein ya koi file daalein.")
    else:
        with st.spinner("AI aapki listing taiyar kar raha hai..."):
            contents = []
            
            prompt = """
            You are an expert Indian Real Estate Copywriter for 360 Views Services. 
            Convert the provided input into a highly professional, attractive property listing in Hinglish (Roman Hindi).
            Use formatting like bold text, bullet points, and clear sections: 
            - 🌟 Overview
            - 💎 Features & Amenities
            - 📍 Location Highlights
            - 💰 Pricing & USP
            """
            contents.append(prompt)
            
            if audio_bytes:
                contents.append({"mime_type": "audio/wav", "data": audio_bytes})
            elif audio_file:
                contents.append({"mime_type": "audio/mp3", "data": audio_file.read()})
                
            if image_file:
                img = PIL.Image.open(image_file)
                contents.append(img)
            if text_input:
                contents.append(text_input)

            try:
                response = model.generate_content(contents)
                st.session_state['draft'] = response.text
            except Exception as e:
                st.error(f"Error: {e}")

# --- 6. WhatsApp Output ---
if 'draft' in st.session_state:
    st.divider()
    st.markdown("### 📋 Aapki Listing")
    st.info(st.session_state['draft'])
    
    YOUR_PHONE_NUMBER = "918643002478"
    encoded_text = urllib.parse.quote(st.session_state['draft'])
    wa_url = f"https://wa.me/{YOUR_PHONE_NUMBER}?text={encoded_text}"
    
    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; height:3em; background-color:#25D366; color:white; border:none; border-radius:16px; font-weight:bold; font-size:18px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:10px;">Send to Aloof on WhatsApp 📲</button></a>', unsafe_allow_html=True)
