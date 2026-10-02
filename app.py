import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google import genai
import json
import time

st.set_page_config(page_title="Proyector de Actas Electorales", layout="wide")

# Estilos CSS personalizados para la interfaz electoral
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #ffcc00;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #e6b800;
        color: #000000;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗳️ Sistema de Registro y Proyección Inteligente de Actas Electorales")
st.markdown("---")

DB_FILE = "base_datos_actas.csv"

# Inicializar cliente de Gemini de forma segura
try:
    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    client = genai.Client(api_key=api_key) if api_key else None
except Exception:
    client = None

# Carga de la imagen del acta
uploaded_file = st.file_uploader("Subir imagen de Acta de Sufragio (.jpg, .png)", type=["jpg", "jpeg", "png"])

# Valores por defecto en cero
default_vals = {
    "mesa": "",
    "p1": 0, "p2": 0, "p3": 0, "p4": 0,
    "p5": 0, "p6": 0, "p7": 0, "p8": 0,
    "blancos": 0, "nulos": 0, "impugnados": 0, "total": 0
}

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Acta cargada correctamente", width=450)
    
    # Botón manual para procesar con IA
    if client:
        if st.button("🤖 Procesar / Leer Acta con Inteligencia Artificial"):
            with st.spinner("Analizando acta, por favor espera un momento..."):
                extracted = None
                modelos_a_probar = ['gemini-1.5-flash', 'gemini-flash-latest']
                prompt = """
                Analiza esta acta electoral de sufragio y extrae estrictamente en formato JSON los siguientes campos numéricos y de texto:
                - mesa (número de mesa, ej: "000101")
                - p1 (votos para AMANECER DE NUEVO)
                - p2 (votos para AMOR)
                - p3 (votos para GOTAS DE LLUVIA)
                - p4 (votos para LA MAGIA DEL ENCUENTRO)
                - p5 (votos para CUIDEMOS EL PLANETA)
                - p6 (votos para LOS CAMPEONES)
                - p7 (votos para ORDENANDO LA CASA)
                - p8 (votos para COLECCIONISTA DE OBJETOS)
                - blancos (votos en blanco)
                - nulos (votos nulos)
                - impugnados (votos impugnados)
                - total (total votos emitidos)
                Devuelve únicamente el objeto JSON válido sin bloques markdown ni texto adicional.
                """
                
                for modelo in modelos_a_probar:
                    try:
                        response = client.models.generate_content(
                            model=modelo,
                            contents=[image, prompt]
                        )
                        text_res = response.text.strip().replace("```json", "").replace("```", "")
                        extracted = json.loads(text_res)
                        break
                    except Exception as e:
                        time.sleep(1)
                        continue
                
                if extracted:
                    st.session_state["parsed_data"] = extracted
                    st.success("¡Datos extraídos con éxito por la IA!")
                    st.rerun()
                else:
                    st.warning("No se pudo conectar con la IA. Los campos están listos para ingreso manual.")

    data = st.session_state.get("parsed_data", default_vals)

    with st.form(key="acta_form_inteligente"):
        st.subheader("📝 Verificación y Registro de Datos del Acta")
        
        col_mesa, col_tipo = st.columns(2)
        with col_mesa:
            mesa = st.text_input("N° de Mesa de Votación", value=str(data.get("mesa", "")))
        with col_tipo:
            tipo_acta = st.selectbox("Tipo de Elección", ["Regional / Municipal", "Presidencial", "Congresal"])
        
        st.markdown("---")
        st.markdown("**Votos por Organización Política:**")
        
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.number_input("1. AMANECER DE NUEVO", min_value=0, value=int(data.get("p1", 0)), step=1)
            p2 = st.number_input("2. AMOR", min_value=0, value=int(data.get("p2", 0)), step=1)
            p3 = st.number_input("3. GOTAS DE LLUVIA", min_value=0, value=int(data.get("p3", 0)), step=1)
            p4 = st.number_input("4. LA MAGIA DEL ENCUENTRO", min_value=0, value=int(data.get("p4", 0)), step=1)
        with col2:
            p5 = st.number_input("5. CUIDEMOS EL PLANETA", min_value=0, value=int(data.get("p5", 0)), step=1)
            p6 = st.number_input("6. LOS CAMPEONES", min_value=0, value=int(data.get("p6", 0)), step=1)
            p7 = st.number_input("7. ORDENANDO LA CASA", min_value=0, value=int(data.get("p7", 0)), step=1)
            p8 = st.number_input("8. COLECCIONISTA DE OBJETOS", min_value=0, value=int(data.get("p8", 0)), step=1)
            
        st.markdown("---")
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        with col_b1:
            b_blanco = st.number_input("Votos en Blanco", min_value=0, value=int(data.get("blancos", 0)), step=1)
        with col_b2:
            b_nulo = st.number_input("Votos Nulos", min_value=0, value=int(data.get("nulos", 0)), step=1)
        with col_b3:
            b_impugnado = st.number_input("Votos Impugnados", min_value=0, value=int(data.get("impugnados", 0)), step=1)
        with col_b4:
            total_emitidos = st.number_input("Total Votos Emitidos", min_value=0, value=int(data.get("total", 0)), step=1)
        
        submit_button = st.form_submit_button(label="💾 Guardar y Consolidar Acta")
        
        if submit_button:
            nuevo_registro = {
                "Mesa": mesa,
                "Tipo": tipo_acta,
                "Fecha_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "AMANECER DE NUEVO": p1,
                "AMOR": p2,
                "GOTAS DE LLUVIA": p3,
                "LA MAGIA DEL ENCUENTRO": p4,
                "CUIDEMOS EL PLANETA": p5,
                "LOS CAMPEONES": p6,
                "ORDENANDO LA CASA": p7,
                "COLECCIONISTA DE OBJETOS": p8,
                "VOTOS EN BLANCO": b_blanco,
                "VOTOS NULOS": b_nulo,
                "VOTOS IMPUGNADOS": b_impugnado,
                "TOTAL EMITIDOS": total_emitidos
            }
            
            if os.path.exists(DB_FILE):
                df_existente = pd.read_csv(DB_FILE)
                df_nuevo = pd.concat([df_existente, pd.DataFrame([nuevo_registro])], ignore_index=True)
            else:
                df_nuevo = pd.DataFrame([nuevo_registro])
                
            df_nuevo.to_csv(DB_FILE, index=False)
            
            if "parsed_data" in st.session_state:
                del st.session_state["parsed_data"]
            if "last_file" in st.session_state:
                del st.session_state["last_file"]
                
            st.success(f"¡Mesa N° {mesa} registrada con éxito!")
            time.sleep(1)
            st.rerun()

