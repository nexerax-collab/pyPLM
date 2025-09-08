import streamlit as st
import pandas as pd
import altair as alt

# --- Konfiguration der Seite ---
st.set_page_config(page_title="Optimaler Elterngeld-Berater", layout="wide", page_icon="👨‍👩‍👧")

# --- Vereinfachte Berechnungsfunktionen ---
def calculate_basic_eg(net_income):
    if net_income <= 300: return 300
    if net_income >= 2770: return 1800
    if net_income >= 1240: return 0.65 * net_income
    if net_income > 1000: return 0.65 * net_income + 0.01 * (1240 - net_income)
    return 0.67 * net_income

def calculate_plus_eg(net_income, part_time_income):
    max_eg_plus = calculate_basic_eg(net_income) / 2
    income_diff = net_income - part_time_income
    
    if income_diff >= 1240:
        calculated_eg_plus = 0.65 * income_diff
    elif income_diff > 1000:
        calculated_eg_plus = 0.65 * income_diff + 0.01 * (1240 - income_diff)
    else:
        calculated_eg_plus = 0.67 * income_diff
    
    return max(150, min(max_eg_plus, calculated_eg_plus))

# --- Chatbot-Funktion in der Seitenleiste ---
def get_gemini_response(prompt):
    # Hier muss Ihr Code für die Gemini API-Integration rein.
    # Wichtiger Sicherheitshinweis: Speichern Sie Ihren API-Schlüssel nicht direkt im Code!
    # Nutzen Sie stattdessen Streamlit Secrets: st.secrets["GEMINI_API_KEY"]
    
    # Beispiel-Antworten (Platzhalter)
    responses = {
        "Wie lange bekommt man Basiselterngeld?": "Basiselterngeld kann für maximal 14 Monate bezogen werden, wenn beide Elternteile es beantragen und die Voraussetzungen erfüllen.",
        "Was ist ElterngeldPlus?": "ElterngeldPlus ermöglicht es, länger Elterngeld zu beziehen. Ein Monat Basiselterngeld entspricht zwei Monaten ElterngeldPlus. Es ist besonders vorteilhaft, wenn Sie während des Bezugs in Teilzeit arbeiten möchten.",
        "Wie wird das Einkommen berechnet?": "Das Elterngeld berechnet sich in der Regel anhand des durchschnittlichen monatlichen Nettoeinkommens der 12 Monate vor der Geburt. Bei Selbstständigen gibt es besondere Regelungen.",
        "Was ist der Partnerschaftsbonus?": "Der Partnerschaftsbonus besteht aus vier zusätzlichen ElterngeldPlus-Monaten, die Paare erhalten, wenn sie in dieser Zeit beide gleichzeitig in Teilzeit arbeiten.",
        "default": "Ich bin ein Elterngeld-Experte. Fragen Sie mich, was Sie wissen möchten. (Dies ist eine Beispiel-Antwort. Hier würde die Gemini-Antwort stehen.)"
    }
    
    for question, answer in responses.items():
        if question.lower() in prompt.lower():
            return answer
    return responses["default"]

st.sidebar.title("💬 Ihr Elterngeld-Chatbot")
st.sidebar.markdown("Stellen Sie Ihre Fragen zum Elterngeld.")

# Initialisiere den Chat-Verlauf in der Seitenleiste
if "messages" not in st.session_state:
    st.session_state.messages = []

# Zeige den bisherigen Chat-Verlauf
for message in st.session_state.messages:
    with st.sidebar.chat_message(message["role"]):
        st.markdown(message["content"])

# Verarbeite Nutzereingaben
if user_prompt := st.sidebar.chat_input("Ihre Frage..."):
    # Füge Nutzereingabe zum Chat-Verlauf hinzu
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.sidebar.chat_message("user"):
        st.markdown(user_prompt)
    
    # Hole die Antwort vom Chatbot
    with st.sidebar.spinner("Antwort wird generiert..."):
        ai_response = get_gemini_response(user_prompt)
    
    # Füge Chatbot-Antwort zum Chat-Verlauf hinzu
    with st.sidebar.chat_message("assistant"):
        st.markdown(ai_response)
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

# --- Haupt-App-Logik ---
st.title("👨‍👩‍👧 Ihr optimaler Elterngeld-Berater")
st.markdown("Willkommen! Finden Sie in nur 3 Schritten die beste Elterngeld-Lösung für Ihre Familie.")

