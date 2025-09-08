import streamlit as st
import pandas as pd
from datetime import datetime
# from gemini_api import GeminiAPI # Platzhalter für die tatsächliche API-Integration

# Konfiguration der Seite
st.set_page_config(page_title="Elterngeld-Berater", layout="wide")

# Titel und Einleitung
st.title("👨‍👩‍👧 Elterngeld-Berater")
st.markdown("Willkommen! Finden Sie die beste Elterngeld-Variante für Ihre Familie.")

# --- Sektion 1: Begrüßung und Information ---
st.header("1. Wichtige Informationen")
st.markdown("Das Elterngeld unterstützt Familien nach der Geburt. Es gibt drei Varianten: **Basiselterngeld**, **ElterngeldPlus** und den **Partnerschaftsbonus**.")
# ... weitere Erklärungen

st.divider()

# --- Sektion 2: Intelligenter Fragebogen ---
st.header("2. Intelligenter Fragebogen")
st.markdown("Beantworten Sie die folgenden Fragen, um eine individuelle Empfehlung zu erhalten.")

with st.form("elterngeld_form"):
    einkommen = st.number_input("Durchschnittliches monatliches Nettoeinkommen vor der Geburt (in €):", min_value=0, value=2000)
    elternzeit_dauer = st.radio("Wie lange planen Sie, in Elternzeit zu gehen?", ("12 Monate", "24 Monate oder länger"))
    teilzeit_wunsch = st.checkbox("Möchten Sie während der Elternzeit in Teilzeit arbeiten?")
    partnerschaftsbonus_wunsch = st.checkbox("Wünschen sich beide Elternteile eine gemeinsame Elternzeit (Partnerschaftsbonus)?")
    
    submitted = st.form_submit_button("Empfehlung anzeigen")
    
    if submitted:
        # Hier die Logik mit Gewichtung
        score_basis = 0
        score_plus = 0
        score_bonus = 0
        
        # Logik für Basiselterngeld vs. ElterngeldPlus
        if elternzeit_dauer == "12 Monate":
            score_basis += 5
        else:
            score_plus += 5
        
        if teilzeit_wunsch:
            score_plus += 10
        
        if partnerschaftsbonus_wunsch:
            score_bonus += 10
            
        # Besten Vorschlag ermitteln
        scores = {"Basiselterngeld": score_basis, "ElterngeldPlus": score_plus, "Partnerschaftsbonus": score_bonus}
        beste_option = max(scores, key=scores.get)
        
        st.subheader("💡 Unsere Empfehlung:")
        st.success(f"Basierend auf Ihren Antworten ist die **{beste_option}**-Variante am besten für Sie geeignet.")
        # Optional: Detailliertere Begründung hinzufügen

st.divider()

# --- Sektion 3: Varianten-Planer ---
st.header("3. Elterngeld-Planer")
st.markdown("Spielen Sie verschiedene Szenarien durch und planen Sie Ihre Monate.")
# Hier kommt der Code für den interaktiven Planer (z.B. mit st.slider, st.columns)
# ...

st.divider()

# --- Sektion 4: Chatbot ---
st.header("4. Chatbot (GEMINI-Powered)")
st.markdown("Stellen Sie spezifische Fragen zum Elterngeld.")

# Hier kommt der Code für die Chatbot-Integration (mit st.chat_message)
# ...
