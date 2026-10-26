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
    st.markdown("<div style='color:#ff4b4b;'><i class='ph-fill ph-warning-circle'></i> API Key missing from Streamlit secrets.</div>", unsafe_allow_html=True)
    st.stop()

# --- 2. Page Config & State ---
st.set_page_config(page_title="BrokerVoice PRO", layout="centered")

# Top Right Theme Toggle
col1, col2 = st.columns([8, 2])
with col2:
    is_light = st.toggle("Light Mode", value=False)
    theme = 'light' if is_light else 'dark'

# --- 3. PREMIUM CSS (Obsidian & Bronze) ---
if theme == 'dark':
    bg_color = "#161618" # Light Obsidian
    text_color = "#E2E8F0"
    card_bg = "#1E1E20"
    border_color = "#333336"
    bronze_accent = "#C5832B"
    bronze_hover = "#D49A4A"
    input_bg = "#121212"
else:
    bg_color = "#F4F4F5"
    text_color = "#18181B"
    card_bg = "#FFFFFF"
    border_color = "#E4E4E7"
    bronze_accent = "#A66D24"
    bronze_hover = "#8A5A1E"
    input_bg = "#F9FAFB"

st.markdown(f"""
<style>
    @import url("https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css");
    @import url("https://unpkg.com/@phosphor-icons/web@2.1.1/src/fill/style.css");

    /* Global */
    .stApp {{
        background-color: {bg_color};
    }}
    
    #MainMenu, header, footer {{visibility: hidden;}}
    
    /* Typography Overrides */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5 {{
        color: {text_color} !important;
    }}
    
    /* The Card Container */
    [data-testid="block-container"] {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 2rem 2.5rem !important;
        max-width: 650px !important;
        margin-top: 1rem !important;
        margin-bottom: 2rem !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }}

    /* Inputs */
    [data-testid="stFileUploader"] > div > div, 
    [data-testid="stTextArea"] > div > div > textarea {{
        background-color: {input_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        color: {text_color} !important;
        padding: 12px;
    }}
    
    .stTextArea textarea::placeholder {{
        color: {text_color} !important;
        opacity: 0.5 !important;
    }}

    /* Upload Button */
    [data-testid="baseButton-secondary"] {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        color: {text_color} !important;
        border-radius: 8px !important;
    }}
    
    /* Primary Generate Button */
    [data-testid="baseButton-primary"] {{
        background: linear-gradient(135deg, {bronze_accent}, {bronze_hover}) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        height: 50px;
        box-shadow: 0 4px 15px rgba(197, 131, 43, 0.2);
    }}

    /* Mic Container */
    .mic-container {{
        display: flex; align-items: center; gap: 15px;
        background: {input_bg}; border: 1px solid {border_color};
        border-radius: 8px; padding: 15px; margin-bottom: 20px;
    }}
    
    /* Custom Alerts (Emoji Bypass) */
    .alert-box {{
        padding: 12px; border-radius: 8px; margin-bottom: 15px; font-weight: 500;
        display: flex; align-items: center; gap: 8px; font-size: 14px;
    }}
    .alert-success {{ background: rgba(46, 204, 113, 0.1); color: #2ecc71; border: 1px solid #2ecc71; }}
    .alert-warning {{ background: rgba(241, 196, 15, 0.1); color: #d4ac0d; border: 1px solid #d4ac0d; }}
    
</style>
""", unsafe_allow_html=True)

# --- 4. Header ---
st.markdown(f"<h2 style='text-align: center; margin-bottom: 5px; color: {bronze_accent} !important;'><i class='ph-fill ph-buildings'></i> BrokerVoice PRO</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 14px; opacity: 0.7;'>Apni awaaz ya photo ko professional listing mein badlein.</p>", unsafe_allow_html=True)
st.write("") 

