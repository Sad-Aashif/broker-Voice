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

# --- 2. Page Config ---
st.set_page_config(page_title="BrokerVoice PRO", layout="centered", initial_sidebar_state="collapsed")

# --- 3. Theme State ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# --- 4. CSS Variables & Styling ---
if st.session_state.theme == 'light':
    bg_color = "#F4F6F8"       # Soothing off-white
    card_bg = "#FFFFFF"        # Pure white cards
    text_color = "#1E293B"     # Dark slate for readability
    text_muted = "#64748B"
    border_color = "#E2E8F0"
    accent_color = "#2563EB"   # Premium blue
    input_bg = "#F8FAFC"
    snow_opacity = "0.15"
    icon_color = "#1E293B"
else:
    bg_color = "#0F172A"       # Deep Obsidian
    card_bg = "#1E293B"        # Slightly lighter slate for cards
    text_color = "#F1F5F9"     # Light text
    text_muted = "#94A3B8"
    border_color = "#334155"
    accent_color = "#38BDF8"   # Bright sky blue
    input_bg = "#0B1120"
    snow_opacity = "0.3"
    icon_color = "#F1F5F9"

st.markdown(f"""
<style>
    /* Fonts & Icons */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    @import url("https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css");
    @import url("https://unpkg.com/@phosphor-icons/web@2.1.1/src/fill/style.css");

    /* Global Typography */
    html, body, [class*="st-"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, button, span, div {{
        font-family: 'Poppins', sans-serif !important;
    }}
    
    /* Background & Text */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    h1, h2, h3, h4, h5, p, .stMarkdown {{
        color: {text_color} !important;
    }}
    
    /* Hide Streamlit Defaults */
    #MainMenu, header, footer {{visibility: hidden;}}

    /* Main Container */
    [data-testid="block-container"] {{
        padding-top: 2rem !important;
        max-width: 700px !important;
        z-index: 10;
    }}

    /* File Uploaders & Text Area */
    [data-testid="stFileUploader"] > div > div,
    [data-testid="stTextArea"] > div > div > textarea {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 16px !important;
        color: {text_color} !important;
        padding: 12px;
        transition: border 0.3s ease;
    }}
    [data-testid="stFileUploader"]:hover > div > div,
    [data-testid="stTextArea"] > div > div > textarea:focus {{
        border-color: {accent_color} !important;
    }}
    
    /* Fix Text Area Placeholder */
    .stTextArea textarea::placeholder {{
        color: {text_muted} !important;
    }}

    /* Native Container Border (For Mic) */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 16px !important;
        padding: 10px;
    }}

    /* Generate Button (Pill Shape, Centered) */
    [data-testid="baseButton-primary"] {{
        background: linear-gradient(135deg, {accent_color}, {accent_color}) !important;
        color: #FFFFFF !important;
        border-radius: 30px !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        padding: 12px 40px !important;
        width: auto !important;
        margin: 0 auto !important;
        display: block !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    [data-testid="baseButton-primary"]:active {{
        transform: scale(0.98);
    }}

    /* WhatsApp Button */
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

    /* Custom Subtle Snow Animation */
    .snow-bg {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        pointer-events: none; z-index: 0;
        background-image: 
        radial-gradient(2px 2px at 20px 30px, rgba(255,255,255,{snow_opacity}), transparent),
        radial-gradient(3px 3px at 150px 90px, rgba(255,255,255,{snow_opacity}), transparent),
        radial-gradient(2px 2px at 280px 150px, rgba(255,255,255,{snow_opacity}), transparent),
        radial-gradient(4px 4px at 400px 50px, rgba(255,255,255,{snow_opacity}), transparent);
        background-size: 400px 400px;
        animation: snow-anim 20s linear infinite;
    }}
    @keyframes snow-anim {{ 
        0% {{ transform: translateY(-20px); }} 
        100% {{ transform: translateY(100vh); }} 
    }}

    /* Icon spacing helper */
    .ph {{ color: {accent_color} !important; margin-right: 6px; vertical-align: middle; }}
    .ph-fill {{ color: {accent_color} !important; margin-right: 6px; vertical-align: middle; }}
</style>
<div class="snow-bg"></div>
""", unsafe_allow_html=True)

# --- 5. Top Bar (Theme Toggle) ---
col1, col2 = st.columns([8, 2])
with col2:
    # Toggle with no emoji, just native text and state
    is_dark = st.toggle("Dark Mode", value=st.session_state.theme == 'dark')
    if is_dark != (st.session_state.theme == 'dark'):
        st.session_state.theme = 'dark' if is_dark else 'light'
        st.rerun()

