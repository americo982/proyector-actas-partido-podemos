import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Proyector de Actas Electorales", layout="wide")

st.title("🗳️ Sistema de Registro y Proyección de Actas Electorales")
st.markdown("Sube la imagen de cada acta para extraer y acumular automáticamente los votos en la base de datos central.")

# Archivo CSV que actuará como base de datos en la nube
DB_FILE = "base_datos_actas.csv"

# Carga de la imagen del acta
uploaded_file = st.file_uploader("Subir imagen de Acta de Sufragio (.jpg, .png)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Acta cargada", width=400)
    
    st.success("¡Imagen recibida! Verifique los datos extraídos:")
    
    # Formulario de registro de datos del acta
    with st.form(key="acta_form"):
        st.subheader("Datos Extraídos del Acta")
        mesa = st.text_input("N° de Mesa", value="000000")
        
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.number_input("AMANECER DE NUEVO", value=32)
            p2 = st.number_input("AMOR", value=32)
            p3 = st.number_input("GOTAS DE LLUVIA", value=32)
            p4 = st.number_input("LA MAGIA DEL ENCUENTRO", value=32)
        with col2:
            p5 = st.number_input("CUIDEMOS EL PLANETA", value=32)
            p6 = st.number_input("LOS CAMPEONES", value=32)
            p7 = st.number_input("ORDENANDO LA CASA", value=32)
            p8 = st.number_input("COLECCIONISTA DE OBJETOS", value=32)
            
        st.markdown("---")
        b_blanco = st.number_input("Votos en Blanco", value=15)
        b_nulo = st.number_input("Votos Nulos", value=9)
        b_impugnado = st.number_input("Votos Impugnados", value=0)
        total_emitidos = st.number_input("Total de Votos Emitidos", value=280)
        
        submit_button = st.form_submit_button(label="💾 Guardar Acta en la Base de Datos")
        
        if submit_button:
            nuevo_registro = {
                "Mesa": mesa,
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
            
            # Guardar o acumular en el archivo CSV
            if os.path.exists(DB_FILE):
                df_existente = pd.read_csv(DB_FILE)
                df_nuevo = pd.concat([df_existente, pd.DataFrame([nuevo_registro])], ignore_index=True)
            else:
                df_nuevo = pd.DataFrame([nuevo_registro])
                
            df_nuevo.to_csv(DB_FILE, index=False)
            st.balloons()
            st.success(f"¡Mesa N° {mesa} registrada con éxito! Total de actas en sistema: {len(df_nuevo)}")

st.markdown("---")
st.subheader("📊 Consolidado General y Proyecciones")

if os.path.exists(DB_FILE):
    df_db = pd.read_csv(DB_FILE)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(label="Actas Procesadas", value=len(df_db))
    with col_b:
        st.metric(label="Total Votos Emitidos Acumulados", value=int(df_db["TOTAL EMITIDOS"].sum()))
        
    with st.expander("Ver tabla completa de actas registradas"):
        st.dataframe(df_db)
        
        # Botón para descargar la base de datos en Excel/CSV
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
    st.info("ℹ️ Aún no hay actas registradas. Sube la primera acta arriba para comenzar la base de datos.")
