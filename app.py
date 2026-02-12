import streamlit as st
import math

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(
    page_title="Interpretare Gazometrie (ABG)",
    page_icon="🫁",
    layout="centered"
)

# --- STILIZARE CSS ---
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #0E4F75;
        text-align: center;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 20px;
    }
    .step-box {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #0E4F75;
        margin-bottom: 20px;
    }
    .result-alert {
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-header">Interpretare Gazometrie Arterială (ABG)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Bazat pe ghidul ATS / Yale - Dr. David A. Kaufman</div>', unsafe_allow_html=True)

st.info("Această aplicație urmează abordarea în 6 pași descrisă în materialul American Thoracic Society.")

# --- SIDEBAR: INPUT DATE ---
st.sidebar.header("Introducere Date Pacient")

ph = st.sidebar.number_input("pH", min_value=6.80, max_value=7.80, value=7.40, step=0.01, format="%.2f")
paco2 = st.sidebar.number_input("PaCO2 (mmHg)", min_value=10.0, max_value=150.0, value=40.0, step=1.0)
hco3 = st.sidebar.number_input("HCO3- (mEq/L)", min_value=5.0, max_value=60.0, value=24.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Electroliți (pentru Anion Gap)")
na = st.sidebar.number_input("Na+ (Sodiu)", min_value=100.0, max_value=180.0, value=140.0, step=1.0)
cl = st.sidebar.number_input("Cl- (Clor)", min_value=60.0, max_value=140.0, value=100.0, step=1.0)
albumin = st.sidebar.number_input("Albumina (g/dL)", min_value=0.5, max_value=6.0, value=4.0, step=0.1)

# --- LOGICA DE INTERPRETARE ---

def interpret_abg():
    # STEP 1: Consistență Internă (Henderson-Hasselbalch)
    st.markdown("### Pasul 1: Verificarea Consistenței Interne")
    
    # Formula din text: [H+] = 24 * (PaCO2 / HCO3)
    calc_h_plus = 24 * (paco2 / hco3)
    
    # Maparea pH la H+ (aprox din tabelul textului)
    # Folosim formula inversă pentru precizie: pH = -log10(H+ * 10^-9) => H+ (nmol/L) = 10^(9 - pH)
    actual_h_plus_from_ph = 10**(9 - ph)
    
    st.write(f"Calculat [H+] (bazat pe CO2/HCO3): **{calc_h_plus:.1f} nmol/L**")
    st.write(f"Așteptat [H+] (bazat pe pH): **{actual_h_plus_from_ph:.1f} nmol/L**")
    
    diff = abs(calc_h_plus - actual_h_plus_from_ph)
    if diff > 10: # Marjă de eroare acceptabilă
        st.warning("⚠️ Valorile par inconsistente (Diferență mare între pH și relația PaCO2/HCO3). Posibilă eroare de recoltare sau analizor.")
    else:
        st.success("✅ Datele sunt consistente intern.")

    # STEP 2: Acidemia vs Alkalemia
    st.markdown("### Pasul 2: Acidemie sau Alcalemie?")
    primary_status = ""
    if ph < 7.35:
        primary_status = "Acidemie"
        st.error(f"pH {ph} < 7.35: **Acidemie**")
    elif ph > 7.45:
        primary_status = "Alcalemie"
        st.info(f"pH {ph} > 7.45: **Alcalemie**")
    else:
        primary_status = "pH Normal"
        st.success(f"pH {ph} (7.35 - 7.45): **pH în limite normale** (Posibilă tulburare mixtă compensată)")

    # STEP 3: Respirator vs Metabolic
    st.markdown("### Pasul 3: Tulburare Respiratorie sau Metabolică?")
    
    primary_disorder = "Nedeterminat"
    
    # Analiză direcțională
    # Normal PaCO2 = 40, Normal HCO3 = 24
    paco2_dir = "↑" if paco2 > 42 else ("↓" if paco2 < 38 else "↔")
    hco3_dir = "↑" if hco3 > 26 else ("↓" if hco3 < 22 else "↔")
    
    st.write(f"Direcția PaCO2: {paco2_dir} | Direcția HCO3-: {hco3_dir}")

    if primary_status == "Acidemie":
        if paco2 > 42: # Acidemie + CO2 crescut = Respirator
            primary_disorder = "Acidoză Respiratorie"
        elif hco3 < 22: # Acidemie + HCO3 scăzut = Metabolic
            primary_disorder = "Acidoză Metabolică"
        else:
            primary_disorder = "Acidoză (Mixtă sau Complexă)"
            
    elif primary_status == "Alcalemie":
        if paco2 < 38: # Alcalemie + CO2 scăzut = Respirator
            primary_disorder = "Alcaloză Respiratorie"
        elif hco3 > 26: # Alcalemie + HCO3 crescut = Metabolic
            primary_disorder = "Alcaloză Metabolică"
        else:
            primary_disorder = "Alcaloză (Mixtă sau Complexă)"
    
    else: # pH Normal
        if paco2 > 42 and hco3 > 26:
            st.write("PaCO2 ↑ și HCO3 ↑ cu pH Normal -> Acidoză Respiratorie + Alcaloză Metabolică")
        elif paco2 < 38 and hco3 < 22:
            st.write("PaCO2 ↓ și HCO3 ↓ cu pH Normal -> Alcaloză Respiratorie + Acidoză Metabolică")
            
    st.markdown(f"#### Tulburare Primară Identificată: **{primary_disorder}**")

    # STEP 4: Compensare
    st.markdown("### Pasul 4: Compensarea")
    
    secondary_disorder = []
    
    if "Acidoză Metabolică" in primary_disorder:
        # Winter's Formula: PaCO2 = (1.5 * HCO3) + 8 (+/- 2)
        expected_paco2 = (1.5 * hco3) + 8
        st.write(f"PaCO2 așteptat (Formula Winter): {expected_paco2:.1f} ± 2 mmHg")
        
        if paco2 < (expected_paco2 - 2):
            st.warning("PaCO2 măsurat este mai mic decât cel așteptat -> **Alcaloză Respiratorie Concomitentă**")
            secondary_disorder.append("Alcaloză Respiratorie")
        elif paco2 > (expected_paco2 + 2):
            st.warning("PaCO2 măsurat este mai mare decât cel așteptat -> **Acidoză Respiratorie Concomitentă**")
            secondary_disorder.append("Acidoză Respiratorie")
        else:
            st.success("Compensare Respiratorie Adecvată (Pură).")

    elif "Alcaloză Metabolică" in primary_disorder:
        # PaCO2 = 40 + 0.6 * (HCO3 - 24)
        expected_paco2 = 40 + 0.6 * (hco3 - 24)
        st.write(f"PaCO2 așteptat: {expected_paco2:.1f} mmHg")
        # Textul nu da o marjă exactă, dar uzual e +/- 2
        if abs(paco2 - expected_paco2) > 5: # Marjă largă
            st.warning("Compensarea nu pare adecvată (posibilă tulburare mixtă).")
        else:
            st.success("Compensare Respiratorie Adecvată.")

    elif "Acidoză Respiratorie" in primary_disorder:
        delta_paco2 = paco2 - 40
        # Acute: HCO3 crește cu delta_paco2 / 10
        exp_hco3_acute = 24 + (delta_paco2 / 10)
        # Chronic: HCO3 crește cu 3.5 * delta_paco2 / 10
        exp_hco3_chronic = 24 + (3.5 * (delta_paco2 / 10))
        
        st.write(f"HCO3 așteptat dacă Acut: {exp_hco3_acute:.1f} (±3)")
        st.write(f"HCO3 așteptat dacă Cronic: {exp_hco3_chronic:.1f}")
        
        if abs(hco3 - exp_hco3_acute) <= 3:
            st.info("Tipar: **Acidoză Respiratorie Acută**")
        elif abs(hco3 - exp_hco3_chronic) <= 3:
            st.info("Tipar: **Acidoză Respiratorie Cronică**")
        else:
            st.warning("HCO3 nu se potrivește nici cu acut, nici cu cronic pur. Posibilă tulburare Metabolică suprapusă.")

    elif "Alcaloză Respiratorie" in primary_disorder:
        delta_paco2 = 40 - paco2
        # Acute: HCO3 scade cu 2 * delta / 10
        exp_hco3_acute = 24 - (2 * (delta_paco2 / 10))
        # Chronic: HCO3 scade cu 5 * delta / 10
        exp_hco3_chronic = 24 - (5 * (delta_paco2 / 10)) # Range 5-7 conform textului
        
        st.write(f"HCO3 așteptat dacă Acut: {exp_hco3_acute:.1f}")
        st.write(f"HCO3 așteptat dacă Cronic: ~{exp_hco3_chronic:.1f}")
        
        if hco3 > exp_hco3_acute + 2:
             st.warning("HCO3 mai mare decât așteptat -> Acidoză Metabolică suprapusă?")
        elif hco3 < exp_hco3_chronic - 2:
             st.warning("HCO3 mai mic decât așteptat -> Alcaloză Metabolică suprapusă?")

    # STEP 5: Anion Gap
    st.markdown("### Pasul 5: Calcul Anion Gap (AG)")
    
    # AG = Na - (Cl + HCO3)
    ag = na - (cl + hco3)
    
    # Ajustare pentru Albumină
    # Textul spune: Normal AG scade cu 2.5 pentru fiecare 1g/dL albumină sub 4.0
    # Normal AG e considerat 12.
    # Dacă albumina e 4.0, expected AG = 12.
    # Dacă albumina e 2.0, expected AG = 12 - (2.5 * 2) = 7.
    
    albumin_diff = 4.0 - albumin
    expected_ag = 12.0
    if albumin_diff > 0:
        expected_ag = 12.0 - (2.5 * albumin_diff)
    
    st.write(f"Anion Gap Calculat: **{ag:.1f} mEq/L**")
    st.write(f"Anion Gap Normal Așteptat (ajustat pt albumină {albumin}): **{expected_ag:.1f} mEq/L**")
    
    high_ag_met_acidosis = False
    
    if ag > (expected_ag + 2): # Folosim o marjă de +/- 2
        st.error("⚠️ **Anion Gap Crescut (High AG)** -> Acidoză Metabolică cu AG Crescut prezentă.")
        high_ag_met_acidosis = True
        st.markdown("""
        *Cauze posibile (MUDPILES):* Metanol, Uremie, DKA, Paraldehidă, Isoniazidă/Iron, Lactat, Etilen Glicol, Salicilați.
        """)
    else:
        st.success("Anion Gap Normal.")
        if "Acidoză Metabolică" in primary_disorder:
            st.info("Acesta sugerează o Acidoză Metabolică cu AG Normal (Hyperchloremic). Cauze: Diaree, RTA, etc.")

    # STEP 6: Delta Gap
    if high_ag_met_acidosis:
        st.markdown("### Pasul 6: Delta Gap (Raportul ΔAG / ΔHCO3)")
        
        delta_ag = ag - 12 # Presupunând 12 ca baseline standard
        delta_hco3 = 24 - hco3
        
        if delta_hco3 == 0:
            ratio = 0 # Evită împărțirea la zero
        else:
            ratio = delta_ag / delta_hco3
            
        st.write(f"ΔAG ({delta_ag:.1f}) / ΔHCO3 ({delta_hco3:.1f}) = **{ratio:.2f}**")
        
        if ratio < 1.0:
            st.warning("Raport < 1.0: Sugerează **Acidoză Metabolică Non-AG Concomitentă** (AG Normal).")
        elif 1.0 <= ratio <= 2.0:
            st.success("Raport 1.0 - 2.0: **Acidoză Metabolică cu AG Crescut Pură** (Fără alte tulburări metabolice).")
        elif ratio > 2.0:
            st.warning("Raport > 2.0: Sugerează **Alcaloză Metabolică Concomitentă** (sau BPOC cronic compensat).")

    st.markdown("---")
    st.caption("Disclaimer: Această aplicație este un instrument educațional bazat pe ghidul ATS. Nu înlocuiește judecata clinică profesională.")

if st.button("Interpretează Rezultatele", type="primary"):
    interpret_abg()
else:
    st.write("Introduceți valorile în bara laterală și apăsați butonul de mai sus.")