# Initialisiere Session State
if 'page' not in st.session_state:
    st.session_state.page = "start"
if 'data' not in st.session_state:
    st.session_state.data = {}

# --- Schritt 1: Dateneingabe ---
if st.session_state.page == "start":
    st.header("1. Schritt: Ihre Situation & Wünsche")
    st.markdown("Erzählen Sie uns, was Ihnen am wichtigsten ist.")

    with st.form("input_form"):
        st.subheader("Ihre persönlichen Daten")
        st.session_state.data['income_p1'] = st.number_input("Durchschnittliches monatliches Nettoeinkommen Elternteil 1 (in €):", min_value=300, value=2500)
        st.session_state.data['income_p2'] = st.number_input("Durchschnittliches monatliches Nettoeinkommen Elternteil 2 (in €):", min_value=300, value=1500)
        
        st.session_state.data['part_time_p1'] = st.checkbox("Elternteil 1 plant Teilzeitarbeit während des Bezugs")
        st.session_state.data['part_time_p2'] = st.checkbox("Elternteil 2 plant Teilzeitarbeit während des Bezugs")
        
        if st.session_state.data['part_time_p1']:
            st.session_state.data['part_time_income_p1'] = st.number_input("Geplantes monatliches Teilzeit-Nettoeinkommen (Elternteil 1):", min_value=0, value=800)
        
        if st.session_state.data['part_time_p2']:
            st.session_state.data['part_time_income_p2'] = st.number_input("Geplantes monatliches Teilzeit-Nettoeinkommen (Elternteil 2):", min_value=0, value=800)
        
        st.subheader("Ihr Ziel")
        st.session_state.data['preference'] = st.radio("Was ist Ihnen am wichtigsten?", 
            ("Maximale Auszahlung in kurzer Zeit", "Längstmögliche Bezugsdauer", "Optimale Flexibilität"),
            index=1 if st.session_state.data.get('part_time_p1') or st.session_state.data.get('part_time_p2') else 0
        )
        
        submitted = st.form_submit_button("Optionen anzeigen")
        if submitted:
            st.session_state.page = "options"
            st.rerun()  # Die korrekte Funktion

# --- Schritt 2: Optionen vergleichen ---
elif st.session_state.page == "options":
    st.header("2. Schritt: Ihre besten Optionen")
    st.markdown("Basierend auf Ihren Angaben haben wir drei optimale Modelle für Sie ermittelt.")

    col1, col2, col3 = st.columns(3)
    
    # ---- Option 1: Maximale Auszahlung ----
    with col1:
        st.subheader("🚀 Maximum-Einkommen")
        st.markdown("**Das ist für Sie:** Wenn Sie in der kürzesten Zeit das höchste Elterngeld erhalten möchten.")
        
        total_months_1 = 12
        eg_p1_1 = calculate_basic_eg(st.session_state.data['income_p1'])
        eg_p2_1 = calculate_basic_eg(st.session_state.data['income_p2'])
        
        total_payment_1 = (eg_p1_1 * 6) + (eg_p2_1 * 6)
        
        st.metric(label="Geschätzte Gesamtauszahlung", value=f"{total_payment_1:,.2f} €")
        st.metric(label="Bezugsdauer", value=f"{total_months_1} Monate")
        
        if st.button("Diese Option planen"):
            st.session_state.page = "plan"
            st.session_state.plan = {"months_p1": 6, "months_p2": 6, "mode": "basic"}
            st.rerun() # Dies ist die korrigierte Zeile

    # ---- Option 2: Längste Bezugsdauer ----
    with col2:
        st.subheader("⏳ Längste Zeit")
        st.markdown("**Das ist für Sie:** Wenn Sie so lange wie möglich bei Ihrem Kind bleiben wollen, auch in Teilzeit.")
        
        total_months_2 = 24
        eg_p1_2 = calculate_plus_eg(st.session_state.data['income_p1'], st.session_state.data.get('part_time_income_p1', 0))
        eg_p2_2 = calculate_plus_eg(st.session_state.data['income_p2'], st.session_state.data.get('part_time_income_p2', 0))
        
        total_payment_2 = (eg_p1_2 * 12) + (eg_p2_2 * 12)
        
        st.metric(label="Geschätzte Gesamtauszahlung", value=f"{total_payment_2:,.2f} €")
        st.metric(label="Bezugsdauer", value=f"{total_months_2} Monate")
        
        if st.button("Diese Option planen "):
            st.session_state.page = "plan"
            st.session_state.plan = {"months_p1": 12, "months_p2": 12, "mode": "plus"}
            st.experimental_rerun()
            
    # ---- Option 3: Maximale Flexibilität ----
    with col3:
        st.subheader("💫 Optimale Flexibilität")
        st.markdown("**Das ist für Sie:** Wenn Sie Basis- und Plus-Monate mischen und gleichzeitig Elternzeit nehmen möchten.")
        
        total_months_3 = 16 # Beispiel mit Partnerschaftsbonus
        eg_p1_3 = calculate_basic_eg(st.session_state.data['income_p1'])
        eg_p2_3 = calculate_plus_eg(st.session_state.data['income_p2'], st.session_state.data.get('part_time_income_p2', 0))
        
        total_payment_3 = (eg_p1_3 * 8) + (eg_p2_3 * 8)
        
        st.metric(label="Geschätzte Gesamtauszahlung", value=f"{total_payment_3:,.2f} €")
        st.metric(label="Bezugsdauer", value=f"{total_months_3} Monate")
        
        if st.button("Diese Option planen  "):
            st.session_state.page = "plan"
            st.session_state.plan = {"months_p1": 8, "months_p2": 8, "mode": "mixed"}
            st.experimental_rerun()

