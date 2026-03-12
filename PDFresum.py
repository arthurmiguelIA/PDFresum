import pdfplumber
import streamlit as st
from gtts import gTTS
from io import BytesIO
import re

st.title("📄 Resumidor Automático de PDFs")

uploaded_file = st.file_uploader("Escolha o seu arquivo PDF", type="pdf")

def limpar_texto(texto):
    texto = re.sub(r'\d+', '', texto)
    texto = re.sub(r'[^A-Za-zÀ-ÿ .,;!?-]+', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def dividir_sentencas(texto):
    return re.split(r'(?<=[.!?]) +', texto)

def gerar_resumo(texto, max_sentencas=5):
    texto_limpo = limpar_texto(texto)
    sentencas = dividir_sentencas(texto_limpo)
    if len(sentencas) <= max_sentencas:
        return " ".join(sentencas)
    return " ".join(sentencas[:max_sentencas])

def gerar_audio(texto):
    tts = gTTS(texto, lang='pt')
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        texto = ""
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texto += t

    if texto.strip() == "":
        st.warning("Não foi possível extrair texto deste PDF.")
    else:
        st.info("PDF processado! Gerando resumo...")

        resumo_texto = gerar_resumo(texto, max_sentencas=7)

        palavras_unicas = []
        for p in resumo_texto.split():
            if len(palavras_unicas) == 0 or p != palavras_unicas[-1]:
                palavras_unicas.append(p)
        resumo_texto = " ".join(palavras_unicas)

        st.subheader("Resumo do PDF:")
        st.write(resumo_texto)

        if st.button("Ouvir Resumo"):
            audio_bytes = gerar_audio(resumo_texto)
            st.audio(audio_bytes, format='audio/mp3')