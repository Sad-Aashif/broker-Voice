import streamlit as st
import google.generativeai as genai
import PIL.Image
import urllib.parse

# --- 1. Secure API Setup ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3.5-flash-lite') # ERROR FIXED YAHAN
except KeyError:
    st.error("API Key missing. Please set GEMINI_API_KEY in Streamlit secrets.")
    st.stop()

# --- 2. Page Config (Responsive) ---
st.set_page_config(
    page_title="BrokerVoice PRO",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={}
)

# --- 3. Theme State ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# --- 4. Exact Color Palette ---
if st.session_state.theme == 'light':
    bg_color = "#F4F4F5"       # Light Grey
    text_color = "#18181B"     # Deep Dark
    text_muted = "#71717A"
    card_bg = "#FFFFFF"
    border_color = "#E4E4E7"
    snow_color = "rgba(0, 0, 0, 0.05)"
    footer_bg = "#FFFFFF"
else:
    bg_color = "#0F0F11"       # Obsidian
    text_color = "#F4F4F5"     # Light text
    text_muted = "#A1A1AA"
    card_bg = "#18181B"        # Slightly lighter obsidian
    border_color = "#27272A"
    snow_color = "rgba(255, 255, 255, 0.2)"
    footer_bg = "#18181B"

btn_green = "#22C55E"          # Generate Button (Green)
btn_whatsapp = "#25D366"       # WhatsApp Button

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
    
    /* Base colors */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        transition: background-color 0.3s ease;
    }}
    h1, h2, h3, h4, h5, p, .stMarkdown {{
        color: {text_color} !important;
    }}
    
    /* Hide Streamlit chrome */
    #MainMenu, header, footer {{visibility: hidden;}}

    /* Main container */
    [data-testid="block-container"] {{
        padding-top: 2rem !important;
        padding-bottom: 120px !important; /* Space for footer */
        max-width: 700px !important;
        z-index: 10;
    }}

    /* ----- FIXED FILE UPLOADER (NO OVERLAP) ----- */
    [data-testid="stFileUploader"] {{
        width: 100% !important;
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 16px !important;
        padding: 10px !important;
    }}
    [data-testid="stFileUploader"] > div > div {{
        background-color: transparent !important;
        border: none !important;
    }}
    /* Upload Button */
    [data-testid="stFileUploader"] button {{
        background-color: {text_color} !important;
        color: {bg_color} !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        white-space: nowrap !important; /* Fix text break */
        min-width: 120px !important;
    }}
    
    /* ----- NATIVE AUDIO INPUT (MIC BUTTON) ----- */
    [data-testid="stAudioInput"] {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 16px !important;
        padding: 10px !important;
    }}
    /* Style the record button inside */
    [data-testid="stAudioInput"] button {{
        background-color: {text_color} !important;
        color: {bg_color} !important;
        border-radius: 50% !important; /* Circle */
        width: 60px !important;
        height: 60px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
    }}
    [data-testid="stAudioInput"] button svg {{
        fill: {bg_color} !important;
        width: 30px !important;
        height: 30px !important;
    }}

    /* ----- TEXT AREA ----- */
    .stTextArea textarea {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 16px !important;
        color: {text_color} !important;
        padding: 16px !important;
        font-size: 16px !important;
    }}
    .stTextArea textarea::placeholder {{
        color: {text_muted} !important;
    }}

    /* ----- GREEN GENERATE BUTTON ----- */
    [data-testid="baseButton-primary"] {{
        background-color: {btn_green} !important;
        color: #FFFFFF !important;
        border-radius: 30px !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        padding: 12px 40px !important;
        width: auto !important;
        margin: 0 auto !important;
        display: block !important;
        box-shadow: 0 4px 14px rgba(34, 197, 94, 0.3);
        transition: transform 0.2s ease;
    }}
    [data-testid="baseButton-primary"]:active {{
        transform: scale(0.98);
    }}

    /* ----- WHATSAPP BUTTON ----- */
    .whatsapp-btn {{
        background-color: {btn_whatsapp}; 
        color: white; 
        border: none; 
        border-radius: 30px; 
        font-weight: 600; 
        font-size: 16px; 
        padding: 12px 30px; 
        cursor: pointer; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        gap: 10px;
        margin: 0 auto; 
        width: fit-content; 
        text-decoration: none;
        box-shadow: 0 4px 14px rgba(37, 211, 102, 0.3);
        transition: transform 0.2s ease;
    }}
    .whatsapp-btn:active {{ transform: scale(0.98); }}

    /* ----- SNOW ANIMATION ----- */
    .snow-bg {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        pointer-events: none; z-index: 0;
        background-image: 
        radial-gradient(2px 2px at 20px 30px, {snow_color}, transparent),
        radial-gradient(3px 3px at 150px 90px, {snow_color}, transparent),
        radial-gradient(2px 2px at 280px 150px, {snow_color}, transparent),
        radial-gradient(4px 4px at 400px 50px, {snow_color}, transparent);
        background-size: 400px 400px;
        animation: snow-anim 20s linear infinite;
    }}
    @keyframes snow-anim {{ 
        0% {{ transform: translateY(-20px); }} 
        100% {{ transform: translateY(100vh); }} 
    }}

    /* ----- FOOTER (SNOW GROUND + SNOWMEN) ----- */
    .snow-footer {{
        position: fixed;
        bottom: 0; left: 0; right: 0;
        height: 90px;
        background: {footer_bg};
        border-radius: 50% 50% 0 0 / 100% 100% 0 0;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        padding: 0 30px 15px 30px;
        z-index: 99;
        box-shadow: 0 -10px 20px rgba(0,0,0,0.05);
    }}
    .snow-footer span {{ font-size: 32px; }}
    .house-center {{ font-size: 45px !important; margin-bottom: -5px; }}

    /* ----- ICON COLORS ----- */
    .ph, .ph-fill {{ 
        color: {text_color} !important; 
        margin-right: 6px; 
        vertical-align: middle; 
        font-size: 1.2em;
    }}

    /* ============================================
       RESPONSIVE DESIGN (MOBILE)
       ============================================ */
    @media (max-width: 768px) {{
        [data-testid="block-container"] {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        [data-testid="stHorizontalBlock"] {{
            flex-direction: column !important;
            gap: 10px !important;
        }}
        [data-testid="baseButton-primary"], .whatsapp-btn {{
            width: 100% !important;
            padding: 14px 20px !important;
        }}
        h2 {{ font-size: 1.5rem !important; }}
        h5 {{ font-size: 1.1rem !important; }}
        .snow-footer {{ padding: 0 10px 10px 10px; height: 70px; }}
        .snow-footer span {{ font-size: 24px; }}
        .house-center {{ font-size: 32px !important; }}
    }}
</style>
<div class="snow-bg"></div>

<!-- Snow Footer with Snowmen & House -->
<div class="snow-footer">
    <span>☃️⛄</span>
    <span class="house-center">🏠</span>
    <span>⛄☃️</span>
</div>
""", unsafe_allow_html=True)

# --- 5. Header & Toggle ---
col1, col2 = st.columns([7, 3])
with col2:
    is_dark = st.toggle("Dark Mode", value=st.session_state.theme == 'dark')
    if is_dark != (st.session_state.theme == 'dark'):
        st.session_state.theme = 'dark' if is_dark else 'light'
        st.rerun()

st.markdown(f"<h2 style='text-align: center; font-weight: 700;'><i class='ph-fill ph-house-line'></i> BrokerVoice PRO</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 14px; color: {text_muted} !important;'><i class='ph-fill ph-magic-wand'></i> Apni awaaz ya photo ko professional listing mein badlein.</p>", unsafe_allow_html=True)
st.write("")

# --- 6. Inputs ---
st.markdown(f"<h5 style='font-weight: 600;'><i class='ph-fill ph-microphone-stage'></i> Record Live Audio</h5>", unsafe_allow_html=True)
# Using native st.audio_input
audio_bytes = st.audio_input("Tap to Record", key="live_audio")

if audio_bytes:
    st.markdown(f"<div style='color: #10B981; margin-bottom: 15px; font-weight: 500;'><i class='ph-fill ph-check-circle' style='color: #10B981 !important;'></i> Awaaz record ho gayi!</div>", unsafe_allow_html=True)

st.markdown(f"<h5 style='font-weight: 600; margin-top:20px;'><i class='ph-fill ph-folder-open'></i> Ya File Upload Karein</h5>", unsafe_allow_html=True)

st.markdown(f"<p style='font-size:14px; margin-bottom:5px; font-weight:500;'><i class='ph-fill ph-file-audio'></i> Voice note upload karein</p>", unsafe_allow_html=True)
audio_file = st.file_uploader("Voice Note", type=["mp3", "m4a", "wav"], label_visibility="collapsed")

st.markdown(f"<p style='font-size:14px; margin-bottom:5px; margin-top:15px; font-weight:500;'><i class='ph-fill ph-image'></i> Property ki photo upload karein</p>", unsafe_allow_html=True)
image_file = st.file_uploader("Photo", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="img")

st.markdown(f"<p style='font-size:14px; margin-bottom:5px; margin-top:15px; font-weight:500;'><i class='ph-fill ph-pencil-simple'></i> Koi aur details (optional)</p>", unsafe_allow_html=True)
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
                contents.append({"mime_type": "audio/wav", "data": audio_bytes.read()})
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

# --- 8. Output & Reset ---
if 'draft' in st.session_state:
    st.divider()
    st.markdown(f"<h4 style='font-weight: 600; text-align:center;'><i class='ph-fill ph-clipboard-text'></i> Aapki Listing</h4>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background: {card_bg}; border: 1px solid {border_color}; padding: 20px; border-radius: 16px; margin-bottom: 25px; white-space: pre-wrap; font-family: monospace; color: {text_color};'>
    {st.session_state['draft']}
    </div>
    """, unsafe_allow_html=True)
    
    YOUR_PHONE_NUMBER = "918643002478"
    encoded_text = urllib.parse.quote(st.session_state['draft'])
    wa_url = f"https://wa.me/{YOUR_PHONE_NUMBER}?text={encoded_text}"
    
    # Official WhatsApp SVG Logo Embedded
    whatsapp_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
        <path d="M12.031 2C6.502 2 2 6.502 2 12.031c0 1.77.458 3.434 1.258 4.89L2 22l5.22-1.22a9.964 9.964 0 004.81 1.22c5.53 0 10.032-4.502 10.032-10.031C22.062 6.502 17.56 2 12.031 2zm0 18.353c-1.555 0-3.03-.413-4.33-1.166l-.31-.177-3.22.75.76-3.13-.188-.31A8.31 8.31 0 013.674 12.03c0-4.61 3.75-8.36 8.36-8.36 4.61 0 8.36 3.75 8.36 8.36 0 4.61-3.75 8.36-8.36 8.36zm4.66-6.24c-.255-.128-1.512-.745-1.745-.83-.232-.086-.402-.128-.572.128-.17.255-.66 1.105-.81 1.275-.15.17-.3.19-.555.064-.255-.128-1.08-.398-2.055-1.268-.76-.678-1.27-1.516-1.42-1.772-.15-.255-.015-.393.112-.52.115-.115.255-.3.382-.45.127-.15.17-.255.255-.425.085-.17.043-.318-.02-.446-.064-.127-.573-1.38-.783-1.887-.206-.493-.418-.427-.574-.434a10.3 10.3 0 00-.49-.01c-.17 0-.446.064-.68.32-.232.255-.888.868-.888 2.115 0 1.248.908 2.454 1.034 2.624.127.17 1.788 2.73 4.333 3.83 1.33.575 1.85.465 2.185.34.336-.127 1.083-.442 1.235-.868.15-.425.15-.79.106-.868-.043-.078-.16-.127-.415-.255z"/>
    </svg>"""
    
    st.markdown(f'<div style="display: flex; justify-content: center;"><a href="{wa_url}" target="_blank" style="text-decoration:none;"><button class="whatsapp-btn">{whatsapp_svg} Send on WhatsApp</button></a></div>', unsafe_allow_html=True)
    
    st.write("")
    
    # PERFECT RESET LOGIC YAHAN HAI
    col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
    with col_r2:
        if st.button("🔄 Nayi Listing Banayein (Reset)", use_container_width=True):
            del st.session_state['draft']
            st.rerun()
