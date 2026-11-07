import streamlit as st
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown  # Libreria per convertire il Markdown in HTML pulito per l'email

st.set_page_config(page_title="Squadra Agenti IA Didattica", page_icon="🤖", layout="centered")

st.title("🤖 Squadra di Agenti IA per la Didattica")
st.write("Genera contenuti didattici avanzati con un team multi-agente via OpenRouter e inviali via email.")

# Sezione Credenziali e Input
with st.sidebar:
    st.header("⚙️ Configurazione")
    api_key = st.text_input("OpenRouter API Key", type="password")
    
    modello_scelto = st.selectbox(
        "Modello OpenRouter",
        [
            "openrouter/auto",
            "anthropic/claude-3.5-haiku",
            "deepseek/deepseek-chat",
            "google/gemini-flash-1.5"
        ],
        index=0
    )
    
    st.markdown("---")
    st.header("📧 Configurazione Email")
    mittente = st.text_input("Tuo Gmail (Mittente)", placeholder="tuamail@gmail.com")
    password_app = st.text_input("App Password (16 caratteri)", type="password", placeholder="xxxx xxxx xxxx xxxx")
    destinatario = st.text_input("Email Destinatario", placeholder="destinatario@scuola.it")

tema = st.text_input("🎯 Tema della lezione o argomento:", "L'uso degli Agenti IA nella didattica")

if st.button("🚀 1. Avvia la Squadra di Agenti", type="primary"):
    if not api_key:
        st.error("⚠️ Inserisci la tua OpenRouter API Key nella barra laterale.")
    elif not tema:
        st.error("⚠️ Inserisci un tema valido.")
    else:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
        # --- AGENTE 1: IL RICERCATORE ---
        with st.spinner("⏳ Agente 1 (Ricercatore) al lavoro..."):
            try:
                prompt_ricerca = f"""
                Sei un Ricercatore di Tendenze Digitali esperto in scuola e didattica.
                Analizza il tema '{tema}' e individua 3 opportunità o punti chiave fondamentali.
                Restituisci unicamente un elenco puntato chiaro e sintetico con i 3 punti usando il grassetto Markdown.
                """
                res1 = client.chat.completions.create(
                    model=modello_scelto,
                    messages=[{"role": "user", "content": prompt_ricerca}]
                )
                punti_chiave = res1.choices[0].message.content
                st.session_state['punti_chiave'] = punti_chiave
            except Exception as e:
                st.error(f"Errore Agente 1: {e}")
                punti_chiave = None

        # --- AGENTE 2: LO SCRITTORE ---
        if punti_chiave:
            with st.spinner("⏳ Agente 2 (Scrittore) al lavoro..."):
                try:
                    prompt_scrittura = f"""
                    Sei un Redattore esperto in comunicazione per insegnanti.
                    Prendi questi punti chiave e scrivi un post divulgativo di circa 100-120 parole rivolto ai docenti:
                    {punti_chiave}
                    """
                    res2 = client.chat.completions.create(
                        model=modello_scelto,
                        messages=[{"role": "user", "content": prompt_scrittura}]
                    )
                    post_bozza = res2.choices[0].message.content
                    st.session_state['post_bozza'] = post_bozza
                except Exception as e:
                    st.error(f"Errore Agente 2: {e}")
                    post_bozza = None

            # --- AGENTE 3: L'EDITOR / REVISORE ---
            if post_bozza:
                with st.spinner("⏳ Agente 3 (Editor Didattico) in fase di revisione..."):
                    try:
                        prompt_revisione = f"""
                        Sei un Editor scolastico pignolo. Rivedi questo post divulgativo scritto per i docenti.
                        Migliora il tono rendendolo ingaggiante, chiaro, professionale ma accessibile, ed evita qualsiasi gergo aziendale o robotico. 
                        Ecco il testo da ottimizzare:
                        {post_bozza}
                        """
                        res3 = client.chat.completions.create(
                            model=modello_scelto,
                            messages=[{"role": "user", "content": prompt_revisione}]
                        )
                        post_finale = res3.choices[0].message.content
                        st.session_state['post_finale'] = post_finale
                    except Exception as e:
                        st.error(f"Errore Agente 3: {e}")
                        st.session_state['post_finale'] = post_bozza

# --- VISUALIZZAZIONE DEI RISULTATI ---
if 'punti_chiave' in st.session_state:
    st.markdown("---")
    st.subheader("🔍 1. Analisi (Ricercatore)")
    st.markdown(st.session_state['punti_chiave'])

if 'post_bozza' in st.session_state:
    st.subheader("✍️ 2. Prima Bozza (Scrittore)")
    st.write(st.session_state['post_bozza'])

if 'post_finale' in st.session_state:
    st.subheader("🎯 3. Post Revisionato e Ottimizzato (Editor)")
    st.info(st.session_state['post_finale'])
    
    # Sezione invio email
    st.markdown("---")
    if st.button("📧 2. Invia Report via Email", type="primary"):
        if not mittente or not password_app or not destinatario:
            st.error("⚠️ Compila tutti i campi email nella barra laterale.")
        else:
            with st.spinner("⏳ Invio email in corso..."):
                try:
                    # Conversione da Markdown ad HTML vero per l'email
                    html_punti_chiave = markdown.markdown(st.session_state['punti_chiave'])
                    html_post_bozza = markdown.markdown(st.session_state['post_bozza'])
                    html_post_finale = markdown.markdown(st.session_state['post_finale'])
                    
                    msg = MIMEMultipart()
                    msg['From'] = mittente
                    msg['To'] = destinatario
                    msg['Subject'] = f"🤖 Report IA Didattica: {tema}"
                    
                    corpo_html = f"""
                    <html>
                      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                        <h2 style="color: #1a73e8;">Report Generato dalla Squadra di Agenti IA</h2>
                        <p><strong>Tema trattato:</strong> {tema}</p>
                        <hr>
                        <h3 style="color: #3c4043;">🔍 1. Punti Chiave (Ricercatore)</h3>
                        <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #dadce0; border-radius: 4px;">
                          {html_punti_chiave}
                        </div>
                        
                        <h3 style="color: #3c4043; margin-top: 20px;">✍️ 2. Prima Bozza (Scrittore)</h3>
                        <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; border-radius: 4px;">
                          {html_post_bozza}
                        </div>
                        
                        <h3 style="color: #3c4043; margin-top: 20px;">🎯 3. Versione Finale Revisionata (Editor)</h3>
                        <div style="background: #e8f0fe; padding: 15px; border-left: 4px solid #1a73e8; border-radius: 4px;">
                          {html_post_finale}
                        </div>
                        
                        <hr style="margin-top: 25px;">
                        <p style="font-size: 0.8em; color: #777;">Generato tramite Web App Streamlit e OpenRouter.</p>
                      </body>
                    </html>
                    """
                    msg.attach(MIMEText(corpo_html, 'html'))
                    
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login(mittente, password_app)
                    server.sendmail(mittente, destinatario, msg.as_string())
                    server.quit()
                    
                    st.success(f"✅ Email inviata con successo a {destinatario}!")
                except Exception as e:
                    st.error(f"❌ Errore nell'invio dell'email: {e}")
