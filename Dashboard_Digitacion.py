import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
import requests
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import io

# CONFIGURACIÓN DE PÁGINA PARA HACERLA MÁS ANCHA
st.set_page_config(
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🔹 Crear las pestañas ---
tab1, tab2, tab3 = st.tabs(["📊 Digitación SIS", "📅 Asegurados", "📈 Indicadores"])

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

# CSS GLOBAL PARA TÍTULOS EN NEGRO
st.markdown("""
<style>
    /* FORZAR TODOS LOS TÍTULOS A SER NEGROS */
    h1, h2, h3, h4, h5, h6 {
        color: black !important;
        background: none !important;
        -webkit-background-clip: initial !important;
        -webkit-text-fill-color: black !important;
        background-clip: initial !important;
    }
    
    .stHeader {
        color: black !important;
    }
    
    /* Títulos específicos de Streamlit */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: black !important;
        background: none !important;
    }
    
    /* Sobrescribir cualquier otro estilo */
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 {
        color: black !important;
        background: none !important;
        -webkit-background-clip: initial !important;
        -webkit-text-fill-color: black !important;
    }
</style>
""", unsafe_allow_html=True)

# 🟦 TAB 1: Dashboard Digitación
with tab1:
    st.header("📈 Dashboard Digitación ARFSIS Web")
    
    # --- Cargar archivos desde Drive ---
    url_excel_digitacion = "https://drive.google.com/uc?id=1TvDHKdACvOyheNCdNGZ_nt_yZcaLrYrC"
    url_excel_mensual = "https://docs.google.com/spreadsheets/d/1UKKeYJ2XtzEkPvntDqQLUJUrg0NJCnvP/export?format=xlsx"    
    url_excel_anual = "https://docs.google.com/spreadsheets/d/1UKKeYJ2XtzEkPvntDqQLUJUrg0NJCnvP/export?format=xlsx"
    url_excel_resumen_aseg = "https://docs.google.com/spreadsheets/d/1uD9DrmrjCpsjh0faK04glBG2yrz3_nnY/export?format=xlsx"       
    url_indic_hiperten = "https://docs.google.com/spreadsheets/d/1EAar2Uvf8CeNF6tQDURUgGvQdc3HWG41/export?format=xlsx"       

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
            url_data = requests.get(url_excel_anual).content
            df = pd.read_excel(BytesIO(url_data), sheet_name='Data_Anual', engine='openpyxl')
            return df
        except Exception as e:
            st.error(f"Error cargando datos anuales: {e}")
            return pd.DataFrame()               

    # Cargar ambos datasets
    with st.spinner('Cargando datos de digitación...'):
        df_digitacion = cargar_datos_digitacion()

    with st.spinner('Cargando datos mensuales...'):
        df_mensual = cargar_datos_mensual()

    with st.spinner('Cargando datos anuales...'):
        df_anual = cargar_datos_anual()

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

    # Limpiar nombres de columnas
    df_digitacion.columns = df_digitacion.columns.str.strip()
    df_mensual.columns = df_mensual.columns.str.strip()
    df_anual.columns = df_anual.columns.str.strip()

    # Mostrar información de éxito
    st.success("✅ Datos cargados correctamente")

    # Inicializar variables para las figuras
    fig1, fig2, fig3 = None, None, None

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
        
        if len(df_resumen) > 0:
            ax1.plot(df_resumen["Mesletras"], df_resumen["Cantidad"], marker='o', linewidth=3, color='#007ACC')
            
            # --- Etiquetas grandes y visibles ---
            max_val = max(df_resumen["Cantidad"])
            for i, val in enumerate(df_resumen["Cantidad"]):
                ax1.text(i, val + (max_val * 0.03), str(val),
                        ha='center', fontsize=12, weight='bold', color='black',
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=2))
            
            # --- Personalización del primer gráfico ---
            ax1.set_xlabel("Mes", fontsize=16, weight='bold')
            ax1.set_ylabel("Cantidad Total", fontsize=16, weight='bold')
            plt.xticks(fontsize=12, rotation=45)
            plt.yticks(fontsize=12)
            ax1.grid(True, linestyle='--', alpha=0.5)
            ax1.set_ylim(bottom=0)
            plt.subplots_adjust(top=0.85)
        else:
            ax1.text(0.5, 0.5, 'No hay datos disponibles', ha='center', va='center', transform=ax1.transAxes, fontsize=14)
        
        st.pyplot(fig1)

    # --- LIENZO 2: VISTA GENERAL ---
    with st.expander("🌐 **VISTA GENERAL - TODOS LOS PUNTOS**", expanded=True):
        st.subheader("Análisis Consolidado")
        
        # --- GRÁFICO 2: TOTAL GENERAL POR MES (TODOS LOS PPDD) ---
        st.subheader("📊 Total General por Mes (Todos los Puntos)")
        df_total_mes = df_digitacion.groupby(["Mes", "Mesletras"], as_index=False)["Cantidad"].sum()
        df_total_mes = df_total_mes.sort_values("Mes")
        
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        
        if len(df_total_mes) > 0:
            ax2.plot(df_total_mes["Mesletras"], df_total_mes["Cantidad"], marker='o', linewidth=3, color='#28a745')
            
            # --- Etiquetas para el total general (MODIFICADO) ---
            max_val = max(df_total_mes["Cantidad"])
            for i, val in enumerate(df_total_mes["Cantidad"]):
                ax2.text(i, val + (max_val * 0.03), f'{val:,}',
                        ha='center', fontsize=11, weight='bold', color='black',
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=2))
            
            # --- Personalización del segundo gráfico ---
            ax2.set_title("Total General de Cantidad por Mes (Todos los PPDD)", fontsize=14, weight='bold')
            ax2.set_xlabel("Mes", fontsize=16, weight='bold')
            ax2.set_ylabel("Cantidad Total", fontsize=16, weight='bold')
            plt.xticks(fontsize=12, rotation=45)
            plt.yticks(fontsize=12)
            ax2.grid(True, linestyle='--', alpha=0.5)
            ax2.set_ylim(bottom=0, top=80000)
            plt.subplots_adjust(top=0.85)
        else:
            ax2.text(0.5, 0.5, 'No hay datos disponibles', ha='center', va='center', transform=ax2.transAxes, fontsize=14)
        
        st.pyplot(fig2)

    # --- LIENZO 3: ANÁLISIS POR PERSONA ---
    with st.expander("👥 **ANÁLISIS POR PERSONA**", expanded=True):
        st.subheader("Desempeño Individual")
        
        # --- GRÁFICO 3: TENDENCIA POR PERSONA ---
        # Filtro por Ppdd para el gráfico de personas
        punto_personas = st.selectbox("Selecciona Punto de Digitación para ver Personas", puntos, key="personas")
        st.subheader("📊 Tendencia de Cantidad por Persona - " + punto_personas)            
        
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
            
        else:
            st.info("Por favor selecciona al menos una persona para visualizar el gráfico.")

    # --- LIENZO 4: LISTADO DE DATOS MENSUALES MEJORADO ---
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

                # FUNCIÓN PARA DETERMINAR COLOR DEL INDICADOR
                def obtener_color_indicador(val):
                    if val == 'N/A' or val is None:
                        return 'lightgray'
                    
                    try:
                        if isinstance(val, str) and '%' in val:
                            num_val = float(val.replace('%', '')) / 100
                        else:
                            num_val = float(val)
                        
                        if num_val >= 0.75:
                            return '#00b050'
                        elif num_val >= 0.60:
                            return '#ffcc66'
                        elif num_val >= 0.25:
                            return '#ff7c80'
                        else:
                            return '#ff0000'
                    except (ValueError, TypeError):
                        return 'lightgray'

                # FUNCIÓN PARA DETERMINAR COLOR DE TEXTO
                def obtener_color_texto(val):
                    if val == 'N/A' or val is None:
                        return 'black'
                    
                    try:
                        if isinstance(val, str) and '%' in val:
                            num_val = float(val.replace('%', '')) / 100
                        else:
                            num_val = float(val)
                        
                        if num_val >= 0.75:
                            return 'white'
                        elif num_val >= 0.60:
                            return 'black'
                        elif num_val >= 0.25:
                            return 'black'
                        else:
                            return 'white'
                    except (ValueError, TypeError):
                        return 'black'

                # CREAR TABLA HTML MEJORADA CON AUTO-AJUSTE Y ESTILO MÁS LLAMATIVO
                html_table = """
                <div style="font-size: 17px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                <table style="width: 100%; border-collapse: collapse; font-size: 17px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 10px; overflow: hidden;">
                    <thead>
                        <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                """
                
                # Encabezados de la tabla con auto-ajuste
                for col in df_mostrar_formateado.columns:
                    if col == 'N°':
                        html_table += f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; width: 60px;">{col}</th>'
                    elif col == 'CodPpdd':
                        html_table += f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; width: 100px;">{col}</th>'
                    elif col == 'Ppdd':
                        html_table += f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; width: auto;">{col}</th>'
                    elif col in ['Oportunos', 'Total_Fuas']:
                        html_table += f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; width: 120px;">{col}</th>'
                    elif col == 'Indicador':
                        html_table += f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; width: 100px;">{col}</th>'
                    else:
                        html_table += f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; width: auto;">{col}</th>'
                
                html_table += "</tr></thead><tbody>"
                
                # Filas de la tabla con efecto hover
                for idx, row in df_mostrar_formateado.iterrows():
                    row_bg = "#f9f9f9" if idx % 2 == 0 else "#ffffff"
                    html_table += f'<tr style="border: 1px solid #e0e0e0; background-color: {row_bg}; transition: all 0.3s ease;">'
                    
                    for i, (col, val) in enumerate(row.items()):
                        if col == 'Indicador':
                            bg_color = obtener_color_indicador(val)
                            text_color = obtener_color_texto(val)
                            html_table += f'<td style="padding: 10px; text-align: center; border: 1px solid #e0e0e0; font-size: 16px; font-weight: bold; background-color: {bg_color}; color: {text_color}; border-radius: 5px;">{val}</td>'
                        else:
                            html_table += f'<td style="padding: 10px; text-align: center; border: 1px solid #e0e0e0; font-size: 16px;">{val}</td>'
                    
                    html_table += '</tr>'
                
                html_table += """</tbody></table>
                <style>
                    table tbody tr:hover {
                        background-color: #f0f8ff !important;
                        transform: translateY(-1px);
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                </style>
                </div>"""
                
                # MOSTRAR TABLA HTML MEJORADA
                st.markdown(html_table, unsafe_allow_html=True)

                # Leyenda de colores con diseño mejorado
                st.markdown("""
                <div style="font-size: 16px; margin-top: 30px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <strong style="font-size: 18px; color: #2c3e50;">🎨 Leyenda de Indicadores:</strong><br><br>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    <span style='color: white; background-color: #00b050; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>Bueno (75-100%)</span>
                    <span style='color: black; background-color: #ffcc66; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>Regular (60-74%)</span>
                    <span style='color: black; background-color: #ff7c80; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>En Proceso (25-59%)</span>
                    <span style='color: white; background-color: #ff0000; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>Malo (0-24%)</span>
                    <span style='color: black; background-color: lightgray; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>Datos Inválidos</span>
                </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar información adicional con estilo mejorado
                st.markdown(f"""
                <div style="font-size: 14px; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 12px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #2196f3; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <strong>ℹ️ Información:</strong> Mostrando {len(df_mostrar_mensual)} registros del mes {mes_seleccionado} del Año {Año_seleccionado}, ordenados por Indicador (mayor a menor).
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.error("No se encontraron las columnas especificadas en el dataset.")
                st.write("Columnas disponibles en el dataset:", list(df_filtradomensual.columns))

            # CSS GLOBAL MEJORADO SOLO PARA ESTE LIENZO
            st.markdown("""
            <style>
            /* Hacer todo el texto de Streamlit más legible */
            .stApp {
                font-size: 16px !important;
            }
            
            /* Títulos en negro */
            h1, h2, h3 {
                font-size: 24px !important;
                color: black !important;
                background: none !important;
                -webkit-background-clip: initial !important;
                -webkit-text-fill-color: black !important;
                background-clip: initial !important;
                font-weight: bold !important;
            }
            
            /* Métricas con estilo mejorado */
            [data-testid="stMetricLabel"] {
                font-size: 14px !important;
                font-weight: bold !important;
                color: #2c3e50 !important;
            }
            [data-testid="stMetricValue"] {
                font-size: 28px !important;
                font-weight: bold !important;
            }
            [data-testid="stMetricDelta"] {
                font-size: 14px !important;
                font-weight: bold !important;
            }
            
            /* Selectboxes y controles mejorados */
            .stSelectbox label, .stSlider label {
                font-size: 14px !important;
                font-weight: bold !important;
                color: #2c3e50 !important;
            }
            
            /* Botones con estilo moderno */
            .stDownloadButton button {
                font-size: 14px !important;
                padding: 10px 20px !important;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 25px !important;
                font-weight: bold !important;
                transition: all 0.3s ease !important;
            }
            
            .stDownloadButton button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
            }
            
            /* Expander con estilo mejorado */
            .streamlit-expanderHeader {
                font-size: 18px !important;
                font-weight: bold !important;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
                border-radius: 10px !important;
                padding: 15px !important;
            }
            </style>
            """, unsafe_allow_html=True)

            # MOSTRAR MÉTRICAS DE RESUMEN CON ESTILO MEJORADO
            st.subheader(f"📈 Resumen - Mes {mes_seleccionado} / Año {Año_seleccionado}")
            
            # Contenedor para métricas con fondo gradiente
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_registros = len(df_filtradomensual)
                st.metric("Total de Registros", f"{total_registros:,}", delta_color="off")
            
            with col2:
                if 'Oportunos' in df_filtradomensual.columns:
                    oportunos_numerico = pd.to_numeric(df_filtradomensual['Oportunos'], errors='coerce').fillna(0)
                    total_oportunos = int(oportunos_numerico.sum())
                    st.metric("Total Oportunos", f"{total_oportunos:,}", delta_color="off")
                else:
                    st.metric("Total Oportunos", "N/A", delta_color="off")
            
            with col3:
                if 'Total_Fuas' in df_filtradomensual.columns:
                    fuas_numerico = pd.to_numeric(df_filtradomensual['Total_Fuas'], errors='coerce').fillna(0)
                    total_fuas = int(fuas_numerico.sum())
                    st.metric("Total FUAS", f"{total_fuas:,}", delta_color="off")
                else:
                    st.metric("Total FUAS", "N/A", delta_color="off")
            
            with col4:
                if 'Indicador' in df_filtradomensual.columns:
                    indicador_numerico = pd.to_numeric(df_filtradomensual['Indicador'], errors='coerce')
                    indicador_promedio = indicador_numerico.mean() * 100
                    st.metric("Indicador Promedio", f"{indicador_promedio:.1f}%", delta_color="off")
                else:
                    st.metric("Indicador Promedio", "N/A", delta_color="off")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Botón para descargar datos - CON ESTILO MEJORADO
            st.subheader("💾 Exportar Datos Filtrados")
            
            # Crear archivo Excel en memoria
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_filtradomensual.to_excel(writer, sheet_name='Datos_Mensuales', index=False)
            excel_buffer.seek(0)
            
            st.download_button(
                label="📥 Descargar listado filtrado en Excel",
                data=excel_buffer,
                file_name=f"datos_mensuales_{mes_seleccionado}_{Año_seleccionado}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # --- LIENZO 5: LISTADO DE DATOS ACUMULADOS ANUAL ---
    with st.expander("📊 **LISTADO DE DATOS ANUAL**", expanded=True):
        st.subheader("📋 Listado Completo de Datos Acumulado")
        
        # Verificar si hay datos en el dataset anual
        if df_anual.empty or len(df_anual) == 0:
            st.warning("No hay datos disponibles en el dataset anual.")
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

            # --- Mostrar advertencia si no hay datos ---
            if df_filtradoanual.empty:
                st.warning("No hay datos disponibles para ese mes y año.")
            else:
                # Ordenar por Indicador de mayor a menor si la columna existe
                if 'Indicador' in df_filtradoanual.columns:
                    df_filtradoanual = df_filtradoanual.sort_values('Indicador', ascending=False)
                else:
                    st.warning("No se encontró la columna 'Indicador' para ordenar")
                
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

                    # CREAR TABLA HTML MEJORADA CON AUTO-AJUSTE Y ESTILO MÁS LLAMATIVO (MISMO FORMATO QUE LIENZO 4)
                    html_table = """
                    <div style="font-size: 17px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 17px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 10px; overflow: hidden;">
                        <thead>
                            <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    """
                    
                    # Encabezados de la tabla con auto-ajuste
                    for col in df_mostrar_formateado_ac.columns:
                        if col == 'N°':
                            html_table += f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; width: 60px;">{col}</th>'
                        elif col == 'CodPpdd':
                            html_table += f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; width: 100px;">{col}</th>'
                        elif col == 'Ppdd':
                            html_table += f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; width: auto;">{col}</th>'
                        elif col in ['Oportunos', 'Total_Fuas']:
                            html_table += f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; width: 120px;">{col}</th>'
                        elif col == 'Indicador':
                            html_table += f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; width: 100px;">{col}</th>'
                        else:
                            html_table += f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-size: 18px; font-weight: bold; width: auto;">{col}</th>'
                    
                    html_table += "</tr></thead><tbody>"
                    
                    # Filas de la tabla con efecto hover
                    for idx, row in df_mostrar_formateado_ac.iterrows():
                        row_bg = "#f9f9f9" if idx % 2 == 0 else "#ffffff"
                        html_table += f'<tr style="border: 1px solid #e0e0e0; background-color: {row_bg}; transition: all 0.3s ease;">'
                        
                        for i, (col, val) in enumerate(row.items()):
                            if col == 'Indicador':
                                bg_color = obtener_color_indicador(val)
                                text_color = obtener_color_texto(val)
                                html_table += f'<td style="padding: 10px; text-align: center; border: 1px solid #e0e0e0; font-size: 16px; font-weight: bold; background-color: {bg_color}; color: {text_color}; border-radius: 5px;">{val}</td>'
                            else:
                                html_table += f'<td style="padding: 10px; text-align: center; border: 1px solid #e0e0e0; font-size: 16px;">{val}</td>'
                        
                        html_table += '</tr>'
                    
                    html_table += """</tbody></table>
                    <style>
                        table tbody tr:hover {
                            background-color: #f0f8ff !important;
                            transform: translateY(-1px);
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }
                    </style>
                    </div>"""
                    
                    # MOSTRAR TABLA HTML MEJORADA
                    st.markdown(html_table, unsafe_allow_html=True)

                    # Leyenda de colores con diseño mejorado (MISMO FORMATO QUE LIENZO 4)
                    st.markdown("""
                    <div style="font-size: 16px; margin-top: 30px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <strong style="font-size: 18px; color: #2c3e50;">🎨 Leyenda de Indicadores:</strong><br><br>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                        <span style='color: white; background-color: #00b050; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>Bueno (75-100%)</span>
                        <span style='color: black; background-color: #ffcc66; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>Regular (60-74%)</span>
                        <span style='color: black; background-color: #ff7c80; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>En Proceso (25-59%)</span>
                        <span style='color: white; background-color: #ff0000; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>Malo (0-24%)</span>
                        <span style='color: black; background-color: lightgray; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>Datos Inválidos</span>
                    </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Mostrar información adicional con estilo mejorado
                    st.markdown(f"""
                    <div style="font-size: 14px; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 12px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #2196f3; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <strong>ℹ️ Información:</strong> Mostrando {len(df_mostrar_anual)} registros del mes {mes_seleccionado_ac} del Año {Año_seleccionado_ac}, ordenados por Indicador (mayor a menor).
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    st.error("No se encontraron las columnas especificadas en el dataset.")
                    st.write("Columnas disponibles en el dataset:", list(df_filtradoanual.columns))

                # CSS GLOBAL MEJORADO SOLO PARA ESTE LIENZO (MISMO FORMATO QUE LIENZO 4)
                st.markdown("""
                <style>
                /* Hacer todo el texto de Streamlit más legible */
                .stApp {
                    font-size: 16px !important;
                }
                
                /* Títulos en negro */
                h1, h2, h3 {
                    font-size: 24px !important;
                    color: black !important;
                    background: none !important;
                    -webkit-background-clip: initial !important;
                    -webkit-text-fill-color: black !important;
                    background-clip: initial !important;
                    font-weight: bold !important;
                }
                
                /* Métricas con estilo mejorado */
                [data-testid="stMetricLabel"] {
                    font-size: 14px !important;
                    font-weight: bold !important;
                    color: #2c3e50 !important;
                }
                [data-testid="stMetricValue"] {
                    font-size: 28px !important;
                    font-weight: bold !important;
                }
                [data-testid="stMetricDelta"] {
                    font-size: 14px !important;
                    font-weight: bold !important;
                }
                
                /* Selectboxes y controles mejorados */
                .stSelectbox label, .stSlider label {
                    font-size: 14px !important;
                    font-weight: bold !important;
                    color: #2c3e50 !important;
                }
                
                /* Botones con estilo moderno */
                .stDownloadButton button {
                    font-size: 14px !important;
                    padding: 10px 20px !important;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 25px !important;
                    font-weight: bold !important;
                    transition: all 0.3s ease !important;
                }
                
                .stDownloadButton button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
                }
                
                /* Expander con estilo mejorado */
                .streamlit-expanderHeader {
                    font-size: 18px !important;
                    font-weight: bold !important;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
                    border-radius: 10px !important;
                    padding: 15px !important;
                }
                </style>
                """, unsafe_allow_html=True)

                # MOSTRAR MÉTRICAS DE RESUMEN CON ESTILO MEJORADO (MISMO FORMATO QUE LIENZO 4)
                st.subheader(f"📈 Resumen - Mes {mes_seleccionado_ac} / Año {Año_seleccionado_ac}")
                
                # Contenedor para métricas con fondo gradiente
                st.markdown("""
                <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_registros = len(df_filtradoanual)
                    st.metric("Total de Registros", f"{total_registros:,}", delta_color="off")
                
                with col2:
                    if 'Oportunos' in df_filtradoanual.columns:
                        oportunos_numerico = pd.to_numeric(df_filtradoanual['Oportunos'], errors='coerce').fillna(0)
                        total_oportunos = int(oportunos_numerico.sum())
                        st.metric("Total Oportunos", f"{total_oportunos:,}", delta_color="off")
                    else:
                        st.metric("Total Oportunos", "N/A", delta_color="off")
                
                with col3:
                    if 'Total_Fuas' in df_filtradoanual.columns:
                        fuas_numerico = pd.to_numeric(df_filtradoanual['Total_Fuas'], errors='coerce').fillna(0)
                        total_fuas = int(fuas_numerico.sum())
                        st.metric("Total FUAS", f"{total_fuas:,}", delta_color="off")
                    else:
                        st.metric("Total FUAS", "N/A", delta_color="off")
                
                with col4:
                    if 'Indicador' in df_filtradoanual.columns:
                        indicador_numerico = pd.to_numeric(df_filtradoanual['Indicador'], errors='coerce')
                        indicador_promedio = indicador_numerico.mean() * 100
                        st.metric("Indicador Promedio", f"{indicador_promedio:.1f}%", delta_color="off")
                    else:
                        st.metric("Indicador Promedio", "N/A", delta_color="off")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Botón para descargar datos - CON ESTILO MEJORADO (MISMO FORMATO QUE LIENZO 4)
                st.subheader("💾 Exportar Datos Filtrados")
                
                # Crear archivo Excel en memoria
                excel_buffer_anual = BytesIO()
                with pd.ExcelWriter(excel_buffer_anual, engine='openpyxl') as writer:
                    df_filtradoanual.to_excel(writer, sheet_name='Datos_Anuales', index=False)
                excel_buffer_anual.seek(0)
                
                st.download_button(
                    label="📥 Descargar listado filtrado en Excel",
                    data=excel_buffer_anual,
                    file_name=f"datos_anuales_{mes_seleccionado_ac}_{Año_seleccionado_ac}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    # --- LIENZO 6: EXPORTACIÓN DE DATOS ---
    with st.expander("💾 **EXPORTACIÓN DE DATOS**", expanded=False):
        st.subheader("Descargar Reportes")
        
        # --- Botón para PDF con todos los gráficos ---
        buffer = BytesIO()
        with PdfPages(buffer) as pdf:
            # Verificar que las figuras existan antes de guardarlas
            if fig1 is not None:
                fig1.savefig(pdf, format='pdf', bbox_inches='tight')
            if fig2 is not None:
                fig2.savefig(pdf, format='pdf', bbox_inches='tight')
            if fig3 is not None:
                fig3.savefig(pdf, format='pdf', bbox_inches='tight')
                
        buffer.seek(0)
        
        st.download_button(
            label="📄 Descargar todos los gráficos en PDF",
            data=buffer,
            file_name="graficos_digitacion_completo.pdf",
            mime="application/pdf"
        )
        
        # Botones adicionales para descargar datos en Excel - CAMBIADOS A XLSX
        col1, col2 = st.columns(2)
        with col1:
            # Crear archivo Excel para datos de digitación
            excel_digitacion = BytesIO()
            with pd.ExcelWriter(excel_digitacion, engine='openpyxl') as writer:
                df_digitacion.to_excel(writer, sheet_name='Datos_Digitacion', index=False)
            excel_digitacion.seek(0)
            
            st.download_button(
                label="📥 Descargar datos de digitación",
                data=excel_digitacion,
                file_name="datos_digitacion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col2:
            if not df_mensual.empty:
                # Crear archivo Excel para datos mensuales
                excel_mensual = BytesIO()
                with pd.ExcelWriter(excel_mensual, engine='openpyxl') as writer:
                    df_mensual.to_excel(writer, sheet_name='Datos_Mensuales', index=False)
                excel_mensual.seek(0)
                
                st.download_button(
                    label="📥 Descargar datos mensuales completos",
                    data=excel_mensual,
                    file_name="datos_mensuales_completos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("No hay datos mensuales para descargar")

# 🟦 TAB 2: Asegurados
with tab2:
    st.header("📅 Asegurados por Punto de Digitación")

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

    with st.spinner('Cargando datos resumen asegurados por PPDD...'):
        df_resumen_aseg_por_ppdd = cargar_datos_resumen_aseg_por_ppdd()            

    with st.spinner('Cargando datos resumen asegurados por EESS...'):
        df_resumen_aseg_por_eess = cargar_datos_resumen_aseg_por_eess()            

    with st.spinner('Cargando datos resumen asegurados por Microrred...'):
        df_resumen_aseg_por_mic = cargar_datos_resumen_aseg_por_mic()            

    if df_resumen_aseg_por_ppdd.empty:
        st.warning("No se pudieron cargar los datos de asegurados por PPDD. Algunas funciones no estarán disponibles.")
        df_resumen_aseg_por_ppdd = pd.DataFrame(columns=['Nro', 'Ppdd', 'Asegurados'])

    if df_resumen_aseg_por_mic.empty:
        st.warning("No se pudieron cargar los datos de asegurados por microrred. Algunas funciones no estarán disponibles.")
        df_resumen_aseg_por_mic = pd.DataFrame(columns=['Nro', 'Microrred','Asegurados'])

    if df_resumen_aseg_por_eess.empty:
        st.warning("No se pudieron cargar los datos de asegurados por EESS. Algunas funciones no estarán disponibles.")
        df_resumen_aseg_por_eess = pd.DataFrame(columns=['Nro', 'Red','Microrred','Uni_func','Ppdd','Renaes','Eess','Asegurados'])

    df_resumen_aseg_por_ppdd.columns = df_resumen_aseg_por_ppdd.columns.str.strip()
    df_resumen_aseg_por_eess.columns = df_resumen_aseg_por_eess.columns.str.strip()
    df_resumen_aseg_por_mic.columns = df_resumen_aseg_por_mic.columns.str.strip()

    # LIENZO 7 ASEGURADOS POR PUNTOS DE DIGITACION
    # st.header("👥 Asegurados por Punto de Digitación")
    
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
            gb_asegurados = GridOptionsBuilder.from_dataframe(df_mostrar_asegurados)
            
            gb_asegurados.configure_default_column(
                resizable=True,
                sortable=True,
                filter=True,
                wrapText=False,
                cellStyle={"fontSize": "16px", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontWeight": "300"},
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
                cellStyle={"textAlign": "center", "fontWeight": "300", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "16px"}
            )
            
            gb_asegurados.configure_column(
                "Ppdd",
                headerName="Punto de Digitación",
                width=400,
                minWidth=400,
                maxWidth=400,
                cellStyle={"fontWeight": "300", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "16px"}
            )
            
            gb_asegurados.configure_column(
                "Asegurados",
                headerName="Total Asegurados",
                width=150,
                minWidth=150,
                maxWidth=150,
                type=["numericColumn"],
                cellStyle={"textAlign": "right", "fontWeight": "300", "color": "#007ACC", "fontFamily": "'Bahnschrift Light', 'Segoe UI', sans-serif", "fontSize": "16px"}
            )
            
            # Configurar opciones del grid (aumentar ligeramente la altura de fila para la fuente más grande)
            gb_asegurados.configure_grid_options(
                rowHeight=35,
                headerHeight=45,
                domLayout='normal',
                suppressColumnVirtualisation=True
            )
            
            grid_options_asegurados = gb_asegurados.build()
            
            # CSS personalizado con Bahnschrift Light y fuente más grande
            custom_css_asegurados = {
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
                ".header-asegurados": {
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
            
            # CALCULAR ALTURA EXACTA PARA REGISTROS
            num_registros = len(df_mostrar_asegurados)
            altura_header = 45
            altura_fila = 35
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

# 🟦 TAB 3: Indicadores
with tab3:
    # --- GRÁFICO DE BARRAS DINÁMICO - INDICADOR HIPERTENSIÓN ---
    with st.expander("📊 **INDICADOR DE HIPERTENSIÓN**", expanded=True):
        st.subheader("Filtros para el Indicador")
        
        @st.cache_data
        def cargar_datos_indic_hiperten():
            try:
                url_data = requests.get(url_indic_hiperten).content
                df = pd.read_excel(BytesIO(url_data), sheet_name='Hoja1', engine='openpyxl')
                return df
            except Exception as e:
                st.error(f"Error cargando datos de Hipertensos: {e}")
                return pd.DataFrame()

        with st.spinner('Cargando datos resumen Hipertensos por EESS...'):
            df_indic_hiperten = cargar_datos_indic_hiperten()

        if df_indic_hiperten.empty:
            st.warning("No se pudieron cargar los datos de hipertensos. Algunas funciones no estarán disponibles.")
            df_indic_hiperten = pd.DataFrame(columns=['Nro','Microrred','Numerador','Denominador','Indicador','Mes','Anio'])

        # Limpiar nombres de columnas
        df_indic_hiperten.columns = df_indic_hiperten.columns.str.strip()

        # Verificar que las columnas necesarias existan
        required_columns = ['Mes', 'Anio', 'Microrred', 'Numerador', 'Denominador', 'Indicador']
        if all(col in df_indic_hiperten.columns for col in required_columns):
            
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
                
                if meses_ordenados:
                    mes_seleccionado = st.selectbox("Selecciona Mes", meses_ordenados)
                else:
                    mes_seleccionado = None
                    st.warning("No hay meses disponibles en los datos")
            
            with col2:
                anios = df_indic_hiperten["Anio"].unique()
                if len(anios) > 0:
                    anio_seleccionado = st.selectbox("Selecciona Año", sorted(anios, reverse=True))
                else:
                    anio_seleccionado = None
                    st.warning("No hay años disponibles en los datos")
            
            # --- Filtrar datos según selección ---
            if mes_seleccionado and anio_seleccionado:
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
            else:
                st.warning("Selecciona un mes y año válidos para ver los datos.")
        else:
            st.error("Las columnas necesarias no están disponibles en los datos de hipertensión")
            st.write("Columnas disponibles:", list(df_indic_hiperten.columns))