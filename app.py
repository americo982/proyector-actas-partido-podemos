import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import numpy as np
import easyocr
import re

st.set_page_config(page_title="Proyector de Actas con Lectura Automática IA", layout="wide")

st.title("🤖 Sistema Inteligente de Lectura y Proyección de Actas Electorales")
st.markdown("Sube la imagen del acta. El sistema leerá automáticamente los votos para ahorrarte tiempo y evitar errores.")

DB_FILE = "base_datos_actas.csv"

# Inicializar el lector de OCR de forma cacheada para que cargue rápido
@st.cache_resource
def cargar_lector_ocr():
    # Carga el modelo en español e inglés
    return easyocr.Reader(['es', 'en'], gpu=False)

with st.spinner("Cargando modelo de Inteligencia Artificial para lectura..."):
    reader = cargar_lector_ocr()

# Carga de la imagen del acta
uploaded_file = st.file_uploader("Subir imagen de Acta de Sufragio (.jpg, .png)", type=["jpg", "jpeg", "png"])

datos_detectados = {}

if uploaded_file is not None:
    imagen_pil = Image.open(uploaded_file)
    st.image(imagen_pil, caption="Acta cargada", width=400)
    
    with st.spinner("🔍 Leyendo automáticamente los datos del acta..."):
        # Convertir imagen PIL a arreglo de Numpy para EasyOCR
        imagen_np = np.array(imagen_pil)
        
        # Ejecutar OCR
        resultados_ocr = reader.readtext(imagen_np)
        
        # Unir todo el texto detectado o analizar bloques
        texto_completo = " ".join([res[1] for res in resultados_ocr])
        
        # Función auxiliar para buscar números cerca de palabras clave o dentro del texto
        def buscar_valor_partido(palabras_clave):
            # Recorrer los resultados para encontrar coincidencias cercanas
            for i, (bbox, text, prob) in enumerate(resultados_ocr):
                if any(pc.upper() in text.upper() for pc in palabras_clave):
                    # Buscar un número en el mismo renglón o en el bloque contiguo a la derecha
                    # Revisamos los elementos siguientes en la lista de OCR
                    for j in range(i + 1, min(i + 4, len(resultados_ocr))):
                        s_bbox, s_text, s_prob = resultados_ocr[j]
                        # Limpiar texto para ver si es un número válido
                        s_limpio = re.sub(r'[^0-9]', '', s_text)
                        if s_limpio.isdigit() and len(s_limpio) <= 3:
                            return int(s_limpio)
            return 0

        # Mapeo de partidos y sus palabras clave en el acta
        p1_val = buscar_valor_partido(["AMANECER", "NUEVO"])
        p2_val = buscar_valor_partido(["AMOR"])
        p3_val = buscar_valor_partido(["GOTAS", "LLUVIA"])
        p4_val = buscar_valor_partido(["MAGIA", "ENCUENTRO"])
        p5_val = buscar_valor_partido(["CUIDEMOS", "PLANETA"])
        p6_val = buscar_valor_partido(["CAMPEONES"])
        p7_val = buscar_valor_partido(["ORDENANDO", "CASA"])
        p8_val = buscar_valor_partido(["COLECCIONISTA", "OBJETOS"])
        
        b_blanco = buscar_valor_partido(["BLANCO"])
        b_nulo = buscar_valor_partido(["NULO"])
        total_val = buscar_valor_partido(["TOTAL", "EMITIDOS"])

        # Intentar capturar número de mesa
        mesa_val = "000101"
        for bbox, text, prob in resultados_ocr:
            match_mesa = re.search(r'\b(000\d{3}|\d{6})\b', text)
            if match_mesa:
                mesa_val = match_mesa.group(1)
                break

    st.success("¡Lectura automática finalizada! Revisa los campos detectados:")

    with st.form(key="acta_form_auto"):
        st.subheader("Datos Extraídos por la IA (Modificables si deseas corregir)")
        mesa = st.text_input("N° de Mesa", value=mesa_val)
        
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.number_input("AMANECER DE NUEVO", min_value=0, value=p1_val, step=1)
            p2 = st.number_input("AMOR", min_value=0, value=p2_val, step=1)
            p3 = st.number_input("GOTAS DE LLUVIA", min_value=0, value=p3_val, step=1)
            p4 = st.number_input("LA MAGIA DEL ENCUENTRO", min_value=0, value=p4_val, step=1)
        with col2:
            p5 = st.number_input("CUIDEMOS EL PLANETA", min_value=0, value=p5_val, step=1)
            p6 = st.number_input("LOS CAMPEONES", min_value=0, value=p6_val, step=1)
            p7 = st.number_input("ORDENANDO LA CASA", min_value=0, value=p7_val, step=1)
            p8 = st.number_input("COLECCIONISTA DE OBJETOS", min_value=0, value=p8_val, step=1)
            
        st.markdown("---")
        b_blanco_input = st.number_input("Votos en Blanco", min_value=0, value=b_blanco, step=1)
        b_nulo_input = st.number_input("Votos Nulos", min_value=0, value=b_nulo, step=1)
        total_emitidos = st.number_input("Total de Votos Emitidos", min_value=0, value=total_val if total_val > 0 else 280, step=1)
        
        submit_button = st.form_submit_button(label="💾 Confirmar y Guardar en la Base de Datos")
        
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
                "VOTOS EN BLANCO": b_blanco_input,
                "VOTOS NULOS": b_nulo_input,
                "TOTAL EMITIDOS": total_emitidos
            }
            
            if os.path.exists(DB_FILE):
                df_existente = pd.read_csv(DB_FILE)
                df_nuevo = pd.concat([df_existente, pd.DataFrame([nuevo_registro])], ignore_index=True)
            else:
                df_nuevo = pd.DataFrame([nuevo_registro])
                
            df_nuevo.to_csv(DB_FILE, index=False)
            st.balloons()
            st.success(f"¡Mesa N° {mesa} registrada con éxito! Total de actas en el sistema: {len(df_nuevo)}")

# --- SECCIÓN DE CONSOLIDADO Y GRÁFICOS ---
st.markdown("---")
st.subheader("📊 Consolidado General y Proyecciones")

if os.path.exists(DB_FILE):
    df_db = pd.read_csv(DB_FILE)
    
    if st.button("🗑️ Reiniciar / Borrar Base de Datos Actual"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.rerun()

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(label="Actas Procesadas", value=len(df_db))
    with col_b:
        st.metric(label="Total Votos Emitidos Acumulados", value=int(df_db["TOTAL EMITIDOS"].sum()))
        
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
