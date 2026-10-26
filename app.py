import streamlit as st
import google.generativeai as genai
import PIL.Image
import urllib.parse
from audio_recorder_streamlit import audio_recorder

# --- 1. API Setup ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except KeyError:
    st.error("API Key missing. Please set GEMINI_API_KEY in Streamlit secrets.")
    st.stop()

# --- 2. Page Config (Responsive by default) ---
st.set_page_config(
    page_title="BrokerVoice PRO",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={}  # hide default menu
)

# --- 3. Theme State ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# --- 4. Skyline Digital Palette & Responsive CSS ---
if st.session_state.theme == 'light':
    bg_canvas = "#FEFFFF"      # Twilight Blue / pure white
    text_primary = "#0B101A"   # Dark Grey
    text_muted = "#4B5563"
    border_hairline = "#E5E7EB"
    accent = "#0129BA"         # International Klein Blue
    card_bg = "#FFFFFF"
    snow_color = "rgba(1, 41, 186, 0.08)"  # subtle blue snow for light mode
else:
    bg_canvas = "#0B101A"      # Dark Grey
    text_primary = "#FEFFFF"   # Twilight Blue
    text_muted = "#9CA3AF"
    border_hairline = "#161B2E" # Mirage
    accent = "#3B82F6"         # Brighter blue for dark mode contrast
    card_bg = "#161B2E"        # Mirage card
    snow_color = "rgba(255, 255, 255, 0.2)" # white snow for dark mode

