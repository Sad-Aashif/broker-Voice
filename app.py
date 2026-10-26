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

# --- 2. Page Config & Default Light State ---
st.set_page_config(page_title="BrokerVoice PRO", layout="centered")

col1, col2 = st.columns([8, 2])
with col2:
    is_dark = st.toggle("🌙 Dark Mode", value=False) # Default Light Mode
    theme = 'dark' if is_dark else 'light'

# --- 3. PREMIUM MODERN CSS (Soothing Colors & Poppins) ---
if theme == 'light':
    bg_color = "#F4F6F8"         # Soft Pearl / Off-white
    card_bg = "#FFFFFF"          # Pure White cards
    text_color = "#1E293B"       # Slate Dark
    border_color = "#E2E8F0"
    accent_color = "#2563EB"     # Clean Blue
    snow_color = "rgba(0, 0, 0, 0.1)" # Dark subtle snow for light mode
else:
    bg_color = "#121826"         # Deep Charcoal
    card_bg = "#1F2937"          # Dark Gray cards
    text_color = "#F8FAFC"       # Slate Light
    border_color = "#334155"
    accent_color = "#3B82F6"     # Bright Blue
    snow_color = "rgba(255, 255, 255, 0.15)" # Light subtle snow for dark mode

st.markdown(f"""
<style>
    /* Import Poppins Font & Phosphor Icons (Lucide alternative) */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    @import url("https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css");

    /* Apply Poppins Globally */
    html, body, [class*="st-"], .stMarkdown, p, h1, h2, h3, h4, h5, label, button {{
        font-family: 'Poppins', sans-serif !important;
        color: {text_color} !important;
    }}
    
    .stApp {{
        background-color: {bg_color};
        transition: background-color 0.3s ease;
    }}
    
    #MainMenu, header, footer {{visibility: hidden;}}
    
    /* Center Container Spacing */
    [data-testid="block-container"] {{
        padding-top: 1rem;
        max-width: 700px !important;
        z-index: 10;
    }}

    /* 4-5 Modern Rounded Boxes (Inputs) */
    [data-testid="stFileUploader"] > div > div, 
    [data-testid="stTextArea"] > div > div > textarea {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 20px !important; /* Smooth rounded corners */
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }}
    
    .stTextArea textarea::placeholder {{
        color: {text_color} !important;
        opacity: 0.4 !important;
    }}

    /* Mic Container */
    .mic-container {{
        display: flex; align-items: center; gap: 15px;
        background: {card_bg}; 
        border: 1px solid {border_color};
        border-radius: 20px; 
        padding: 16px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }}

    /* ✨ Generate Button (Smaller, Rounded Pill) */
    [data-testid="baseButton-primary"] {{
        background-color: {accent_color} !important;
        color: #FFFFFF !important;
        border-radius: 30px !important; /* Pill shape */
        border: none !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        padding: 10px 40px !important;
        width: auto !important; /* Not full width */
        margin: 0 auto !important;
        display: block !important;
        box-shadow: 0 8px 16px rgba(37, 99, 235, 0.2);
    }}

    /* WhatsApp Button */
    .whatsapp-btn {{
        background-color: #25D366; color: white; border: none; 
        border-radius: 30px; font-weight: 600; font-size: 16px; 
        padding: 12px 30px; cursor: pointer; display: flex; 
        align-items: center; justify-content: center; gap: 8px;
        margin: 0 auto; width: fit-content; text-decoration: none;
        box-shadow: 0 8px 16px rgba(37, 211, 102, 0.2);
        font-family: 'Poppins', sans-serif;
    }}

    /* Subtle CSS Snow Animation */
    .snow-bg {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        pointer-events: none; z-index: 0;
        background-image: 
        radial-gradient(3px 3px at 20px 30px, {snow_color}, transparent),
        radial-gradient(4px 4px at 150px 90px, {snow_color}, transparent),
        radial-gradient(2px 2px at 280px 150px, {snow_color}, transparent);
        background-size: 300px 300px;
        animation: snow-anim 15s linear infinite;
    }}
    @keyframes snow-anim {{ 0% {{ transform: translateY(-10px); }} 100% {{ transform: translateY(100vh); }} }}
</style>
<div class="snow-bg"></div>
""", unsafe_allow_html=True)

