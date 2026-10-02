import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import pytesseract
import re

# Configurar la ruta de tesseract (necesario para que funcione en Streamlit Cloud)
# Esto busca la instalación definida en packages.txt
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

st.set_page_config(page_title="Proyector de Actas Electorales IA", layout="wide")

st.title("🤖 Sistema de Registro y Proyección de Actas Electorales con IA")
st.markdown("Sube la imagen de cada acta. El sistema intentará leer los datos automáticamente y te permitirá verificarlos.")

DB_FILE = "base_datos_actas.csv"

# --- FUNCION DE OCR SIMPLIFICADA ---
def extraer_datos_acta(imagen_pil):
    """
    Toma una imagen PIL y usa pytesseract para extraer texto y buscar números clave.
    """
    try:
        # Preprocesamiento para mejorar el OCR (convertir a escala de grises y binarizar)
        imagen_gris = imagen_pil.convert('L')
        # Se puede ajustar el umbral (threshold) si es necesario
        imagen_binaria = imagen_gris.point(lambda x: 0 if x < 140 else 255, '1')
        
        # Extraer texto
        texto_extraido = pytesseract.image_to_string(imagen_binaria, lang='spa')
        
        # Mapeo de nombres de partidos en la imagen a claves de la base de datos
        # Ajustar los patrones de búsqueda según el texto exacto que detecte Tesseract en tus actas
        mapeo_claves = {
            "AMANECER DE NUEVO": ["AMANECER", "DE NUEVO"],
            "AMOR": ["AMOR"],
            "GOTAS DE LLUVIA": ["GOTAS", "LLUVIA"],
            "LA MAGIA DEL ENCUENTRO": ["MAGIA", "ENCUENTRO"],
            "CUIDEMOS EL PLANETA": ["CUIDEMOS", "PLANETA"],
            "LOS CAMPEONES": ["CAMPEONES"],
            "ORDENANDO LA CASA": ["ORDENANDO", "CASA"],
            "COLECCIONISTA DE OBJETOS": ["COLECCIONISTA", "OBJETOS"],
            "VOTOS EN BLANCO": ["VOTOS EN BLANCO", "BLANCO"],
            "VOTOS NULOS": ["VOTOS NULOS", "NULOS"],
            "TOTAL VOTOS EMITIDOS": ["TOTAL VOTOS EMITIDOS", "TOTAL", "VOTOS EMITIDOS"]
        }

        datos_detectados = {}
        lineas_texto = texto_extraido.split('\n')

        # Intentar buscar el N° de Mesa (usualmente en la parte superior)
        mesa = "No detectado"
        for linea in lineas_texto[:15]: # Buscar solo en el encabezado
             match_mesa = re.search(r'\b(000\d{3}|MESA\s*N[°º°]\s*(\d{6}))\b', linea, re.IGNORECASE)
             if match_mesa:
                 mesa = match_mesa.group(0).replace("MESA N° ", "").replace("MESA N°", "")
                 break

        datos_detectados["Mesa"] = mesa.strip()

        # Buscar votos para cada partido
        for clave_db, palabras_clave in mapeo_claves.items():
            valor_encontrado = 0
            for linea in lineas_texto:
                # Verificar si la línea contiene las palabras clave del partido
                if all(palabra.upper() in linea.upper() for palabra in palabras_clave):
                    # Buscar un número al final de la línea o cerca del final
                    match_numero = re.search(r'(\d+)\s*$', linea)
                    if match_numero:
                        try:
                            valor_encontrado = int(match_numero.group(1))
                            break # Asignar el primer número encontrado que coincida con la descripción
                        except ValueError:
                            pass
            datos_detectados[clave_db] = valor_encontrado
            
        return datos_detectados

    except Exception as e:
        st.error(f"Error durante el proceso de OCR: {e}")
        return None

