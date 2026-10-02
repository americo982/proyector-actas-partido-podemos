import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Proyector de Actas Electorales", layout="wide")

st.title("🗳️ Sistema de Registro y Proyección de Actas Electorales")
st.markdown("Sube tu acta de sufragio para visualizarla y registra los votos con rapidez.")

DB_FILE = "base_datos_actas.csv"

# Carga de la imagen del acta
uploaded_file = st.file_uploader("Subir imagen de Acta de Sufragio (.jpg, .png)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Acta cargada correctamente", width=450)
    
    st.info("💡 **Consejo rápido:** Visualiza los números en la imagen de arriba y confirma o ajusta los valores en el formulario de abajo para guardarlos al instante.")
    
    with st.form(key="acta_form_eficiente"):
        st.subheader("📝 Registro de Datos del Acta")
        
        col_mesa, col_tipo = st.columns(2)
        with col_mesa:
            mesa = st.text_input("N° de Mesa de Votación", value="000101")
        with col_tipo:
            tipo_acta = st.selectbox("Tipo de Elección", ["Regional / Municipal", "Presidencial", "Congresal"])
        
        st.markdown("---")
        st.markdown("**Votos por Organización Política:**")
        
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.number_input("1. AMANECER DE NUEVO", min_value=0, value=20, step=1)
            p2 = st.number_input("2. AMOR", min_value=0, value=58, step=1)
            p3 = st.number_input("3. GOTAS DE LLUVIA", min_value=0, value=42, step=1)
            p4 = st.number_input("4. LA MAGIA DEL ENCUENTRO", min_value=0, value=35, step=1)
        with col2:
            p5 = st.number_input("5. CUIDEMOS EL PLANETA", min_value=0, value=48, step=1)
            p6 = st.number_input("6. LOS CAMPEONES", min_value=0, value=30, step=1)
            p7 = st.number_input("7. ORDENANDO LA CASA", min_value=0, value=25, step=1)
            p8 = st.number_input("8. COLECCIONISTA DE OBJETOS", min_value=0, value=15, step=1)
            
        st.markdown("---")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            b_blanco = st.number_input("Votos en Blanco", min_value=0, value=8, step=1)
        with col_b2:
            b_nulo = st.number_input("Votos Nulos", min_value=0, value=2, step=1)
        with col_b3:
            total_emitidos = st.number_input("Total Votos Emitidos", min_value=0, value=280, step=1)
        
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
                "TOTAL EMITIDOS": total_emitidos
            }
            
            if os.path.exists(DB_FILE):
                df_existente = pd.read_csv(DB_FILE)
                df_nuevo = pd.concat([df_existente, pd.DataFrame([nuevo_registro])], ignore_index=True)
            else:
                df_nuevo = pd.DataFrame([nuevo_registro])
                
            df_nuevo.to_csv(DB_FILE, index=False)
            st.balloons()
            st.success(f"¡Mesa N° {mesa} registrada con éxito! Total de actas acumuladas: {len(df_nuevo)}")

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
    st.info("ℹ️ Aún no hay actas registradas. Sube la primera acta arriba para comenzar.")
