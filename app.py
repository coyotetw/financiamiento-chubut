import streamlit as st
import pandas as pd
import re

# ── CONFIGURACIÓN DE PÁGINA ──
st.set_page_config(
    page_title="Líneas de Financiamiento · Chubut",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ESTILOS CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.hero {
    background: linear-gradient(135deg, #20788C 0%, #0F5A6B 100%);
    border-radius: 14px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: white;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    margin: 0 0 .4rem 0;
}
.hero p { opacity: .75; margin: 0; font-size: 14px; }

.stat-box {
    background: white;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    border-top: 3px solid #20788C;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    text-align: center;
}
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #20788C;
    line-height: 1;
}
.stat-label { font-size: 12px; color: #888; margin-top: 4px; }

.card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: .75rem;
    border: 1.5px solid #E8E6E0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: border-color .2s;
}
.card:hover { border-color: #20788C; }
.card-name {
    font-family: 'Syne', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: #1A1A1A;
    margin-bottom: 6px;
}
.pill {
    display: inline-block;
    font-size: 11px;
    font-weight: 500;
    padding: 2px 10px;
    border-radius: 20px;
    margin-right: 5px;
    margin-bottom: 6px;
}
.pill-teal   { background:#E1F5EE; color:#0F6E56; }
.pill-orange { background:#FEF0EC; color:#C94020; }
.pill-blue   { background:#E6F1FB; color:#185FA5; }
.pill-amber  { background:#FEF5E0; color:#854F0B; }
.pill-pink   { background:#FBEAF0; color:#993356; }
.pill-green  { background:#EAF3DE; color:#3B6D11; }
.pill-gray   { background:#F1EFE8; color:#5F5E5A; }

.tasa-big {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
}
.tasa-low  { color: #1D9E75; }
.tasa-high { color: #C94040; }
.tasa-mid  { color: #20788C; }
.tasa-na   { color: #888; font-size: 1rem; }

.meta-key  { font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: .04em; }
.meta-val  { font-size: 13px; color: #1A1A1A; font-weight: 500; }
.obs-text  { font-size: 12px; color: #777; line-height: 1.55; margin-top: 8px; border-top: 1px solid #eee; padding-top: 8px; }

.footer-bar {
    text-align: center;
    font-size: 12px;
    color: #aaa;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
}
</style>
""", unsafe_allow_html=True)

# ── ID DE TU GOOGLE SHEET ──
SHEET_ID = "1jemf0nXgGg8wpAzvVEbcXv6npRCQugMh_esI8Qei82A"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# ── FUNCIONES ──
def parseTasa(val):
    if not val or str(val).strip() in ['---', 'nan', '', '0', '0.0']:
        return None
    s = re.sub(r'[%\s]', '', str(val)).replace(',', '.')
    try:
        return float(s)
    except:
        return None

def inferTag(row):
    text = ' '.join([
        str(row.get('TAG', '')),
        str(row.get('DESTINO', '')),
        str(row.get('NOMBRE DE LA LINEA', '')),
        str(row.get('OBSERVACIONES', '')),
        str(row.get('DESTINATARIOS', ''))
    ]).upper()
    if re.search(r'COMEX|EXPORT|IMPORTA|COMERCIO EXTERIOR', text): return 'COMEX'
    if re.search(r'CAPITAL DE TRABAJO|CAPITAL\s+TRABAJO|CHUBUT EMPRENDE', text): return 'Capital de trabajo'
    if re.search(r'BIEN(ES)?\s*DE\s*CAPITAL|MAQUINARIA|EQUIPAMIENTO', text): return 'Bienes de capital'
    if re.search(r'DISCAPACIDAD|INCLUS|VULNERAB|SOCIAL', text): return 'Inclusión social'
    if re.search(r'EMPLEO VERDE|INCLUIR TRABAJO|CONTRATA', text): return 'Empleo'
    if re.search(r'INVERSI', text): return 'Inversión'
    if re.search(r'PRODUCCI|AGRO|GANAD|PESCA|ACUICU', text): return 'Producción'
    return 'General'

def entidadNombre(row):
    ent = str(row.get('ENTIDAD', '')).upper()
    lin = str(row.get('NOMBRE DE LA LINEA', '')).upper()
    if re.search(r'CHUBUT EMPRENDE|INCLUIR TRABAJO|DISCAPACIDAD|EMPLEO VERDE', lin):
        return 'Sec. Trabajo · Chubut'
    if 'CRECER' in lin or 'PRODUCCI' in ent: return 'Min. de Producción'
    if 'BICE' in ent: return 'Banco BICE'
    if 'CFI' in ent: return 'CFI'
    if re.search(r'BNA|NACI[OÓ]N', ent): return 'Banco Nación'
    if 'CHUBUT' in ent: return 'Banco del Chubut'
    return ent if ent and ent not in ['---', 'NAN'] else 'Sin especificar'

def clean(v):
    s = str(v).strip()
    return '' if s in ['---', 'nan', 'None', '0', '0.0', ''] else s

TAG_COLORS = {
    'COMEX': 'pill-amber',
    'Capital de trabajo': 'pill-orange',
    'Bienes de capital': 'pill-blue',
    'Inclusión social': 'pill-pink',
    'Empleo': 'pill-green',
    'Inversión': 'pill-blue',
    'Producción': 'pill-teal',
    'General': 'pill-gray',
}

@st.cache_data(ttl=900)  # cache 15 minutos
def cargar_datos():
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip().str.upper()
    if 'ENTIDAD' in df.columns:
        df['ENTIDAD'] = df['ENTIDAD'].ffill().fillna('---')
    col_linea = 'NOMBRE DE LA LINEA' if 'NOMBRE DE LA LINEA' in df.columns else df.columns[1]
    df['_entidad'] = df.apply(entidadNombre, axis=1)
    df['_tag']     = df.apply(inferTag, axis=1)
    df['_tasa']    = df[df.columns[df.columns.str.contains('TASA')]].iloc[:, 0].apply(parseTasa) if any('TASA' in c for c in df.columns) else None
    df = df[df[col_linea].notna()]
    df = df[~df[col_linea].str.strip().isin(['', '---', 'nan'])]
    return df, col_linea

# ── CARGA DE DATOS ──
try:
    df, col_linea = cargar_datos()
    error = False
except Exception as e:
    st.error(f"⚠️ No se pudieron cargar los datos del Google Sheet. Verificá que sea público.\n\nDetalle: {e}")
    st.stop()
    error = True

# ── HERO ──
st.markdown("""
<div class="hero">
  <h1>💼 Líneas de Financiamiento · Chubut</h1>
  <p>Ministerio de Producción · Explorá créditos para PyMEs, productores y emprendedores · Actualización automática</p>
</div>
""", unsafe_allow_html=True)

# ── STATS ──
tasas_all = df['_tasa'].dropna()
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{len(df)}</div><div class="stat-label">líneas disponibles</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{df["_entidad"].nunique()}</div><div class="stat-label">entidades</div></div>', unsafe_allow_html=True)
with c3:
    val = f"{tasas_all.min():.1f}%" if len(tasas_all) else "—"
    st.markdown(f'<div class="stat-box"><div class="stat-num">{val}</div><div class="stat-label">tasa mínima</div></div>', unsafe_allow_html=True)
with c4:
    val = f"{tasas_all.max():.1f}%" if len(tasas_all) else "—"
    st.markdown(f'<div class="stat-box"><div class="stat-num">{val}</div><div class="stat-label">tasa máxima</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── SIDEBAR FILTROS ──
with st.sidebar:
    st.markdown("### 🔍 Filtros")

    busqueda = st.text_input("Buscar por nombre", placeholder="Ej: CRECER, capital, PyME...")

    entidades = ['Todas'] + sorted(df['_entidad'].unique().tolist())
    entidad_sel = st.selectbox("Entidad", entidades)

    tags_disp = ['Todos'] + sorted(df['_tag'].unique().tolist())
    tag_sel = st.selectbox("Destino del crédito", tags_disp)

    orden_sel = st.selectbox("Ordenar por tasa", [
        "Sin orden", "Menor a mayor ↑", "Mayor a menor ↓"
    ])

    st.markdown("---")
    st.markdown("**Contacto**")
    st.markdown("📧 herramientasfinancieraschubut@gmail.com")
    st.markdown("📱 WhatsApp: 2804276775")

# ── FILTRADO ──
mask = pd.Series([True] * len(df), index=df.index)

if busqueda:
    haystack = df[col_linea].fillna('') + ' ' + df['_entidad'].fillna('') + ' ' + df.get('DESTINATARIOS', pd.Series('')).fillna('')
    mask &= haystack.str.contains(busqueda, case=False, na=False)

if entidad_sel != 'Todas':
    mask &= df['_entidad'] == entidad_sel

if tag_sel != 'Todos':
    mask &= df['_tag'] == tag_sel

df_fil = df[mask].copy()

if orden_sel == "Menor a mayor ↑":
    df_fil = df_fil.sort_values('_tasa', ascending=True, na_position='last')
elif orden_sel == "Mayor a menor ↓":
    df_fil = df_fil.sort_values('_tasa', ascending=False, na_position='last')

# ── RESULTADOS ──
hay_filtro = busqueda or entidad_sel != 'Todas' or tag_sel != 'Todos'
st.markdown(f"**{len(df_fil)}** de **{len(df)}** líneas" + (" · con filtros activos" if hay_filtro else ""))

tasas_fil = df_fil['_tasa'].dropna()
min_t = tasas_fil.min() if len(tasas_fil) else None
max_t = tasas_fil.max() if len(tasas_fil) else None

if df_fil.empty:
    st.info("No hay líneas que coincidan con los filtros. Probá cambiarlos.")
else:
    for _, row in df_fil.iterrows():
        nombre  = clean(row.get(col_linea, '')) or '—'
        entidad = row['_entidad']
        tag     = row['_tag']
        tasa_n  = row['_tasa']
        tag_cls = TAG_COLORS.get(tag, 'pill-gray')

        if tasa_n is not None:
            tasa_txt = f"{tasa_n:.1f}%"
            if tasa_n == min_t:   tasa_cls = 'tasa-low'
            elif tasa_n == max_t: tasa_cls = 'tasa-high'
            else:                 tasa_cls = 'tasa-mid'
        else:
            raw = clean(row.get('TASA', ''))
            tasa_txt = raw if raw else '—'
            tasa_cls = 'tasa-na'

        monto  = clean(row.get('MONTO', ''))
        plazo  = clean(row.get('PLAZO', ''))
        gracia = clean(row.get('MESES DE GRACIA', ''))
        dest   = clean(row.get('DESTINATARIOS', ''))
        obs    = clean(row.get('OBSERVACIONES', '')) or clean(row.get('DESTINO', ''))

        meta_items = []
        if monto:  meta_items.append(('Monto', monto))
        if plazo:  meta_items.append(('Plazo', plazo))
        if gracia and gracia not in ['0', '0.0']: meta_items.append(('Gracia', gracia + ' meses'))
        if dest:   meta_items.append(('Para', dest))

        meta_html = ''
        if meta_items:
            cols_html = ''.join([
                f'<div style="flex:1;min-width:120px"><div class="meta-key">{k}</div><div class="meta-val">{v}</div></div>'
                for k, v in meta_items
            ])
            meta_html = f'<div style="display:flex;flex-wrap:wrap;gap:8px 16px;margin-top:10px">{cols_html}</div>'

        obs_html = f'<div class="obs-text">{obs}</div>' if obs else ''

        st.markdown(f"""
        <div class="card">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;flex-wrap:wrap">
            <div class="card-name">{nombre}</div>
            <span class="pill pill-teal">{entidad}</span>
          </div>
          <div>
            <span class="pill {tag_cls}">{tag}</span>
          </div>
          <div style="margin-top:8px">
            <span style="font-size:11px;color:#999;text-transform:uppercase;letter-spacing:.04em">Tasa anual · </span>
            <span class="tasa-big {tasa_cls}">{tasa_txt}</span>
          </div>
          {meta_html}
          {obs_html}
        </div>
        """, unsafe_allow_html=True)

# ── FOOTER ──
st.markdown("""
<div class="footer-bar">
  Dirección de Promoción de las Inversiones · Ministerio de Producción · Provincia del Chubut
</div>
""", unsafe_allow_html=True)
