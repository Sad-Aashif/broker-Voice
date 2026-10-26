import streamlit as st
import google.generativeai as genai
import PIL.Image
import urllib.parse

# --- 1. API Setup (Secure using Streamlit Secrets) ---
# Ye code directly Streamlit ke hidden locker se key uthayega
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except KeyError:
    st.error("API Key missing! Deploy karte waqt Streamlit secrets mein GEMINI_API_KEY daalna zaroori hai.")
    st.stop()

# --- 2. Page Design ---
st.set_page_config(page_title="BrokerVoice", page_icon="🏠", layout="centered")

st.title("🏠 BrokerVoice")
st.write("Apni property ki details (Voice/Photo) upload karein. AI use professional Hinglish listing mein badal dega.")

# --- 3. Inputs ---
audio_file = st.file_uploader("🎤 Voice Note upload karein (mp3, m4a, wav)", type=["mp3", "m4a", "wav"])
image_file = st.file_uploader("📸 Property ya Diary ki photo (jpg, png)", type=["jpg", "jpeg", "png"])
text_input = st.text_area("📝 (Optional) Kuch aur details likhni hain?", height=100)

if st.button("Generate Listing 🚀"):
    if not audio_file and not image_file and not text_input:
        st.warning("Kripya koi audio, photo ya text zaroor daalein!")
    else:
        with st.spinner("AI aapki details process kar raha hai... thoda wait karein."):
            contents = []
            
            prompt = """
            You are an expert Indian Real Estate Copywriter working for 360 Views Services. 
            Based on the provided input (audio/image/text), extract the property details.
            Convert this into a highly professional, attractive property listing in Hinglish (Roman Hindi).
            Use formatting like bold text, bullet points, and clear sections: 
            - Overview
            - Features & Amenities
            - Location Highlights
            - Pricing & USP
            
            Keep it persuasive, exactly how top brokers write on 99acres or MagicBricks.
            If any information is missing in the input, do not invent it. Just leave it out.
            """
            contents.append(prompt)
            
            if audio_file:
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
                st.error(f"Ek error aayi: {e}")

# --- 4. Output & WhatsApp Button ---
if 'draft' in st.session_state:
    st.success("✅ Listing Ready!")
    st.markdown(st.session_state['draft'])
    
    # Tumhara Number (Bina + lagaye)
    YOUR_PHONE_NUMBER = "918643002478"
    
    encoded_text = urllib.parse.quote(st.session_state['draft'])
    wa_url = f"https://wa.me/{YOUR_PHONE_NUMBER}?text={encoded_text}"
    
    # Custom green WhatsApp Button
    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; height:3em; background-color:#25D366; color:white; border:none; border-radius:10px; font-weight:bold; font-size:16px; cursor:pointer;">Send to Aloof on WhatsApp 📲</button></a>', unsafe_allow_html=True)
