import streamlit as st
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown
from docx import Document
import io
import re

st.set_page_config(page_title="Squadra Agenti IA Didattica", page_icon="🤖", layout="centered")

st.title("🤖 Squadra di Agenti IA per la Didattica")
st.write("Genera report, articoli per Word ed invia email formattate con un team multi-agente.")

# --- FUNZIONE PER CONVERTIRE MARKDOWN IN FORMATTAZIONE WORD REALE ---
def append_markdown_to_docx(doc, text):
    lines = text.split('\n')
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        # Gestione Intestazioni (Headers Markdown)
        if line_str.startswith('### '):
            doc.add_heading(line_str.replace('### ', ''), level=3)
        elif line_str.startswith('## '):
            doc.add_heading(line_str.replace('## ', ''), level=2)
        elif line_str.startswith('# '):
            doc.add_heading(line_str.replace('# ', ''), level=1)
        else:
            # Gestione Paragrafi e Elenchi con Grassetto (**testo**)
            p = doc.add_paragraph()
            # Regex per separare il testo normale da quello tra **
            parts = re.split(r'(\*\*.*?\*\*)', line)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    # Testo in Grassetto
                    bold_text = part[2:-2]
                    p.add_run(bold_text).bold = True
                else:
                    # Testo Normale
                    p.add_run(part)

# --- SIDEBAR CONFIGURAZIONE ---
with st.sidebar:
    st.header("⚙️ Configurazione OpenRouter")
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

# --- EXECUZIONE AGENTI ---
if st.button("🚀 Avvia la Squadra di Agenti", type="primary"):
    if not api_key or not tema:
        st.error("⚠️ Inserisci la tua API Key e il tema della lezione.")
    else:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        
        # --- AGENTE 1: RICERCATORE ---
        with st.spinner("⏳ Agente 1 (Ricercatore) al lavoro..."):
            try:
                res1 = client.chat.completions.create(
                    model=modello_scelto,
                    messages=[{"role": "user", "content": f"Sei un Ricercatore Didattico. Analizza il tema '{tema}' e individua 3 punti chiave fondamentali. Usa il grassetto Markdown per i concetti principali."}]
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

            # --- AGENTE 3: REDATTORE SENIOR (ARTICOLO ESTESO) ---
            if post_breve:
                with st.spinner("⏳ Agente 3 (Redattore Senior) sta redigendo l'articolo di approfondimento..."):
                    try:
                        prompt_articolo = f"""
                        Sei un Giornalista ed Esperto di Didattica Digitale.
                        Prendi l'aspetto più innovativo tra questi punti chiave:
                        {punti_chiave}
                        
                        Scrivi un ARTICOLO DI APPROFONDIMENTO COMPLETO (circa 400 parole) destinato a una rivista o blog scolastico.
                        Struttura l'articolo con un titolo principale, dei sottotitoli (usando ###) ed evidenzia i termini importanti con il **grassetto**.
                        """
                        res3 = client.chat.completions.create(
                            model=modello_scelto,
                            messages=[{"role": "user", "content": prompt_articolo}]
                        )
                        articolo_esteso = res3.choices[0].message.content
                        st.session_state['articolo_esteso'] = articolo_esteso
                    except Exception as e:
                        st.error(f"Errore Agente 3: {e}")

# --- VISUALIZZAZIONE & DOWNLOAD WORD ---
if 'punti_chiave' in st.session_state:
    st.markdown("---")
    st.subheader("🔍 1. Punti Chiave (Ricercatore)")
    st.markdown(st.session_state['punti_chiave'])

if 'post_breve' in st.session_state:
    st.subheader("✍️ 2. Sintesi Divulgativa (Scrittore)")
    st.write(st.session_state['post_breve'])

if 'articolo_esteso' in st.session_state:
    st.subheader("📰 3. Articolo di Approfondimento (Redattore Senior)")
    st.info(st.session_state['articolo_esteso'])
    
    # Costruzione del file Word formattato correttamente
    doc = Document()
    doc.add_heading(f"Report & Articolo: {tema}", level=0)
    
    doc.add_heading("Punti Chiave", level=1)
    append_markdown_to_docx(doc, st.session_state['punti_chiave'])
    
    doc.add_heading("Articolo di Approfondimento", level=1)
    append_markdown_to_docx(doc, st.session_state['articolo_esteso'])
    
    bio = io.BytesIO()
    doc.save(bio)
    
    st.download_button(
        label="📄 Scarica Articolo Formattato in Word (.docx)",
        data=bio.getvalue(),
        file_name=f"Articolo_{tema.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # --- SEZIONE INVIO EMAIL RIPRISTINATA ---
    st.markdown("---")
    if st.button("📧 Invia Sintesi via Email", type="primary"):
        if not mittente or not password_app or not destinatario:
            st.error("⚠️ Compila tutti i campi email nella barra laterale (Mittente, App Password e Destinatario).")
        else:
            with st.spinner("⏳ Invio email in corso..."):
                try:
                    # Conversione Markdown -> HTML per l'email
                    html_punti_chiave = markdown.markdown(st.session_state['punti_chiave'])
                    html_post_breve = markdown.markdown(st.session_state['post_breve'])
                    
                    msg = MIMEMultipart()
                    msg['From'] = mittente
                    msg['To'] = destinatario
                    msg['Subject'] = f"🤖 Report & Sintesi IA: {tema}"
                    
                    corpo_html = f"""
                    <html>
                      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                        <h2 style="color: #1a73e8;">Report Generato dalla Squadra IA</h2>
                        <p><strong>Tema trattato:</strong> {tema}</p>
                        <hr>
                        <h3 style="color: #1a73e8;">🔍 1. Punti Chiave</h3>
                        <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #1a73e8;">
                          {html_punti_chiave}
                        </div>
                        
                        <h3 style="color: #ffc107; margin-top: 20px;">✍️ 2. Sintesi Divulgativa</h3>
                        <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107;">
                          {html_post_breve}
                        </div>
                        
                        <hr style="margin-top: 25px;">
                        <p style="font-size: 0.8em; color: #777;">Sintesi generata via Streamlit & OpenRouter. L'articolo esteso è stato scaricato in formato Word.</p>
                      </body>
                    </html>
                    """
                    msg.attach(MIMEText(corpo_html, 'html'))
                    
                    # Connessione SMTP Gmail
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login(mittente, password_app)
                    server.sendmail(mittente, destinatario, msg.as_string())
                    server.quit()
                    
                    st.success(f"✅ Email inviata con successo a {destinatario}!")
                except Exception as e:
                    st.error(f"❌ Errore durante l'invio dell'email: {e}")
