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

# --- 2. GLASSMORPHISM PREMIUM UI & CSS ---
st.set_page_config(page_title="BrokerVoice PRO", page_icon="🏠", layout="centered")

st.markdown("""
<style>
    @import url("https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css");
    @import url("https://unpkg.com/@phosphor-icons/web@2.1.1/src/fill/style.css");

    /* 1. Full Screen Background Image */
    .stApp {
        /* Yahan apni pasand ki snow background image ka link daal sakte ho */
        background-image: url('https://images.unsplash.com/photo-1542601098-3adb3baeb198?q=80&w=2000&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Hide Defaults */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 2. The Glass Card (Center Container) */
    [data-testid="block-container"] {
        background: rgba(15, 23, 42, 0.75) !important; /* Dark transparent blue */
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 3rem 2.5rem !important;
        max-width: 750px !important;
        margin-top: 3rem !important;
        margin-bottom: 3rem !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }

    /* All text inside the card */
    h1, h2, h3, h4, p, label, .stMarkdown {
        color: #E2E8F0 !important;
    }
    
    /* 3. Sleek Inputs styling */
    [data-testid="stFileUploader"], [data-testid="stTextArea"] {
        background-color: rgba(0, 0, 0, 0.4) !important;
        border: 1px dashed rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 10px;
        transition: border 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover { border: 1px dashed rgba(255, 255, 255, 0.5) !important; }
    
    .stTextArea textarea {
        background-color: transparent !important;
        color: white !important;
        border: none !important;
    }
    .stTextArea textarea::placeholder { color: rgba(255, 255, 255, 0.4) !important; }
    
    /* Generate Button */
    [data-testid="baseButton-secondary"] {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        background: linear-gradient(90deg, #0ea5e9, #2563eb) !important;
        border: none !important;
        color: white !important;
        height: 50px;
        margin-top: 1rem;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
    }
    
    /* Mic Container tweaks */
    .mic-container {
        display: flex; align-items: center; justify-content: flex-start; gap: 15px;
        background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px; padding: 15px 20px; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Header ---
st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 5px;'>BrokerVoice PRO <span style='font-size: 28px;'>🏠</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 14px; opacity: 0.8;'>Apni awaaz ya photo ko professional listing mein badlein.</p>", unsafe_allow_html=True)
st.write("") # Spacer

# --- 4. Inputs ---
st.markdown("##### <i class='ph ph-microphone'></i> Record Live Audio", unsafe_allow_html=True)
st.markdown("<div class='mic-container'>", unsafe_allow_html=True)
audio_bytes = audio_recorder(text="Tap to Record", recording_color="#FF4B4B", neutral_color="#ffffff", icon_size="1.5x")
st.markdown("</div>", unsafe_allow_html=True)

if audio_bytes:
    st.success("✅ Awaaz record ho gayi!")

st.markdown("##### <i class='ph ph-folder-open'></i> Ya File Upload Karein", unsafe_allow_html=True)

st.markdown("<p style='font-size:14px; margin-bottom:5px; margin-top:10px;'><i class='ph ph-music-notes'></i> Voice note upload karein</p>", unsafe_allow_html=True)
audio_file = st.file_uploader("", type=["mp3", "m4a", "wav"], label_visibility="collapsed")

st.markdown("<p style='font-size:14px; margin-bottom:5px; margin-top:15px;'><i class='ph ph-image'></i> Property ki photo upload karein</p>", unsafe_allow_html=True)
image_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="img")

st.markdown("<p style='font-size:14px; margin-bottom:5px; margin-top:15px;'><i class='ph ph-info'></i> Koi aur details, jaankaari (optional)</p>", unsafe_allow_html=True)
text_input = st.text_area("", height=60, placeholder="Example: Highway se 2km door...", label_visibility="collapsed")

# --- 5. Processing Engine ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("✨ Generate Listing", use_container_width=True):
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
    st.markdown("### <i class='ph-fill ph-clipboard-text'></i> Aapki Listing", unsafe_allow_html=True)
    st.info(st.session_state['draft'])
    
    YOUR_PHONE_NUMBER = "918643002478"
    encoded_text = urllib.parse.quote(st.session_state['draft'])
    wa_url = f"https://wa.me/{YOUR_PHONE_NUMBER}?text={encoded_text}"
    
    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; height:3em; background-color:#25D366; color:white; border:none; border-radius:12px; font-weight:bold; font-size:16px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px;"><i class="ph-fill ph-whatsapp-logo" style="font-size: 20px;"></i> Send to Aloof on WhatsApp</button></a>', unsafe_allow_html=True)
