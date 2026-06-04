# Visor de Escenarios de Riesgo — Fenómeno El Niño (UNGRD)
### App de Streamlit rediseñado · backend de datos en Python intacto

Esta versión **conserva el mismo motor de datos en Python** del visor original
(`datos_base_analisis.parquet` → pandas → Folium + Altair) y aplica encima el
**rediseño visual** de campaña: hero "Frente al Fenómeno de El Niño", título con
tipografía Anton, KPIs pulidos, leyenda del mapa legible y crédito a
*Christian Euscátegui*.

> Los datos NO cambian ni se vuelven sintéticos: se leen en vivo desde el
> parquet con pandas, igual que antes. Solo cambia la presentación.

---

## Cómo integrarlo en tu repositorio

Tu repositorio `visor-nino-2026-2027` ya contiene los datos. Solo tienes que:

1. **Reemplazar** tu `08_visor_dinamico.py` por el de esta carpeta.
2. **Copiar** `hero-incendio.jpg` a la **raíz del repo** (junto al `.py`).
3. (Opcional) usar este `requirements.txt` — es idéntico al tuyo.

Estructura final esperada en la raíz del repo:

```
08_visor_dinamico.py            ← reemplazado (rediseño)
hero-incendio.jpg               ← NUEVO (hero de campaña)
datos_base_analisis.parquet     ← ya existe
colombia_departamentos.json     ← ya existe
colombia_municipios.json        ← ya existe
LOGO_UNGRD.png                  ← ya existe
requirements.txt                ← ya existe
.streamlit/config.toml          ← ya existe
```

## Desplegar

**Streamlit Community Cloud:** conecta el repo en https://share.streamlit.io y
apunta a `08_visor_dinamico.py`.

**Local:**
```bash
pip install -r requirements.txt
streamlit run 08_visor_dinamico.py
```

## Qué cambió exactamente

| Capa | Estado |
|---|---|
| Carga de datos (`cargar_base_maestra`, `cargar_geojsons`) | **Sin cambios** |
| Filtros temporales/climáticos/geográficos | **Sin cambios** |
| Agregaciones, mapa Folium, ranking Altair, Excel | **Sin cambios** |
| Encabezado / hero | Rediseñado (imagen de campaña + título Anton) |
| Tarjetas KPI | Rediseñadas (jerarquía, hover, números tabulares) |
| CSS de leyenda del mapa | Mejorado (opaco, sin traslapes) |
| Pie de página | Conserva crédito a Christian Euscátegui |