st.markdown(f"""
<style>
    /* Fonts & Icons */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Poppins:wght@400;500;600&display=swap');
    @import url("https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css");
    @import url("https://unpkg.com/@phosphor-icons/web@2.1.1/src/fill/style.css");

    /* Global Typography */
    html, body, [class*="st-"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, button, span, div {{
        font-family: 'Poppins', sans-serif !important;
    }}
    h1, h2, h3, h4, h5 {{
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
    }}
    
    /* Base colors */
    .stApp {{
        background-color: {bg_canvas};
        color: {text_primary};
    }}
    h1, h2, h3, h4, h5, p, .stMarkdown {{
        color: {text_primary} !important;
    }}
    
    /* Hide Streamlit chrome */
    #MainMenu, header, footer {{visibility: hidden;}}

    /* Main container */
    [data-testid="block-container"] {{
        padding-top: 2rem !important;
        max-width: 720px !important;
        z-index: 10;
    }}

    /* ----- FILE UPLOADER (FIXED OVERLAP) ----- */
    [data-testid="stFileUploader"] {{
        width: 100% !important;
        background-color: {card_bg} !important;
        border: 1px solid {border_hairline} !important;
        border-radius: 16px !important;
        padding: 12px !important;
        box-sizing: border-box !important;
    }}
    [data-testid="stFileUploader"] > div > div {{
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }}
    /* Upload button inside */
    [data-testid="stFileUploader"] button {{
        background-color: {accent} !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-size: 14px !important;
        padding: 8px 16px !important;
        width: auto !important;
        margin: 0 !important;
    }}
    /* File name text */
    [data-testid="stFileUploader"] label {{
        color: {text_muted} !important;
        font-size: 13px !important;
    }}

    /* ----- TEXT AREA ----- */
    .stTextArea textarea {{
        background-color: {card_bg} !important;
        border: 1px solid {border_hairline} !important;
        border-radius: 16px !important;
        color: {text_primary} !important;
        padding: 12px !important;
        font-size: 16px !important;  /* Prevents iOS zoom */
    }}
    .stTextArea textarea::placeholder {{
        color: {text_muted} !important;
        opacity: 0.7 !important;
    }}

    /* ----- MIC CONTAINER ----- */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {card_bg} !important;
        border: 1px solid {border_hairline} !important;
        border-radius: 16px !important;
        padding: 15px !important;
    }}

    /* ----- GENERATE BUTTON (Pill, Centered) ----- */
    [data-testid="baseButton-primary"] {{
        background-color: {accent} !important;
        color: #ffffff !important;
        border-radius: 30px !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        padding: 12px 40px !important;
        width: auto !important;
        margin: 0 auto !important;
        display: block !important;
        box-shadow: 0 4px 14px rgba(1, 41, 186, 0.25);
        transition: transform 0.2s ease;
    }}
    [data-testid="baseButton-primary"]:active {{
        transform: scale(0.98);
    }}

    /* ----- WHATSAPP BUTTON ----- */
    .whatsapp-btn {{
        background-color: #25D366; color: white; border: none; 
        border-radius: 30px; font-weight: 600; font-size: 16px; 
        padding: 12px 30px; cursor: pointer; display: flex; 
        align-items: center; justify-content: center; gap: 8px;
        margin: 0 auto; width: fit-content; text-decoration: none;
        box-shadow: 0 4px 14px rgba(37, 211, 102, 0.3);
        transition: transform 0.2s ease;
    }}
    .whatsapp-btn:active {{ transform: scale(0.98); }}

    /* ----- SNOW ANIMATION (Subtle, works in both themes) ----- */
    .snow-bg {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        pointer-events: none; z-index: 0;
        background-image: 
        radial-gradient(2px 2px at 20px 30px, {snow_color}, transparent),
        radial-gradient(3px 3px at 150px 90px, {snow_color}, transparent),
        radial-gradient(2px 2px at 280px 150px, {snow_color}, transparent),
        radial-gradient(4px 4px at 400px 50px, {snow_color}, transparent);
        background-size: 400px 400px;
        animation: snow-anim 25s linear infinite;
    }}
    @keyframes snow-anim {{ 
        0% {{ transform: translateY(-20px); }} 
        100% {{ transform: translateY(100vh); }} 
    }}

    /* ----- ICON COLOR ----- */
    .ph, .ph-fill {{ 
        color: {accent} !important; 
        margin-right: 6px; 
        vertical-align: middle; 
        font-size: 1.2em;
    }}

    /* ============================================
       RESPONSIVE DESIGN (MOBILE FIRST)
       ============================================ */
    @media (max-width: 768px) {{
        [data-testid="block-container"] {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }}

        /* Stack columns for mobile */
        [data-testid="stHorizontalBlock"] {{
            flex-direction: column !important;
            gap: 10px !important;
        }}

        /* Full-width buttons on mobile */
        [data-testid="baseButton-primary"] {{
            width: 100% !important;
            padding: 14px 20px !important;
            font-size: 16px !important;
        }}
        .whatsapp-btn {{
            width: 100% !important;
            padding: 14px 20px !important;
        }}

        /* Touch-friendly toggle */
        [data-testid="stToggle"] {{
            width: 100% !important;
            margin-bottom: 10px;
        }}

        /* Ensure file uploader doesn't overflow */
        [data-testid="stFileUploader"] {{
            max-width: 100% !important;
        }}

        /* Font size adjustments */
        h2 {{ font-size: 1.5rem !important; }}
        h5 {{ font-size: 1.1rem !important; }}
    }}

    @media (min-width: 769px) and (max-width: 1024px) {{
        /* Tablet adjustments */
        [data-testid="block-container"] {{
            max-width: 600px !important;
        }}
    }}
</style>
<div class="snow-bg"></div>
""", unsafe_allow_html=True)

# --- 5. Header & Theme Toggle (Responsive) ---
col1, col2 = st.columns([7, 3])
with col2:
    is_dark = st.toggle("🌙 Dark Mode", value=st.session_state.theme == 'dark')
    if is_dark != (st.session_state.theme == 'dark'):
        st.session_state.theme = 'dark' if is_dark else 'light'
        st.rerun()