# --- Schritt 3: Persönlicher Planer ---
elif st.session_state.page == "plan":
    st.header("3. Schritt: Ihr persönlicher Plan")
    st.markdown("Passen Sie die Monate an und sehen Sie live die Auswirkungen auf Ihre Finanzen.")
    
    plan_mode = st.session_state.plan['mode']
    
    max_months_total = 14
    if plan_mode == 'plus':
        max_months_total = 28
    
    st.subheader("Monatsaufteilung")
    
    col_plan1, col_plan2 = st.columns(2)
    with col_plan1:
        months_p1 = st.slider("Monate Elternteil 1:", 0, max_months_total, st.session_state.plan['months_p1'])
    with col_plan2:
        months_p2 = st.slider("Monate Elternteil 2:", 0, max_months_total, st.session_state.plan['months_p2'])

    total_months = months_p1 + months_p2
    st.info(f"Geplante Gesamtdauer: {total_months} Monate")

    # --- Statistik und Visualisierung ---
    st.subheader("Ihre Finanzen im Überblick")
    
    payments_data = []
    
    income_p1 = st.session_state.data['income_p1']
    income_p2 = st.session_state.data['income_p2']
    
    for i in range(months_p1):
        payment = calculate_basic_eg(income_p1)
        if st.session_state.data.get('part_time_p1', False):
            payment = calculate_plus_eg(income_p1, st.session_state.data.get('part_time_income_p1', 0))
        payments_data.append({"Monat": i+1, "Zahlung": payment, "Elternteil": "Elternteil 1"})
    
    for i in range(months_p2):
        payment = calculate_basic_eg(income_p2)
        if st.session_state.data.get('part_time_p2', False):
            payment = calculate_plus_eg(income_p2, st.session_state.data.get('part_time_income_p2', 0))
        payments_data.append({"Monat": months_p1 + i + 1, "Zahlung": payment, "Elternteil": "Elternteil 2"})
        
    df_payments = pd.DataFrame(payments_data)

    if not df_payments.empty:
        total_payment = df_payments["Zahlung"].sum()
        total_income_before = (income_p1 * months_p1) + (income_p2 * months_p2)
        income_loss = total_income_before - total_payment
        
        col_stats1, col_stats2 = st.columns(2)
        with col_stats1:
            st.metric(label="Geschätzte Gesamtauszahlung", value=f"{total_payment:,.2f} €")
        with col_stats2:
            st.metric(label="Einkommensverlust", value=f"{income_loss:,.2f} €")
        
        chart = alt.Chart(df_payments).mark_bar().encode(
            x=alt.X("Monat:O", title="Monat seit der Geburt"),
            y=alt.Y("Zahlung:Q", title="Zahlung in €"),
            color=alt.Color("Elternteil:N"),
            tooltip=["Monat", "Zahlung", "Elternteil"]
        ).properties(
            title="Monatliche Auszahlungen"
        )
        st.altair_chart(chart, use_container_width=True)
    
    if st.button("⬅️ Zurück zu den Optionen"):
        st.session_state.page = "options"
        st.experimental_rerun()
