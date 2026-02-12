import streamlit as st
import math

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(
    page_title="Interpretare Gazometrie (Gazo Simplă)",
    page_icon="💉",
    layout="centered"
)

# --- STILIZARE CSS ---
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #0E4F75;
        text-align: center;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        text-align: center;
        margin-bottom: 20px;
    }
    .recommendation-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin-top: 20px;
    }
    .normal-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-header">Interpretare Gazometrie Arterială</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analiză rapidă + Recomandări de analize suplimentare</div>', unsafe_allow_html=True)

# --- SIDEBAR: INPUT DATE (CONFORM IMAGINII) ---
st.sidebar.header("Introduceți valorile din Buletin")

# Date obligatorii din imagine
ph = st.sidebar.number_input("pH Arterial", min_value=6.80, max_value=7.80, value=7.43, step=0.01, format="%.2f")
pco2 = st.sidebar.number_input("pCO2 (mmHg)", min_value=10.0, max_value=150.0, value=54.0, step=0.1)
po2 = st.sidebar.number_input("pO2 (mmHg)", min_value=10.0, max_value=500.0, value=68.0, step=0.1)
co2_total = st.sidebar.number_input("CO2 Total (mmol/L) / HCO3", min_value=5.0, max_value=60.0, value=37.5, step=0.1, help="De obicei HCO3 sau CO2 Total pe aparat")
base_excess = st.sidebar.number_input("Excès de bases (BE)", min_value=-30.0, max_value=30.0, value=9.0, step=0.1)
sao2 = st.sidebar.number_input("Saturație O2 (%)", min_value=50.0, max_value=100.0, value=94.6, step=0.1)
hb = st.sidebar.number_input("Hemoglobină (g/dL)", min_value=3.0, max_value=25.0, value=18.2, step=0.1)
lactat = st.sidebar.number_input("Lactate (mmol/L)", min_value=0.0, max_value=20.0, value=1.2, step=0.1)

# FiO2 estimat pentru calcul oxigenare
st.sidebar.markdown("---")
fio2_percent = st.sidebar.number_input("FiO2 estimat (%)", min_value=21, max_value=100, value=21, help="Aer atmosferic = 21%")
fio2 = fio2_percent / 100.0

# --- FUNCȚII LOGICĂ ---

def interpret_oxygenation():
    st.markdown("### 1. Evaluare Oxigenare")
    col1, col2 = st.columns(2)
    
    # Raport P/F
    pf_ratio = po2 / fio2
    
    status_oxy = ""
    color_oxy = "green"
    
    if po2 < 60:
        status_oxy = "Hipoxemie Severă (Insuficiență Respiratorie)"
        color_oxy = "red"
    elif po2 < 80:
        status_oxy = "Hipoxemie Ușoară/Moderată"
        color_oxy = "orange"
    else:
        status_oxy = "Normoxemie"
    
    col1.metric("pO2", f"{po2} mmHg")
    col2.metric("P/F Ratio", f"{int(pf_ratio)}")
    
    st.markdown(f"Status: **:{color_oxy}[{status_oxy}]**")
    
    if pf_ratio < 300:
        st.warning(f"⚠️ P/F Ratio ({int(pf_ratio)}) < 300 sugerează afectare pulmonară (ARDS criteria dacă e acut).")

def interpret_acid_base():
    st.markdown("### 2. Echilibru Acido-Bazic")
    
    # 1. pH Check
    if ph < 7.35:
        ph_status = "Acidemie"
        trend = "Acidoză"
    elif ph > 7.45:
        ph_status = "Alcalemie"
        trend = "Alcaloză"
    else:
        ph_status = "pH Normal"
        # Determine trend based on midpoint 7.40
        if ph < 7.40: trend = "Acidoză"
        else: trend = "Alcaloză"

    st.write(f"Stare pH: **{ph_status}** ({trend} predominantă)")

    # 2. Determine Primary Disorder
    # PCO2 Normal: 35-45, HCO3 (CO2Tot) Normal: 22-26
    
    pco2_status = "Acid" if pco2 > 45 else ("Alcalin" if pco2 < 35 else "Normal")
    metabolic_status = "Alcalin" if co2_total > 26 else ("Acid" if co2_total < 22 else "Normal")
    
    primary_dx = "Nedeterminat"
    explanation = ""

    # Logică simplificată ATS
    if trend == "Acidoză":
        if pco2 > 45 and co2_total < 22:
            primary_dx = "Acidoză Mixtă (Resp + Meta)"
        elif pco2 > 45:
            primary_dx = "Acidoză Respiratorie"
            explanation = "CO2 reținut (hipoventilație)."
        elif co2_total < 22:
            primary_dx = "Acidoză Metabolică"
            explanation = "Bicarbonat scăzut."
            
    elif trend == "Alcaloză":
        if pco2 < 35 and co2_total > 26:
            primary_dx = "Alcaloză Mixtă (Resp + Meta)"
        elif pco2 < 35:
            primary_dx = "Alcaloză Respiratorie"
            explanation = "CO2 eliminat excesiv (hiperventilație)."
        elif co2_total > 26:
            primary_dx = "Alcaloză Metabolică"
            explanation = "Bicarbonat/Baze în exces."

    st.info(f"🧬 Diagnostic Principal Probabil: **{primary_dx}**")
    if explanation:
        st.caption(explanation)

    # 3. Compensare (dacă pH e normal sau aproape normal)
    if ph_status == "pH Normal" and primary_dx != "Nedeterminat":
        st.success("Tulburarea este **Complet Compensată**.")
    elif primary_dx != "Nedeterminat":
        st.warning("Tulburarea este **Parțial Compensată** sau **Decompensată**.")

    return primary_dx, trend

