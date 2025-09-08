import streamlit as st
import pandas as pd
import altair as alt # Für die Visualisierung
import random # Für die Chatbot-Simulation

# ---- Konfiguration der Seite ----
st.set_page_config(page_title="Elterngeld-Berater 2.0", layout="wide", page_icon="👨‍👩‍👧")

# ---- Dummy-Funktionen für die Elterngeld-Berechnung (gemäß aktuellen Richtlinien) ----
def calculate_basic_elterngeld(net_income):
    """
    Berechnet das Basiselterngeld basierend auf dem Nettoeinkommen.
    Einfache Modellierung. Realistischerweise sind die Regeln komplexer.
    """
    if net_income >= 1240:
        return 0.65 * net_income
    elif net_income > 1000:
        return 0.65 * net_income + 0.01 * (1240 - net_income)
    else:
        return 0.67 * net_income

def calculate_plus_elterngeld(net_income, part_time_income):
    """
    Berechnet das ElterngeldPlus bei Teilzeitarbeit.
    Einfache Modellierung. Realistischerweise sind die Regeln komplexer.
    """
    # ElterngeldPlus ist max. die Hälfte des Basiselterngelds
    max_eg_plus = calculate_basic_elterngeld(net_income) / 2
    # Einkommen während der Elternzeit wird angerechnet
    income_after = net_income - part_time_income
    calculated_eg_plus = calculate_basic_elterngeld(income_after)
    
    return min(max_eg_plus, calculated_eg_plus)

# ---- Start der Streamlit App ----

# Header
st.title("👨‍👩‍👧 Intelligenter Elterngeld-Berater")
st.markdown("Ihr persönlicher Assistent zur Planung des Elterngelds in Deutschland. Finden Sie die beste Variante, spielen Sie Szenarien durch und erhalten Sie Antworten auf Ihre Fragen.")

st.divider()

# ---- Sektion 1: Intelligenter Fragenkatalog ----
st.header("1. Intelligenter Fragenkatalog mit Gewichtung")
st.markdown("Beantworten Sie die Fragen, um eine auf Ihre Situation zugeschnittene Empfehlung zu erhalten.")

# Formular für den Fragenkatalog
with st.form("intelligent_questionnaire"):
    st.subheader("Ihre Situation")
    income_parent_1 = st.number_input("Durchschnittliches monatliches Nettoeinkommen von Elternteil 1 (in €):", min_value=300, value=2500)
    income_parent_2 = st.number_input("Durchschnittliches monatliches Nettoeinkommen von Elternteil 2 (in €):", min_value=300, value=1500)
    
    st.subheader("Ihre Wünsche")
    duration_wish = st.selectbox("Gewünschte Dauer des Elterngeldbezugs:", ["12 Monate (Basiselterngeld)", "24 Monate (ElterngeldPlus)", "36 Monate oder länger (Mix)"])
    part_time_parent_1 = st.checkbox("Möchten Sie (Elternteil 1) in der Elternzeit in Teilzeit arbeiten?")
    part_time_parent_2 = st.checkbox("Möchten Sie (Elternteil 2) in der Elternzeit in Teilzeit arbeiten?")
    
    shared_months_wish = st.checkbox("Wünschen sich beide Elternteile eine gemeinsame Elternzeit (Partnerschaftsbonus)?")
    
    submitted = st.form_submit_button("Empfehlung berechnen")

    if submitted:
        # ---- Logik mit Gewichtung ----
        score_basis = 0
        score_plus = 0
        score_bonus = 0
        
        # Bewertung der Wünsche
        if "12 Monate" in duration_wish:
            score_basis += 10
        elif "24 Monate" in duration_wish:
            score_plus += 10
        else: # Mix aus Basis und Plus
            score_plus += 5
            score_basis += 5

        if part_time_parent_1 or part_time_parent_2:
            score_plus += 20 # Hohe Gewichtung für Teilzeitarbeit
            score_basis -= 5
        
        if shared_months_wish:
            score_bonus += 15 # Hohe Gewichtung für Partnerschaftsbonus
            score_basis -= 5 # Geringe Gewichtung gegen Basis EG

        scores = {
            "Basiselterngeld": score_basis,
            "ElterngeldPlus": score_plus,
            "Partnerschaftsbonus": score_bonus
        }

        # Finden der besten Option
        best_option = max(scores, key=scores.get)
        
        st.subheader("💡 Ihre persönliche Empfehlung")
        st.success(f"Basierend auf Ihren Antworten ist die **{best_option}**-Variante am besten für Ihre Familie geeignet.")
        st.info("Diese Empfehlung dient als Orientierung. Nutzen Sie den Planer, um Details zu simulieren.")

st.divider()

# ---- Sektion 2: Elterngeld-Planer ----
st.header("2. Elterngeld-Planer")
st.markdown("Simulieren Sie verschiedene Szenarien, indem Sie die Schieberegler anpassen. Die voraussichtlichen Auszahlungen werden in Echtzeit berechnet.")
st.markdown("⚠️ Die Berechnungen sind stark vereinfacht und dienen nur zur Veranschaulichung.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Ihre Planung")
    months_parent_1 = st.slider("Elterngeldmonate Elternteil 1:", 0, 14, 7)
    months_parent_2 = st.slider("Elterngeldmonate Elternteil 2:", 0, 14, 7)
    
    is_part_time_parent_1 = st.checkbox("Elternteil 1 arbeitet in Teilzeit", False)
    is_part_time_parent_2 = st.checkbox("Elternteil 2 arbeitet in Teilzeit", False)
    
    part_time_income_parent_1 = 0
    if is_part_time_parent_1:
        part_time_income_parent_1 = st.number_input("Teilzeit-Einkommen Elternteil 1 (in €):", min_value=0, value=800)
    
    part_time_income_parent_2 = 0
    if is_part_time_parent_2:
        part_time_income_parent_2 = st.number_input("Teilzeit-Einkommen Elternteil 2 (in €):", min_value=0, value=800)
        
    st.markdown(f"**Gesamte geplante Monate:** {months_parent_1 + months_parent_2}")
    
