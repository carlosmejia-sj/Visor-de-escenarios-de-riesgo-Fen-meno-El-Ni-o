#pip install streamlit-folium
import streamlit as st
import pandas as pd
import folium
import os
import json
import altair as alt
from streamlit_folium import st_folium
import base64
from PIL import Image
import io

# =====================================================================
# 1. CONFIGURACIÓN DE PÁGINA
# =====================================================================
st.set_page_config(
    page_title="Visor de Escenarios de Riesgo — Fenómeno El Niño (UNGRD)",
    layout="wide",
    page_icon="🔥",
)

# =====================================================================
# 2. RUTAS BASE  (los datos siguen viniendo de Python / archivos locales)
# =====================================================================
DIRECTORIO_ACTUAL  = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_DATOS      = os.path.join(DIRECTORIO_ACTUAL, "datos_base_analisis.parquet")
GEOJSON_DEPTOS     = os.path.join(DIRECTORIO_ACTUAL, "colombia_departamentos.json")
GEOJSON_MUNICIPIOS = os.path.join(DIRECTORIO_ACTUAL, "colombia_municipios.json")
LOGO_UNGRD         = os.path.join(DIRECTORIO_ACTUAL, "LOGO_UNGRD.png")
HERO_CAMPANA       = os.path.join(DIRECTORIO_ACTUAL, "hero-incendio.jpg")

DIC_METRICAS = {
    "Frecuencia (Total eventos)": "FRECUENCIA",
    "Familias afectadas": "FAMILIAS",
    "Personas afectadas": "PERSONAS",
    "Acueductos afectados": "ACUED.",
    "Centros de salud afectados": "C.SALUD",
    "Vías afectadas": "VIAS",
    "Hectáreas afectadas": "HECTAREAS",
}


def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception:
        return None


# =====================================================================
# 3. ESTILOS  (rediseño visual — paleta de campaña UNGRD)
# =====================================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700;800;900&family=Anton&display=swap');

:root{
  --azul-inst:#222d5d; --amarillo:#ffd100;
  --ui-titulo:#003366; --ui-primario:#0154a5; --ui-link:#0056b3; --ui-label:#004085;
  --rojo:#e0121c; --teal:#17a2b8;
  --camp-naranja:#f07f1e; --camp-rojo:#e0121c;
  --gris-50:#f8f9fa; --gris-200:#e9ecef; --gris-300:#dee2e6; --gris-400:#ced4da;
  --gris-600:#6c757d; --gris-700:#495057; --tinta:#262730;
}

html, body, [class*="css"], .stMarkdown, p, div { font-family:'Source Sans 3','Segoe UI',system-ui,sans-serif; }

/* Reduce el espacio superior por defecto para el hero a sangre */
.block-container { padding-top:1rem !important; }

/* ---------- HERO DE CAMPAÑA ---------- */
.vz-hero{ position:relative; border-radius:10px; overflow:hidden; height:300px;
  background-size:cover; background-position:center 34%; margin-bottom:0; }
.vz-hero-scrim{ position:absolute; inset:0;
  background:linear-gradient(90deg,rgba(15,18,24,.66) 0%,rgba(15,18,24,.30) 40%,rgba(15,18,24,0) 62%),
             linear-gradient(0deg,rgba(15,18,24,.72) 0%,rgba(15,18,24,0) 44%); }
.vz-hero-logo{ position:absolute; top:18px; left:22px; background:#fff; border-radius:8px;
  padding:9px 13px; box-shadow:0 3px 12px rgba(0,0,0,.28); }
.vz-hero-logo img{ width:120px; display:block; }
.vz-hero-copy{ position:absolute; left:24px; bottom:22px; right:24px; }
.vz-hero-eyebrow{ display:inline-block; background:var(--camp-naranja); color:#fff;
  font-weight:800; font-size:11.5px; letter-spacing:.06em; text-transform:uppercase;
  padding:4px 11px; border-radius:4px; margin-bottom:12px; }
.vz-hero-title{ font-family:'Anton','Archivo Black',sans-serif; color:#fff;
  font-size:clamp(28px,3.4vw,44px); line-height:1.06; text-transform:uppercase;
  letter-spacing:.01em; text-shadow:0 2px 14px rgba(0,0,0,.45); max-width:900px; }
.vz-hero-title .hl{ color:var(--camp-naranja); }
.vz-hero-title .nb{ white-space:nowrap; }
.vz-hero-rule{ height:6px; border-radius:0 0 4px 4px; margin-bottom:14px;
  background:linear-gradient(90deg,var(--camp-rojo) 0%,var(--camp-naranja) 55%,var(--amarillo) 100%); }