# --- 5. Inputs ---
st.markdown(f"<h5 style='color: {bronze_accent} !important;'><i class='ph ph-microphone-stage'></i> Record Live Audio</h5>", unsafe_allow_html=True)
st.markdown("<div class='mic-container'>", unsafe_allow_html=True)
audio_bytes = audio_recorder(text="Tap to Record", recording_color="#FF4B4B", neutral_color=text_color, icon_size="1.5x")
st.markdown("</div>", unsafe_allow_html=True)

if audio_bytes:
    st.markdown("<div class='alert-box alert-success'><i class='ph-fill ph-check-circle'></i> Awaaz record ho gayi</div>", unsafe_allow_html=True)

st.markdown(f"<h5 style='color: {bronze_accent} !important; margin-top:20px;'><i class='ph ph-folder-open'></i> Ya File Upload Karein</h5>", unsafe_allow_html=True)

st.markdown("<p style='font-size:14px; margin-bottom:5px; margin-top:10px;'><i class='ph ph-file-audio'></i> Voice note upload karein</p>", unsafe_allow_html=True)
audio_file = st.file_uploader("", type=["mp3", "m4a", "wav"], label_visibility="collapsed")

st.markdown("<p style='font-size:14px; margin-bottom:5px; margin-top:15px;'><i class='ph ph-image'></i> Property ki photo upload karein</p>", unsafe_allow_html=True)
image_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="img")

st.markdown("<p style='font-size:14px; margin-bottom:5px; margin-top:15px;'><i class='ph ph-text-aa'></i> Koi aur details (optional)</p>", unsafe_allow_html=True)
text_input = st.text_area("", height=60, placeholder="Example: Highway se 2km door...", label_visibility="collapsed")

# --- 6. Processing Engine ---
st.markdown("<br>", unsafe_allow_html=True)

if st.button("Generate Listing", type="primary", use_container_width=True):
    if not audio_bytes and not audio_file and not image_file and not text_input:
        st.markdown("<div class='alert-box alert-warning'><i class='ph-fill ph-warning-circle'></i> Kripya live record karein ya koi file daalein.</div>", unsafe_allow_html=True)
    else:
        with st.spinner("AI aapki listing taiyar kar raha hai..."):
            contents = []
            prompt = """
            You are an expert Indian Real Estate Copywriter for 360 Views Services. 
            Convert the provided input into a highly professional, attractive property listing in Hinglish (Roman Hindi).
            Use formatting like bold text, bullet points, and clear sections: 
            - Overview
            - Features & Amenities
            - Location Highlights
            - Pricing & USP
            STRICT INSTRUCTION: DO NOT USE ANY EMOJIS IN THE OUTPUT.
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
                st.markdown(f"<div class='alert-box alert-warning'><i class='ph-fill ph-warning-circle'></i> Error: {e}</div>", unsafe_allow_html=True)

# --- 7. WhatsApp Output ---
if 'draft' in st.session_state:
    st.divider()
    st.markdown(f"<h4 style='color: {bronze_accent} !important;'><i class='ph-fill ph-clipboard-text'></i> Aapki Listing</h4>", unsafe_allow_html=True)
    st.markdown(f"<div style='background: {input_bg}; border: 1px solid {border_color}; padding: 15px; border-radius: 8px; margin-bottom: 15px; white-space: pre-wrap; font-family: monospace;'>{st.session_state['draft']}</div>", unsafe_allow_html=True)
    
    YOUR_PHONE_NUMBER = "918643002478"
    encoded_text = urllib.parse.quote(st.session_state['draft'])
    wa_url = f"https://wa.me/{YOUR_PHONE_NUMBER}?text={encoded_text}"
    
    st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:3em; background: linear-gradient(135deg, #25D366, #128C7E); color:white; border:none; border-radius:8px; font-weight:bold; font-size:16px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px;"><i class="ph-fill ph-whatsapp-logo" style="font-size: 20px;"></i> Send to Aloof on WhatsApp</button></a>', unsafe_allow_html=True)
