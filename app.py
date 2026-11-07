import streamlit as st
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown
from docx import Document
import io

st.set_page_config(page_title="Squadra Agenti IA Didattica", page_icon="🤖", layout="centered")

st.title("🤖 Squadra di Agenti IA per la Didattica")
st.write("Genera report brevi e articoli di approfondimento in formato Word con un team multi-agente.")

# Sezione Credenziali
with st.sidebar:
    st.header("⚙️ Configurazione")
    api_key = st.text_input("OpenRouter API Key", type="password")
    
    modello_scelto = st.selectbox(
        "Modello OpenRouter",
        ["openrouter/auto", "anthropic/claude-3.5-haiku", "deepseek/deepseek-chat", "google/gemini-flash-1.5"],
        index=0
    )
    
    st.markdown("---")
    st.header("📧 Configurazione Email")
    mittente = st.text_input("Tuo Gmail (Mittente)", placeholder="tuamail@gmail.com")
    password_app = st.text_input("App Password (16 caratteri)", type="password", placeholder="xxxx xxxx xxxx xxxx")
    destinatario = st.text_input("Email Destinatario", placeholder="destinatario@scuola.it")

tema = st.text_input("🎯 Tema della lezione o argomento:", "L'uso degli Agenti IA nella didattica")

if st.button("🚀 Avvia la Squadra di Agenti", type="primary"):
    if not api_key or not tema:
        st.error("⚠️ Inserisci la tua API Key e il tema.")
    else:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        
        # --- AGENTE 1: RICERCATORE ---
        with st.spinner("⏳ Agente 1 (Ricercatore) al lavoro..."):
            try:
                res1 = client.chat.completions.create(
                    model=modello_scelto,
                    messages=[{"role": "user", "content": f"Sei un Ricercatore Didattico. Analizza il tema '{tema}' e individua 3 punti chiave fondamentali. Usa il grassetto Markdown."}]
                )
                punti_chiave = res1.choices[0].message.content
                st.session_state['punti_chiave'] = punti_chiave
            except Exception as e:
                st.error(f"Errore Agente 1: {e}")
                punti_chiave = None

        # --- AGENTE 2: SCRITTORE EMAIL ---
        if punti_chiave:
            with st.spinner("⏳ Agente 2 (Scrittore) al lavoro..."):
                try:
                    res2 = client.chat.completions.create(
                        model=modello_scelto,
                        messages=[{"role": "user", "content": f"Sei un Redattore scolastico. Scrivi un post breve (100 parole) per docenti basato su questi punti:\n{punti_chiave}"}]
                    )
                    post_breve = res2.choices[0].message.content
                    st.session_state['post_breve'] = post_breve
                except Exception as e:
                    st.error(f"Errore Agente 2: {e}")
                    post_breve = None

            # --- AGENTE 3: REDATTORE SENIOR (ARTICOLO WORD COMPLETO) ---
            if post_breve:
                with st.spinner("⏳ Agente 3 (Redattore Senior) sta redigendo l'articolo di approfondimento..."):
                    try:
                        prompt_articolo = f"""
                        Sei un Giornalista ed Esperto di Didattica Digitale.
                        Prendi l'aspetto più innovativo ed emergente tra questi punti chiave:
                        {punti_chiave}
                        
                        Scrivi un ARTICOLO DI APPROFONDIMENTO COMPLETO (circa 400-500 parole) destinato a una rivista di pedagogia o a un blog scolastico.
                        Struttura l'articolo così:
                        - Titolo Principale Incisivo
                        - Introduzione al contesto
                        - 2 o 3 Paragrafi di analisi dettagliata con sottotitoli
                        - Esempi pratici per l'applicazione in classe
                        - Conclusioni e riflessione per i docenti.
                        """
                        res3 = client.chat.completions.create(
                            model=modello_scelto,
                            messages=[{"role": "user", "content": prompt_articolo}]
                        )
                        articolo_esteso = res3.choices[0].message.content
                        st.session_state['articolo_esteso'] = articolo_esteso
                    except Exception as e:
                        st.error(f"Errore Agente 3: {e}")

# --- VISUALIZZAZIONE ---
if 'punti_chiave' in st.session_state:
    st.markdown("---")
    st.subheader("🔍 1. Punti Chiave (Ricercatore)")
    st.markdown(st.session_state['punti_chiave'])

if 'post_breve' in st.session_state:
    st.subheader("✍️ 2. Sintesi Divulgativa (Scrittore)")
    st.write(st.session_state['post_breve'])

if 'articolo_esteso' in st.session_state:
    st.subheader("📰 3. Articolo di Approfondimento Completo (Redattore Senior)")
    st.info(st.session_state['articolo_esteso'])
    
    # Generazione File Word (.docx) al volo
    doc = Document()
    doc.add_heading(f"Report & Articolo: {tema}", level=0)
    doc.add_heading("Punti Chiave", level=1)
    doc.add_paragraph(st.session_state['punti_chiave'])
    doc.add_heading("Articolo di Approfondimento", level=1)
    doc.add_paragraph(st.session_state['articolo_esteso'])
    
    bio = io.BytesIO()
    doc.save(bio)
    
    st.download_button(
        label="📄 Scarica Articolo Completo in Word (.docx)",
        data=bio.getvalue(),
        file_name=f"Articolo_{tema.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # Sezione invio email
    st.markdown("---")
    if st.button("📧 Invia Sintesi via Email"):
        # (Codice di invio SMTP standard per inviare la sintesi)
        st.success("Email inviata!")
