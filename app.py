
import os
import re
import streamlit as st
from openai import OpenAI   # new v1 SDK import

# ─────────────────────────────────────────────────────────────
# 1.  Configure API key (works locally & in Streamlit Cloud)
# ─────────────────────────────────────────────────────────────
OPENAI_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not OPENAI_KEY:
    st.error(
        "⚠️  OPENAI_API_KEY not found. Add it to Streamlit secrets or "
        "set it as an environment variable before running."
    )
    st.stop()

client = OpenAI(api_key=OPENAI_KEY)

# ─────────────────────────────────────────────────────────────
# 2.  Streamlit UI
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Typeface Blog AI Demo", layout="wide")
st.title("📄 Blog Post Generator + Readability Assistant")

prompt      = st.text_input("Blog Topic", "Boba Tea Craze")
tone        = st.selectbox("Tone", ["Friendly", "Professional", "Playful", "Authoritative"], index=0)
creativity  = st.slider("Creativity (temperature)", 0.0, 1.0, 0.6, 0.05)

# ─────────────────────────────────────────────────────────────
# 3.  Utility functions
# ─────────────────────────────────────────────────────────────
def count_syllables(word: str) -> int:
    vowels = "aeiouy"
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    count, prev = 0, False
    for c in word:
        if c in vowels:
            if not prev:
                count += 1
            prev = True
        else:
            prev = False
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)

def readability(text: str) -> float:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    words     = re.findall(r"[A-Za-z']+", text)
    if not words:
        return 100.0
    syll      = sum(count_syllables(w) for w in words)
    wps       = len(words) / max(1, len(sentences))
    spw       = syll / len(words)
    score     = 206.835 - 1.015 * wps - 84.6 * spw
    return round(max(0, min(100, score)), 1)

# ─────────────────────────────────────────────────────────────
# 4.  Generate blog draft on button click
# ─────────────────────────────────────────────────────────────
if st.button("Generate Outline + Draft"):
    with st.spinner("Calling OpenAI..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert marketing copywriter."
                },
                {
                    "role": "user",
                    "content": (
                        f"Write an outline and a 600‑word blog article about "
                        f"{prompt}. Tone: {tone}."
                    )
                },
            ],
            temperature=creativity,
        )
        draft = response.choices[0].message.content.strip()

    # ── Display results ──────────────────────────────────────
    st.subheader("AI Draft")
    st.write(draft)
    st.markdown("---")

    score = readability(draft)
    st.metric("Flesch Reading Ease", f"{score}/100")
    st.progress(score / 100)

    st.markdown("#### Next‑Step Recommendations")
    if score < 50:
        st.warning(
            "Consider shortening sentences and using simpler words to improve readability."
        )

