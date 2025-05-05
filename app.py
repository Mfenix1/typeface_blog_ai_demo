
import os, openai, textwrap
import streamlit as st

st.set_page_config(page_title="Typeface Blog AI Demo", layout="wide")

st.title("📄 Blog Post Generator + Readability Assistant")
openai.api_key = st.secrets.get(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
)

prompt = st.text_input("Blog Topic", "Boba Tea Craze")
tone = st.selectbox("Tone", ["Friendly", "Professional", "Playful", "Authoritative"], index=0)
creativity = st.slider("Creativity (temperature)", 0.0, 1.0, 0.6, 0.05)

def count_syllables(word):
    import re
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev = False
    for char in re.sub(r'[^a-z]', '', word):
        if char in vowels:
            if not prev:
                count += 1
            prev = True
        else:
            prev = False
    if word.endswith("e") and count > 1:
        count -= 1
    return count or 1

def readability(text):
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    words = re.findall(r'[A-Za-z\']+', text)
    syllables = sum(count_syllables(w) for w in words)
    words_per_sentence = len(words) / max(1, len(sentences))
    syllables_per_word = syllables / max(1, len(words))
    fre = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
    return round(max(0, min(100, fre)), 1)

if st.button("Generate Outline + Draft"):
    with st.spinner("Calling OpenAI..."):
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert marketing copywriter."},
                {"role": "user", "content": f"Write an outline then a 600-word blog article about {prompt}. Tone: {tone}. Include a catchy title."}
            ],
            temperature=creativity
        )
        draft = response.choices[0].message.content.strip()
    st.subheader("AI Draft")
    st.write(draft)
    st.markdown("---")
    score = readability(draft)
    st.metric("Flesch Reading Ease", f"{score}/100", delta=None)
    color = "green" if score >= 60 else "orange" if score >= 30 else "red"
    st.progress(score/100)
    st.info(f"Readability Score: **{score}** — {'Easy' if score>=60 else 'Fair' if score>=30 else 'Difficult'}", icon="🚦")
    st.markdown("#### Next Step Recommendations")
    if score < 50:
        st.warning("Consider shortening sentences and using simpler words to improve readability.")

