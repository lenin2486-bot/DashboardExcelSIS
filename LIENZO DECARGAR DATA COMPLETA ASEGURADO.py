#LIENZO DECARGAR DATA COMPLETA ASEGURADOS
        st.header("📈 Dashboard Asegurados")
        @st.cache_data
        def cargar_datos_asegurados():
            try:
                url_data = requests.get(url_excel_asegurados).content
                df = pd.read_excel(BytesIO(url_data), sheet_name='Hoja1', engine='openpyxl')
                return df
            except Exception as e:
                st.error(f"Error cargando datos de asegurados: {e}")
                return pd.DataFrame()        
            
        # Cargar ambos datasets
        with st.spinner('Cargando datos de asegurados...'):
           df_asegurados = cargar_datos_asegurados()    

        # Verificar si los datos se cargaron correctamente
        if df_asegurados.empty:
            st.error("No se pudieron cargar los datos de asegurados. El dashboard no funcionará correctamente.")
            st.stop()           

       # Limpiar nombres de columnas
        df_asegurados.columns = df_asegurados.columns.str.strip()

        # Mostrar información de éxito
        st.success("✅ Datos cargados correctamente")            

       # Mostrar información de las columnas disponibles en el sidebar para debug
        st.sidebar.subheader("🔍 Columnas Disponibles")
        st.sidebar.write("**Asegurados:**", list(df_asegurados.columns))