# --- INTERFAZ DE USUARIO ---
uploaded_file = st.file_uploader("Subir imagen de Acta de Sufragio (.jpg, .png)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Acta cargada para análisis", width=400)
    
    with st.spinner("🧠 La IA está analizando la imagen... esto puede tomar unos segundos."):
        imagen_pil = Image.open(uploaded_file)
        datos_leidos = extraer_datos_acta(imagen_pil)

    if datos_leidos:
        st.success(f"¡Lectura automática completada! Verifique los datos para la Mesa N° **{datos_leidos.get('Mesa', 'No detectado')}** y luego guarde.")
        
        # Formulario con valores precargados por el OCR
        with st.form(key="acta_form_ia"):
            st.subheader("Datos del Acta (Verifique y corrija si es necesario)")
            mesa = st.text_input("N° de Mesa", value=datos_leidos.get("Mesa", "000101"))
            
            col1, col2 = st.columns(2)
            with col1:
                p1 = st.number_input("AMANECER DE NUEVO", min_value=0, value=datos_leidos.get("AMANECER DE NUEVO", 32), step=1)
                p2 = st.number_input("AMOR", min_value=0, value=datos_leidos.get("AMOR", 32), step=1)
                p3 = st.number_input("GOTAS DE LLUVIA", min_value=0, value=datos_leidos.get("GOTAS DE LLUVIA", 32), step=1)
                p4 = st.number_input("LA MAGIA DEL ENCUENTRO", min_value=0, value=datos_leidos.get("LA MAGIA DEL ENCUENTRO", 32), step=1)
            with col2:
                p5 = st.number_input("CUIDEMOS EL PLANETA", min_value=0, value=datos_leidos.get("CUIDEMOS EL PLANETA", 32), step=1)
                p6 = st.number_input("LOS CAMPEONES", min_value=0, value=datos_leidos.get("LOS CAMPEONES", 32), step=1)
                p7 = st.number_input("ORDENANDO LA CASA", min_value=0, value=datos_leidos.get("ORDENANDO LA CASA", 32), step=1)
                p8 = st.number_input("COLECCIONISTA DE OBJETOS", min_value=0, value=datos_leidos.get("COLECCIONISTA DE OBJETOS", 32), step=1)
                
            st.markdown("---")
            b_blanco = st.number_input("Votos en Blanco", min_value=0, value=datos_leidos.get("VOTOS EN BLANCO", 15), step=1)
            b_nulo = st.number_input("Votos Nulos", min_value=0, value=datos_leidos.get("VOTOS NULOS", 9), step=1)
            total_emitidos = st.number_input("Total de Votos Emitidos", min_value=0, value=datos_leidos.get("TOTAL VOTOS EMITIDOS", 280), step=1)
            
            submit_button = st.form_submit_button(label="💾 Guardar Acta Verificada")
            
            if submit_button:
                nuevo_registro = {
                    "Mesa": mesa,
                    "Fecha_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "AMANECER DE NUEVO": p1, "AMOR": p2, "GOTAS DE LLUVIA": p3,
                    "LA MAGIA DEL ENCUENTRO": p4, "CUIDEMOS EL PLANETA": p5,
                    "LOS CAMPEONES": p6, "ORDENANDO LA CASA": p7,
                    "COLECCIONISTA DE OBJETOS": p8, "VOTOS EN BLANCO": b_blanco,
                    "VOTOS NULOS": b_nulo, "TOTAL EMITIDOS": total_emitidos
                }
                
                if os.path.exists(DB_FILE):
                    df_existente = pd.read_csv(DB_FILE)
                    df_nuevo = pd.concat([df_existente, pd.DataFrame([nuevo_registro])], ignore_index=True)
                else:
                    df_nuevo = pd.DataFrame([nuevo_registro])
                    
                df_nuevo.to_csv(DB_FILE, index=False)
                st.balloons()
                st.success(f"¡Mesa N° {mesa} registrada! Total de actas en sistema: {len(df_nuevo)}")
    else:
        st.error("El sistema no pudo extraer datos automáticamente de esta imagen. Por favor, ingréselos manualmente abajo.")

# --- SECCION DE CONSOLIDADO ---
st.markdown("---")
st.subheader("📊 Consolidado General y Proyecciones")

if os.path.exists(DB_FILE):
    df_db = pd.read_csv(DB_FILE)
    
    if st.button("🗑️ Reiniciar / Borrar Base de Datos Actual"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.experimental_rerun()

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(label="Actas Procesadas", value=len(df_db))
    with col_b:
        st.metric(label="Total Votos Emitidos Acumulados", value=int(df_db["TOTAL EMITIDOS"].sum()))
        
    with st.expander("Ver tabla completa de actas registradas"):
        st.dataframe(df_db)
        st.download_button("📥 Descargar Base de Datos", df_db.to_csv(index=False), "base_datos_consolidado.csv", "text/csv")
    
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
    st.info("Aún no hay actas registradas. Sube la primera acta arriba para comenzar.")
