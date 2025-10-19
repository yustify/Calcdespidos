import streamlit as st
from datetime import date, datetime
from dateutil.relativedelta import relativedelta # Necesita instalarse: pip install python-dateutil

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Calculadora de Despido", page_icon="⚖️", layout="centered")

# --- ESTILO CSS MODIFICADO ---
st.markdown("""
<style>
    h1 { 
        text-align: center; 
        /* Eliminamos color fijo para que se adapte al tema */
    } 
    .stButton > button { 
        /* Mantenemos el estilo del botón, suele funcionar bien en ambos temas */
        background-color: #B22222; 
        color: white; 
        border-radius: 5px; 
    }
    .stDateInput > label, 
    .stNumberInput > label, 
    .stRadio > label { 
        font-weight: bold; 
        /* Eliminamos color fijo */
    }
    .result-box { 
        /* Eliminamos fondo fijo */
        border: 1px solid #dcdcdc; 
        border-radius: 5px; 
        padding: 1em; 
        margin-top: 1em; 
    }
    .result-box h3 { 
        /* Eliminamos color fijo */
    }
    .result-box strong { 
        font-size: 1.2em; 
        /* Eliminamos color fijo, el tema pondrá uno que contraste */
    }
</style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
st.title("⚖️ Calculadora Simplificada de Despido (España)")
st.warning("IMPORTANTE: Esta es una estimación simplificada y no reemplaza el cálculo profesional.")

# --- ENTRADA DE DATOS ---
st.subheader("Datos del Trabajador y Contrato:")
col1, col2 = st.columns(2)
with col1:
    fecha_alta = st.date_input("Fecha de Alta", value=date(date.today().year - 1, date.today().month, date.today().day))
    salario_bruto_anual = st.number_input("Salario Bruto Anual (€)", min_value=0.0, step=100.0, value=20000.0)
    tipo_despido = st.radio("Tipo de Despido", ["Improcedente", "Objetivo", "Disciplinario (Sin Indemnización)"])

with col2:
    fecha_baja = st.date_input("Fecha de Baja", value=date.today())
    pagas_extra = st.radio("Pagas Extra", ["12 (Prorrateadas)", "14"])
    
st.subheader("Datos para el Finiquito:")
col_fin1, col_fin2 = st.columns(2)
with col_fin1:
     dias_vacaciones_pendientes = st.number_input("Días de Vacaciones Pendientes", min_value=0, step=1, value=0)
with col_fin2:
    preaviso_incumplido_dias = st.number_input("Días de Preaviso Incumplido (si aplica)", min_value=0, step=1, value=0) 

# --- BOTÓN DE CÁLCULO ---
st.markdown("---")
if st.button("Calcular Estimación"):
    if fecha_alta and fecha_baja and salario_bruto_anual >= 0:
        if fecha_baja < fecha_alta:
            st.error("Error: La fecha de baja no puede ser anterior a la fecha de alta.")
        else:
            # --- CÁLCULOS (sin cambios en la lógica) ---
            antiguedad = relativedelta(fecha_baja, fecha_alta)
            anios_completos = antiguedad.years
            meses_completos = antiguedad.months + (1 if antiguedad.days > 0 else 0) 
            antiguedad_total_meses = anios_completos * 12 + meses_completos
            antiguedad_anios_calculo = antiguedad_total_meses / 12.0 

            salario_diario = salario_bruto_anual / 365.0

            indemnizacion = 0.0
            if tipo_despido == "Improcedente":
                dias_indemnizacion = 33
                indemnizacion = salario_diario * dias_indemnizacion * antiguedad_anios_calculo
                salario_mensual_aprox = salario_bruto_anual / 12.0
                tope_indemnizacion = 24 * salario_mensual_aprox
                indemnizacion = min(indemnizacion, tope_indemnizacion)

            elif tipo_despido == "Objetivo":
                dias_indemnizacion = 20
                indemnizacion = salario_diario * dias_indemnizacion * antiguedad_anios_calculo
                salario_mensual_aprox = salario_bruto_anual / 12.0
                tope_indemnizacion = 12 * salario_mensual_aprox
                indemnizacion = min(indemnizacion, tope_indemnizacion)
            
            dias_trabajados_ultimo_mes = fecha_baja.day
            salario_ultimo_mes = salario_diario * dias_trabajados_ultimo_mes

            paga_extra_proporcional = 0.0
            if pagas_extra == "14":
                if fecha_baja.month <= 6:
                     dias_devengo_verano = (fecha_baja - date(fecha_baja.year, 1, 1)).days + 1
                     paga_extra_proporcional += (salario_bruto_anual / 14.0 / 180.0) * dias_devengo_verano 
                else: 
                      paga_extra_proporcional += (salario_bruto_anual / 14.0)
                if fecha_baja.month > 6:
                    dias_devengo_navidad = (fecha_baja - date(fecha_baja.year, 7, 1)).days + 1
                    paga_extra_proporcional += (salario_bruto_anual / 14.0 / 180.0) * dias_devengo_navidad

            valor_vacaciones = salario_diario * dias_vacaciones_pendientes
            descuento_preaviso = salario_diario * preaviso_incumplido_dias
            finiquito_bruto = salario_ultimo_mes + paga_extra_proporcional + valor_vacaciones - descuento_preaviso

            # --- MOSTRAR RESULTADOS (HTML modificado para quitar estilos inline) ---
            st.markdown("---")
            st.subheader("Estimación del Cálculo:")

            st.markdown(f"""
            <div class="result-box">
                <h3>Antigüedad Calculada:</h3>
                <strong>{anios_completos} años y {meses_completos} meses</strong> ({antiguedad_anios_calculo:.2f} años para cálculo)
            </div> """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="result-box">
                <h3>Indemnización ({tipo_despido}):</h3>
                Estimación Bruta: <strong>{indemnizacion:,.2f} €</strong>
                <br><small>(Este importe puede estar exento de IRPF hasta cierto límite legal)</small>
            </div> """, unsafe_allow_html=True)

            st.markdown(f"""
             <div class="result-box">
                <h3>Finiquito (Liquidación):</h3>
                - Salario días trabajados ({dias_trabajados_ultimo_mes} días): {salario_ultimo_mes:,.2f} €<br>
                - Parte Proporcional Pagas Extra: {paga_extra_proporcional:,.2f} €<br>
                - Vacaciones no disfrutadas ({dias_vacaciones_pendientes} días): {valor_vacaciones:,.2f} €<br>
                - Descuento Preaviso Incumplido ({preaviso_incumplido_dias} días): {-descuento_preaviso:,.2f} €<br>
                <strong>Estimación Finiquito Bruto: {finiquito_bruto:,.2f} €</strong>
                <br><small>(A este importe se le aplicarán las retenciones de IRPF y Seguridad Social)</small>
            </div> """, unsafe_allow_html=True)

            # Quitamos el estilo inline del último cuadro
            st.markdown(f"""
             <div class="result-box"> 
                <h3>Total Estimado a Recibir (Bruto):</h3>
                Indemnización + Finiquito = <strong>{(indemnizacion + finiquito_bruto):,.2f} €</strong>
                <br><small>(Recuerda: Finiquito sujeto a IRPF/SS, Indemnización exenta hasta límite)</small>
            </div> """, unsafe_allow_html=True)
    else:
        st.warning("Por favor, rellena todas las fechas y el salario.")