st.markdown(f"<h2 style='text-align: center; font-weight: 800;'><i class='ph ph-house-line'></i> BrokerVoice PRO</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 14px; color: {text_muted} !important;'><i class='ph ph-magic-wand'></i> Apni awaaz ya photo ko professional listing mein badlein.</p>", unsafe_allow_html=True)
st.write("")

# --- 6. Input Section ---
st.markdown(f"<h5 style='font-weight: 600;'><i class='ph ph-microphone-stage'></i> Record Live Audio</h5>", unsafe_allow_html=True)
with st.container(border=True):
    audio_bytes = audio_recorder(text="Tap to Record", recording_color="#EF4444", neutral_color=accent, icon_size="2x")

if audio_bytes:
    st.markdown(f"<div style='color: #10B981; margin-bottom: 15px; font-weight: 500;'><i class='ph-fill ph-check-circle' style='color: #10B981 !important;'></i> Awaaz record ho gayi!</div>", unsafe_allow_html=True)

st.markdown(f"<h5 style='font-weight: 600; margin-top:20px;'><i class='ph ph-folder-open'></i> Ya File Upload Karein</h5>", unsafe_allow_html=True)

st.markdown(f"<p style='font-size:14px; margin-bottom:5px; font-weight:500;'><i class='ph ph-file-audio'></i> Voice note upload karein</p>", unsafe_allow_html=True)
audio_file = st.file_uploader("Voice Note", type=["mp3", "m4a", "wav"], label_visibility="collapsed")

st.markdown(f"<p style='font-size:14px; margin-bottom:5px; margin-top:15px; font-weight:500;'><i class='ph ph-image'></i> Property ki photo upload karein</p>", unsafe_allow_html=True)
image_file = st.file_uploader("Photo", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="img")

st.markdown(f"<p style='font-size:14px; margin-bottom:5px; margin-top:15px; font-weight:500;'><i class='ph ph-pencil-simple'></i> Koi aur details (optional)</p>", unsafe_allow_html=True)
text_input = st.text_area("Details", height=80, placeholder="Example: Highway se 2km door...", label_visibility="collapsed")

# --- 7. Process ---
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
with btn_col2:
    generate_clicked = st.button("✨ Generate Listing", type="primary", use_container_width=True)

if generate_clicked:
    if not audio_bytes and not audio_file and not image_file and not text_input:
        st.markdown(f"<div style='color: #EF4444; font-weight: 500;'><i class='ph-fill ph-warning-circle' style='color: #EF4444 !important;'></i> Kripya koi input daalein.</div>", unsafe_allow_html=True)
    else:
        with st.spinner("AI listing taiyar kar raha hai..."):
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
                st.markdown(f"<div style='color: #EF4444;'><i class='ph-fill ph-x-circle' style='color: #EF4444 !important;'></i> Error: {e}</div>", unsafe_allow_html=True)

# --- 8. Output ---
if 'draft' in st.session_state:
    st.divider()
    st.markdown(f"<h4 style='font-weight: 600; text-align:center;'><i class='ph ph-clipboard-text'></i> Aapki Listing</h4>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background: {card_bg}; border: 1px solid {border_hairline}; padding: 20px; border-radius: 16px; margin-bottom: 25px; white-space: pre-wrap; font-family: monospace; color: {text_primary};'>
    {st.session_state['draft']}
    </div>
    """, unsafe_allow_html=True)
    
    YOUR_PHONE_NUMBER = "918643002478"
    encoded_text = urllib.parse.quote(st.session_state['draft'])
    wa_url = f"https://wa.me/{YOUR_PHONE_NUMBER}?text={encoded_text}"
    
    st.markdown(f'<div style="display: flex; justify-content: center;"><a href="{wa_url}" target="_blank" style="text-decoration:none;"><button class="whatsapp-btn"><i class="ph-fill ph-whatsapp-logo" style="font-size: 22px; color: white !important; margin-right: 0;"></i> Send on WhatsApp</button></a></div>', unsafe_allow_html=True)