# --- 6. Header ---
st.markdown(f"<h2 style='text-align: center; font-weight: 700;'><i class='ph ph-house-line'></i> BrokerVoice PRO</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 14px; color: {text_muted} !important;'><i class='ph ph-magic-wand'></i> Apni awaaz ya photo ko professional listing mein badlein.</p>", unsafe_allow_html=True)
st.write("")

# --- 7. Inputs Section ---
st.markdown(f"<h5 style='font-weight: 600;'><i class='ph ph-microphone-stage'></i> Record Live Audio</h5>", unsafe_allow_html=True)

# Using native container border for the mic component
with st.container(border=True):
    audio_bytes = audio_recorder(text="Tap to Record", recording_color="#EF4444", neutral_color=accent_color, icon_size="2x")

if audio_bytes:
    st.markdown(f"<div style='color: #10B981; margin-bottom: 15px; font-weight: 500;'><i class='ph-fill ph-check-circle' style='color: #10B981 !important;'></i> Awaaz record ho gayi!</div>", unsafe_allow_html=True)

st.markdown(f"<h5 style='font-weight: 600; margin-top:20px;'><i class='ph ph-folder-open'></i> Ya File Upload Karein</h5>", unsafe_allow_html=True)

st.markdown(f"<p style='font-size:14px; margin-bottom:5px; font-weight:500;'><i class='ph ph-file-audio'></i> Voice note upload karein</p>", unsafe_allow_html=True)
audio_file = st.file_uploader("Voice Note", type=["mp3", "m4a", "wav"], label_visibility="collapsed")

st.markdown(f"<p style='font-size:14px; margin-bottom:5px; margin-top:15px; font-weight:500;'><i class='ph ph-image'></i> Property ki photo upload karein</p>", unsafe_allow_html=True)
image_file = st.file_uploader("Photo", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="img")

st.markdown(f"<p style='font-size:14px; margin-bottom:5px; margin-top:15px; font-weight:500;'><i class='ph ph-pencil-simple'></i> Koi aur details (optional)</p>", unsafe_allow_html=True)
text_input = st.text_area("Details", height=80, placeholder="Example: Highway se 2km door...", label_visibility="collapsed")

# --- 8. Processing Engine ---
st.markdown("<br>", unsafe_allow_html=True)

# Center the button using columns
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
with btn_col2:
    generate_clicked = st.button("✨ Generate Listing", type="primary", use_container_width=True)

if generate_clicked:
    if not audio_bytes and not audio_file and not image_file and not text_input:
        st.markdown(f"<div style='color: #EF4444; margin-bottom: 15px; font-weight: 500;'><i class='ph-fill ph-warning-circle' style='color: #EF4444 !important;'></i> Kripya live record karein ya koi file daalein.</div>", unsafe_allow_html=True)
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
                st.markdown(f"<div style='color: #EF4444; margin-bottom: 15px; font-weight: 500;'><i class='ph-fill ph-x-circle' style='color: #EF4444 !important;'></i> Error: {e}</div>", unsafe_allow_html=True)

# --- 9. WhatsApp Output ---
if 'draft' in st.session_state:
    st.divider()
    st.markdown(f"<h4 style='font-weight: 600; text-align:center;'><i class='ph ph-clipboard-text'></i> Aapki Listing</h4>", unsafe_allow_html=True)
    
    # Premium Output Box
    st.markdown(f"""
    <div style='background: {card_bg}; border: 1px solid {border_color}; padding: 20px; border-radius: 16px; margin-bottom: 25px; white-space: pre-wrap; font-family: monospace; color: {text_color};'>
    {st.session_state['draft']}
    </div>
    """, unsafe_allow_html=True)
    
    YOUR_PHONE_NUMBER = "918643002478"
    encoded_text = urllib.parse.quote(st.session_state['draft'])
    wa_url = f"https://wa.me/{YOUR_PHONE_NUMBER}?text={encoded_text}"
    
    st.markdown(f'<div style="display: flex; justify-content: center;"><a href="{wa_url}" target="_blank" style="text-decoration:none;"><button class="whatsapp-btn"><i class="ph-fill ph-whatsapp-logo" style="font-size: 22px; color: white !important; margin-right: 0;"></i> Send on WhatsApp</button></a></div>', unsafe_allow_html=True)