.vz-subbar{ display:flex; align-items:center; justify-content:space-between; gap:14px; margin:2px 0 6px; }
.vz-subbar-t{ font-size:13.5px; font-weight:700; color:var(--gris-700); }
.vz-subbar-tag{ flex-shrink:0; white-space:nowrap; font-size:11px; font-weight:800; text-transform:uppercase;
  letter-spacing:.05em; color:#fff; background:var(--camp-rojo); padding:4px 11px; border-radius:4px; }

/* ---------- TÍTULOS DE SECCIÓN ---------- */
.seccion-titulo{ position:relative; color:var(--ui-link); font-weight:800; font-size:20px;
  text-transform:uppercase; letter-spacing:.02em; margin:22px 0 18px; padding-left:15px; line-height:1.25; }
.seccion-titulo::before{ content:""; position:absolute; left:0; top:3px; bottom:3px; width:5px;
  border-radius:3px; background:var(--camp-naranja); }

/* ---------- LABELS DE WIDGETS ---------- */
.stSelectbox label, .stRadio label, .stMultiSelect label, .stCheckbox label, .stDateInput label{
  font-weight:700 !important; color:var(--ui-label) !important; font-size:13.5px !important; }

/* ---------- KPI CARDS (rediseñadas) ---------- */
.kpi-card{ position:relative; background:#fff; border:1px solid var(--gris-200);
  border-left:5px solid var(--ui-link); border-radius:6px; padding:13px 12px 12px;
  box-shadow:0 1px 3px rgba(0,0,0,.07); text-align:left; height:100%;
  transition:box-shadow .15s, transform .15s; }
.kpi-card:hover{ box-shadow:0 4px 12px rgba(0,0,0,.12); transform:translateY(-1px); }
.kpi-titulo{ font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:.04em; color:var(--gris-600); }
.kpi-valor{ font-size:23px; font-weight:800; color:var(--rojo); margin-top:5px; line-height:1;
  font-variant-numeric:tabular-nums; letter-spacing:-.01em; }

/* ---------- IMPACTO HEADER ---------- */
.impacto-head{ font-size:18px; font-weight:800; color:var(--ui-titulo); margin:24px 0 14px; }

/* ---------- GLOSARIO + FOOTER ---------- */
.glosario-caja{ background:var(--gris-200); border-left:4px solid var(--teal); border-radius:5px;
  padding:14px 18px; font-size:13.5px; color:var(--gris-700); line-height:1.55; margin-top:34px; }
.footer{ background:var(--gris-50); border-top:2px solid var(--gris-300); border-radius:5px;
  margin-top:16px; padding:18px 20px; font-size:13px; color:var(--gris-700); }
.footer ul{ margin:8px 0; padding-left:20px; }
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================================
# 4. HERO DE CAMPAÑA  (encabezado institucional rediseñado)
# =====================================================================
hero_b64 = get_image_base64(HERO_CAMPANA)
logo_b64 = get_image_base64(LOGO_UNGRD)

hero_bg = f"background-image:url(data:image/jpeg;base64,{hero_b64});" if hero_b64 else "background:#003366;"
logo_html = (
    f'<div class="vz-hero-logo"><img src="data:image/png;base64,{logo_b64}" alt="UNGRD"></div>'
    if logo_b64 else ""
)

st.markdown(
    f"""
<div class="vz-hero" style="{hero_bg}">
  <div class="vz-hero-scrim"></div>
  {logo_html}
  <div class="vz-hero-copy">
    <span class="vz-hero-eyebrow">⚠ Conocimiento del Riesgo · UNGRD</span>
    <div class="vz-hero-title">Visor de escenarios de <span class="hl">riesgo</span> — <span class="nb">Fenómeno El Niño</span></div>
  </div>
</div>
<div class="vz-hero-rule"></div>
<div class="vz-subbar">
  <span class="vz-subbar-t">Tablero analítico y dinámico de afectaciones históricas por evento</span>
  <span class="vz-subbar-tag">Análogo Niño 2023–2024</span>
</div>
""",
    unsafe_allow_html=True,
)

# =====================================================================
# 5. FUNCIONES DE CARGA MAESTRAS  (sin cambios — datos reales)
# =====================================================================
@st.cache_data
def cargar_base_maestra():
    df = pd.read_parquet(ARCHIVO_DATOS)
    df = df[df['FECHA_DATETIME'] >= pd.to_datetime("2023-06-01")].copy()
    trim_map = {
        "JJA_2023": "junio-agosto_2023", "SON_2023": "septiembre-noviembre_2023",
        "DEF_2023_2024": "diciembre_2023-febrero_2024", "MAM_2024": "marzo-mayo_2024",
    }
    df['TRIMESTRE_FORMAL'] = df['PERIODO_TRIMESTRAL'].map(trim_map)
    return df


@st.cache_data
def cargar_geojsons():
    with open(GEOJSON_DEPTOS, 'r', encoding='utf-8') as f:
        geo_d = json.load(f)
    for feature in geo_d.get('features', []):
        feature['properties']['COD_GEO'] = str(feature['properties'].get('DPTO_CCDGO', '0')).zfill(2)
        feature['properties']['NOMBRE_GEO'] = feature['properties'].get('DPTO_CNMBR', 'Desconocido')

    with open(GEOJSON_MUNICIPIOS, 'r', encoding='utf-8') as f:
        geo_m = json.load(f)
    for feature in geo_m.get('features', []):
        cod = feature['properties'].get('MPIO_CCNCT') or feature['properties'].get('DPMP') or "0"
        feature['properties']['COD_GEO'] = str(cod).zfill(5)
        feature['properties']['NOMBRE_GEO'] = feature['properties'].get('MPIO_CNMBR', 'Desconocido')

    return geo_d, geo_m


df = cargar_base_maestra()
geo_deptos, geo_municipios = cargar_geojsons()

# =====================================================================
# 6. PANEL DE CONTROL  (sin cambios funcionales)
# =====================================================================
st.markdown("<h3 class='seccion-titulo'>Tablero analítico y dinámico como aporte a la definición de escenarios de riesgo</h3>", unsafe_allow_html=True)

# Filtros Temporales
st.markdown("**1. Configuración de temporalidad**")
tipo_filtro_temp = st.radio("Seleccione el alcance temporal:", ["Todo el periodo (personalizado)", "Por mes específico", "Por trimestre"], horizontal=True)
c_ft1, c_ft2, c_ft3 = st.columns(3)

if tipo_filtro_temp == "Todo el periodo (personalizado)":
    f_ini, f_fin = df['FECHA_DATETIME'].min().date(), df['FECHA_DATETIME'].max().date()
    with c_ft1: d_desde = st.date_input("Desde:", value=f_ini, min_value=f_ini, max_value=f_fin)
    with c_ft2: d_hasta = st.date_input("Hasta:", value=f_fin, min_value=f_ini, max_value=f_fin)
    mask_temporal = (df['FECHA_DATETIME'].dt.date >= d_desde) & (df['FECHA_DATETIME'].dt.date <= d_hasta)
    titulo_fecha = f"({d_desde} al {d_hasta})"
elif tipo_filtro_temp == "Por mes específico":
    with c_ft1: mes_sel = st.selectbox("Seleccione el mes:", sorted(df['PERIODO_MENSUAL'].unique()))
    mask_temporal = df['PERIODO_MENSUAL'] == mes_sel
    titulo_fecha = f"({mes_sel})"
else:
    with c_ft1: trim_sel = st.selectbox("Seleccione el trimestre:", sorted([t for t in df['TRIMESTRE_FORMAL'].unique() if pd.notna(t)]))
    mask_temporal = df['TRIMESTRE_FORMAL'] == trim_sel
    titulo_fecha = f"({trim_sel})"

# Filtros Geográficos y Climáticos
st.markdown("**2. Filtros climáticos y geográficos**")
c_f1, c_f2, c_f3 = st.columns([1, 2, 1])

with c_f1:
    cat_clima = st.selectbox("Categoría climática:", ["Todas", "Lluviosos", "Secos"])

eventos_disp = sorted(df[df['CATEGORIA_CLIMA'] == cat_clima]['EVENTO'].dropna().unique()) if cat_clima != "Todas" else sorted(df['EVENTO'].dropna().unique())

with c_f2:
    todos_evt = st.checkbox("Seleccionar todos los tipos de evento", value=True)
    if todos_evt:
        eventos_sel = eventos_disp
    else:
        eventos_sel = st.multiselect("Tipos de evento a evaluar (haga clic en la 'X' para quitar):", eventos_disp, default=eventos_disp)

with c_f3:
    deptos_reales = sorted([d for d in df['Nombre Departamento'].dropna().unique() if "BOGOTA" not in d])
    depto_sel = st.selectbox("Nivel geográfico (Departamento):", ["Todos (Nacional)"] + deptos_reales)

# Aplicar filtros
df_dinamico = df[mask_temporal].copy()
if cat_clima != "Todas": df_dinamico = df_dinamico[df_dinamico['CATEGORIA_CLIMA'] == cat_clima]
if eventos_sel: df_dinamico = df_dinamico[df_dinamico['EVENTO'].isin(eventos_sel)]

# Configurar Geometría
if depto_sel != "Todos (Nacional)":
    df_dinamico = df_dinamico[df_dinamico['Nombre Departamento'] == depto_sel]
    col_agrup, col_nom = 'Codigo Municipio', 'Nombre Municipio'
    geo_data_activa = {'type': 'FeatureCollection', 'features': []}
    if not df_dinamico.empty:
        cod_depto = df_dinamico['Codigo Departamento'].iloc[0]
        geo_data_activa['features'] = [f for f in geo_municipios['features'] if f['properties'].get('COD_GEO', '').startswith(cod_depto)]
    alias_geo, titulo_zoom = "Municipio:", f"Municipios de {depto_sel}"
else:
    col_agrup, col_nom = 'Codigo Departamento', 'Nombre Departamento'
    geo_data_activa, alias_geo, titulo_zoom = geo_deptos, "Departamento:", "Nacional (Departamentos)"

# =====================================================================
# 7. VISUALIZACIÓN
# =====================================================================
st.markdown(f"<div class='impacto-head'>📌 Impacto consolidado {titulo_fecha} — Nivel: {titulo_zoom}</div>", unsafe_allow_html=True)
k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-titulo'>Eventos</div><div class='kpi-valor'>{len(df_dinamico):,}</div></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-titulo'>Familias</div><div class='kpi-valor'>{int(df_dinamico['FAMILIAS'].sum()):,}</div></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-titulo'>Personas</div><div class='kpi-valor'>{int(df_dinamico['PERSONAS'].sum()):,}</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-titulo'>Acueductos</div><div class='kpi-valor'>{int(df_dinamico['ACUED.'].sum()):,}</div></div>", unsafe_allow_html=True)
with k5: st.markdown(f"<div class='kpi-card'><div class='kpi-titulo'>C. Salud</div><div class='kpi-valor'>{int(df_dinamico['C.SALUD'].sum()):,}</div></div>", unsafe_allow_html=True)
with k6: st.markdown(f"<div class='kpi-card'><div class='kpi-titulo'>Vías</div><div class='kpi-valor'>{int(df_dinamico['VIAS'].sum()):,}</div></div>", unsafe_allow_html=True)
with k7: st.markdown(f"<div class='kpi-card'><div class='kpi-titulo'>Hectáreas</div><div class='kpi-valor'>{int(df_dinamico['HECTAREAS'].sum()):,}</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_mapa, col_graficos = st.columns([0.5, 0.5])

with col_mapa:
    metrica_mapa_txt = st.selectbox("¿Qué variable específica desea mapear y graficar?", list(DIC_METRICAS.keys()))
    metrica_columna = DIC_METRICAS[metrica_mapa_txt]

    if metrica_columna == "FRECUENCIA":
        if cat_clima == "Todas": escala_c_fol, escala_c_alt = 'YlOrRd', 'yelloworangered'
        elif cat_clima == "Lluviosos": escala_c_fol, escala_c_alt = 'PuBu', 'tealblues'
        else: escala_c_fol, escala_c_alt = 'OrRd', 'orangered'
    else:
        if "HECTAREAS" in metrica_columna: escala_c_fol, escala_c_alt = 'YlGn', 'yellowgreen'
        elif "VIAS" in metrica_columna: escala_c_fol, escala_c_alt = 'PuRd', 'purplered'
        else: escala_c_fol, escala_c_alt = 'YlOrBr', 'yelloworangebrown'

    if not df_dinamico.empty and len(geo_data_activa['features']) > 0:
        if metrica_columna == "FRECUENCIA":
            agrup_dinamico = df_dinamico.groupby(col_agrup).size().reset_index(name='Valor')
        else:
            agrup_dinamico = df_dinamico.groupby(col_agrup)[metrica_columna].sum().reset_index(name='Valor')

        agrup_dinamico[col_agrup] = agrup_dinamico[col_agrup].astype(str)
        agrup_dinamico[col_agrup] = agrup_dinamico[col_agrup].str.zfill(2) if depto_sel == "Todos (Nacional)" else agrup_dinamico[col_agrup].str.zfill(5)

        m_dinamico = folium.Map(location=[4.5709, -74.2973], zoom_start=5, tiles="CartoDB positron", control_scale=True)

        # CSS inyectado: leyenda legible, sin traslapes, texto negro
        css_leyenda = """
        <style>
            svg text { fill: #000000 !important; font-weight: bold !important; font-size: 10px !important; }
            .legend { transform: scale(0.9); transform-origin: top right;
                      background-color: rgba(255,255,255,0.94) !important; border:1px solid #dee2e6 !important;
                      border-radius: 5px; padding: 6px 8px !important; box-shadow:0 2px 8px rgba(0,0,0,.14); }
        </style>
        """
        m_dinamico.get_root().html.add_child(folium.Element(css_leyenda))

        if agrup_dinamico['Valor'].sum() > 0:
            calc_bins = agrup_dinamico['Valor'].quantile([0, 0.25, 0.5, 0.75, 1.0]).tolist()
            u_bins = sorted(list(set(calc_bins)))
            cp = folium.Choropleth(
                geo_data=geo_data_activa, name='choropleth', data=agrup_dinamico,
                columns=[col_agrup, 'Valor'], key_on='feature.properties.COD_GEO',
                fill_color=escala_c_fol, fill_opacity=0.8, line_opacity=0.3,
                legend_name=metrica_mapa_txt, bins=u_bins if len(u_bins) >= 4 else 4,
            ).add_to(m_dinamico)

            for s in cp.geojson.data['features']:
                val = agrup_dinamico.loc[agrup_dinamico[col_agrup] == s['properties']['COD_GEO'], 'Valor'].values
                s['properties']['Met'] = int(val[0]) if len(val) > 0 else 0

            estilo = "font-size: 11px; font-family: sans-serif; padding: 5px; background: rgba(255,255,255,0.9); border: 1px solid #005; border-radius: 4px; z-index: 99999; color: black;"
            folium.GeoJsonTooltip(['NOMBRE_GEO', 'Met'], aliases=[alias_geo, f'{metrica_mapa_txt}:'], style=estilo).add_to(cp.geojson)

            if depto_sel != "Todos (Nacional)": m_dinamico.fit_bounds(cp.get_bounds())
            st_folium(m_dinamico, width=500, height=450, returned_objects=[])
        else:
            st.warning(f"No hay registros de {metrica_mapa_txt.lower()} para esta selección.")
    else:
        st.info("Sin datos para dibujar el mapa.")

with col_graficos:
    if not df_dinamico.empty:
        if metrica_columna == "FRECUENCIA":
            df_top = df_dinamico[col_nom].value_counts().reset_index()
            df_top.columns = ['Territorio', 'Valor']
        else:
            df_top = df_dinamico.groupby(col_nom)[metrica_columna].sum().reset_index()
            df_top.columns = ['Territorio', 'Valor']

        df_top = df_top[df_top['Valor'] > 0].sort_values('Valor', ascending=False)

        if not df_top.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_top.to_excel(writer, index=False, sheet_name='Ranking')

            st.download_button(
                label=f"📥 Descargar ranking de {metrica_mapa_txt.lower()} en Excel",
                data=buffer.getvalue(),
                file_name=f"Ranking_{metrica_mapa_txt}_{depto_sel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

            chart1 = alt.Chart(df_top.head(10)).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X('Valor:Q', title=metrica_mapa_txt),
                y=alt.Y('Territorio:N', sort='-x', title='', axis=alt.Axis(labelLimit=500, labelFontSize=11)),
                color=alt.Color('Valor:Q', scale=alt.Scale(scheme=escala_c_alt), legend=None),
                tooltip=['Territorio', 'Valor'],
            ).properties(
                height=350,
                title=alt.TitleParams(text=f"Top 10 — {titulo_zoom}"),
            ).configure_axis(
                labelColor='black', titleColor='black', tickColor='black', domainColor='black',
            ).configure_title(color='black')

            st.altair_chart(chart1, use_container_width=True)

# =====================================================================
# 8. PIE DE PÁGINA GLOBAL CON GLOSARIO
# =====================================================================
st.markdown(
    """
<div class="glosario-caja">
    <b>📖 Clasificación climática de eventos:</b><br>
    <b>🌧️ Condiciones lluviosas:</b> Avenida torrencial, creciente súbita, granizada, inundación, movimiento en masa, tormenta eléctrica, vendaval.<br>
    <b>☀️ Condiciones secas:</b> Desabastecimiento de agua, helada, incendio forestal, racionamiento, sequía.
</div>
<div class="footer">
    <b>Fuentes y créditos técnicos:</b>
    <ul>
        <li>Reportes de emergencias históricos de la Subdirección para el Conocimiento del Riesgo (UNGRD).</li>
        <li>Librerías de análisis y visualización (Streamlit, Pandas, Folium, Altair, PIL).</li>
        <li>Geografía oficial DANE (DIVIPOLA).</li>
    </ul>
    <b>Realizado por:</b> Christian Euscátegui. (SCR/UNGRD).<br>
    <b>Elaboración:</b> Mayo de 2026.
</div>
""",
    unsafe_allow_html=True,
)