# --- 4. Header ---
st.markdown(f"<h2 style='text-align: center; font-weight: 700; color: {accent_color} !important;'><i class='ph ph-house'></i> BrokerVoice PRO</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 15px; opacity: 0.7;'>Apni awaaz ya photo ko professional listing mein badlein.</p>", unsafe_allow_html=True)
st.write("")

# --- 5. Inputs (Clean Lucide-style Icons) ---
st.markdown(f"<h5 style='font-weight: 600;'><i class='ph ph-microphone'></i> Record Live Audio</h5>", unsafe_allow_html=True)
st.markdown("<div class='mic-container'>", unsafe_allow_html=True)
audio_bytes = audio_recorder(text="Tap to Record", recording_color="#EF4444", neutral_color=text_color, icon_size="1.5x")
st.markdown("</div>", unsafe_allow_html=True)

if audio_bytes:
    st.info("Awaaz record ho gayi")

st.markdown(f"<h5 style='font-weight: 600; margin-top:20px;'><i class='ph ph-folder'></i> Ya File Upload Karein</h5>", unsafe_allow_html=True)

st.markdown("<p style='font-size:14px; margin-bottom:5px; margin-top:10px; font-weight:500;'><i class='ph ph-file-audio'></i> Voice note upload karein</p>", unsafe_allow_html=True)
audio_file = st.file_uploader("", type=["mp3", "m4a", "wav"], label_visibility="collapsed")

st.markdown("<p style='font-size:14px; margin-bottom:5px; margin-top:15px; font-weight:500;'><i class='ph ph-image'></i> Property ki photo upload karein</p>", unsafe_allow_html=True)
image_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="img")

st.markdown("<p style='font-size:14px; margin-bottom:5px; margin-top:15px; font-weight:500;'><i class='ph ph-pencil-simple'></i> Koi aur details (optional)</p>", unsafe_allow_html=True)
text_input = st.text_area("", height=60, placeholder="Example: Highway se 2km door...", label_visibility="collapsed")

# --- 6. Processing Engine ---
st.markdown("<br>", unsafe_allow_html=True)

# Using columns to make the button smaller and centered
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
with btn_col2:
    generate_clicked = st.button("✨ Generate Listing", type="primary", use_container_width=True)

if generate_clicked:
    if not audio_bytes and not audio_file and not image_file and not text_input:
        st.warning("Kripya live record karein ya koi file daalein.")
    else:
        with st.spinner("AI aapki listing taiyar kar raha hai..."):
            contents = []
            prompt = """
            You are an expert Indian Real Estate Copywriter for 360 Views Services. 
            Convert the provided input into a highly professional, attractive property listing in Hinglish (Roman Hindi).
            Use formatting like bold text, bullet points, and clear sections.
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
                st.error(f"Error: {e}")

# --- 7. WhatsApp Output ---
if 'draft' in st.session_state:
    st.divider()
    st.markdown(f"<h4 style='font-weight: 600; text-align:center;'><i class='ph ph-clipboard-text'></i> Aapki Listing</h4>", unsafe_allow_html=True)
    st.markdown(f"<div style='background: {card_bg}; border: 1px solid {border_color}; padding: 20px; border-radius: 20px; margin-bottom: 25px; white-space: pre-wrap; font-family: monospace;'>{st.session_state['draft']}</div>", unsafe_allow_html=True)
    
    YOUR_PHONE_NUMBER = "918643002478"
    encoded_text = urllib.parse.quote(st.session_state['draft'])
    wa_url = f"https://wa.me/{YOUR_PHONE_NUMBER}?text={encoded_text}"
    
    st.markdown(f'<div style="display: flex; justify-content: center;"><a href="{wa_url}" target="_blank" style="text-decoration:none;"><button class="whatsapp-btn"><i class="ph ph-whatsapp-logo" style="font-size: 22px;"></i> Send to Aloof on WhatsApp</button></a></div>', unsafe_allow_html=True)