def recommend_labs(primary_dx, trend):
    st.markdown("### 3. Ce analize să ceri în plus?")
    
    recs = []
    
    # 1. Verificare Lactat (deja introdus)
    if lactat > 2.0:
        st.error(f"⚠️ **LACTAT CRESCUT ({lactat})**: Acidoză lactică prezentă (Tip A - ischemie sau Tip B).")
        recs.append("Monitorizare Lactat seriat.")
    
    # 2. Logica pentru Acidoză Metabolică
    if "Acidoză Metabolică" in primary_dx or (trend == "Acidoză" and co2_total < 22):
        st.markdown('<div class="recommendation-box">🛑 <b>URGENT: Calcul Anion Gap necesar</b><br>Pacientul are o componentă de acidoză metabolică. Trebuie să diferențiezi între AG Crescut (MUDPILES) și AG Normal (Diaree/RTA).</div>', unsafe_allow_html=True)
        recs.append("**Ionogramă Serică (Na, K, Cl)** - Obligatoriu pentru calcul Anion Gap.")
        recs.append("**Albumină** - Pentru corecția Anion Gap.")
        recs.append("**Glicemie** - Pentru a exclude cetoacidoza diabetică.")
        recs.append("**Uree și Creatinină** - Pentru a exclude uremia (insuficiență renală).")
        if lactat < 2.0:
            recs.append("**Sumar de urină (Corpi cetonici)** - Dacă glicemia e mică (ex: inaniție/alcool).")

    # 3. Logica pentru Alcaloză Metabolică (Cazul din imaginea ta: pH 7.43, CO2 54, BE +9)
    elif "Alcaloză Metabolică" in primary_dx or (trend == "Alcaloză" and co2_total > 26):
        st.markdown('<div class="recommendation-box">💡 <b>Context: Alcaloză Metabolică</b><br>De obicei cauzată de pierderi de acid (vărsături, diuretice) sau exces de mineralocorticoizi.</div>', unsafe_allow_html=True)
        recs.append("**Ionogramă (Na, K, Cl)** - Caută Hipokaliemie și Hipocloremie (sensibilă la Clor).")
        recs.append("**Volum urinar / Stare de hidratare** - Alcaloza de contracție?")
        recs.append("Verifică medicația: Diuretice de ansă/tiazidice?")

    # 4. Logica pentru Respirator
    elif "Respiratorie" in primary_dx:
        if trend == "Acidoză":
            recs.append("Cauză posibilă: BPOC, Sedare, Obstrucție. Verifică istoricul.")
        else: # Alcaloză resp
            recs.append("Cauză posibilă: Durere, Anxietate, Embolie Pulmonară (mai ales dacă pO2 e mic).")

    # 5. Hemoglobina
    if hb < 7.0:
        recs.append("Hemogramă completă + Grup Sanguin (Anemie severă).")
    elif hb > 18.0:
        recs.append("Posibilă Poliglobulie (secundară hipoxiei cronice?). Hidratare?")

    if recs:
        st.write("📋 **Lista de comenzi sugerată:**")
        for rec in recs:
            st.markdown(f"- {rec}")
    else:
        st.markdown('<div class="normal-box">Nu sunt recomandări critice suplimentare bazate strict pe gazo. Corelează cu clinica.</div>', unsafe_allow_html=True)

# --- EXECUȚIE ---

if st.button("Interpretează Rezultatele", type="primary"):
    interpret_oxygenation()
    st.divider()
    dx, tr = interpret_acid_base()
    st.divider()
    recommend_labs(dx, tr)
    
    # Secțiune ascunsă pentru când vin rezultatele de la laborator
    with st.expander("Ai primit rezultatele la Ionogramă? Calculează Anion Gap aici"):
        st.write("Dacă ai cerut Na și Cl, introdu-le aici:")
        na_late = st.number_input("Na+ (Sodiu)", 100, 180, 140)
        cl_late = st.number_input("Cl- (Clor)", 60, 140, 100)
        
        ag_late = na_late - (cl_late + co2_total)
        st.write(f"**Anion Gap Calculat:** {ag_late:.1f}")
        if ag_late > 12:
            st.error("Anion Gap Crescut!")
        else:
            st.success("Anion Gap Normal.")

else:
    st.info("Apasă butonul de mai sus pentru analiză.")