with col2:
    st.subheader("Simulation der Auszahlungen")
    monthly_payments = []
    
    # Basiselterngeld Berechnung
    base_eg_p1 = calculate_basic_elterngeld(income_parent_1)
    base_eg_p2 = calculate_basic_elterngeld(income_parent_2)
    
    # ElterngeldPlus Berechnung
    plus_eg_p1 = calculate_plus_elterngeld(income_parent_1, part_time_income_parent_1) if is_part_time_parent_1 else 0
    plus_eg_p2 = calculate_plus_elterngeld(income_parent_2, part_time_income_parent_2) if is_part_time_parent_2 else 0

    # Daten für die Visualisierung vorbereiten
    data = []
    for month in range(1, months_parent_1 + 1):
        payment = plus_eg_p1 if is_part_time_parent_1 else base_eg_p1
        data.append({"Monat": month, "Zahlung": payment, "Elternteil": "Elternteil 1"})
    
    for month in range(1, months_parent_2 + 1):
        payment = plus_eg_p2 if is_part_time_parent_2 else base_eg_p2
        data.append({"Monat": months_parent_1 + month, "Zahlung": payment, "Elternteil": "Elternteil 2"})
    
    df_payments = pd.DataFrame(data)
    
    if not df_payments.empty:
        total_payment = df_payments["Zahlung"].sum()
        st.markdown(f"**Voraussichtliche Gesamtauszahlung:** **{total_payment:,.2f} €**")
        
        chart = alt.Chart(df_payments).mark_bar().encode(
            x=alt.X("Monat:O", title="Monat seit der Geburt"),
            y=alt.Y("Zahlung:Q", title="Voraussichtliche Zahlung (€)"),
            color=alt.Color("Elternteil:N", title="Beziehender Elternteil"),
            tooltip=["Monat", "Zahlung", "Elternteil"]
        ).properties(
            title="Monatliche Auszahlungen",
            height=300
        )
        st.altair_chart(chart, use_container_width=True)

st.divider()

# ---- Sektion 3: Chatbot (Gemini-Powered) ----
st.header("3. Ihr persönlicher Elterngeld-Chatbot")
st.markdown("Fragen Sie den Chatbot alles, was Sie wissen möchten.")

# Dummy-Funktion für die Gemini-API (ersetzen Sie dies mit Ihrem Code)
def get_gemini_response(prompt):
    # Hier würde der tatsächliche API-Aufruf zu Gemini stattfinden
    # Beachten Sie, dass Sie Ihren API-Schlüssel nicht direkt in den Code schreiben sollten.
    # Stattdessen nutzen Sie st.secrets.
    # api_key = st.secrets["gemini_api_key"]
    # model = GeminiAPI(api_key=api_key)
    # response = model.generate_content(prompt)
    # return response.text
    
    # Platzhalter-Antworten
    responses = {
        "Wie lange bekommt man Basiselterngeld?": "Basiselterngeld kann für maximal 14 Monate bezogen werden, wenn beide Elternteile es beantragen.",
        "Was ist ElterngeldPlus?": "ElterngeldPlus ermöglicht es, Teilzeit zu arbeiten, während man Elterngeld bezieht. Ein Monat Basiselterngeld entspricht zwei Monaten ElterngeldPlus.",
        "Wie wird das Einkommen berechnet?": "Das Elterngeld berechnet sich in der Regel anhand des durchschnittlichen Nettoeinkommens der 12 Monate vor der Geburt. Bei Selbstständigen sind die Regeln komplexer.",
        "Was ist der Partnerschaftsbonus?": "Der Partnerschaftsbonus sind vier zusätzliche ElterngeldPlus-Monate, die Paare erhalten, wenn sie in dieser Zeit gleichzeitig in Teilzeit arbeiten.",
        "default": "Als spezialisierter Elterngeld-Experte kann ich Ihnen die meisten Fragen beantworten. Bitte fragen Sie genauer nach."
    }
    
    # Suche nach passender Antwort
    for question, answer in responses.items():
        if question.lower() in prompt.lower():
            return answer
    return responses["default"]

# Initialisiere den Chat-Verlauf
if "messages" not in st.session_state:
    st.session_state.messages = []

# Zeige den bisherigen Chat-Verlauf
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Verarbeite Nutzereingaben
if user_prompt := st.chat_input("Stellen Sie Ihre Frage zum Elterngeld..."):
    # Füge Nutzereingabe zum Chat-Verlauf hinzu
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    # Hole die Antwort vom Chatbot
    with st.spinner("Antwort wird generiert..."):
        ai_response = get_gemini_response(user_prompt)
    
    # Füge Chatbot-Antwort zum Chat-Verlauf hinzu
    with st.chat_message("assistant"):
        st.markdown(ai_response)
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