# --- SECCIÓN DE CONSOLIDADO Y GRÁFICOS ---
st.markdown("---")
st.subheader("📊 Consolidado General y Proyecciones")

if os.path.exists(DB_FILE):
    df_db = pd.read_csv(DB_FILE)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric(label="Actas Procesadas", value=len(df_db))
    with col_b:
        st.metric(label="Total Votos Emitidos Acumulados", value=int(df_db["TOTAL EMITIDOS"].sum()))
    with col_c:
        if st.button("🗑️ Reiniciar / Borrar Base de Datos"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
                st.rerun()
        
    with st.expander("Ver tabla completa de actas registradas"):
        st.dataframe(df_db)
        st.download_button(
            label="📥 Descargar Base de Datos Completa (CSV)",
            data=df_db.to_csv(index=False).encode('utf-8'),
            file_name="base_datos_actas_consolidado.csv",
            mime="text/csv",
        )
    
    st.subheader("🎯 Gráfico de Votos Acumulados por Partido")
    columnas_partidos = [
        "AMANECER DE NUEVO", "AMOR", "GOTAS DE LLUVIA", 
        "LA MAGIA DEL ENCUENTRO", "CUIDEMOS EL PLANETA", 
        "LOS CAMPEONES", "ORDENANDO LA CASA", "COLECCIONISTA DE OBJETOS"
    ]
    totales_partidos = df_db[columnas_partidos].sum().reset_index()
    totales_partidos.columns = ["Organización Política", "Total Acumulado"]
    st.bar_chart(totales_partidos.set_index("Organización Política"))
else:
    st.info("ℹ Aún no hay actas registradas. Sube la primera acta arriba para comenzar.")
