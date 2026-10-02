# Extracción automática con IA
    if client and ("parsed_data" not in st.session_state or st.session_state.get("last_file") != uploaded_file.name):
        with st.spinner("🤖 Leyendo el acta de forma inteligente..."):
            try:
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
                - total (total votos emitidos)
                Devuelve únicamente el objeto JSON válido sin bloques markdown ni texto adicional.
                """
                response = client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=[image, prompt]
                )
                text_res = response.text.strip().replace("```json", "").replace("```", "")
                extracted = json.loads(text_res)
                
                st.session_state["parsed_data"] = extracted
                st.session_state["last_file"] = uploaded_file.name
                st.success("✅ ¡Datos extraídos con éxito del acta!")
            except Exception as e:
                st.warning(f"Usando valores por defecto. Detalle: {e}")
                st.session_state["parsed_data"] = default_vals
                st.session_state["last_file"] = uploaded_file.name
