import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
import requests
import numpy as np
from st_aggrid import JsCode

# CONFIGURACIÓN DE PÁGINA PARA HACERLA MÁS ANCHA
import streamlit as st

st.set_page_config(
    #page_title="Dashboard de Digitación",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🔹 Crear las pestañas ---
tab1, tab2, tab3 = st.tabs(["📊 Digitación SIS", "📅 Asegurados", "📈 Indicadores"])

# 🟦 TAB 1: Dashboard Digitación
with tab1:
        st.header("📈 Dashboard Digitación")
        # CSS con !important y selector correcto
        st.markdown("""
        <style>
        /* Contenedor principal */
        .appview-container .main .block-container {
            max-width: 1000px !important;   /* ✅ cambia este valor para ajustar el ancho */
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            margin: auto !important;
        }

        /* Responsive */
        @media (min-width: 1600px) {
            .appview-container .main .block-container {
                max-width: 1300px !important;
            }
        }

        @media (max-width: 1200px) {
            .appview-container .main .block-container {
                max-width: 90% !important;
            }
        }

        @media (max-width: 768px) {
            .appview-container .main .block-container {
                max-width: 100% !important;
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        #st.title("📊 Dashboard de Digitación")

        # --- Cargar archivos desde Drive ---
        url_excel_digitacion = "https://drive.google.com/uc?id=1TvDHKdACvOyheNCdNGZ_nt_yZcaLrYrC"
        url_excel_mensual = "https://docs.google.com/spreadsheets/d/1UKKeYJ2XtzEkPvntDqQLUJUrg0NJCnvP/export?format=xlsx"    
        url_excel_resumen_aseg ="https://docs.google.com/spreadsheets/d/1uD9DrmrjCpsjh0faK04glBG2yrz3_nnY/export?format=xlsx"       
        url_indic_hiperten="https://docs.google.com/spreadsheets/d/1EAar2Uvf8CeNF6tQDURUgGvQdc3HWG41/export?format=xlsx"       

        @st.cache_data
        def cargar_datos_digitacion():
            try:
                url_data = requests.get(url_excel_digitacion).content
                df = pd.read_excel(BytesIO(url_data), sheet_name='Data', engine='openpyxl')
                return df
            except Exception as e:
                st.error(f"Error cargando datos de digitación: {e}")
                return pd.DataFrame()

        @st.cache_data
        def cargar_datos_mensual():
            try:
                url_data = requests.get(url_excel_mensual).content
                df = pd.read_excel(BytesIO(url_data), sheet_name='Data_Mensual', engine='openpyxl')
                return df
            except Exception as e:
                st.error(f"Error cargando datos mensuales: {e}")
                return pd.DataFrame()

        @st.cache_data
        def cargar_datos_anual():
            try:
                url_data = requests.get(url_excel_mensual).content
                df = pd.read_excel(BytesIO(url_data), sheet_name='Data_Anual', engine='openpyxl')
                return df
            except Exception as e:
                st.error(f"Error cargando datos anuales: {e}")
                return pd.DataFrame()

        @st.cache_data
        def cargar_datos_resumen_aseg_por_ppdd():
            try:
                url_data = requests.get(url_excel_resumen_aseg).content
                df = pd.read_excel(BytesIO(url_data), sheet_name='Por_PPDD', engine='openpyxl')
                return df
            except Exception as e:
                st.error(f"Error cargando datos asegurados: {e}")
                return pd.DataFrame()            

        @st.cache_data
        def cargar_datos_resumen_aseg_por_eess():
            try:
                url_data = requests.get(url_excel_resumen_aseg).content
                df = pd.read_excel(BytesIO(url_data), sheet_name='Por_EESS', engine='openpyxl')
                return df
            except Exception as e:
                st.error(f"Error cargando datos asegurados: {e}")
                return pd.DataFrame()            
            
        @st.cache_data
        def cargar_datos_resumen_aseg_por_mic():
            try:
                url_data = requests.get(url_excel_resumen_aseg).content
                df = pd.read_excel(BytesIO(url_data), sheet_name='Por_Mic', engine='openpyxl')
                return df
            except Exception as e:
                st.error(f"Error cargando datos asegurados: {e}")
                return pd.DataFrame()                        

        @st.cache_data
        def cargar_datos_indic_hiperten():
            try:
                url_data = requests.get(url_indic_hiperten).content
                df = pd.read_excel(BytesIO(url_data), sheet_name='Hoja1', engine='openpyxl')
                return df
            except Exception as e:
                st.error(f"Error cargando datos asegurados: {e}")
                return pd.DataFrame()

        # Cargar ambos datasets
        with st.spinner('Cargando datos de digitación...'):
            df_digitacion = cargar_datos_digitacion()

        with st.spinner('Cargando datos mensuales...'):
            df_mensual = cargar_datos_mensual()

        with st.spinner('Cargando datos anuales...'):
            df_anual = cargar_datos_anual()

        with st.spinner('Cargando datos resumen asegurados por PPDD...'):
            df_resumen_aseg_por_ppdd = cargar_datos_resumen_aseg_por_ppdd()            

        with st.spinner('Cargando datos resumen asegurados por EESS...'):
            df_resumen_aseg_por_eess = cargar_datos_resumen_aseg_por_eess()            

        with st.spinner('Cargando datos resumen asegurados por EESS...'):
            df_resumen_aseg_por_mic = cargar_datos_resumen_aseg_por_mic()            

        with st.spinner('Cargando datos resumen asegurados por EESS...'):
            df_indic_hiperten = cargar_datos_indic_hiperten()

        # Verificar si los datos se cargaron correctamente
        if df_digitacion.empty:
            st.error("No se pudieron cargar los datos de digitación. El dashboard no funcionará correctamente.")
            st.stop()

        if df_mensual.empty:
            st.warning("No se pudieron cargar los datos mensuales. Algunas funciones no estarán disponibles.")
            # Crear un DataFrame vacío con las columnas esperadas para evitar errores
            df_mensual = pd.DataFrame(columns=['Formula', 'Nro', 'CodPpdd', 'Ppdd', 'Oportunos', 'Total_Fuas', 'Indicador', 'Mes', 'Año'])

        if df_anual.empty:
            st.warning("No se pudieron cargar los datos anuales. Algunas funciones no estarán disponibles.")
            # Crear un DataFrame vacío con las columnas esperadas para evitar errores
            df_anual = pd.DataFrame(columns=['Formula', 'Nro', 'CodPpdd', 'Ppdd', 'Oportunos', 'Total_Fuas', 'Indicador', 'Mes', 'Año'])

        if df_resumen_aseg_por_ppdd.empty:
            st.warning("No se pudieron cargar los datos de asegurados. Algunas funciones no estarán disponibles.")
            # Crear un DataFrame vacío con las columnas esperadas para evitar errores
            df_resumen_aseg_por_ppdd = pd.DataFrame(columns=['Nro',	'Ppdd',	'Asegurados'])

        if df_resumen_aseg_por_mic.empty:
            st.warning("No se pudieron cargar los datos de asegurados. Algunas funciones no estarán disponibles.")
            # Crear un DataFrame vacío con las columnas esperadas para evitar errores
            df_resumen_aseg_por_mic = pd.DataFrame(columns=['Nro',	'Microrred','Asegurados'])

        if df_resumen_aseg_por_eess.empty:
            st.warning("No se pudieron cargar los datos de asegurados. Algunas funciones no estarán disponibles.")
            # Crear un DataFrame vacío con las columnas esperadas para evitar errores
            df_resumen_aseg_por_eess = pd.DataFrame(columns=['Nro',	'Red','Microrred','Uni_func','Ppdd','Renaes','Eess','Asegurados'])

        if df_indic_hiperten.empty:
            st.warning("No se pudieron cargar los datos de asegurados. Algunas funciones no estarán disponibles.")
            # Crear un DataFrame vacío con las columnas esperadas para evitar errores
            df_indic_hiperten = pd.DataFrame(columns=['Nro','Microrred','Numerador','Denominador','Indicador'])

        # Limpiar nombres de columnas
        df_digitacion.columns = df_digitacion.columns.str.strip()
        df_mensual.columns = df_mensual.columns.str.strip()
        df_anual.columns = df_anual.columns.str.strip()
        df_resumen_aseg_por_ppdd.columns = df_resumen_aseg_por_ppdd.columns.str.strip()
        df_resumen_aseg_por_eess.columns = df_resumen_aseg_por_eess.columns.str.strip()
        df_resumen_aseg_por_mic.columns = df_resumen_aseg_por_mic.columns.str.strip()
        df_indic_hiperten.columns = df_indic_hiperten.columns.str.strip()

        # Mostrar información de éxito
        st.success("✅ Datos cargados correctamente")

        # Mostrar información de las columnas disponibles en el sidebar para debug
        st.sidebar.subheader("🔍 Columnas Disponibles")
        st.sidebar.write("**Digitación:**", list(df_digitacion.columns))
        st.sidebar.write("**Mensual:**", list(df_mensual.columns))
        st.sidebar.write("**Anual:**", list(df_anual.columns))
        st.sidebar.write("**resumen_aseg_por_ppdd:**", list(df_resumen_aseg_por_ppdd.columns))
        st.sidebar.write("**resumen_aseg_por_eess:**", list(df_resumen_aseg_por_eess.columns))        

        # --- FUNCIÓN MEJORADA PARA LIMPIAR DATOS NUMÉRICOS ---
        def limpiar_y_preparar_dataframe(df, columnas_numericas):
            """
            Limpia y prepara un DataFrame para mostrar en tablas
            """
            df_limpio = df.copy()
            
            # Convertir columnas numéricas de forma segura
            for col in columnas_numericas:
                if col in df_limpio.columns:
                    # Conversión robusta
                    df_limpio[col] = pd.to_numeric(df_limpio[col], errors='coerce')
                    # Reemplazar NaN por 0
                    df_limpio[col] = df_limpio[col].fillna(0)
            
            return df_limpio

        # --- LIENZO 1: ANÁLISIS POR PUNTO DE DIGITACIÓN ---
        with st.expander("📍 **ANÁLISIS POR PUNTO DE DIGITACIÓN**", expanded=True):
            st.subheader("Selección de Punto")
            
            # --- Selección de PPDD ---
            puntos = df_digitacion["Ppdd"].unique()
            punto = st.selectbox("Selecciona Punto de Digitación", puntos)
            
            # --- Filtrar y agrupar por mes (PARA EL PUNTO SELECCIONADO) ---
            df_filtrado = df_digitacion[df_digitacion["Ppdd"] == punto]
            df_resumen = df_filtrado.groupby(["Mes", "Mesletras"], as_index=False)["Cantidad"].sum()
            df_resumen = df_resumen.sort_values("Mes")
            
            # --- GRÁFICO 1: Tendencia del punto seleccionado ---
            st.subheader(f"📈 Tendencia de Cantidad por Mes - {punto}")
            fig1, ax1 = plt.subplots(figsize=(12, 6))
            ax1.plot(df_resumen["Mesletras"], df_resumen["Cantidad"], marker='o', linewidth=3, color='#007ACC')
            
            # --- Etiquetas grandes y visibles ---
            for i, val in enumerate(df_resumen["Cantidad"]):
                ax1.text(i, val + (max(df_resumen["Cantidad"]) * 0.03), str(val),
                        ha='center', fontsize=14, weight='bold', color='black',
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=2))
            
            # --- Personalización del primer gráfico ---
            ax1.set_title(f"Tendencia de Cantidad por Mes - {punto}", fontsize=20, weight='bold')
            ax1.set_xlabel("Mes", fontsize=16, weight='bold')
            ax1.set_ylabel("Cantidad Total", fontsize=16, weight='bold')
            plt.xticks(fontsize=14, rotation=45)
            plt.yticks(fontsize=14)
            ax1.grid(True, linestyle='--', alpha=0.5)
            ax1.set_ylim(bottom=0)
            plt.subplots_adjust(top=0.85)
            st.pyplot(fig1)

        # --- LIENZO 2: VISTA GENERAL ---
        with st.expander("🌐 **VISTA GENERAL - TODOS LOS PUNTOS**", expanded=True):
            st.subheader("Análisis Consolidado")
            
            # --- GRÁFICO 2: TOTAL GENERAL POR MES (TODOS LOS PPDD) ---
            st.subheader("📊 Total General por Mes (Todos los Puntos)")
            df_total_mes = df_digitacion.groupby(["Mes", "Mesletras"], as_index=False)["Cantidad"].sum()
            df_total_mes = df_total_mes.sort_values("Mes")
            
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            ax2.plot(df_total_mes["Mesletras"], df_total_mes["Cantidad"], marker='o', linewidth=3, color='#28a745')
            
            # --- Etiquetas para el total general ---
            for i, val in enumerate(df_total_mes["Cantidad"]):
                ax2.text(i, val + (max(df_total_mes["Cantidad"]) * 0.03), f'{val:,}',
                        ha='center', fontsize=14, weight='bold', color='black',
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=2))
            
            # --- Personalización del segundo gráfico ---
            ax2.set_title("Total General de Cantidad por Mes (Todos los PPDD)", fontsize=20, weight='bold')
            ax2.set_xlabel("Mes", fontsize=16, weight='bold')
            ax2.set_ylabel("Cantidad Total", fontsize=16, weight='bold')
            plt.xticks(fontsize=14, rotation=45)
            plt.yticks(fontsize=14)
            ax2.grid(True, linestyle='--', alpha=0.5)
            ax2.set_ylim(bottom=0, top=80000)
            plt.subplots_adjust(top=0.85)
            st.pyplot(fig2)

        # --- LIENZO 3: ANÁLISIS POR PERSONA ---
        with st.expander("👥 **ANÁLISIS POR PERSONA**", expanded=True):
            st.subheader("Desempeño Individual")
            
            # --- GRÁFICO 3: TENDENCIA POR PERSONA ---
            st.subheader("📊 Tendencia de Cantidad por Persona")
            
            # Filtro por Ppdd para el gráfico de personas
            punto_personas = st.selectbox("Selecciona Punto de Digitación para ver Personas", puntos, key="personas")
            
            # Filtrar datos por el punto seleccionado
            df_personas = df_digitacion[df_digitacion["Ppdd"] == punto_personas]
            
            # Obtener lista de personas disponibles en ese punto
            personas = df_personas["Nombres"].unique()
            personas_seleccionadas = st.multiselect(
                "Selecciona las personas a visualizar", 
                personas, 
                default=personas[:3] if len(personas) >= 3 else personas  # Mostrar máximo 3 por defecto
            )
            
            if personas_seleccionadas:
                # Filtrar por personas seleccionadas
                df_personas_filtrado = df_personas[df_personas["Nombres"].isin(personas_seleccionadas)]
                
                # Agrupar por mes y persona
                df_personas_mes = df_personas_filtrado.groupby(["Mes", "Mesletras", "Nombres"], as_index=False)["Cantidad"].sum()
                df_personas_mes = df_personas_mes.sort_values("Mes")
                
                # Crear gráfico de tendencias por persona
                fig3, ax3 = plt.subplots(figsize=(14, 8))
                
                # Colores para las diferentes personas
                colores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
                
                # Graficar línea para cada persona
                for i, persona in enumerate(personas_seleccionadas):
                    df_persona = df_personas_mes[df_personas_mes["Nombres"] == persona]
                    color = colores[i % len(colores)]
                    ax3.plot(df_persona["Mesletras"], df_persona["Cantidad"], 
                            marker='o', linewidth=2.5, label=persona, color=color, markersize=8)
                    
                    # Añadir etiquetas de valores (MÁS GRANDES)
                    for j, (mes, cantidad) in enumerate(zip(df_persona["Mesletras"], df_persona["Cantidad"])):
                        ax3.annotate(f'{cantidad}', 
                                    (mes, cantidad),
                                    textcoords="offset points",
                                    xytext=(0,10),
                                    ha='center',
                                    fontsize=12,
                                    weight='bold')
                
                # --- Personalización del gráfico ---
                ax3.set_title(f"Tendencia de Cantidad por Persona - {punto_personas}", fontsize=20, weight='bold')
                ax3.set_xlabel("Mes", fontsize=16, weight='bold')
                ax3.set_ylabel("Cantidad", fontsize=16, weight='bold')
                plt.xticks(fontsize=14, rotation=45)
                plt.yticks(fontsize=14)
                ax3.grid(True, linestyle='--', alpha=0.3)
                ax3.set_ylim(bottom=0)
                
                # LEYENDA DEBAJO DEL GRÁFICO
                ax3.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), 
                        ncol=min(3, len(personas_seleccionadas)), fontsize=14, frameon=True)
                
                # Ajustar diseño para hacer espacio para la leyenda
                plt.tight_layout()
                plt.subplots_adjust(bottom=0.2)
                st.pyplot(fig3)
                
                # Mostrar tabla de datos de personas
                st.subheader(f"📋 Datos por Persona - {punto_personas}")
                df_tabla_personas = df_personas_mes.pivot_table(
                    index=['Mes', 'Mesletras'], 
                    columns='Nombres', 
                    values='Cantidad', 
                    fill_value=0
                ).reset_index()
                
                df_tabla_personas = df_tabla_personas[['Mesletras'] + list(personas_seleccionadas)]
                df_tabla_personas = df_tabla_personas.rename(columns={'Mesletras': 'Mes'})
                
                # índice empieza en 1
                df_tabla_personas.index = df_tabla_personas.index + 1
                
                # USAR DATA EDITOR PARA MOSTRAR FILTROS
                st.data_editor(
                    df_tabla_personas,
                    use_container_width=True,
                    hide_index=True,
                    disabled=True  # Hacerla de solo lectura
                )
                
            else:
                st.info("Por favor selecciona al menos una persona para visualizar el gráfico.")

        # --- LIENZO 4: LISTADO DE DATOS MENSUALES ---
        with st.expander("📊 **LISTADO DE DATOS MENSUALES**", expanded=True):
            st.subheader("📋 Listado Completo de Datos Mensuales")
            
            # Verificar si hay datos en el dataset anual
            if df_mensual.empty or len(df_mensual) == 0:
                st.warning("No hay datos disponibles en el dataset mensual.")
            else:
                # Filtros por mes y Año
                col1, col2 = st.columns(2)
                
                with col1:
                    # Obtener meses disponibles ordenados
                    orden_meses = [
                        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                    ]

                    # Filtrar solo los meses que existen en el DataFrame
                    meses_disponibles = df_mensual["Mes"].dropna().unique()

                    # Ordenar los meses según el orden natural
                    meses_disponibles = sorted(
                        [m for m in meses_disponibles if m in orden_meses],
                        key=lambda x: orden_meses.index(x)
                    )

                    mes_seleccionado = st.selectbox(
                        "📅 Seleccione el mes:",
                        options=meses_disponibles,
                        key="mes_mensual",
                        index=meses_disponibles.index("Enero") if "Enero" in meses_disponibles else 0
                    )
                
                with col2:
                    # Obtener Años disponibles ordenados
                    if 'Año' in df_mensual.columns:
                        Años_disponibles = sorted(df_mensual['Año'].unique())
                        Año_seleccionado = st.selectbox(
                            "Selecciona el Año", 
                            options=Años_disponibles,
                            key="anio_mensual",
                            index=len(Años_disponibles)-1 if len(Años_disponibles) > 0 else 0
                        )
                    else:
                        st.error("No se encontró la columna 'Año' en los datos")
                        Año_seleccionado = None
                
                # Aplicar filtros
                if mes_seleccionado and Año_seleccionado and 'Mes' in df_mensual.columns and 'Año' in df_mensual.columns:
                    df_filtradomensual = df_mensual[
                        (df_mensual['Mes'] == mes_seleccionado) & 
                        (df_mensual['Año'] == Año_seleccionado)
                    ].copy()
                else:
                    df_filtradomensual = df_mensual.copy()
                
                # Ordenar por Indicador de mayor a menor si la columna existe
                if 'Indicador' in df_filtradomensual.columns:
                    df_filtradomensual = df_filtradomensual.sort_values('Indicador', ascending=False)
                else:
                    st.warning("No se encontró la columna 'Indicador' para ordenar")
                
                # Mostrar el listado de datos
                st.subheader("📊 Listado Detallado (Ordenado por Indicador - Mayor a Menor)")
                
                # Columnas a mostrar
                columnas_a_mostrar = ['CodPpdd', 'Ppdd', 'Oportunos', 'Total_Fuas', 'Indicador']
                
                # Verificar que las columnas existan en el DataFrame
                columnas_existentes = [col for col in columnas_a_mostrar if col in df_filtradomensual.columns]
                
                if columnas_existentes:
                    # Preparar DataFrame para mostrar
                    df_mostrar_mensual = df_filtradomensual[columnas_existentes].copy().head(23)
                    df_mostrar_mensual = df_mostrar_mensual.reset_index(drop=True)
                    df_mostrar_mensual.insert(0, "N°", range(1, len(df_mostrar_mensual) + 1))

                    # LIMPIAR DATOS NUMÉRICOS
                    columnas_numericas = ["N°", "CodPpdd", "Oportunos", "Total_Fuas", "Indicador"]
                    df_mostrar_mensual = limpiar_y_preparar_dataframe(df_mostrar_mensual, columnas_numericas)
                    
                    # Crear una versión para mostrar con el indicador formateado como porcentaje
                    df_mostrar_formateado = df_mostrar_mensual.copy()
                    if 'Indicador' in df_mostrar_formateado.columns:
                        df_mostrar_formateado['Indicador'] = df_mostrar_formateado['Indicador'].apply(
                            lambda x: f"{x:.1%}" if isinstance(x, (int, float)) and not pd.isna(x) else "N/A"
                        )
                    
                    # APLICAR ESTILOS CON COLORES AL INDICADOR
                    cell_style_indicador = JsCode("""
                    function(params) {
                        if (params.value === 'N/A' || params.value === null || params.value === undefined) {
                            return {backgroundColor: 'lightgray', color: 'black', fontWeight: 'bold', textAlign: 'center'};
                        }

                        var val = parseFloat(params.value.toString().replace('%', '')) / 100;

                        if (val >= 0.75) {
                            return {backgroundColor: '#00b050', color: 'white', fontWeight: 'bold', textAlign: 'center',fontSize: '19px'};
                        } else if (val >= 0.60) {
                            return {backgroundColor: '#ffcc66', color: 'black', fontWeight: 'bold', textAlign: 'center',fontSize: '19px'};
                        } else if (val >= 0.25) {
                            return {backgroundColor: '#ff7c80', color: 'black', fontWeight: 'bold', textAlign: 'center',fontSize: '19px'};
                        } else {
                            return {backgroundColor: '#ff0000', color: 'white', fontWeight: 'bold', textAlign: 'center',fontSize: '19px'};
                        }
                    }
                    """)

                    
                    # MOSTRAR SOLO LA TABLA CON COLORES

                    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

                    # --- build grid options ---
                    gb = GridOptionsBuilder.from_dataframe(df_mostrar_formateado)

                    gb.configure_default_column(
                        resizable=True,
                        sortable=True,
                        filter=True,
                        wrapText=True,
                        autoHeight=True,
                        cellStyle={"fontSize": "18px", "fontFamily": "Segoe UI"},
                        headerClass="custom-header"   # clase que aplicaremos al header
                    )

                    # ajustar alturas
                    gb.configure_grid_options(rowHeight=32, headerHeight=44, domLayout='normal')

                #Color Columna Indicador
                    gb.configure_column(
                        "Indicador",
                    cellStyle=cell_style_indicador,
                    valueFormatter=JsCode("(function(params) { if (!params.value) return ''; return params.value; })")
                    )
                
                #Color Columna Indicador

                    grid_options = gb.build()
                    grid_options["uuid"] = "mensual"
                    # --- CSS que se inyecta DENTRO del componente (custom_css) ---
                    custom_css = {
                        # variables del tema (afectan todo el grid, buen fallback)
                        ".ag-theme-streamlit": {
                            "--ag-font-size": "20px",
                            "--ag-header-height": "44px"
                        },
                        # selectores directamente sobre header (por compatibilidad)
                        ".ag-header-cell-label": {
                            "font-size": "20px",
                            "font-weight": "600",
                            "font-family": "Segoe UI"
                        },
                        ".ag-header-cell-text": {
                            "font-size": "20px",
                            "font-weight": "600"
                        },
                        # clase que asignamos con headerClass
                        ".custom-header": {
                            "font-size": "20px",
                            "font-weight": "600"
                        }
                    }

                    # --- render AgGrid y pasar custom_css ---
                    AgGrid(
                        df_mostrar_formateado,
                        gridOptions=grid_options,
                        height=780,
                        auto_size_columns=True,          # 👈 SOLO ESTA
                        update_mode=GridUpdateMode.NO_UPDATE,
                        enable_enterprise_modules=False,
                        theme='streamlit',
                        custom_css=custom_css,
                        allow_unsafe_jscode=True,
                        key="grid_mensual" 
                    )

                    st.markdown("""
                        <style>
                        .custom-header {
                            font-size: 20px !important;
                            font-weight: 600 !important;
                            font-family: 'Segoe UI', sans-serif !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)

                    # Fin Tabla con Colores

                    # Leyenda de colores
                    st.markdown("""
                    **🎨 Leyenda de Indicadores:**
                    - <span style='color: white; background-color: #00b050; padding: 2px 6px; border-radius: 3px; font-weight: bold;'>Bueno (75-100%)</span>
                    - <span style='color: black; background-color: #ffcc66; padding: 2px 6px; border-radius: 3px; font-weight: bold;'>Regular (60-74%)</span>
                    - <span style='color: black; background-color: #ff7c80; padding: 2px 6px; border-radius: 3px; font-weight: bold;'>En Proceso (25-59%)</span>
                    - <span style='color: white; background-color: #ff0000; padding: 2px 6px; border-radius: 3px; font-weight: bold;'>Malo (0-24%)</span>
                    - <span style='color: black; background-color: lightgray; padding: 2px 6px; border-radius: 3px; font-weight: bold;'>Datos Inválidos</span>
                    """, unsafe_allow_html=True)
                    
                    # Mostrar información adicional
                    st.info(f"ℹ️ Mostrando {len(df_mostrar_mensual)} registros del mes {mes_seleccionado} del Año {Año_seleccionado}, ordenados por Indicador (mayor a menor).")
                    
                else:
                    st.error("No se encontraron las columnas especificadas en el dataset.")
                    st.write("Columnas disponibles en el dataset:", list(df_filtradomensual.columns))

                # MOSTRAR MÉTRICAS DE RESUMEN
                st.subheader(f"📈 Resumen - Mes {mes_seleccionado} / Año {Año_seleccionado}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_registros = len(df_filtradomensual)
                    st.metric("Total de Registros", f"{total_registros:,}")
                
                with col2:
                    if 'Oportunos' in df_filtradomensual.columns:
                        # Conversión segura para el cálculo
                        oportunos_numerico = pd.to_numeric(df_filtradomensual['Oportunos'], errors='coerce').fillna(0)
                        total_oportunos = int(oportunos_numerico.sum())
                        st.metric("Total Oportunos", f"{total_oportunos:,}")
                    else:
                        st.metric("Total Oportunos", "N/A")
                
                with col3:
                    if 'Total_Fuas' in df_filtradomensual.columns:
                        # Conversión segura para el cálculo
                        fuas_numerico = pd.to_numeric(df_filtradomensual['Total_Fuas'], errors='coerce').fillna(0)
                        total_fuas = int(fuas_numerico.sum())
                        st.metric("Total FUAS", f"{total_fuas:,}")
                    else:
                        st.metric("Total FUAS", "N/A")
                
                with col4:
                    if 'Indicador' in df_filtradomensual.columns:
                        indicador_numerico = pd.to_numeric(df_filtradomensual['Indicador'], errors='coerce')
                        indicador_promedio = indicador_numerico.mean() * 100
                        st.metric("Indicador Promedio", f"{indicador_promedio:.1f}%")
                    else:
                        st.metric("Indicador Promedio", "N/A")
                
                # Botón para descargar datos
                st.subheader("💾 Exportar Datos Filtrados")
                
                csv = df_filtradomensual.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar listado filtrado en CSV",
                    data=csv,
                    file_name=f"datos_mensuales_{mes_seleccionado}_{Año_seleccionado}.csv",
                    mime="text/csv"
                )

            # --- Pequeño script JS para volver a enfocar el selectbox ---
                st.markdown(
                    """
                    <script>
                    const selects = parent.document.querySelectorAll('select');
                    if (selects.length > 0) {
                        // selecciona el último select (por si hay más de uno en la página)
                        const s = selects[selects.length - 1];
                        setTimeout(() => { s.focus(); }, 300);
                    }
                    </script>
                    """,
                    unsafe_allow_html=True
                )

        # --- LIENZO 5: LISTADO DE DATOS ACUMULADOS ANUAL ---
        with st.expander("📊 **LISTADO DE DATOS ANUAL**", expanded=True):
            st.subheader("📋 Listado Completo de Datos Acumulado")
            
            # Verificar si hay datos en el dataset anual
            if df_anual.empty or len(df_anual) == 0:
                st.warning("No hay datos disponibles en el dataset mensual.")
            else:
                # Filtros por mes y Año
                col1_ac, col2_ac = st.columns(2)
                
                with col1_ac:
                    # Obtener meses disponibles ordenados
                    orden_meses_ac = [
                        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                    ]

                    # Filtrar solo los meses que existen en el DataFrame
                    meses_disponibles_ac = df_anual["Mes"].dropna().unique()

                    # Ordenar los meses según el orden natural
                    meses_disponibles_ac = sorted(
                        [m for m in meses_disponibles_ac if m in orden_meses_ac],
                        key=lambda x: orden_meses_ac.index(x)
                    )

                    mes_seleccionado_ac = st.selectbox(
                        "📅 Seleccione el mes:",
                        options=meses_disponibles_ac,
                        key="mes_anual",
                        index=meses_disponibles_ac.index("Enero") if "Enero" in meses_disponibles_ac else 0
                    )
                
                with col2_ac:
                    # Obtener Años disponibles ordenados
                    if 'Año' in df_anual.columns:
                        Años_disponibles_ac = sorted(df_anual['Año'].unique())
                        Año_seleccionado_ac = st.selectbox(
                            "Selecciona el Año", 
                            options=Años_disponibles_ac,
                            key="anio_anual",
                            index=len(Años_disponibles_ac)-1 if len(Años_disponibles_ac) > 0 else 0
                        )
                    else:
                        st.error("No se encontró la columna 'Año' en los datos")
                        Año_seleccionado_ac = None
                
                # Aplicar filtros
                if mes_seleccionado_ac and Año_seleccionado_ac and 'Mes' in df_anual.columns and 'Año' in df_anual.columns:
                    df_filtradoanual = df_anual[
                        (df_anual['Mes'] == mes_seleccionado_ac) & 
                        (df_anual['Año'] == Año_seleccionado_ac)
                    ].copy()
                else:
                    df_filtradoanual = df_anual.copy()

                # --- Aplicar filtros ---
                if mes_seleccionado_ac and Año_seleccionado_ac and 'Mes' in df_anual.columns and 'Año' in df_anual.columns:
                    df_filtradoanual = df_anual[
                        (df_anual['Mes'] == mes_seleccionado_ac) &
                        (df_anual['Año'] == Año_seleccionado_ac)
                    ].copy()
                else:
                    df_filtradoanual = df_anual.copy()

                # --- Mostrar advertencia si no hay datos ---
                if df_filtradoanual.empty:
                    st.warning("No hay datos disponibles para ese mes y año.")
                else:
                    # --- Generar dataframe para mostrar ---
                    df_mostrar_formateado_ac = df_filtradoanual.copy()

                    # --- Crear configuración de la tabla ---
                    gb_ac = GridOptionsBuilder.from_dataframe(df_mostrar_formateado_ac)

                    # 🔧 Parche para versiones 1.1.9 (evita error 'list' object has no attribute values)
                    if isinstance(gb._GridOptionsBuilder__grid_options.get("columnDefs"), list):
                        gb._GridOptionsBuilder__grid_options["columnDefs"] = {
                            str(i): col for i, col in enumerate(
                                gb._GridOptionsBuilder__grid_options["columnDefs"]
                            )
                        }

                    grid_options_ac = gb.build()

                    # --- Clave dinámica: fuerza redibujo al cambiar filtros ---
                    grid_key = f"grid_ac_{mes_seleccionado_ac}_{Año_seleccionado_ac}"

                # Fin Filtros

                # Ordenar por Indicador de mayor a menor si la columna existe
                if 'Indicador' in df_filtradoanual.columns:
                    df_filtradoanual = df_filtradoanual.sort_values('Indicador', ascending=False)
                else:
                    st.warning("No se encontró la columna 'Indicador' para ordenar")
                
                # Mostrar el listado de datos
                st.subheader("📊 Listado Detallado (Ordenado por Indicador - Mayor a Menor)")
                
                # Columnas a mostrar
                columnas_a_mostrar_ac = ['CodPpdd', 'Ppdd', 'Oportunos', 'Total_Fuas', 'Indicador']
                
                # Verificar que las columnas existan en el DataFrame
                columnas_existentes_ac = [col for col in columnas_a_mostrar_ac if col in df_filtradoanual.columns]
                
                if columnas_existentes_ac:
                    # Preparar DataFrame para mostrar
                    df_mostrar_anual = df_filtradoanual[columnas_existentes_ac].copy().head(23)
                    df_mostrar_anual = df_mostrar_anual.reset_index(drop=True)
                    df_mostrar_anual.insert(0, "N°", range(1, len(df_mostrar_anual) + 1))

                    # LIMPIAR DATOS NUMÉRICOS
                    columnas_numericas_ac = ["N°", "CodPpdd", "Oportunos", "Total_Fuas", "Indicador"]
                    df_mostrar_anual = limpiar_y_preparar_dataframe(df_mostrar_anual, columnas_numericas_ac)
                    
                    # Crear una versión para mostrar con el indicador formateado como porcentaje
                    df_mostrar_formateado_ac = df_mostrar_anual.copy()
                    if 'Indicador' in df_mostrar_formateado_ac.columns:
                        df_mostrar_formateado_ac['Indicador'] = df_mostrar_formateado_ac['Indicador'].apply(
                            lambda x: f"{x:.1%}" if isinstance(x, (int, float)) and not pd.isna(x) else "N/A"
                        )
                    
                    # APLICAR ESTILOS CON COLORES AL INDICADOR
                    cell_style_indicador_ac = JsCode("""
                    function(params) {
                        if (params.value === 'N/A' || params.value === null || params.value === undefined) {
                            return {backgroundColor: 'lightgray', color: 'black', fontWeight: 'bold', textAlign: 'center'};
                        }

                        var val = parseFloat(params.value.toString().replace('%', '')) / 100;

                        if (val >= 0.75) {
                            return {backgroundColor: '#00b050', color: 'white', fontWeight: 'bold', textAlign: 'center',fontSize: '19px'};
                        } else if (val >= 0.60) {
                            return {backgroundColor: '#ffcc66', color: 'black', fontWeight: 'bold', textAlign: 'center',fontSize: '19px'};
                        } else if (val >= 0.25) {
                            return {backgroundColor: '#ff7c80', color: 'black', fontWeight: 'bold', textAlign: 'center',fontSize: '19px'};
                        } else {
                            return {backgroundColor: '#ff0000', color: 'white', fontWeight: 'bold', textAlign: 'center',fontSize: '19px'};
                        }
                    }
                    """)

                    
                    # MOSTRAR SOLO LA TABLA CON COLORES

                    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

                    # --- Renombrar la columna problemática ---
                    df_mostrar_formateado_ac = df_mostrar_formateado_ac.rename(columns={"N°": "Nro"})

                    df_mostrar_formateado_ac = df_mostrar_formateado_ac.astype({
                        "Nro": "int",
                        "CodPpdd": "int",
                        "Oportunos": "int",
                        "Total_Fuas": "int"
                    })


                    # --- build grid options ---
                    gb_ac = GridOptionsBuilder.from_dataframe(df_mostrar_formateado_ac)

                    gb_ac.configure_default_column(
                        resizable=True,
                        sortable=True,
                        filter=True,
                        wrapText=True,
                        autoHeight=True,
                        cellStyle={"fontSize": "18px", "fontFamily": "Segoe UI"},
                        headerClass="custom-header"   # clase que aplicaremos al header
                    )

                    # ajustar alturas
                    gb_ac.configure_grid_options(rowHeight=32, headerHeight=44, domLayout='normal')

                    #Color Columna Indicador
                    gb_ac.configure_column(
                        "Indicador",
                    cellStyle=cell_style_indicador_ac,
                    valueFormatter=JsCode("(function(params) { if (!params.value) return ''; return params.value; })")
                )
                
                #Color Columna Indicador

                    print("DEBUG -> Tipo de gb:", type(gb))
                    print("DEBUG -> Contenido columnDefs:", type(getattr(gb, "_GridOptionsBuilder__grid_options", {}).get("columnDefs")))


                    grid_options_ac = gb_ac.build()
                    grid_options_ac["uuid"] = "acumulado"  # 👈 clave única “manual”
                    grid_options_ac["suppressPropertyUpdates"] = False  # 👈 truco para forzar ID distinto

                    # --- CSS que se inyecta DENTRO del componente (mis_estilos) ---
                    mis_estilos = {
                        # variables del tema (afectan todo el grid, buen fallback)
                        ".ag-theme-streamlit": {
                            "--ag-font-size": "20px",
                            "--ag-header-height": "44px"
                        },
                        # selectores directamente sobre header (por compatibilidad)
                        ".ag-header-cell-label": {
                            "font-size": "20px",
                            "font-weight": "600",
                            "font-family": "Segoe UI"
                        },
                        ".ag-header-cell-text": {
                            "font-size": "20px",
                            "font-weight": "600"
                        },
                        # clase que asignamos con headerClass
                        ".custom-header": {
                            "font-size": "20px",
                            "font-weight": "600"
                        }
                    }
                    
                    #df_mostrar_formateado_ac = df_mostrar_formateado_ac.rename(columns={"N°": "Nro"})
                    # --- render AgGrid y pasar mis_estilos ---
                    AgGrid(
                        df_mostrar_formateado_ac,
                        gridOptions=grid_options_ac.copy(),
                        height=780,
                        auto_size_columns=True,          # 👈 SOLO ESTA
                        update_mode=GridUpdateMode.NO_UPDATE,
                        enable_enterprise_modules=False,
                        theme='streamlit',
                        custom_css=mis_estilos,
                        allow_unsafe_jscode=True,
                        key=f"grid_{mes_seleccionado_ac}_{Año_seleccionado_ac}"
                    )

                    st.markdown("""
                        <style>
                        .custom-header {
                            font-size: 20px !important;
                            font-weight: 600 !important;
                            font-family: 'Segoe UI', sans-serif !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)

                    # Fin Tabla con Colores

                    # Leyenda de colores
                    st.markdown("""
                    **🎨 Leyenda de Indicadores:**
                    - <span style='color: white; background-color: #00b050; padding: 2px 6px; border-radius: 3px; font-weight: bold;'>Bueno (75-100%)</span>
                    - <span style='color: black; background-color: #ffcc66; padding: 2px 6px; border-radius: 3px; font-weight: bold;'>Regular (60-74%)</span>
                    - <span style='color: black; background-color: #ff7c80; padding: 2px 6px; border-radius: 3px; font-weight: bold;'>En Proceso (25-59%)</span>
                    - <span style='color: white; background-color: #ff0000; padding: 2px 6px; border-radius: 3px; font-weight: bold;'>Malo (0-24%)</span>
                    - <span style='color: black; background-color: lightgray; padding: 2px 6px; border-radius: 3px; font-weight: bold;'>Datos Inválidos</span>
                    """, unsafe_allow_html=True)
                    
                    # Mostrar información adicional
                    st.info(f"ℹ️ Mostrando {len(df_mostrar_anual)} registros del mes {mes_seleccionado_ac} del Año {Año_seleccionado_ac}, ordenados por Indicador (mayor a menor).")
                    
                else:
                    st.error("No se encontraron las columnas especificadas en el dataset.")
                    st.write("Columnas disponibles en el dataset:", list(df_filtradoanual.columns))

                # MOSTRAR MÉTRICAS DE RESUMEN
                st.subheader(f"📈 Resumen - Mes {mes_seleccionado} / Año {Año_seleccionado}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_registros = len(df_filtradoanual)
                    st.metric("Total de Registros", f"{total_registros:,}")
                
                with col2:
                    if 'Oportunos' in df_filtradoanual.columns:
                        # Conversión segura para el cálculo
                        oportunos_numerico = pd.to_numeric(df_filtradoanual['Oportunos'], errors='coerce').fillna(0)
                        total_oportunos = int(oportunos_numerico.sum())
                        st.metric("Total Oportunos", f"{total_oportunos:,}")
                    else:
                        st.metric("Total Oportunos", "N/A")
                
                with col3:
                    if 'Total_Fuas' in df_filtradoanual.columns:
                        # Conversión segura para el cálculo
                        fuas_numerico = pd.to_numeric(df_filtradoanual['Total_Fuas'], errors='coerce').fillna(0)
                        total_fuas = int(fuas_numerico.sum())
                        st.metric("Total FUAS", f"{total_fuas:,}")
                    else:
                        st.metric("Total FUAS", "N/A")
                
                with col4:
                    if 'Indicador' in df_filtradoanual.columns:
                        indicador_numerico = pd.to_numeric(df_filtradoanual['Indicador'], errors='coerce')
                        indicador_promedio = indicador_numerico.mean() * 100
                        st.metric("Indicador Promedio", f"{indicador_promedio:.1f}%")
                    else:
                        st.metric("Indicador Promedio", "N/A")
                
                # Botón para descargar datos
                st.subheader("💾 Exportar Datos Filtrados")
                
                csv = df_filtradoanual.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar listado filtrado en CSV",
                    data=csv,
                    file_name=f"datos_anuales_{mes_seleccionado}_{Año_seleccionado}.csv",
                    mime="text/csv"
                )

                # --- Script JS para enfocar SOLO este selectbox ---
                st.markdown(
                    """
                    <script>
                    // Buscar el select más cercano al texto "Selecciona el año"
                    const labels = parent.document.querySelectorAll('label');
                    labels.forEach(lbl => {
                        if (lbl.textContent.includes('Selecciona el año')) {
                            const sel = lbl.parentElement.querySelector('select');
                            if (sel) setTimeout(() => sel.focus(), 300);
                        }
                    });
                    </script>
                    """,
                    unsafe_allow_html=True
                )

        # --- LIENZO 6: EXPORTACIÓN ---
        with st.expander("💾 **EXPORTACIÓN DE DATOS**", expanded=False):
            st.subheader("Descargar Reportes")
            
            # --- Botón para PDF con todos los gráficos ---
            buffer = BytesIO()
            with PdfPages(buffer) as pdf:
                fig1.savefig(pdf, format='pdf', bbox_inches='tight')
                fig2.savefig(pdf, format='pdf', bbox_inches='tight')
                if 'personas_seleccionadas' in locals() and personas_seleccionadas:
                    fig3.savefig(pdf, format='pdf', bbox_inches='tight')
                    
            buffer.seek(0)
            
            st.download_button(
                label="📄 Descargar todos los gráficos en PDF",
                data=buffer,
                file_name=f"graficos_digitacion_completo.pdf",
                mime="application/pdf"
            )
            
            # Botón adicional para descargar datos en Excel
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Descargar datos de digitación",
                    data=df_digitacion.to_csv(index=False).encode('utf-8'),
                    file_name="datos_digitacion.csv",
                    mime="text/csv"
                )
            with col2:
                if not df_mensual.empty:
                    st.download_button(
                        label="📥 Descargar datos mensuales completos",
                        data=df_mensual.to_csv(index=False).encode('utf-8'),
                        file_name="datos_mensuales_completos.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No hay datos mensuales para descargar")

with tab2:

# LIENZO 7 ASEGURADOS POR PUNTOS DE DIGITACION    
    import io  # Agregar esta línea con las otras importaciones
    st.header("📅 Asegurados por Punto de Digitación")
    
    # Verificar si hay datos disponibles y que sea un DataFrame
    if (not hasattr(df_resumen_aseg_por_ppdd, 'columns') or 
        df_resumen_aseg_por_ppdd.empty or 
        not isinstance(df_resumen_aseg_por_ppdd, pd.DataFrame)):
        
        st.error("❌ No hay datos disponibles de asegurados o hubo un error en la carga.")
        st.info("Los datos de asegurados no se pudieron cargar correctamente.")
        
    else:
        # Asegurarnos de que las columnas estén limpias
        df_resumen_aseg_por_ppdd.columns = df_resumen_aseg_por_ppdd.columns.str.strip()
        
        # Verificar que las columnas requeridas existan
        columnas_requeridas = ['Nro', 'Ppdd', 'Asegurados']
        columnas_existentes = [col for col in columnas_requeridas if col in df_resumen_aseg_por_ppdd.columns]
        
        if len(columnas_existentes) == 3:
            # Preparar el DataFrame para mostrar
            df_mostrar_asegurados = df_resumen_aseg_por_ppdd[columnas_existentes].copy()
            
            # Limpiar datos numéricos
            df_mostrar_asegurados = limpiar_y_preparar_dataframe(df_mostrar_asegurados, ['Nro', 'Asegurados'])
            
            # Ordenar por número
            df_mostrar_asegurados = df_mostrar_asegurados.sort_values('Nro').reset_index(drop=True)
            
            st.subheader("👥 Listado de Asegurados por Punto de Digitación")
            
            # Configuración de AgGrid
            from st_aggrid import AgGrid, GridOptionsBuilder
            
            gb_asegurados = GridOptionsBuilder.from_dataframe(df_mostrar_asegurados)
            
            gb_asegurados.configure_default_column(
                resizable=True,
                sortable=True,
                filter=True,
                wrapText=False,
                cellStyle={"fontSize": "16px", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontWeight": "300"},  # 👈 16px en lugar de 14px
                headerClass="header-asegurados"
            )
            
            # Configurar columnas específicas con anchos FIJOS
            gb_asegurados.configure_column(
                "Nro",
                headerName="N°",
                width=80,
                minWidth=80,
                maxWidth=80,
                type=["numericColumn"],
                cellStyle={"textAlign": "center", "fontWeight": "300", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "16px"}  # 👈 16px
            )
            
            gb_asegurados.configure_column(
                "Ppdd",
                headerName="Punto de Digitación",
                width=400,
                minWidth=400,
                maxWidth=400,
                cellStyle={"fontWeight": "300", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "16px"}  # 👈 16px
            )
            
            gb_asegurados.configure_column(
                "Asegurados",
                headerName="Total Asegurados",
                width=150,
                minWidth=150,
                maxWidth=150,
                type=["numericColumn"],
                cellStyle={"textAlign": "right", "fontWeight": "300", "color": "#007ACC", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "16px"}  # 👈 16px
            )
            
            # Configurar opciones del grid (aumentar ligeramente la altura de fila para la fuente más grande)
            gb_asegurados.configure_grid_options(
                rowHeight=35,      # 👈 Aumentado de 30px a 35px para la fuente más grande
                headerHeight=45,   # 👈 Aumentado de 40px a 45px
                domLayout='normal',
                suppressColumnVirtualisation=True
            )
            
            grid_options_asegurados = gb_asegurados.build()
            
            # CSS personalizado con Bahnschrift Light y fuente más grande
            custom_css_asegurados = {
                ".ag-theme-streamlit": {
                    "--ag-font-size": "16px",  # 👈 16px en lugar de 14px
                    "--ag-header-height": "45px",  # 👈 Aumentado
                    "--ag-row-height": "35px",  # 👈 Aumentado
                    "--ag-header-background-color": "#f0f2f6",
                    "--ag-odd-row-background-color": "#fafafa",
                    "--ag-font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                },
                ".ag-header-cell-label": {
                    "font-size": "16px",  # 👈 16px
                    "font-weight": "400",
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif"
                },
                ".ag-header-cell-text": {
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                    "font-weight": "400",
                    "font-size": "16px"  # 👈 16px
                },
                ".ag-cell": {
                    "display": "flex",
                    "align-items": "center",
                    "line-height": "1.3",  # 👈 Aumentado ligeramente el line-height
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                    "font-weight": "300",
                    "font-size": "16px"  # 👈 16px
                },
                ".header-asegurados": {
                    "font-size": "16px !important",  # 👈 16px
                    "font-weight": "400 !important",
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif !important",
                    "background-color": "#f0f2f6 !important"
                },
                ".ag-root-wrapper": {
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                },
                ".ag-row": {
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                    "font-weight": "300"
                }
            }
            
            # CALCULAR ALTURA EXACTA PARA 22 REGISTROS (con nuevas alturas)
            num_registros = len(df_mostrar_asegurados)
            altura_header = 45    # 👈 headerHeight aumentado
            altura_fila = 35      # 👈 rowHeight aumentado
            altura_total = altura_header + (num_registros * altura_fila)
            
            # Añadir un pequeño margen extra para mejor visualización
            altura_total_con_margen = altura_total + 10
            
            st.write(f"**Mostrando {num_registros} registros**")
            
            # Mostrar la tabla con altura calculada
            AgGrid(
                df_mostrar_asegurados,
                gridOptions=grid_options_asegurados,
                height=altura_total_con_margen,
                theme='streamlit',
                custom_css=custom_css_asegurados,
                enable_enterprise_modules=False,
                key="grid_asegurados"
            )
            
            # Mostrar métricas resumen
            st.subheader("📊 Resumen de Asegurados")
            
            # CSS para las métricas con fuente más grande
            st.markdown("""
            <style>
            .stMetric {
                font-family: 'Bahnschrift Light', 'Segoe UI', sans-serif !important;
            }
            .stMetric label {
                font-family: 'Bahnschrift Light', 'Segoe UI', sans-serif !important;
                font-weight: 300 !important;
                font-size: 16px !important;  /* 👈 Tamaño aumentado */
            }
            .stMetric value {
                font-family: 'Bahnschrift Light', 'Segoe UI', sans-serif !important;
                font-weight: 400 !important;
                font-size: 18px !important;  /* 👈 Tamaño aumentado */
            }
            </style>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_puntos = len(df_mostrar_asegurados)
                st.metric("Total Puntos de Digitación", f"{total_puntos}")
            
            with col2:
                total_asegurados = df_mostrar_asegurados['Asegurados'].sum()
                st.metric("Total Asegurados", f"{total_asegurados:,}")
            
            with col3:
                promedio_por_punto = total_asegurados / total_puntos if total_puntos > 0 else 0
                st.metric("Promedio por Punto", f"{promedio_por_punto:,.0f}")
            
            # Botón para descargar datos
            st.subheader("💾 Exportar Datos")
            
            # Exportar a Excel en lugar de CSV
            excel_asegurados = io.BytesIO()
            with pd.ExcelWriter(excel_asegurados, engine='openpyxl') as writer:
                df_mostrar_asegurados.to_excel(writer, sheet_name='Asegurados_PPDD', index=False)
            excel_asegurados.seek(0)
            
            st.download_button(
                label="📥 Descargar listado de asegurados en Excel",
                data=excel_asegurados,
                file_name="asegurados_por_ppdd.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        else:
            st.error(f"Faltan columnas requeridas. Columnas disponibles: {list(df_resumen_aseg_por_ppdd.columns)}")
            st.info("Las columnas requeridas son: Nro, Ppdd, Asegurados")
            
            # Mostrar una vista previa de los datos para debugging
            st.subheader("🔍 Vista previa de los datos disponibles")
            st.dataframe(df_resumen_aseg_por_ppdd.head())

# LIENZO 8 ASEGURADOS POR Microrred
    st.header("📅 Asegurados por Microrred")
    
    # Verificar si hay datos disponibles y que sea un DataFrame
    if (not hasattr(df_resumen_aseg_por_mic, 'columns') or 
        df_resumen_aseg_por_mic.empty or 
        not isinstance(df_resumen_aseg_por_mic, pd.DataFrame)):
        
        st.error("❌ No hay datos disponibles de asegurados por microrred o hubo un error en la carga.")
        st.info("Los datos de asegurados por microrred no se pudieron cargar correctamente.")
        
    else:
        # Asegurarnos de que las columnas estén limpias
        df_resumen_aseg_por_mic.columns = df_resumen_aseg_por_mic.columns.str.strip()
        
        # Verificar que las columnas requeridas existan
        columnas_requeridas = ['Nro', 'Microrred', 'Asegurados']
        columnas_existentes = [col for col in columnas_requeridas if col in df_resumen_aseg_por_mic.columns]
        
        if len(columnas_existentes) == 3:
            # Preparar el DataFrame para mostrar
            df_mostrar_microrred = df_resumen_aseg_por_mic[columnas_existentes].copy()
            
            # Limpiar datos numéricos
            df_mostrar_microrred = limpiar_y_preparar_dataframe(df_mostrar_microrred, ['Nro', 'Asegurados'])
            
            # Ordenar por número
            df_mostrar_microrred = df_mostrar_microrred.sort_values('Nro').reset_index(drop=True)
            
            st.subheader("👥 Listado de Asegurados por Microrred")
            
            # Configuración de AgGrid
            from st_aggrid import AgGrid, GridOptionsBuilder
            
            gb_microrred = GridOptionsBuilder.from_dataframe(df_mostrar_microrred)
            
            gb_microrred.configure_default_column(
                resizable=True,
                sortable=True,
                filter=True,
                wrapText=False,
                cellStyle={"fontSize": "16px", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontWeight": "300"},
                headerClass="header-microrred"
            )
            
            # Configurar columnas específicas con anchos FIJOS
            gb_microrred.configure_column(
                "Nro",
                headerName="N°",
                width=80,
                minWidth=80,
                maxWidth=80,
                type=["numericColumn"],
                cellStyle={"textAlign": "center", "fontWeight": "300", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "16px"}
            )
            
            gb_microrred.configure_column(
                "Microrred",
                headerName="Microrred",
                width=400,
                minWidth=400,
                maxWidth=400,
                cellStyle={"fontWeight": "300", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "16px"}
            )
            
            gb_microrred.configure_column(
                "Asegurados",
                headerName="Total Asegurados",
                width=150,
                minWidth=150,
                maxWidth=150,
                type=["numericColumn"],
                cellStyle={"textAlign": "right", "fontWeight": "300", "color": "#007ACC", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "16px"}
            )
            
            # Configurar opciones del grid
            gb_microrred.configure_grid_options(
                rowHeight=35,
                headerHeight=45,
                domLayout='normal',
                suppressColumnVirtualisation=True
            )
            
            grid_options_microrred = gb_microrred.build()
            
            # CSS personalizado con Bahnschrift Light y fuente más grande
            custom_css_microrred = {
                ".ag-theme-streamlit": {
                    "--ag-font-size": "16px",
                    "--ag-header-height": "45px",
                    "--ag-row-height": "35px",
                    "--ag-header-background-color": "#f0f2f6",
                    "--ag-odd-row-background-color": "#fafafa",
                    "--ag-font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                },
                ".ag-header-cell-label": {
                    "font-size": "16px",
                    "font-weight": "400",
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif"
                },
                ".ag-header-cell-text": {
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                    "font-weight": "400",
                    "font-size": "16px"
                },
                ".ag-cell": {
                    "display": "flex",
                    "align-items": "center",
                    "line-height": "1.3",
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                    "font-weight": "300",
                    "font-size": "16px"
                },
                ".header-microrred": {
                    "font-size": "16px !important",
                    "font-weight": "400 !important",
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif !important",
                    "background-color": "#f0f2f6 !important"
                },
                ".ag-root-wrapper": {
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                },
                ".ag-row": {
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                    "font-weight": "300"
                }
            }
            
            # CALCULAR ALTURA EXACTA
            num_registros = len(df_mostrar_microrred)
            altura_header = 45
            altura_fila = 35
            altura_total = altura_header + (num_registros * altura_fila)
            
            # Añadir un pequeño margen extra para mejor visualización
            altura_total_con_margen = altura_total + 10
            
            st.write(f"**Mostrando {num_registros} registros**")
            
            # Mostrar la tabla con altura calculada
            AgGrid(
                df_mostrar_microrred,
                gridOptions=grid_options_microrred,
                height=altura_total_con_margen,
                theme='streamlit',
                custom_css=custom_css_microrred,
                enable_enterprise_modules=False,
                key="grid_microrred"
            )
            
            # Mostrar métricas resumen
            st.subheader("📊 Resumen de Asegurados por Microrred")
            
            # CSS para las métricas con fuente más grande
            st.markdown("""
            <style>
            .stMetric {
                font-family: 'Bahnschrift Light', 'Segoe UI', sans-serif !important;
            }
            .stMetric label {
                font-family: 'Bahnschrift Light', 'Segoe UI', sans-serif !important;
                font-weight: 300 !important;
                font-size: 16px !important;
            }
            .stMetric value {
                font-family: 'Bahnschrift Light', 'Segoe UI', sans-serif !important;
                font-weight: 400 !important;
                font-size: 18px !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_microrredes = len(df_mostrar_microrred)
                st.metric("Total Microrredes", f"{total_microrredes}")
            
            with col2:
                total_asegurados = df_mostrar_microrred['Asegurados'].sum()
                st.metric("Total Asegurados", f"{total_asegurados:,}")
            
            with col3:
                promedio_por_microrred = total_asegurados / total_microrredes if total_microrredes > 0 else 0
                st.metric("Promedio por Microrred", f"{promedio_por_microrred:,.0f}")
            
            # Botón para descargar datos
            st.subheader("💾 Exportar Datos")
            
            # Exportar a Excel en lugar de CSV
            excel_microrred = io.BytesIO()
            with pd.ExcelWriter(excel_microrred, engine='openpyxl') as writer:
                df_mostrar_microrred.to_excel(writer, sheet_name='Asegurados_Microrred', index=False)
            excel_microrred.seek(0)
            
            st.download_button(
                label="📥 Descargar listado de asegurados por microrred en Excel",
                data=excel_microrred,
                file_name="asegurados_por_microrred.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        else:
            st.error(f"Faltan columnas requeridas. Columnas disponibles: {list(df_resumen_aseg_por_mic.columns)}")
            st.info("Las columnas requeridas son: Nro, Microrred, Asegurados")
            
            # Mostrar una vista previa de los datos para debugging
            st.subheader("🔍 Vista previa de los datos disponibles")
            st.dataframe(df_resumen_aseg_por_mic.head())

    import streamlit as st
    import pandas as pd
    import io
    from st_aggrid import AgGrid, GridOptionsBuilder

    # LIENZO ASEGURADOS POR ESTABLECIMIENTO DE SALUD
    st.header("🏥 Asegurados por Establecimiento de Salud")

    # Verificar si hay datos disponibles y que sea un DataFrame
    if (not hasattr(df_resumen_aseg_por_eess, 'columns') or 
        df_resumen_aseg_por_eess.empty or 
        not isinstance(df_resumen_aseg_por_eess, pd.DataFrame)):
        
        st.error("❌ No hay datos disponibles de asegurados por EESS o hubo un error en la carga.")
        st.info("Los datos de asegurados por establecimiento no se pudieron cargar correctamente.")
        
    else:
        # Asegurarnos de que las columnas estén limpias
        df_resumen_aseg_por_eess.columns = df_resumen_aseg_por_eess.columns.str.strip()
        
        # Verificar que las columnas requeridas existan
        columnas_requeridas = ['Nro', 'Red', 'Microrred', 'Uni_func', 'Ppdd', 'Renaes', 'Eess', 'Asegurados']
        columnas_existentes = [col for col in columnas_requeridas if col in df_resumen_aseg_por_eess.columns]
        
        if len(columnas_existentes) == 8:
            # Preparar el DataFrame para mostrar
            df_mostrar_eess = df_resumen_aseg_por_eess[columnas_existentes].copy()
            
            # Limpiar datos numéricos
            df_mostrar_eess = limpiar_y_preparar_dataframe(df_mostrar_eess, ['Nro', 'Renaes', 'Asegurados'])
            
            # Ordenar por número
            df_mostrar_eess = df_mostrar_eess.sort_values('Nro').reset_index(drop=True)
            
            st.subheader("👥 Listado de Asegurados por Establecimiento de Salud")
            
            # BÚSQUEDA INTERACTIVA POR EESS
            st.subheader("🔍 Búsqueda por Establecimiento de Salud")
            
            col_busqueda1, col_busqueda2 = st.columns([2, 1])
            
            with col_busqueda1:
                # Cuadro de búsqueda interactivo
                busqueda_eess = st.text_input(
                    "Escriba el nombre del establecimiento:",
                    placeholder="Comience a escribir el nombre del EESS...",
                    key="busqueda_eess"
                )
            
            with col_busqueda2:
                st.write("")  # Espaciador
                st.write("")  # Espaciador
                # Botón para limpiar búsqueda
                if st.button("🧹 Limpiar Búsqueda", key="limpiar_busqueda_eess"):
                    busqueda_eess = ""
                    st.rerun()
            
            # Filtrar datos según la búsqueda
            if busqueda_eess:
                df_filtrado = df_mostrar_eess[
                    df_mostrar_eess['Eess'].str.contains(busqueda_eess, case=False, na=False)
                ]
            else:
                df_filtrado = df_mostrar_eess.copy()
            
            # Configuración de AgGrid
            gb_eess = GridOptionsBuilder.from_dataframe(df_filtrado)
            
            # CONFIGURACIÓN GLOBAL MÁS ESTRICTA
            gb_eess.configure_default_column(
                resizable=True,
                sortable=True,
                filter=True,
                wrapText=True,
                autoHeight=False,
                suppressSizeToFit=False,
                cellStyle={"fontSize": "14px", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontWeight": "300"},
                headerClass="header-eess"
            )
            
            # Configurar columnas específicas con anchos FIJOS
            gb_eess.configure_column(
                "Nro",
                headerName="N°",
                width=60,
                minWidth=60,
                maxWidth=60,
                type=["numericColumn"],
                resizable=False,
                suppressSizeToFit=True,
                cellStyle={"textAlign": "center", "fontWeight": "300", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "14px"}
            )
            
            gb_eess.configure_column(
                "Red",
                headerName="Red",
                width=120,
                minWidth=120,
                maxWidth=120,
                resizable=False,
                suppressSizeToFit=True,
                cellStyle={"fontWeight": "300", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "14px"}
            )
            
            gb_eess.configure_column(
                "Microrred",
                headerName="Microrred",
                width=150,
                minWidth=150,
                maxWidth=150,
                resizable=False,
                suppressSizeToFit=True,
                cellStyle={"fontWeight": "300", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "14px"}
            )
            
            gb_eess.configure_column(
                "Uni_func",
                headerName="Unidad Funcional",
                width=150,
                minWidth=150,
                maxWidth=150,
                resizable=False,
                suppressSizeToFit=True,
                cellStyle={"fontWeight": "300", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "14px"}
            )
            
            # COLUMNA PPDD CON ANCHO FIJO DE 300 - SOLUCIÓN ESPECÍFICA
            gb_eess.configure_column(
                "Ppdd",
                headerName="PPDD",
                width=300,
                minWidth=300,
                maxWidth=300,
                resizable=False,
                suppressSizeToFit=True,
                suppressAutoSize=True,
                cellStyle={
                    "fontWeight": "300", 
                    "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", 
                    "fontSize": "14px",
                    "whiteSpace": "normal",
                    "wordWrap": "break-word"
                }
            )
            
            gb_eess.configure_column(
                "Renaes",
                headerName="RENAES",
                width=100,
                minWidth=100,
                maxWidth=100,
                type=["numericColumn"],
                resizable=False,
                suppressSizeToFit=True,
                cellStyle={"textAlign": "center", "fontWeight": "300", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "14px"}
            )
            
            gb_eess.configure_column(
                "Eess",
                headerName="Establecimiento de Salud",
                width=300,
                minWidth=300,
                maxWidth=300,
                resizable=False,
                suppressSizeToFit=True,
                cellStyle={"fontWeight": "300", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "14px"}
            )
            
            gb_eess.configure_column(
                "Asegurados",
                headerName="Total Asegurados",
                width=120,
                minWidth=120,
                maxWidth=120,
                type=["numericColumn"],
                resizable=False,
                suppressSizeToFit=True,
                cellStyle={"textAlign": "right", "fontWeight": "300", "color": "#007ACC", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "14px"}
            )
            
            # Configurar opciones del grid para EVITAR autoajuste
            gb_eess.configure_grid_options(
                rowHeight=35,
                headerHeight=45,
                domLayout='normal',
                suppressColumnVirtualisation=True,
                ensureDomOrder=True,
                suppressAutoSize=True,
                suppressSizeToFit=False
            )
            
            grid_options_eess = gb_eess.build()
            
            # CSS personalizado con Bahnschrift Light
            custom_css_eess = {
                ".ag-theme-streamlit": {
                    "--ag-font-size": "14px",
                    "--ag-header-height": "45px",
                    "--ag-row-height": "35px",
                    "--ag-header-background-color": "#f0f2f6",
                    "--ag-odd-row-background-color": "#fafafa",
                    "--ag-font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                    "--ag-cell-horizontal-padding": "8px",
                },
                ".ag-header-cell-label": {
                    "font-size": "14px",
                    "font-weight": "400",
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif"
                },
                ".ag-header-cell-text": {
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                    "font-weight": "400",
                    "font-size": "14px"
                },
                ".ag-cell": {
                    "display": "flex",
                    "align-items": "center",
                    "line-height": "1.3",
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                    "font-weight": "300",
                    "font-size": "14px",
                    "padding-left": "8px",
                    "padding-right": "8px"
                },
                ".header-eess": {
                    "font-size": "14px !important",
                    "font-weight": "400 !important",
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif !important",
                    "background-color": "#f0f2f6 !important"
                },
                ".ag-root-wrapper": {
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                },
                ".ag-row": {
                    "font-family": "'Bahnschrift Light', 'Segoe UI', sans-serif",
                    "font-weight": "300"
                }
            }
            
            # CALCULAR ALTURA EXACTA con límite máximo
            num_registros = len(df_filtrado)
            altura_header = 45
            altura_fila = 35
            altura_total = altura_header + (num_registros * altura_fila)
            
            # Establecer altura máxima para evitar tablas demasiado largas
            altura_maxima = 600
            altura_final = min(altura_total, altura_maxima)
            
            # Añadir un pequeño margen extra para mejor visualización
            altura_final_con_margen = altura_final + 10
            
            # Mostrar información de registros
            if num_registros > 0:
                # Mostrar la tabla PRIMERO
                AgGrid(
                    df_filtrado,
                    gridOptions=grid_options_eess,
                    height=altura_final_con_margen,
                    theme='streamlit',
                    custom_css=custom_css_eess,
                    enable_enterprise_modules=False,
                    key="grid_eess"
                )
                
                # LUEGO mostrar los resultados de búsqueda DEBAJO del cuadro
                if busqueda_eess:
                    st.info(f"🔍 **{len(df_filtrado)}** establecimientos encontrados para: **'{busqueda_eess}'**")
                else:
                    st.info(f"📊 Mostrando todos los **{len(df_filtrado)}** establecimientos")
                
                if altura_total > altura_maxima:
                    st.warning(f"⚠️ Se muestran los primeros {int((altura_maxima - altura_header) / altura_fila)} registros. Use la búsqueda para filtrar resultados.")
                
            else:
                st.warning("🚫 No se encontraron establecimientos que coincidan con la búsqueda.")
                # Mostrar mensaje específico cuando no hay resultados
                if busqueda_eess:
                    st.info(f"🔍 **0** establecimientos encontrados para: **'{busqueda_eess}'**")
            
            # Mostrar métricas resumen
            st.subheader("📊 Resumen de Asegurados por EESS")
            
            # CSS para las métricas
            st.markdown("""
            <style>
            .stMetric {
                font-family: 'Bahnschrift Light', 'Segoe UI', sans-serif !important;
            }
            .stMetric label {
                font-family: 'Bahnschrift Light', 'Segoe UI', sans-serif !important;
                font-weight: 300 !important;
                font-size: 16px !important;
            }
            .stMetric value {
                font-family: 'Bahnschrift Light', 'Segoe UI', sans-serif !important;
                font-weight: 400 !important;
                font-size: 18px !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_eess = len(df_filtrado)
                st.metric("Total EESS", f"{total_eess}")
            
            with col2:
                total_asegurados = df_filtrado['Asegurados'].sum()
                st.metric("Total Asegurados", f"{total_asegurados:,}")
            
            with col3:
                promedio_por_eess = total_asegurados / total_eess if total_eess > 0 else 0
                st.metric("Promedio por EESS", f"{promedio_por_eess:,.0f}")
                
            with col4:
                if busqueda_eess:
                    porcentaje_total = (total_asegurados / df_mostrar_eess['Asegurados'].sum()) * 100 if len(df_mostrar_eess) > 0 else 0
                    st.metric("% del Total", f"{porcentaje_total:.1f}%")
                else:
                    max_asegurados = df_filtrado['Asegurados'].max() if len(df_filtrado) > 0 else 0
                    st.metric("Máximo Asegurados", f"{max_asegurados:,}")
            
            # BOTÓN PARA DESCARGAR DATOS EN EXCEL
            st.subheader("💾 Exportar Datos")
            
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                # Exportar datos filtrados a Excel
                excel_filtrado = io.BytesIO()
                with pd.ExcelWriter(excel_filtrado, engine='openpyxl') as writer:
                    df_filtrado.to_excel(writer, sheet_name='Asegurados_Filtrados', index=False)
                excel_filtrado.seek(0)
                
                st.download_button(
                    label="📥 Descargar datos filtrados en Excel",
                    data=excel_filtrado,
                    file_name="asegurados_por_eess_filtrado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="descarga_excel_eess"
                )
            
            with col_exp2:
                # Exportar todos los datos a Excel
                excel_completo = io.BytesIO()
                with pd.ExcelWriter(excel_completo, engine='openpyxl') as writer:
                    df_mostrar_eess.to_excel(writer, sheet_name='Asegurados_Completo', index=False)
                excel_completo.seek(0)
                
                st.download_button(
                    label="📥 Descargar todos los datos en Excel",
                    data=excel_completo,
                    file_name="asegurados_por_eess_completo.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="descarga_excel_completo_eess"
                )
                
        else:
            st.error(f"Faltan columnas requeridas. Columnas disponibles: {list(df_resumen_aseg_por_eess.columns)}")
            st.info("Las columnas requeridas son: Nro, Red, Microrred, Uni_func, Ppdd, Renaes, Eess, Asegurados")
            
            # Mostrar una vista previa de los datos para debugging
            st.subheader("🔍 Vista previa de los datos disponibles")
            st.dataframe(df_resumen_aseg_por_eess.head())


with tab3:
    # --- GRÁFICO DE BARRAS DINÁMICO - INDICADOR HIPERTENSIÓN ---
    with st.expander("📊 **INDICADOR DE HIPERTENSIÓN**", expanded=True):
        st.subheader("Filtros para el Indicador")
        
        # --- Filtros Mes y Año ---
        col1, col2 = st.columns(2)
        
        with col1:
            # Definir el orden cronológico de los meses
            orden_meses = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            
            # Obtener meses únicos del dataframe y ordenarlos cronológicamente
            meses_disponibles = df_indic_hiperten["Mes"].unique()
            meses_ordenados = [mes for mes in orden_meses if mes in meses_disponibles]
            
            mes_seleccionado = st.selectbox("Selecciona Mes", meses_ordenados)
        
        with col2:
            anios = df_indic_hiperten["Anio"].unique()
            anio_seleccionado = st.selectbox("Selecciona Año", sorted(anios, reverse=True))
        
        # --- Filtrar datos según selección ---
        df_filtrado = df_indic_hiperten[
            (df_indic_hiperten["Mes"] == mes_seleccionado) & 
            (df_indic_hiperten["Anio"] == anio_seleccionado)
        ].copy()
        
        # Verificar si hay datos después del filtrado
        if df_filtrado.empty:
            st.warning("No hay datos para los filtros seleccionados.")
        else:
            # CONVERTIR a porcentaje multiplicando por 100
            df_filtrado["Indicador_porcentaje"] = df_filtrado["Indicador"] * 100
            
            # Ordenar por indicador
            df_filtrado = df_filtrado.sort_values("Indicador_porcentaje", ascending=False)
            
            # --- GRÁFICO DE BARRAS con línea de meta ---
            st.subheader(f"📈 Indicador de Hipertensión - {mes_seleccionado} {anio_seleccionado}")
            
            # Crear figura
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # --- APLICAR COLORES SEGÚN EL PORCENTAJE ALCANZADO ---
            colores_barras = []
            for porcentaje in df_filtrado["Indicador_porcentaje"]:
                if porcentaje >= 40:  # Supera la meta (40%)
                    colores_barras.append('#00b050')  # Verde
                elif porcentaje >= 30:  # Se acerca a la meta (30-39.9%)
                    colores_barras.append('#ffcc66')  # Naranja/Amarillo
                elif porcentaje >= 15:  # Intermedio (15-29.9%)
                    colores_barras.append('#ff7c80')  # Rosa/Rojo claro
                else:  # Muy lejos de la meta (< 15%)
                    colores_barras.append('#ff0000')  # Rojo
            
            # Crear gráfico de barras - USANDO LOS COLORES SEGÚN EL DESEMPEÑO
            barras = ax.bar(df_filtrado["Microrred"], df_filtrado["Indicador_porcentaje"], 
                            color=colores_barras, alpha=0.7, width=0.6)
            
            # --- Línea de meta al 40% ---
            ax.axhline(y=40, color='red', linestyle='--', linewidth=3, label='Meta 40%')
            
            # --- Etiquetas en las barras ---
            for barra, valor, numerador, denominador in zip(barras, df_filtrado["Indicador_porcentaje"], 
                                                        df_filtrado["Numerador"], df_filtrado["Denominador"]):
                height = barra.get_height()
                ax.text(barra.get_x() + barra.get_width()/2., height + 1,
                        f'{valor:.1f}%\n({numerador}/{denominador})',
                        ha='center', va='bottom', fontsize=10, weight='bold', color='black',
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1))
            
            # --- Personalización del gráfico ---
            ax.set_title(f"Indicador de Hipertensión por Microrred - {mes_seleccionado} {anio_seleccionado}", 
                        fontsize=18, weight='bold', pad=20)
            ax.set_xlabel("Microrred", fontsize=14, weight='bold')
            ax.set_ylabel("Indicador (%)", fontsize=14, weight='bold')
            
            # Rotar etiquetas del eje X para mejor legibilidad
            plt.xticks(rotation=45, ha='right', fontsize=12)
            plt.yticks(fontsize=12)
            
            # Límites y grid
            y_max = max(df_filtrado["Indicador_porcentaje"].max() * 1.15, 50)
            ax.set_ylim(bottom=0, top=y_max)
            ax.grid(True, linestyle='--', alpha=0.3, axis='y')
            
            # Leyenda personalizada para los colores
            from matplotlib.patches import Patch
            leyenda_elementos = [
                Patch(facecolor='#00b050', label='≥ 40% (Supera la meta)'),
                Patch(facecolor='#ffcc66', label='30-39.9% (Se acerca a la meta)'),
                Patch(facecolor='#ff7c80', label='15-29.9% (Intermedio)'),
                Patch(facecolor='#ff0000', label='< 15% (Lejos de la meta)'),
                Patch(facecolor='none', edgecolor='red', linestyle='--', label='Meta 40%')
            ]
            ax.legend(handles=leyenda_elementos, loc='upper right', fontsize=10)
            
            # Ajustar layout
            plt.tight_layout()
            st.pyplot(fig)
            
            # --- MOSTRAR MÉTRICAS ---
            st.subheader("📊 Métricas del Indicador")
            
            # Calcular métricas
            promedio_indicador = df_filtrado["Indicador_porcentaje"].mean()
            maximo_indicador = df_filtrado["Indicador_porcentaje"].max()
            minimo_indicador = df_filtrado["Indicador_porcentaje"].min()
            total_pacientes = df_filtrado["Denominador"].sum()
            total_hipertensos = df_filtrado["Numerador"].sum()
            promedio_global = (total_hipertensos / total_pacientes) * 100 if total_pacientes > 0 else 0
            
            # Microrred con mejor y peor desempeño
            mejor_microrred = df_filtrado.loc[df_filtrado["Indicador_porcentaje"].idxmax()]
            peor_microrred = df_filtrado.loc[df_filtrado["Indicador_porcentaje"].idxmin()]
            
            # Crear columnas para las métricas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="📈 Promedio del Indicador",
                    value=f"{promedio_indicador:.1f}%",
                    delta=f"Meta: 40%",
                    delta_color="off"
                )
                
                st.metric(
                    label="👥 Total de Pacientes",
                    value=f"{total_pacientes:,}",
                    help="Total de pacientes en el denominador"
                )
            
            with col2:
                st.metric(
                    label="🎯 Mejor Desempeño",
                    value=f"{maximo_indicador:.1f}%",
                    label_visibility="visible"
                )
                st.write(f"**Microrred:** {mejor_microrred['Microrred']}")
                st.write(f"**Pacientes:** {mejor_microrred['Numerador']}/{mejor_microrred['Denominador']}")
                
            with col3:
                st.metric(
                    label="⚠️ Peor Desempeño",
                    value=f"{minimo_indicador:.1f}%",
                    label_visibility="visible"
                )
                st.write(f"**Microrred:** {peor_microrred['Microrred']}")
                st.write(f"**Pacientes:** {peor_microrred['Numerador']}/{peor_microrred['Denominador']}")
            
            # Métricas adicionales
            col4, col5 = st.columns(2)
            
            with col4:
                st.metric(
                    label="🫀 Total Hipertensos",
                    value=f"{total_hipertensos:,}",
                    help="Total de pacientes hipertensos identificados"
                )
            
            with col5:
                st.metric(
                    label="🌍 Promedio Global",
                    value=f"{promedio_global:.1f}%",
                    help="Porcentaje global (total hipertensos / total pacientes)"
                )
            
            # Mostrar cuántas microrredes superan la meta
            microrredes_sobre_meta = df_filtrado[df_filtrado["Indicador_porcentaje"] >= 40].shape[0]
            total_microrredes = df_filtrado.shape[0]
            porcentaje_sobre_meta = (microrredes_sobre_meta / total_microrredes) * 100
            
            st.info(f"**🏆 Desempeño General:** {microrredes_sobre_meta} de {total_microrredes} microrredes ({porcentaje_sobre_meta:.1f}%) superan la meta del 40%")