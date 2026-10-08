import streamlit as st
import pandas as pd
import os
import random
import calendar
import requests
import json
import zipfile
import io
from datetime import date, datetime, timedelta

# ==============================================================================
# 1. CONFIGURACIÓN Y DISEÑO UI/UX
# ==============================================================================
st.set_page_config(page_title="Gestión Streaming Premium", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
        
        html, body, p, span, div, label, input, textarea, select, button {
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, [data-testid="stMetricValue"] {
            font-family: 'Space Grotesk', sans-serif !important;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        .stApp {
            background: radial-gradient(circle at 50% 0%, #1f1a45 0%, #0a0919 80%) !important;
            color: #f1f1f4 !important;
        }

        [data-testid="stSidebar"] {
            background-color: #0d0c20 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.04) !important;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.25) !important;
        }
        
        h1 {
            background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
            -webkit-background-clip: text;
            -webkit-background-color: transparent;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            letter-spacing: -0.5px !important;
            margin-bottom: 1.5rem !important;
        }
        
        h2 { font-weight: 700 !important; color: #ffffff !important; }

        div[data-testid="stForm"] {
            background-color: #17152e !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3) !important;
            margin-bottom: 2rem !important;
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 14px !important;
            padding: 1.2rem 1.5rem !important;
            transition: all 0.3s ease !important;
        }
        
        div[data-testid="stMetric"] {
            border-left: 3px solid #8B5CF6 !important;
        }
        
        div[data-testid="stMetric"]:hover {
            border-color: rgba(139, 92, 246, 0.35) !important;
            background: rgba(255, 255, 255, 0.03) !important;
            transform: translateY(-2px);
        }

        div[data-testid="stMetricLabel"] > div {
            color: #9aa0a6 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            font-weight: 600 !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
        }

        .stButton > button {
            border-radius: 10px !important;
            padding: 0.6rem 1.8rem !important;
            font-weight: 600 !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%) !important;
            color: #ffffff !important;
            border: none !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            box-shadow: 0 0 25px rgba(139, 92, 246, 0.5) !important;
            transform: translateY(-2px) !important;
        }
        
        .stButton > button[kind="secondary"] {
            background-color: #221f40 !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
        
        .stButton > button[kind="secondary"]:hover {
            background-color: #2d2a52 !important;
            border-color: rgba(255, 255, 255, 0.25) !important;
            transform: translateY(-2px) !important;
        }

        .stTextInput > div > div > input, .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div, .stNumberInput > div > div > input {
            border-radius: 10px !important;
            border: 1px solid #2a2750 !important;
            background-color: #17152e !important;
            color: #ffffff !important;
        }
        
        .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
            border-color: #8B5CF6 !important; box-shadow: 0 0 0 1px #8B5CF6 !important;
        }

        pre {
            border-radius: 12px !important;
            background-color: #0c0b1c !important;
            border: 1px solid #26234a !important;
            padding: 1.2rem !important;
        }

        div[data-testid="stAlert"] {
            border-radius: 14px !important;
            border: none !important;
            background-color: #1b1932 !important;
        }
        .block-container { padding-top: 2.2rem !important; max-width: 1300px !important; }

        /* Menú lateral tipo app */
        [data-testid="stSidebar"] div[role="radiogroup"] { gap: 4px !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label {
            padding: 0.7rem 0.9rem !important;
            border-radius: 10px !important;
            width: 100% !important;
            cursor: pointer !important;
            border-left: 3px solid transparent !important;
            transition: background 0.2s ease !important;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: rgba(139, 92, 246, 0.12) !important;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label p { font-weight: 500 !important; font-size: 0.95rem !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.28), rgba(59, 130, 246, 0.18)) !important;
            border-left: 3px solid #8B5CF6 !important;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { color: #ffffff !important; font-weight: 600 !important; }

        .marca-lateral { padding: 0.4rem 0.4rem 1.2rem 0.4rem; margin-bottom: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.06); }
        .marca-lateral .nombre { font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 700; color: #ffffff; }
        .marca-lateral .sub { font-size: 0.8rem; color: #9a98c0; margin-top: 2px; }
        .caja-tasa { background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 12px; padding: 0.8rem 1rem; margin: 1rem 0 0.8rem 0; }
        .caja-tasa .et { font-size: 0.75rem; color: #9a98c0; }
        .caja-tasa .val { font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; font-weight: 700; color: #ffffff; }

        /* Tablas más limpias */
        [data-testid="stTable"] table { border-collapse: collapse !important; width: 100% !important; }
        [data-testid="stTable"] th { background: #17152e !important; color: #a9a7cf !important; font-weight: 600 !important; text-align: left !important; padding: 0.7rem 0.9rem !important; border-bottom: 1px solid #2a2750 !important; }
        [data-testid="stTable"] td { padding: 0.65rem 0.9rem !important; border-bottom: 1px solid rgba(255,255,255,0.04) !important; }
        [data-testid="stTable"] tr:hover td { background: rgba(139, 92, 246, 0.06) !important; }

        hr { border-color: rgba(255, 255, 255, 0.05) !important; margin: 2.5rem 0 !important; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# CAMBIO: CONTRASEÑA DE ACCESO (si no hay APP_PASSWORD en los secrets, no pide nada)
# ==============================================================================
def verificar_acceso():
    clave_app = st.secrets.get("APP_PASSWORD", "")
    if not clave_app:
        return
    if st.session_state.get("autenticado"):
        return
    st.title("🔒 Acceso privado")
    with st.form("form_login"):
        pw = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar", type="primary"):
            if pw == clave_app:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
    st.stop()

verificar_acceso()

# ==============================================================================
# 2. SISTEMA DE BASE DE DATOS ULTRA-LIGERO
# ==============================================================================
COLUMNAS_INV = ["Plataforma", "Correo", "Clave", "Perfil_Pantalla", "PIN", "Estado", "Fecha_Pago", "IP_Region", "Costo_Matriz"]
COLUMNAS_CLI = ["Cliente", "Telefono", "Plataforma", "Correo", "Perfil_Pantalla", "Fecha_Inicio", "Fecha_Corte", "Metodo_Pago", "Monto", "Clave_Spotify", "Estado_Servicio", "Fecha_Congelamiento", "Meses_Contratados"]
COLUMNAS_PRE = ["Plataforma", "Costo_Matriz", "Precio_Venta_Perfil"]
COLUMNAS_PAG = ["Fecha", "Cliente", "Plataforma", "Correo", "Perfil_Pantalla", "Monto", "Metodo_Pago", "Meses", "Tipo"]
ARCHIVO_PLANTILLAS = "plantillas.json"

def get_headers():
    key = st.secrets["SUPABASE_KEY"]
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

def get_headers_get():
    key = st.secrets["SUPABASE_KEY"]
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

def to_float(val):
    try:
        if pd.isna(val) or val == "" or val is None:
            return 0.0
        return float(str(val).replace(',', '.').replace('$', '').strip())
    except:
        return 0.0

# CAMBIO: lectura con caché de 60 segundos. Si falla la conexión, NO se guarda en caché.
@st.cache_data(ttl=60, show_spinner=False)
def _leer_tabla_cache(tabla, columnas):
    url = f"{st.secrets['SUPABASE_URL']}/rest/v1/{tabla}?select=*"
    res = requests.get(url, headers=get_headers_get(), timeout=10)
    if res.status_code != 200:
        raise Exception("Error leyendo tabla")
    df = pd.DataFrame(res.json())
    if df.empty:
        return pd.DataFrame(columns=columnas).astype(str)
    for col in columnas:
        if col not in df.columns:
            df[col] = ""
    return df[columnas].astype(str).fillna("")

def leer_tabla(tabla, columnas):
    try:
        return _leer_tabla_cache(tabla, columnas)
    except:
        pass
    return pd.DataFrame(columns=columnas).astype(str)

def guardar_tabla(tabla, df, columnas):
    try:
        url_del = f"{st.secrets['SUPABASE_URL']}/rest/v1/{tabla}?{columnas[0]}=not.eq.VALOR_INEXISTENTE"
        r_del = requests.delete(url_del, headers=get_headers(), timeout=10)
        if r_del.status_code >= 300:
            st.error(f"Error al borrar en {tabla}: {r_del.status_code} - {r_del.text}")
            st.cache_data.clear()
            return

        if not df.empty:
            df_clean = df[columnas].fillna("").astype(str)
            records = df_clean.to_dict(orient="records")
            url_ins = f"{st.secrets['SUPABASE_URL']}/rest/v1/{tabla}"
            r_ins = requests.post(url_ins, headers=get_headers(), json=records, timeout=10)
            if r_ins.status_code >= 300:
                st.error(f"Error al guardar en {tabla}: {r_ins.status_code} - {r_ins.text}")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
    st.cache_data.clear()

def agregar_filas(tabla, df, columnas):
    try:
        if not df.empty:
            df_clean = df[columnas].fillna("").astype(str)
            records = df_clean.to_dict(orient="records")
            url_ins = f"{st.secrets['SUPABASE_URL']}/rest/v1/{tabla}"
            r = requests.post(url_ins, headers=get_headers(), json=records, timeout=10)
            if r.status_code >= 300:
                st.error(f"Error al guardar en {tabla}: {r.status_code} - {r.text}")
                st.cache_data.clear()
                return False
    except Exception as e:
        st.error(f"Error insertando: {e}")
        st.cache_data.clear()
        return False
    st.cache_data.clear()
    return True

def obtener_tasa_binance():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    data = {"asset": "USDT", "fiat": "VES", "merchantCheck": False, "page": 1, "rows": 5, "tradeType": "BUY"}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=5)
        if response.status_code == 200:
            res_json = response.json()
            anuncios = res_json.get("data", [])
            if len(anuncios) >= 4:
                return round(float(anuncios[3]["adv"]["price"]) * 1.01, 2)
    except: pass
    return None

# CAMBIO: la tasa de Binance se comparte entre todas las sesiones por 30 minutos
@st.cache_data(ttl=1800, show_spinner=False)
def tasa_binance_cache():
    t = obtener_tasa_binance()
    if t is None:
        raise Exception("Sin tasa")  # así un fallo no se guarda en caché
    return t

def sumar_meses(fecha_obj, meses):
    mes = fecha_obj.month - 1 + int(meses)
    anio = fecha_obj.year + mes // 12
    mes = mes % 12 + 1
    dia = min(fecha_obj.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)

def registrar_pagos(lista):
    """Guarda cada cobro (venta o renovación) en el historial de pagos."""
    if not lista:
        return True
    ok = agregar_filas("pagos", pd.DataFrame(lista), COLUMNAS_PAG)
    if not ok:
        st.session_state.error_pagos = "⚠️ La venta se guardó, pero NO se pudo anotar en el historial de pagos. Revisa que la tabla 'pagos' exista en Supabase."
    return ok

# CAMBIO: ciclo de pago de las matrices y días de aviso
DIAS_CICLO_MATRIZ = 31
DIAS_AVISO_MATRIZ = 3

def costo_con_extras(df_inv, plataforma, correo, costo_base):
    """Costo de la matriz + el costo de sus perfiles extra. Devuelve (total, costo_extras, cantidad_extras)."""
    ext = df_inv[(df_inv["Plataforma"] == plataforma) & (df_inv["IP_Region"] == f"EXTRA de {correo}")].drop_duplicates(subset=["Correo"])
    c_ext = sum([to_float(x) for x in ext["Costo_Matriz"]])
    return to_float(costo_base) + c_ext, c_ext, len(ext)

def actualizar_fecha_pago(plataforma, correo, nueva_fecha):
    """Mueve la fecha de pago de la matriz y la de sus extras."""
    df = leer_tabla("inventario", COLUMNAS_INV)
    df.loc[(df["Plataforma"] == plataforma) & (df["Correo"] == correo), "Fecha_Pago"] = str(nueva_fecha)
    df.loc[(df["Plataforma"] == plataforma) & (df["IP_Region"] == f"EXTRA de {correo}"), "Fecha_Pago"] = str(nueva_fecha)
    guardar_tabla("inventario", df, COLUMNAS_INV)

# Variables de Sesión
if 'pines_azar' not in st.session_state: st.session_state.pines_azar = [str(random.randint(1000, 9999)) for _ in range(50)]
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'ultima_actualizacion' not in st.session_state: st.session_state.ultima_actualizacion = datetime.min
if 'tasa_cambio' not in st.session_state: st.session_state.tasa_cambio = 40.00

ahora = datetime.now()
if (ahora - st.session_state.ultima_actualizacion) > timedelta(minutes=30):
    st.session_state.ultima_actualizacion = ahora
    try:
        tasa_nueva = tasa_binance_cache()  # CAMBIO: usa la versión con caché
    except:
        tasa_nueva = None
    if tasa_nueva:
        st.session_state.tasa_cambio = tasa_nueva

def inicializar_archivos():
    if not os.path.exists(ARCHIVO_PLANTILLAS):
        plantillas_defecto = {
            "cobro": "¡Hola [cliente]! 👋 Paso por acá para recordarte que tus servicios están próximos a vencer:\n\n[servicios]\n*Total a transferir:* $[monto_usd] USD o su equivalente **[monto_bs] Bs**.\n\nMe avisas al realizar el pago para mantener tus pantallas activas sin interrupciones. ¡Muchas gracias! ✨",
            "cotizacion": "¡Hola! Aquí tienes el desglose y la cuenta de tus servicios:\n\n[servicios]\n💰 *Total:* $[monto_usd] USD / *[monto_bs] Bs*\n\n👇 *Puedes realizar tu pago móvil a cualquiera de estas cuentas:* \n\n*Monto a transferir = [monto_bs] bs*",
            "venta": "Plataforma: [plataforma]\n*Correo*: [correo]\n*Clave*: [clave]\n*Perfil*: [perfil] PIN: [pin]\n\n*Vence el*: [fecha_corte]",
            "soporte": "¡Hola! Para solucionar tu inconveniente rápidamente y que sigas disfrutando sin pausas, te he migrado a una pantalla nueva limpia. Aquí tienes los datos actualizados:\n\nPlataforma: [plataforma]\n*Correo*: [correo]\n*Clave*: [clave]\n*Perfil*: [perfil] PIN: [pin]\n\n*Nota: Tu fecha de corte mensual se mantiene igual ([fecha_corte]).*"
        }
        with open(ARCHIVO_PLANTILLAS, 'w', encoding='utf-8') as f:
            json.dump(plantillas_defecto, f, ensure_ascii=False, indent=4)
            
    df_pre = leer_tabla("precios", COLUMNAS_PRE)
    if df_pre.empty:
        df_default = pd.DataFrame([
            {"Plataforma": "NETFLIX", "Costo_Matriz": "9.00", "Precio_Venta_Perfil": "3.00"},
            {"Plataforma": "SPOTIFY", "Costo_Matriz": "5.00", "Precio_Venta_Perfil": "1.50"},
            {"Plataforma": "MAGIS TV", "Costo_Matriz": "8.00", "Precio_Venta_Perfil": "2.50"}
        ]).astype(str)
        agregar_filas("precios", df_default, COLUMNAS_PRE)

def cargar_plantilla(tipo):
    try:
        with open(ARCHIVO_PLANTILLAS, 'r', encoding='utf-8') as f:
            return json.load(f).get(tipo, "")
    except:
        return ""

def armar_mensaje_datos(plataforma, correo, clave, perfil, pin, fecha_corte):
    """Mensaje con los datos de acceso, usando tu plantilla de Venta."""
    try:
        fc = pd.to_datetime(fecha_corte).strftime('%d/%m/%Y')
    except:
        fc = str(fecha_corte)
    cuerpo = cargar_plantilla("venta").replace("[plataforma]", str(plataforma)).replace("[correo]", str(correo)).replace("[clave]", str(clave)).replace("[perfil]", str(perfil)).replace("[pin]", str(pin)).replace("[fecha_corte]", fc)
    return "¡Hola! Aquí tienes tus datos de acceso actualizados:\n\n" + cuerpo

inicializar_archivos()

# ==============================================================================
# 3. NAVEGACIÓN LATERAL
# ==============================================================================
st.sidebar.markdown("""
    <div class="marca-lateral">
        <div class="nombre">📺 Streaming Manager</div>
        <div class="sub">Gestión de cuentas y clientes</div>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Menú Principal", 
    ["📌 Panel Diario", "📦 Registrar Cuentas", "🛒 Vender Perfiles", "🗃️ Base de Datos", "💰 Finanzas", "🛠️ Soportes", "⚙️ Configuración"],
    key="nav_principal",
    label_visibility="collapsed"
)

st.sidebar.markdown(f"""
    <div class="caja-tasa">
        <div class="et">Tasa activa</div>
        <div class="val">{st.session_state.tasa_cambio:,.2f} Bs / USD</div>
    </div>
""", unsafe_allow_html=True)

if st.secrets.get("APP_PASSWORD", ""):
    if st.sidebar.button("🔒 Cerrar sesión", key="btn_logout", type="secondary"):
        st.session_state.autenticado = False
        st.rerun()

st.title("Panel Central de Cuentas")
st.caption(f"Hoy es {date.today().strftime('%d/%m/%Y')}")
if "error_pagos" in st.session_state:
    st.error(st.session_state.pop("error_pagos"))

# ==============================================================================
# MÓDULO 0: PANEL DIARIO 
# ==============================================================================
if menu == "📌 Panel Diario":
    st.header("Lo que tienes que hacer hoy 📝")
    hoy_pd = pd.to_datetime("today").normalize()
    
    df_clientes_raw = leer_tabla("clientes", COLUMNAS_CLI)

    # CAMBIO: tarjetas de resumen arriba
    df_inv_res = leer_tabla("inventario", COLUMNAS_INV)
    act_res = df_clientes_raw[df_clientes_raw["Estado_Servicio"] == "Activo"].copy()
    if act_res.empty:
        act_res["Dias"] = 0
    else:
        act_res["Dias"] = (pd.to_datetime(act_res["Fecha_Corte"], errors="coerce") - hoy_pd).dt.days
    n_venc = act_res[act_res["Dias"] < 0]["Cliente"].nunique()
    n_hoy = act_res[act_res["Dias"] == 0]["Cliente"].nunique()
    n_prox = act_res[(act_res["Dias"] > 0) & (act_res["Dias"] <= 3)]["Cliente"].nunique()
    por_cobrar = sum([to_float(x) for x in act_res[act_res["Dias"] <= 3]["Monto"]])
    n_mat = 0
    total_mat = 0.0
    avisos_mat = []
    if not df_inv_res.empty:
        c_res = df_inv_res.drop_duplicates(subset=["Correo", "Plataforma"])
        c_res = c_res[~c_res["IP_Region"].str.startswith("EXTRA")].copy()
        c_res["Dias"] = (pd.to_datetime(c_res["Fecha_Pago"], errors="coerce") - hoy_pd).dt.days
        c_urg = c_res[c_res["Dias"] <= DIAS_AVISO_MATRIZ].sort_values("Dias")
        for _, r_m in c_urg.iterrows():
            tot_m, _, _ = costo_con_extras(df_inv_res, r_m["Plataforma"], r_m["Correo"], r_m["Costo_Matriz"])
            total_mat += tot_m
            d_m = int(r_m["Dias"])
            cuando = f"VENCIDA hace {abs(d_m)} días" if d_m < 0 else ("vence HOY" if d_m == 0 else f"vence en {d_m} días")
            avisos_mat.append(f"- **{r_m['Plataforma']}** ({r_m['Correo']}): {cuando} | ${tot_m:.2f}")
        n_mat = len(c_urg)

    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Clientes vencidos", n_venc)
    r2.metric("Cobran hoy", n_hoy)
    r3.metric("Próximos 3 días", n_prox)
    r4.metric("Por cobrar (USD)", f"${por_cobrar:,.2f}")
    r5.metric("Matrices por pagar", n_mat)

    if avisos_mat:
        st.warning(
            f"⚠️ **Paga estas cuentas matrices para que no se caigan (aviso {DIAS_AVISO_MATRIZ} días antes):**\n\n"
            + "\n".join(avisos_mat)
            + f"\n\n**Total a pagar: ${total_mat:,.2f} | {total_mat * st.session_state.tasa_cambio:,.2f} Bs**"
        )

    pendientes_activacion = df_clientes_raw[df_clientes_raw["Estado_Servicio"] == "Pendiente"]
    
    if not pendientes_activacion.empty:
        st.markdown("---")
        st.subheader("⏳ Pendientes por Activar (En Pausa)")
        for idx, row in pendientes_activacion.iterrows():
            st.warning(f"🟡 **CLIENTE: {row['Cliente']}** | Plataforma: {row['Plataforma']}")
            col_p1, col_p2, col_p3 = st.columns([2,2,1])
            with col_p1:
                st.markdown("**Correo a activar:**")
                st.code(row['Correo'], language="markdown")
            with col_p2:
                if row['Plataforma'] == "SPOTIFY" and row['Clave_Spotify'] != "":
                    st.markdown("**Contraseña del Cliente:**")
                    st.code(row['Clave_Spotify'], language="markdown")
                else:
                    st.write(" ")
            with col_p3:
                st.write(" ")
                if st.button("✅ Activar", key=f"activar_{str(idx)}", type="primary"):
                    meses = int(to_float(row.get('Meses_Contratados', 1)))
                    df_clientes_raw.at[idx, "Fecha_Inicio"] = str(date.today())
                    df_clientes_raw.at[idx, "Fecha_Corte"] = str(sumar_meses(date.today(), meses if meses > 0 else 1))
                    df_clientes_raw.at[idx, "Estado_Servicio"] = "Activo"
                    guardar_tabla("clientes", df_clientes_raw, COLUMNAS_CLI)
                    st.success("¡Activado!")
                    st.rerun()
        st.markdown("---")
    
    col_cobros, col_pagos = st.columns(2)
    
    with col_cobros:
        st.subheader("🟢 Cobros a Clientes")
        activos = df_clientes_raw[df_clientes_raw["Estado_Servicio"] == "Activo"].copy()
        if not activos.empty:
            activos["Fecha_Real"] = pd.to_datetime(activos["Fecha_Corte"], errors="coerce")
            df_vencidos = activos[(activos["Fecha_Real"].notna()) & ((activos["Fecha_Real"] - hoy_pd).dt.days <= 3)]
            if not df_vencidos.empty:
                for cli in df_vencidos["Cliente"].unique().tolist():
                    df_cli_actual = df_vencidos[df_vencidos["Cliente"] == cli]
                    telefono_cli = df_cli_actual.iloc[0]["Telefono"]
                    dias_minimos = (df_cli_actual["Fecha_Real"] - hoy_pd).dt.days.min()
                    
                    if dias_minimos < 0:
                        st.error(f"👤 **{cli.upper()}** | 🔴 Vencido")
                    elif dias_minimos == 0:
                        st.warning(f"👤 **{cli.upper()}** | 🟡 Cobra Hoy")
                    else:
                        st.info(f"👤 **{cli.upper()}** | 🔵 Próximo")
                    
                    with st.form(key=f"form_cobro_{cli}"):
                        st.code(telefono_cli, language="markdown")
                        checklines_seleccionados = []
                        total_usd_combo = 0.0
                        txt_serv = ""
                        
                        for idx_row, row in df_cli_actual.iterrows():
                            dias = (row["Fecha_Real"] - hoy_pd).days
                            txt_venc = f"Hace {abs(dias)}d" if dias < 0 else ("Hoy" if dias == 0 else f"En {dias}d")
                            m_item = to_float(row.get('Monto', 0))
                            if st.checkbox(f"• {row['Plataforma']} ({row['Perfil_Pantalla']}) | {txt_venc} | ${m_item:.2f}", value=True, key=f"chk_{str(idx_row)}"):
                                checklines_seleccionados.append(idx_row)
                                total_usd_combo += m_item
                                txt_serv += f"- {row['Plataforma']} ({row['Perfil_Pantalla']})\n"
                        
                        t_bs = total_usd_combo * st.session_state.tasa_cambio
                        st.markdown(f"**Total: ${total_usd_combo:.2f} USD | {t_bs:,.2f} Bs**")
                        
                        with st.expander("📋 Ver Mensaje"):
                            st.code(cargar_plantilla("cobro").replace("[cliente]", cli).replace("[servicios]", txt_serv.strip()).replace("[monto_usd]", f"{total_usd_combo:.2f}").replace("[monto_bs]", f"{t_bs:,.2f}").strip(), language="markdown")
                        
                        c_r1, c_r2 = st.columns([1,2])
                        with c_r1:
                            meses_ren = st.number_input("Meses", min_value=1, max_value=12, value=1, key=f"mren_{cli}")
                        with c_r2:
                            opc = st.selectbox("Acción:", ["---", "✅ Sí Renovó (Extender)", "❌ No Renovó (Cortar)"], key=f"acc_{cli}")
                        monto_recibido = st.number_input("Monto total recibido ($). Déjalo en 0 para usar el precio normal", min_value=0.0, step=0.5, value=0.0, key=f"mrec_{cli}")
                        
                        if st.form_submit_button("⚡ Procesar", type="primary"):
                            if opc == "---":
                                st.error("⚠️ Elige acción.")
                            elif not checklines_seleccionados:
                                st.error("⚠️ Marca pantalla.")
                            else:
                                df_full_cli = df_clientes_raw.copy()
                                df_full_inv = leer_tabla("inventario", COLUMNAS_INV)
                                if "Sí Renovó" in opc:
                                    pagos_ren = []
                                    for idx_row in checklines_seleccionados:
                                        f_vieja = datetime.strptime(df_full_cli.loc[idx_row, "Fecha_Corte"], "%Y-%m-%d").date()
                                        meses_prev = max(int(to_float(df_full_cli.loc[idx_row, "Meses_Contratados"])), 1)
                                        monto_prev = to_float(df_full_cli.loc[idx_row, "Monto"])
                                        if monto_recibido > 0:
                                            monto_ren = monto_recibido / len(checklines_seleccionados)
                                        else:
                                            monto_ren = monto_prev / meses_prev * meses_ren
                                        df_full_cli.at[idx_row, "Meses_Contratados"] = str(meses_ren)
                                        df_full_cli.at[idx_row, "Fecha_Corte"] = str(sumar_meses(f_vieja, meses_ren))
                                        df_full_cli.at[idx_row, "Monto"] = str(round(monto_ren, 2))
                                        pagos_ren.append({
                                            "Fecha": str(date.today()), "Cliente": df_full_cli.loc[idx_row, "Cliente"],
                                            "Plataforma": df_full_cli.loc[idx_row, "Plataforma"], "Correo": df_full_cli.loc[idx_row, "Correo"],
                                            "Perfil_Pantalla": df_full_cli.loc[idx_row, "Perfil_Pantalla"], "Monto": str(round(monto_ren, 2)),
                                            "Metodo_Pago": df_full_cli.loc[idx_row, "Metodo_Pago"], "Meses": str(meses_ren), "Tipo": "Renovación"
                                        })
                                    guardar_tabla("clientes", df_full_cli, COLUMNAS_CLI)
                                    registrar_pagos(pagos_ren)
                                    st.rerun()
                                elif "No Renovó" in opc:
                                    i_borrar = []
                                    for idx_row in checklines_seleccionados:
                                        r_d = df_full_cli.loc[idx_row]
                                        m_i = df_full_inv[(df_full_inv["Correo"] == r_d["Correo"]) & (df_full_inv["Perfil_Pantalla"] == r_d["Perfil_Pantalla"])]
                                        if not m_i.empty:
                                            df_full_inv.at[m_i.index[0], "Estado"] = "🔴 En Revisión"
                                        i_borrar.append(idx_row)
                                    guardar_tabla("clientes", df_full_cli.drop(i_borrar), COLUMNAS_CLI)
                                    guardar_tabla("inventario", df_full_inv, COLUMNAS_INV)
                                    st.rerun()
                    st.markdown("---")
            else:
                st.success("¡Todo al día! 😎")
        else:
            st.write("No hay cobros pendientes.")

    with col_pagos:
        st.subheader("🔴 Pagos de Cuentas Matrices")
        df_inv = leer_tabla("inventario", COLUMNAS_INV)
        if not df_inv.empty:
            c_uni = df_inv.drop_duplicates(subset=["Correo", "Plataforma"]).copy()
            c_uni = c_uni[~c_uni["IP_Region"].str.startswith("EXTRA")].copy()
            c_uni["Fecha_Real"] = pd.to_datetime(c_uni["Fecha_Pago"], errors="coerce")
            p_pend = c_uni[(c_uni["Fecha_Real"].notna()) & ((c_uni["Fecha_Real"] - hoy_pd).dt.days <= DIAS_AVISO_MATRIZ)]
            if not p_pend.empty:
                for idx, row in p_pend.sort_values(by="Fecha_Real").iterrows():
                    dias = (row["Fecha_Real"] - hoy_pd).days
                    est = f"🚨 VENCIDA hace {abs(dias)}d" if dias < 0 else ("🔥 PAGAR HOY" if dias == 0 else f"⏳ En {dias}d")
                    c_mat, c_extra, n_extra = costo_con_extras(df_inv, row["Plataforma"], row["Correo"], row.get("Costo_Matriz", 0.0))
                    txt_extra = f" (incluye ${c_extra:.2f} de {n_extra} extra)" if c_extra > 0 else ""
                    st.warning(f"**{row['Plataforma']}** | {est}\n\n💸 Costo: ${c_mat:.2f}{txt_extra} | **{c_mat * st.session_state.tasa_cambio:,.2f} Bs**")
                    with st.expander(f"📋 Ver Credenciales"):
                        st.code(row["Correo"], language="markdown")
                        st.code(row["Clave"], language="markdown")
                        base_pago = max(row["Fecha_Real"].date(), date.today())
                        nueva_31 = base_pago + timedelta(days=DIAS_CICLO_MATRIZ)
                        if st.button(f"✅ Ya pagué (próximo pago: {nueva_31.strftime('%d/%m/%Y')})", key=f"bp31_{str(idx)}", type="primary"):
                            actualizar_fecha_pago(row["Plataforma"], row["Correo"], nueva_31)
                            st.rerun()
                        n_f = st.date_input("O elige otra fecha:", value=row["Fecha_Real"].date(), key=f"fm_{str(idx)}")
                        if st.button("💾 Guardar Fecha", key=f"bm_{str(idx)}"):
                            actualizar_fecha_pago(row["Plataforma"], row["Correo"], n_f)
                            st.rerun()
                st.markdown("---")
            else:
                st.success("¡Sin pagos! 🥳")

    if not df_inv.empty:
        en_revision = df_inv[df_inv["Estado"] == "🔴 En Revisión"]
        if not en_revision.empty:
            st.markdown("---")
            st.subheader("🛠️ Cuentas en Revisión (Limpieza PIN)")
            for idx, row in en_revision.iterrows():
                with st.container():
                    st.error(f"🔴 **{row['Plataforma']}** | Perfil Viejo: **{row['Perfil_Pantalla']}**")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.code(row["Correo"], language="markdown")
                    with c2:
                        st.code(row["Clave"], language="markdown")
                    with c3:
                        np = st.text_input("NUEVO PIN:", value=str(row["PIN"]), key=f"rp_{str(idx)}")
                        if st.button("✅ Reactivar", key=f"rb_{str(idx)}", type="primary"):
                            df_inv.at[idx, "Estado"] = "Disponible"
                            df_inv.at[idx, "PIN"] = str(np)
                            guardar_tabla("inventario", df_inv, COLUMNAS_INV)
                            st.rerun()

# ==============================================================================
# MÓDULO 1: REGISTRAR CUENTAS 
# ==============================================================================
elif menu == "📦 Registrar Cuentas":
    st.subheader("Ingresar nueva cuenta al inventario")
    
    df_precios_act = leer_tabla("precios", COLUMNAS_PRE)
    lista_plataformas = df_precios_act["Plataforma"].unique().tolist()
    if not lista_plataformas:
        lista_plataformas = ["NETFLIX", "SPOTIFY"]
        
    col1, col2 = st.columns(2)
    matriz_padre = None
    fecha_padre = date.today()
    with col1:
        plataforma = st.selectbox("Plataforma (Se añaden desde Finanzas)", lista_plataformas, key="reg_plat")
        
        # CAMBIO: perfil extra (con correo propio, pero se paga junto a otra matriz)
        es_extra = st.checkbox("➕ Es un perfil extra (se paga junto a otra cuenta matriz)", key="reg_extra")
        if es_extra:
            df_inv_reg = leer_tabla("inventario", COLUMNAS_INV)
            mats_reg = df_inv_reg[(df_inv_reg["Plataforma"] == plataforma) & (~df_inv_reg["IP_Region"].str.startswith("EXTRA"))].drop_duplicates(subset=["Correo"])
            opciones_padre = mats_reg["Correo"].tolist()
            if opciones_padre:
                matriz_padre = st.selectbox("Cuenta matriz que lo paga", opciones_padre, key="reg_padre")
                try:
                    fecha_padre = pd.to_datetime(mats_reg[mats_reg["Correo"] == matriz_padre].iloc[0]["Fecha_Pago"]).date()
                except:
                    fecha_padre = date.today()
            else:
                st.warning(f"Primero registra la cuenta matriz de {plataforma}.")
        
        correo = st.text_input("Correo del perfil extra" if es_extra else "Correo de la cuenta principal", key="reg_correo")
        clave = st.text_input("Clave de la cuenta", key="reg_clave")
        if es_extra:
            costo_matriz_input = st.number_input("Costo del extra ($)", min_value=0.0, step=0.5, key="reg_costo_extra", help="Lo que cuesta este extra en la factura de la matriz (Ej: 3).")
            st.caption("💡 Este costo se suma al pago de la cuenta matriz en el Panel Diario.")
        else:
            costo_matriz_input = st.number_input("Costo de esta cuenta ($)", min_value=0.0, step=0.5, key="reg_costo", help="Ponle 0 si es autopagable, o el monto que le pagaste al proveedor por esta cuenta en específico.")
    with col2:
        if es_extra:
            st.info("➕ **Perfil extra:** se registra 1 perfil, con la fecha de pago de su matriz y su propio costo.")
            cantidad_perfiles = 1
            fecha_pago_cuenta = st.date_input("Día de próximo pago (el de la matriz)", value=fecha_padre, disabled=True, key="reg_fecha_extra")
            ip_region = f"EXTRA de {matriz_padre}" if matriz_padre else "EXTRA"
            st.text_input("IP / Región", value=ip_region, disabled=True, key="reg_ip_extra")
        else:
            if plataforma == "SPOTIFY":
                st.info("🎵 **Plan Familiar:** Se reservarán exactamente 6 cupos automáticamente.")
                cantidad_perfiles = 6
            else:
                cantidad_perfiles = st.number_input("Perfiles a vender", min_value=1, max_value=15, value=5, key="reg_cant")
            fecha_pago_cuenta = st.date_input("Día de próximo pago al proveedor (por defecto, 31 días)", value=date.today() + timedelta(days=DIAS_CICLO_MATRIZ), key="reg_fecha")
            ip_region = st.text_input("IP / Región (Ej: USA, Autopagable)", key="reg_ip")
        
    st.markdown("---")
    st.markdown(f"**Configuración rápida de los perfiles:**")
    perfiles_a_guardar = []
    
    for i in range(1, int(cantidad_perfiles) + 1):
        c1, c2 = st.columns(2)
        if plataforma == "SPOTIFY":
            n_def = "Principal" if i == 1 else f"Cupo {i-1}"
            with c1:
                nom = st.text_input(f"Perfil {i}", value=n_def, disabled=True, key=f"nom_spot_{i}")
            with c2:
                pin = "N/A"
        else:
            with c1:
                nom = st.text_input(f"Nombre {i}", value=f"Perfil {i}", key=f"nom_gen_{i}")
            with c2:
                pin = st.text_input(f"PIN {i}", value=st.session_state.pines_azar[i], key=f"pin_gen_{i}")
        perfiles_a_guardar.append({"nombre": nom, "pin": pin})
        
    if st.button("💾 Guardar Cuenta Matriz", type="primary", key="btn_guardar_matriz"):
        if es_extra and not matriz_padre:
            st.error("⚠️ Elige la cuenta matriz que paga este perfil extra.")
        elif correo and clave:
            n_perf = []
            for item in perfiles_a_guardar:
                n_perf.append({
                    "Plataforma": plataforma, "Correo": correo, "Clave": clave, 
                    "Perfil_Pantalla": item["nombre"], "PIN": str(item["pin"]), 
                    "Estado": "Disponible", "Fecha_Pago": str(fecha_pago_cuenta), "IP_Region": ip_region,
                    "Costo_Matriz": str(costo_matriz_input)
                })
            ok = agregar_filas("inventario", pd.DataFrame(n_perf), COLUMNAS_INV)
            if ok:
                st.success("¡Cuenta guardada exitosamente en la Base de Datos de la nube!")
                st.session_state.pines_azar = [str(random.randint(1000, 9999)) for _ in range(50)]

# ==============================================================================
# MÓDULO 2: VENTAS 
# ==============================================================================
elif menu == "🛒 Vender Perfiles":
    st.subheader("🛍️ Armar Combo de Ventas")
    
    if "m_exito" in st.session_state:
        st.success(st.session_state.m_exito)
        st.code(st.session_state.m_copia, language="markdown")
        del st.session_state.m_exito
        del st.session_state.m_copia
    if "m_cotiza" in st.session_state:
        st.info("📋 **Cotización:**")
        st.code(st.session_state.m_cotiza, language="markdown")
        del st.session_state.m_cotiza

    df_inv_actual = leer_tabla("inventario", COLUMNAS_INV)
    df_pre = leer_tabla("precios", COLUMNAS_PRE)
    
    st.markdown("#### 📊 Pantallas Disponibles en Stock")
    lp = df_pre["Plataforma"].unique().tolist()
    
    df_disp_tot = df_inv_actual[df_inv_actual["Estado"] == "Disponible"]
    
    cs1 = st.columns(min(5, len(lp)) if len(lp) > 0 else 1)
    for i, plat in enumerate(lp[:5]):
        cs1[i].metric(label=plat, value=len(df_disp_tot[df_disp_tot["Plataforma"] == plat]))
        
    if len(lp) > 5:
        cs2 = st.columns(len(lp[5:10]))
        for i, plat in enumerate(lp[5:10]):
            cs2[i].metric(label=plat, value=len(df_disp_tot[df_disp_tot["Plataforma"] == plat]))
            
    st.markdown("---")
    
    idx_cart = [item["index_original"] for item in st.session_state.carrito]
    disp = df_disp_tot[~df_disp_tot.index.isin(idx_cart)]
    
    if disp.empty and not st.session_state.carrito:
        st.warning("No tienes perfiles disponibles en el inventario.")
    else:
        cp1, cp2 = st.columns(2)
        with cp1:
            plat_opts = disp["Plataforma"].unique().tolist() if not disp.empty else ["Sin Stock"]
            plat_v = st.selectbox("1. Plataforma:", plat_opts, key="vta_plat")
            
            o_disp = disp[disp["Plataforma"] == plat_v] if plat_v != "Sin Stock" else pd.DataFrame()
            l_perf = o_disp.apply(lambda r: f"{r['Correo']} - {r['Perfil_Pantalla']}", axis=1).tolist() if not o_disp.empty else ["Agotado"]
            p_sel = st.selectbox("2. Perfil / Cupo:", l_perf, key="vta_perf")
        
        if p_sel and p_sel != "Agotado":
            i_sel = o_disp.index[l_perf.index(p_sel)]
            d_p = df_inv_actual.loc[i_sel]
            
            with cp2:
                if plat_v == "SPOTIFY":
                    c_cli_in = st.text_input("📧 Correo del Cliente (Invitación)", placeholder="ejemplo@gmail.com", key=f"vta_corr_spot_{str(i_sel)}")
                    cl_cli_in = st.text_input("🔑 Contraseña del Cliente", type="password", key=f"vta_pass_spot_{str(i_sel)}")
                    n_fin = c_cli_in if c_cli_in.strip() else str(d_p["Perfil_Pantalla"])
                    pin_asig = "N/A"
                else:
                    n_fin = st.text_input("Nombre en pantalla", value=str(d_p["Perfil_Pantalla"]), key=f"vta_nom_gen_{str(i_sel)}")
                    pin_asig = st.text_input("PIN", value=str(d_p["PIN"]), key=f"vta_pin_gen_{str(i_sel)}")
                    c_cli_in = ""
                    cl_cli_in = ""
                
                m_in = st.number_input("Meses a contratar (Máx 12)", min_value=1, max_value=12, value=1, key=f"vta_meses_{str(i_sel)}")
                
                mt = df_pre[df_pre["Plataforma"] == plat_v]
                p_base = to_float(mt.iloc[0]["Precio_Venta_Perfil"]) if not mt.empty else 0.0
                
                p_mes = st.number_input("💰 Precio por Mes ($ - Editable)", min_value=0.0, value=float(p_base), step=0.5, key=f"vta_pmes_{str(i_sel)}")
                
                sug_total = p_mes * m_in
                st.markdown(f"**Total Sugerido: ${sug_total:.2f}**")
                
                usar_desc = st.checkbox("💸 Aplicar Precio Personalizado / Descuento al total", key=f"vta_chk_desc_{str(i_sel)}")
                if usar_desc:
                    p_final = st.number_input("Nuevo Total Final ($)", min_value=0.0, value=float(sug_total), step=0.5, key=f"vta_ptot_{str(i_sel)}")
                else:
                    p_final = sug_total
                
            item_nuevo = {
                "index_original": i_sel, "Plataforma": plat_v, "Correo_Matriz": str(d_p["Correo"]), 
                "Clave_Matriz": str(d_p["Clave"]), "Perfil_Pantalla": n_fin, "PIN": pin_asig, 
                "Meses": m_in, "Precio_Calculado": p_final, "Correo_Cliente": c_cli_in, "Clave_Cliente": cl_cli_in
            }
            cb_a, cb_b = st.columns(2)
            if cb_a.button("➕ Añadir al Combo", type="secondary", key=f"btn_add_{str(i_sel)}"):
                st.session_state.carrito.append(item_nuevo)
                st.rerun()
            if cb_b.button("🚀 Venta (solo este perfil)", type="primary", key=f"btn_venta_{str(i_sel)}"):
                st.session_state.carrito = [item_nuevo]
                st.session_state.aviso_venta = True
                st.rerun()

        if st.session_state.carrito:
            st.markdown("---")
            if st.session_state.pop("aviso_venta", False):
                st.success("✅ Perfil listo. Baja y completa los datos del cliente en el formulario para confirmar la venta.")
            st.subheader("🛒 Carrito Actual")
            st.table(pd.DataFrame(st.session_state.carrito)[["Plataforma", "Perfil_Pantalla", "Meses", "Precio_Calculado"]])
            if st.button("❌ Vaciar Carrito", type="secondary", key="btn_vaciar_cart"):
                st.session_state.carrito = []
                st.rerun()
            
            sug_usd = sum([item["Precio_Calculado"] for item in st.session_state.carrito])
            cart_len = len(st.session_state.carrito)
            
            st.markdown("---")
            with st.form("f_final"):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    cli = st.text_input("Nombre Cliente", key=f"frm_cli_{cart_len}")
                with c2:
                    tel = st.text_input("WhatsApp", value="+58", key=f"frm_tel_{cart_len}")
                with c3:
                    met = st.selectbox("Método de Pago", ["Binance Pay (USDT)", "Pago Móvil", "Zelle", "Efectivo"], key=f"frm_met_{cart_len}")
                with c4:
                    m_tot = st.number_input("Cobro Total Combo ($)", value=float(sug_usd), key=f"frm_mtot_{cart_len}")
                
                st.info("⏱️ **Control de Tiempos:**")
                act_ya = st.checkbox("✅ ¿Servicio activado y entregado al instante?", value=True, key=f"frm_act_{cart_len}")
                
                cb1, cb2 = st.columns(2)
                b_conf = cb1.form_submit_button("🚀 Confirmar Venta", type="primary")
                b_cot = cb2.form_submit_button("📋 Solo Cotizar Cuenta", type="secondary")
                
                if b_cot:
                    t_s = ""
                    for i in st.session_state.carrito:
                        t_s += f"- {i['Plataforma']} ({i['Meses']} Meses)\n"
                    st.session_state.m_cotiza = cargar_plantilla("cotizacion").replace("[servicios]", t_s.strip()).replace("[monto_usd]", f"{m_tot:.2f}").replace("[monto_bs]", f"{m_tot * st.session_state.tasa_cambio:,.2f}")
                    st.rerun()
                
                if b_conf:
                    if not cli.strip():
                        st.error("⚠️ Faltan datos.")
                    else:
                        m_div = round(m_tot / len(st.session_state.carrito), 2)
                        m_uni = ""
                        f_nuevas = []
                        p_nuevos = []
                        e_ini = "Activo" if act_ya else "Pendiente"
                        r_ven = cargar_plantilla("venta")
                        f_base = date.today()
                        
                        for i in st.session_state.carrito:
                            f_c = sumar_meses(f_base, i["Meses"])
                            f_nuevas.append({
                                "Cliente": cli, "Telefono": tel, "Plataforma": i["Plataforma"], 
                                "Correo": i["Correo_Matriz"] if not i["Correo_Cliente"] else i["Correo_Cliente"], 
                                "Perfil_Pantalla": i["Perfil_Pantalla"], "Fecha_Inicio": str(f_base), "Fecha_Corte": str(f_c), 
                                "Metodo_Pago": met, "Monto": str(m_div), "Clave_Spotify": i["Clave_Cliente"], 
                                "Estado_Servicio": e_ini, "Fecha_Congelamiento": "", "Meses_Contratados": str(i["Meses"])
                            })
                            
                            p_nuevos.append({
                                "Fecha": str(f_base), "Cliente": cli, "Plataforma": i["Plataforma"],
                                "Correo": i["Correo_Matriz"] if not i["Correo_Cliente"] else i["Correo_Cliente"],
                                "Perfil_Pantalla": i["Perfil_Pantalla"], "Monto": str(m_div),
                                "Metodo_Pago": met, "Meses": str(i["Meses"]), "Tipo": "Venta"
                            })
                            
                            idx = i["index_original"]
                            df_inv_actual.at[idx, "Estado"] = "Ocupado"
                            df_inv_actual.at[idx, "PIN"] = i["PIN"]
                            df_inv_actual.at[idx, "Perfil_Pantalla"] = i["Perfil_Pantalla"]
                            
                            c_imp = i["Correo_Cliente"] if i["Correo_Cliente"] else i["Correo_Matriz"]
                            m_uni += r_ven.replace("[plataforma]", i["Plataforma"]).replace("[correo]", c_imp).replace("[clave]", i["Clave_Matriz"]).replace("[perfil]", i["Perfil_Pantalla"]).replace("[pin]", i["PIN"]).replace("[fecha_corte]", "En Pausa" if not act_ya else f_c.strftime('%d/%m/%Y')) + "\n\n"
                        
                        agregar_filas("clientes", pd.DataFrame(f_nuevas), COLUMNAS_CLI)
                        guardar_tabla("inventario", df_inv_actual, COLUMNAS_INV)
                        registrar_pagos(p_nuevos)
                        st.session_state.m_exito = "¡Venta Guardada!"
                        st.session_state.m_copia = m_uni.strip()
                        st.session_state.carrito = []
                        st.rerun()

# ==============================================================================
# MÓDULO 3: BASE DE DATOS
# ==============================================================================
elif menu == "🗃️ Base de Datos":
    st.header("🗃️ Gestor de Bases de Datos")
    
    opcion_bd = st.radio("Selecciona la Base de Datos a visualizar:", ["👥 Base de Clientes Activos", "📦 Inventario Completo de Cuentas"], horizontal=True, label_visibility="collapsed", key="bd_radio")
    st.markdown("---")
    
    if opcion_bd == "👥 Base de Clientes Activos":
        st.subheader("Clientes y Fechas")
        df_c = leer_tabla("clientes", COLUMNAS_CLI)
        
        if not df_c.empty:
            st.table(df_c)
            
            st.markdown("---")
            st.subheader("✏️ Editar o Eliminar Cliente")
            
            cli_a_editar = st.selectbox("1. Selecciona el cliente:", ["---"] + sorted(df_c["Cliente"].unique().tolist()), key="edit_cli_sel")
            
            if cli_a_editar != "---":
                filas_cli = df_c[df_c["Cliente"] == cli_a_editar]
                opciones_pantalla = filas_cli.apply(lambda r: f"{r['Plataforma']} - {r['Correo']} ({r['Perfil_Pantalla']})", axis=1).tolist()
                
                pantalla_a_editar = st.selectbox("2. Selecciona el servicio a editar:", opciones_pantalla, key="edit_cli_pant")
                
                if pantalla_a_editar:
                    filtro_busqueda = filas_cli.apply(lambda r: f"{r['Plataforma']} - {r['Correo']} ({r['Perfil_Pantalla']})", axis=1) == pantalla_a_editar
                    idx_real = filas_cli.index[filtro_busqueda].tolist()[0]
                    datos_fila = df_c.loc[idx_real]
                    
                    with st.form("form_edit_cli"):
                        c1, c2, c3 = st.columns(3)
                        n_tel = c1.text_input("Teléfono", value=str(datos_fila["Telefono"]))
                        
                        try:
                            fecha_actual = pd.to_datetime(datos_fila["Fecha_Corte"]).date()
                        except:
                            fecha_actual = date.today()
                            
                        n_f_corte = c2.date_input("Fecha de Corte", value=fecha_actual)
                        
                        opciones_estado = ["Activo", "Pendiente", "Congelado"]
                        idx_estado = opciones_estado.index(datos_fila["Estado_Servicio"]) if datos_fila["Estado_Servicio"] in opciones_estado else 0
                        n_est = c3.selectbox("Estado del Servicio", opciones_estado, index=idx_estado)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        if col_btn1.form_submit_button("💾 Guardar Cambios", type="primary"):
                            df_c.at[idx_real, "Telefono"] = str(n_tel)
                            df_c.at[idx_real, "Fecha_Corte"] = str(n_f_corte)
                            df_c.at[idx_real, "Estado_Servicio"] = str(n_est)
                            guardar_tabla("clientes", df_c, COLUMNAS_CLI)
                            st.success("¡Cliente actualizado en la nube!")
                            st.rerun()
                            
                        if col_btn2.form_submit_button("🗑️ Eliminar Registro de la Nube"): 
                            df_c = df_c.drop(idx_real)
                            guardar_tabla("clientes", df_c, COLUMNAS_CLI)
                            st.warning("¡Registro borrado para siempre!")
                            st.rerun()
        else:
            st.info("La Base de Datos de Clientes está completamente vacía.")
            
    elif opcion_bd == "📦 Inventario Completo de Cuentas":
        st.subheader("Todas las Matrices y Perfiles")
        df_i = leer_tabla("inventario", COLUMNAS_INV)
        
        if not df_i.empty:
            st.table(df_i)
            
            st.markdown("---")
            st.subheader("✏️ Editar o Eliminar Inventario")
            
            opciones_inv = df_i.apply(lambda r: f"{r['Plataforma']} | {r['Correo']} - Perfil: {r['Perfil_Pantalla']}", axis=1).tolist()
            inv_a_editar = st.selectbox("Selecciona la pantalla exacta a modificar:", ["---"] + opciones_inv, key="edit_inv_sel")
            
            if inv_a_editar != "---":
                filtro_busqueda_i = df_i.apply(lambda r: f"{r['Plataforma']} | {r['Correo']} - Perfil: {r['Perfil_Pantalla']}", axis=1) == inv_a_editar
                idx_real_i = df_i.index[filtro_busqueda_i].tolist()[0]
                datos_fila_i = df_i.loc[idx_real_i]
                
                with st.form("form_edit_inv"):
                    ci1, ci2, ci3, ci4 = st.columns(4)
                    
                    opc_est_inv = ["Disponible", "Ocupado", "🔴 En Revisión"]
                    idx_est_inv = opc_est_inv.index(datos_fila_i["Estado"]) if datos_fila_i["Estado"] in opc_est_inv else 0
                    ni_est = ci1.selectbox("Estado", opc_est_inv, index=idx_est_inv)
                    
                    ni_pin = ci2.text_input("PIN", value=str(datos_fila_i["PIN"]))
                    
                    ni_costo = ci3.text_input("Costo ($)", value=str(datos_fila_i.get("Costo_Matriz", "0.0")))
                    
                    try:
                        fecha_pago_act = pd.to_datetime(datos_fila_i["Fecha_Pago"]).date()
                    except:
                        fecha_pago_act = date.today()
                        
                    ni_f_pago = ci4.date_input("Próximo Pago", value=fecha_pago_act)
                    
                    col_btn1_i, col_btn2_i = st.columns(2)
                    if col_btn1_i.form_submit_button("💾 Guardar Cambios", type="primary"):
                        df_i.at[idx_real_i, "Estado"] = str(ni_est)
                        df_i.at[idx_real_i, "PIN"] = str(ni_pin)
                        df_i.at[idx_real_i, "Costo_Matriz"] = str(ni_costo)
                        df_i.at[idx_real_i, "Fecha_Pago"] = str(ni_f_pago)
                        guardar_tabla("inventario", df_i, COLUMNAS_INV)
                        st.success("¡Inventario actualizado en la nube!")
                        st.rerun()
                        
                    if col_btn2_i.form_submit_button("🗑️ Eliminar Registro de la Nube"):
                        df_i = df_i.drop(idx_real_i)
                        guardar_tabla("inventario", df_i, COLUMNAS_INV)
                        st.warning("¡Registro borrado para siempre!")
                        st.rerun()
        else:
            st.info("El Inventario está completamente vacío.")

# ==============================================================================
# MÓDULO 4: FINANZAS 
# ==============================================================================
elif menu == "💰 Finanzas":
    st.header("Centro de Precios y Contabilidad 📊")
    
    st.markdown("### 💱 Tasa de Cambio Oficial")
    c_tasa1, c_tasa2 = st.columns([2, 1])
    with c_tasa1:
        t_man = st.number_input("Tasa Activa (Bs / USD)", min_value=0.01, value=to_float(st.session_state.tasa_cambio), step=0.01, key="fin_tasa")
        if t_man != st.session_state.tasa_cambio:
             st.session_state.tasa_cambio = t_man
             st.session_state.ultima_actualizacion = datetime.now()
    with c_tasa2:
        st.write(" ")
        st.write(" ")
        if st.button("🔄 Consulta Binance P2P", type="secondary", key="fin_btn_bin"):
            t_n = obtener_tasa_binance()
            if t_n:
                st.session_state.tasa_cambio = t_n
                st.session_state.ultima_actualizacion = datetime.now()
                st.success(f"¡Conectado! Tasa: **{t_n} Bs**")
                st.rerun()

    st.markdown("### 📋 Catálogo de Venta al Público")
    df_pre = leer_tabla("precios", COLUMNAS_PRE)
    
    st.table(df_pre[["Plataforma", "Precio_Venta_Perfil"]])
    
    with st.form("form_add_precio"):
        st.markdown("#### ✏️ Agregar o Editar Plataforma")
        c_p1, c_p2 = st.columns(2)
        p_nom = c_p1.text_input("Plataforma (Ej: NETFLIX)")
        p_vent = c_p2.number_input("Precio de Venta Sugerido ($)", min_value=0.0, step=0.5)
        
        if st.form_submit_button("💾 Guardar Catálogo", type="primary"):
            if p_nom.strip() != "":
                nom_up = p_nom.upper().strip()
                if not df_pre.empty and nom_up in df_pre["Plataforma"].values:
                    df_pre.loc[df_pre["Plataforma"] == nom_up, "Precio_Venta_Perfil"] = str(p_vent)
                else:
                    nueva_fila = pd.DataFrame([{"Plataforma": nom_up, "Costo_Matriz": "0", "Precio_Venta_Perfil": str(p_vent)}])
                    df_pre = pd.concat([df_pre, nueva_fila], ignore_index=True)
                
                guardar_tabla("precios", df_pre, COLUMNAS_PRE)
                st.success("¡Catálogo actualizado!")
                st.rerun()
            else:
                st.error("⚠️ Escribe un nombre para la plataforma.")
        
    st.markdown("---")
    df_inv = leer_tabla("inventario", COLUMNAS_INV)
    df_cli = leer_tabla("clientes", COLUMNAS_CLI)
    df_pag = leer_tabla("pagos", COLUMNAS_PAG)

    with st.expander("📥 Importar ventas actuales al historial (hazlo una sola vez)"):
        st.caption("Copia tus clientes actuales al historial de pagos, para que no empiecen en cero. No duplica lo que ya esté anotado.")
        if st.button("📥 Importar ahora", key="btn_imp_pagos", type="secondary"):
            base_imp = df_cli[df_cli["Estado_Servicio"] != "Pendiente"]
            existentes = set(zip(df_pag["Cliente"], df_pag["Plataforma"], df_pag["Perfil_Pantalla"], df_pag["Fecha"]))
            nuevos_imp = []
            for _, r_c in base_imp.iterrows():
                if (r_c["Cliente"], r_c["Plataforma"], r_c["Perfil_Pantalla"], r_c["Fecha_Inicio"]) in existentes:
                    continue
                nuevos_imp.append({
                    "Fecha": r_c["Fecha_Inicio"], "Cliente": r_c["Cliente"], "Plataforma": r_c["Plataforma"],
                    "Correo": r_c["Correo"], "Perfil_Pantalla": r_c["Perfil_Pantalla"], "Monto": r_c["Monto"],
                    "Metodo_Pago": r_c["Metodo_Pago"], "Meses": r_c["Meses_Contratados"], "Tipo": "Importado"
                })
            if nuevos_imp:
                if agregar_filas("pagos", pd.DataFrame(nuevos_imp), COLUMNAS_PAG):
                    st.success(f"¡Listo! Se importaron {len(nuevos_imp)} pagos.")
                    st.rerun()
            else:
                st.info("No hay nada nuevo que importar.")

    # Mes a revisar
    df_pag["Fecha_Real"] = pd.to_datetime(df_pag["Fecha"], errors="coerce")
    df_pag["Mes"] = df_pag["Fecha_Real"].dt.strftime("%Y-%m")
    df_pag["Monto_f"] = df_pag["Monto"].apply(to_float).astype(float)
    meses_disp = sorted([m for m in df_pag["Mes"].dropna().unique().tolist()], reverse=True)
    mes_actual = date.today().strftime("%Y-%m")
    if mes_actual not in meses_disp:
        meses_disp.insert(0, mes_actual)
    mes_sel = st.selectbox("📅 Mes a revisar", meses_disp, key="fin_mes")
    df_mes = df_pag[df_pag["Mes"] == mes_sel]

    st.markdown("### 📊 Rentabilidad Detallada por Plataforma")
    st.caption("Ingresos: pagos recibidos en el mes elegido. Costos: lo que cuestan hoy tus cuentas matrices por mes (31 días).")
    datos_finanzas = []
    
    for plat in df_pre["Plataforma"].unique():
        ing_plat = float(df_mes[df_mes["Plataforma"] == plat]["Monto_f"].sum())
        
        if not df_inv.empty:
            matrices_unicas = df_inv[df_inv["Plataforma"] == plat].drop_duplicates(subset=["Correo"])
            cost_plat = sum([to_float(x.get("Costo_Matriz", 0.0)) for _, x in matrices_unicas.iterrows()])
        else:
            cost_plat = 0.0
            
        if cost_plat > 0 or ing_plat > 0:
            datos_finanzas.append({
                "Plataforma": plat, 
                "Ingresos del mes": f"${ing_plat:.2f}", 
                "Costos Proveedor": f"${cost_plat:.2f}", 
                "Ganancia Neta": f"${ing_plat - cost_plat:.2f}"
            })
            
    if datos_finanzas:
        st.table(pd.DataFrame(datos_finanzas))
    else:
        st.info("Aún no hay movimientos financieros registrados.")

    st.markdown("---")
    
    ingresos_t = float(df_mes["Monto_f"].sum())
    
    if not df_inv.empty:
        matrices_todas = df_inv.drop_duplicates(subset=["Correo", "Plataforma"])
        costos_t = sum([to_float(x.get("Costo_Matriz", 0.0)) for _, x in matrices_todas.iterrows()])
    else:
        costos_t = 0.0
        
    ganancia_t = ingresos_t - costos_t
    ts = st.session_state.tasa_cambio
    
    st.markdown(f"### 📈 Balance del mes ({mes_sel})")
    m1, m2, m3 = st.columns(3)
    m1.metric("💵 Ingresos USD", f"${ingresos_t:,.2f}")
    m2.metric("💵 Costos USD", f"${costos_t:,.2f}")
    m3.metric("💵 Ganancia Neta USD", f"${ganancia_t:,.2f}")
    
    mb1, mb2, mb3 = st.columns(3)
    mb1.metric("🇻🇪 Ingresos Bs", f"{ingresos_t * ts:,.2f} Bs")
    mb2.metric("🇻🇪 Costos Bs", f"{costos_t * ts:,.2f} Bs")
    mb3.metric("🇻🇪 Ganancia Neta Bs", f"{ganancia_t * ts:,.2f} Bs")

    if not df_pag.empty:
        st.markdown("### 🗓️ Ingresos por mes")
        res_mes = df_pag.dropna(subset=["Mes"]).groupby("Mes")["Monto_f"].sum().reset_index().sort_values("Mes", ascending=False).head(12)
        res_mes["Monto_f"] = res_mes["Monto_f"].apply(lambda v: f"${v:,.2f}")
        res_mes.columns = ["Mes", "Ingresos"]
        st.table(res_mes)

    with st.expander(f"🧾 Ver los pagos de {mes_sel}"):
        if df_mes.empty:
            st.write("No hay pagos anotados en este mes.")
        else:
            st.table(df_mes.sort_values("Fecha_Real", ascending=False)[["Fecha", "Cliente", "Plataforma", "Perfil_Pantalla", "Monto", "Tipo"]])

# ==============================================================================
# MÓDULO 5: SOPORTES
# ==============================================================================
elif menu == "🛠️ Soportes":
    st.header("Soporte Técnico 🛠️")
    
    opcion_soporte = st.radio(
        "Selecciona la herramienta a utilizar:", 
        ["🩺 Atender Reporte", "🔄 Cambio Rápido Individual", "🚨 Crisis / Caída Masiva", "🔑 Actualizar Credenciales Matrices"],
        horizontal=True,
        label_visibility="collapsed",
        key="sop_radio"
    )
    st.markdown("---")
    
    if opcion_soporte == "🩺 Atender Reporte":
        st.info("🩺 Un cliente te reporta un problema: elige el cliente, el servicio y el tipo de falla, y te muestro qué hacer.")
        if "m_reporte" in st.session_state:
            st.success(st.session_state.pop("m_reporte_titulo", "¡Listo!"))
            st.code(st.session_state.m_reporte, language="markdown")
            del st.session_state.m_reporte

        df_cli_rep = leer_tabla("clientes", COLUMNAS_CLI)
        df_inv_rep = leer_tabla("inventario", COLUMNAS_INV)

        if df_cli_rep.empty:
            st.info("Todavía no hay clientes registrados.")
        else:
            cli_rep = st.selectbox("1. 👤 ¿Qué cliente reporta?", ["--- Seleccione ---"] + sorted(df_cli_rep["Cliente"].unique().tolist()), key="rep_cli")

            if cli_rep != "--- Seleccione ---":
                df_f_rep = df_cli_rep[(df_cli_rep["Cliente"] == cli_rep) & (df_cli_rep["Estado_Servicio"] != "Pendiente")]
                opc_rep = [""] + [f"{r['Plataforma']} | 📧 {r['Correo']} | Perfil: {r['Perfil_Pantalla']} (ID:{idx})" for idx, r in df_f_rep.iterrows()]
                serv_rep = st.selectbox("2. 📺 ¿Qué servicio tiene el problema?", opc_rep, key="rep_serv")

                if serv_rep:
                    idx_rep = int(serv_rep.split("(ID:")[1].replace(")", ""))
                    d_rep = df_cli_rep.loc[idx_rep]
                    tipos_rep = ["--- Seleccione ---", "🔢 El PIN no coincide", "🔑 El correo o la clave no funcionan", "💳 La cuenta sale sin pago / suspendida", "📺 La pantalla falla o no abre"]
                    tipo_rep = st.selectbox("3. ❓ ¿Qué problema tiene?", tipos_rep, key="rep_tipo")

                    m_inv_rep = df_inv_rep[(df_inv_rep["Plataforma"] == d_rep["Plataforma"]) & (df_inv_rep["Correo"] == d_rep["Correo"]) & (df_inv_rep["Perfil_Pantalla"] == d_rep["Perfil_Pantalla"])]
                    st.markdown("---")

                    if tipo_rep == "📺 La pantalla falla o no abre":
                        st.info("Para este caso usa **🔄 Cambio Rápido Individual**: le asigna una pantalla nueva y deja la vieja en revisión. Si le pasa a varios clientes de la misma cuenta, usa **🚨 Crisis / Caída Masiva**.")

                    elif tipo_rep != "--- Seleccione ---" and m_inv_rep.empty:
                        st.warning("No encontré esta pantalla en el inventario (puede ser un Spotify con correo del cliente, o el perfil cambió de nombre). Revísala en **Base de Datos > Inventario Completo**.")

                    elif tipo_rep == "🔢 El PIN no coincide":
                        i_inv = m_inv_rep.index[0]
                        d_inv = df_inv_rep.loc[i_inv]
                        st.markdown("**PIN guardado en tu sistema:**")
                        st.code(str(d_inv["PIN"]), language="markdown")
                        nuevo_pin = st.text_input("PIN correcto (cámbialo solo si lo cambiaste en la plataforma)", value=str(d_inv["PIN"]), key=f"rep_pin_{idx_rep}")
                        if st.button("💾 Guardar PIN y generar mensaje", type="primary", key=f"btn_rep_pin_{idx_rep}"):
                            if nuevo_pin.strip() == "":
                                st.error("⚠️ El PIN no puede estar vacío.")
                            else:
                                if nuevo_pin.strip() != str(d_inv["PIN"]):
                                    df_inv_rep.at[i_inv, "PIN"] = nuevo_pin.strip()
                                    guardar_tabla("inventario", df_inv_rep, COLUMNAS_INV)
                                st.session_state.m_reporte = armar_mensaje_datos(d_inv["Plataforma"], d_inv["Correo"], d_inv["Clave"], d_inv["Perfil_Pantalla"], nuevo_pin.strip(), d_rep["Fecha_Corte"])
                                st.session_state.m_reporte_titulo = "¡PIN al día! Mensaje listo para enviar:"
                                st.rerun()

                    elif tipo_rep == "🔑 El correo o la clave no funcionan":
                        i_inv = m_inv_rep.index[0]
                        d_inv = df_inv_rep.loc[i_inv]
                        st.markdown("**Datos guardados en tu sistema:**")
                        st.code(str(d_inv["Correo"]), language="markdown")
                        st.code(str(d_inv["Clave"]), language="markdown")
                        nueva_clave_rep = st.text_input("Clave correcta (cámbiala solo si cambió en la plataforma)", value=str(d_inv["Clave"]), key=f"rep_clave_{idx_rep}")
                        st.caption("Si lo que cambió fue el correo de la cuenta, usa **🔑 Actualizar Credenciales Matrices**.")
                        if st.button("💾 Guardar clave y generar mensaje", type="primary", key=f"btn_rep_clave_{idx_rep}"):
                            if nueva_clave_rep.strip() == "":
                                st.error("⚠️ La clave no puede estar vacía.")
                            else:
                                if nueva_clave_rep.strip() != str(d_inv["Clave"]):
                                    mask_cl = (df_inv_rep["Plataforma"] == d_inv["Plataforma"]) & (df_inv_rep["Correo"] == d_inv["Correo"])
                                    df_inv_rep.loc[mask_cl, "Clave"] = nueva_clave_rep.strip()
                                    guardar_tabla("inventario", df_inv_rep, COLUMNAS_INV)
                                st.session_state.m_reporte = armar_mensaje_datos(d_inv["Plataforma"], d_inv["Correo"], nueva_clave_rep.strip(), d_inv["Perfil_Pantalla"], d_inv["PIN"], d_rep["Fecha_Corte"])
                                st.session_state.m_reporte_titulo = "¡Datos al día! Mensaje listo para enviar:"
                                st.rerun()

                    elif tipo_rep == "💳 La cuenta sale sin pago / suspendida":
                        d_inv = df_inv_rep.loc[m_inv_rep.index[0]]
                        ip_txt = str(d_inv["IP_Region"])
                        corr_pago = ip_txt[len("EXTRA de "):] if ip_txt.startswith("EXTRA de ") else d_inv["Correo"]
                        plat_pago = d_inv["Plataforma"]
                        mat_pago = df_inv_rep[(df_inv_rep["Plataforma"] == plat_pago) & (df_inv_rep["Correo"] == corr_pago)]
                        if mat_pago.empty:
                            st.warning("No encontré la cuenta matriz que paga este servicio. Revisa el inventario.")
                        else:
                            fila_mat = mat_pago.iloc[0]
                            tot_pago, c_ext_pago, n_ext_pago = costo_con_extras(df_inv_rep, plat_pago, corr_pago, fila_mat["Costo_Matriz"])
                            n_cli_pago = df_cli_rep[(df_cli_rep["Plataforma"] == plat_pago) & (df_cli_rep["Correo"] == corr_pago)]["Cliente"].nunique()
                            st.markdown(f"**Cuenta que lo paga:** {plat_pago} | `{corr_pago}`")
                            st.markdown(f"**Próximo pago registrado:** {fila_mat['Fecha_Pago']} | **A pagar:** ${tot_pago:.2f} | **Clientes en esa cuenta:** {n_cli_pago}")
                            fp_pago = pd.to_datetime(fila_mat["Fecha_Pago"], errors="coerce")
                            if pd.isna(fp_pago) or fp_pago.date() > date.today():
                                st.warning("En tu sistema esta cuenta todavía no vence. Si en la plataforma sale sin pago, márcala como **por pagar hoy** para que aparezca en el aviso del Panel Diario.")
                                if st.button("🚨 Marcar como POR PAGAR HOY", type="primary", key=f"btn_rep_pago_{idx_rep}"):
                                    actualizar_fecha_pago(plat_pago, corr_pago, date.today())
                                    st.session_state.m_reporte = "¡Hola! Ya estamos reactivando tu cuenta, te aviso apenas quede lista 🙏"
                                    st.session_state.m_reporte_titulo = "Cuenta marcada como por pagar. Mensaje para el cliente:"
                                    st.rerun()
                            else:
                                st.success("Esta cuenta ya está vencida o vence hoy, así que aparece en el aviso del Panel Diario. Págala y pulsa **Ya pagué** ahí.")
                                st.code("¡Hola! Ya estamos reactivando tu cuenta, te aviso apenas quede lista 🙏", language="markdown")
                            if n_cli_pago > 1:
                                st.caption("Hay varios clientes en esta cuenta. Si todos reportan lo mismo, usa **🚨 Crisis / Caída Masiva**.")

    elif opcion_soporte == "🔄 Cambio Rápido Individual":
        if "m_swap" in st.session_state:
            st.success("¡Cambio realizado!")
            st.code(st.session_state.m_swap, language="markdown")
            del st.session_state.m_swap
            
        df_cli = leer_tabla("clientes", COLUMNAS_CLI)
        df_inv = leer_tabla("inventario", COLUMNAS_INV)
        
        if not df_cli.empty:
            cli_sop = st.selectbox("1. 👤 Selecciona al cliente afectado:", ["--- Seleccione ---"] + sorted(df_cli["Cliente"].unique().tolist()), key="sop_cli")
            
            if cli_sop and cli_sop != "--- Seleccione ---":
                df_f = df_cli[(df_cli["Cliente"] == cli_sop) & (df_cli["Estado_Servicio"] != "Pendiente")]
                
                opc_pantallas = [""] + [f"{r['Plataforma']} | 📧 {r['Correo']} | Perfil: {r['Perfil_Pantalla']} (ID:{idx})" for idx, r in df_f.iterrows()]
                serv_af = st.selectbox("2. 📺 ¿Qué pantalla falla?", opc_pantallas, key="sop_pant")
                
                if serv_af and serv_af != "":
                    idx_cli = int(serv_af.split("(ID:")[1].replace(")", ""))
                    d_viejo = df_cli.loc[idx_cli]
                    plat_af = d_viejo["Plataforma"]
                    
                    st.markdown("---")
                    disp = df_inv[(df_inv["Estado"] == "Disponible") & (df_inv["Plataforma"] == plat_af)]
                    
                    if disp.empty:
                        st.error(f"⚠️ No tienes pantallas libres de {plat_af}.")
                    else:
                        l_r = disp.apply(lambda r: f"{r['Correo']} - {r['Perfil_Pantalla']}", axis=1).tolist()
                        p_n = st.selectbox("3. 📦 Nueva pantalla a entregar:", l_r, key="sop_nueva")
                        
                        if st.button("🚀 Ejecutar Intercambio", type="primary", key="btn_swap"):
                            idx_n = disp.index[l_r.index(p_n)]
                            d_n = df_inv.loc[idx_n]
                            
                            m_v = df_inv[(df_inv["Correo"] == d_viejo["Correo"]) & (df_inv["Perfil_Pantalla"] == d_viejo["Perfil_Pantalla"])]
                            if not m_v.empty:
                                df_inv.at[m_v.index[0], "Estado"] = "🔴 En Revisión"
                            
                            df_inv.at[idx_n, "Estado"] = "Ocupado"
                            df_cli.at[idx_cli, "Correo"] = d_n["Correo"]
                            df_cli.at[idx_cli, "Perfil_Pantalla"] = d_n["Perfil_Pantalla"]
                            df_cli.at[idx_cli, "Clave_Spotify"] = "" 
                            
                            guardar_tabla("inventario", df_inv, COLUMNAS_INV)
                            guardar_tabla("clientes", df_cli, COLUMNAS_CLI)
                            
                            try:
                                fc_obj = pd.to_datetime(d_viejo['Fecha_Corte']).strftime('%d/%m/%Y')
                            except:
                                fc_obj = d_viejo['Fecha_Corte']
                            
                            st.session_state.m_swap = cargar_plantilla("soporte").replace("[plataforma]", plat_af).replace("[correo]", d_n['Correo']).replace("[clave]", d_n['Clave']).replace("[perfil]", d_n['Perfil_Pantalla']).replace("[pin]", d_n['PIN']).replace("[fecha_corte]", fc_obj)
                            st.rerun()

    elif opcion_soporte == "🚨 Crisis / Caída Masiva":
        st.info("💥 **Modo Pánico:** Pausa a todos los clientes de una cuenta específica de forma masiva.")
        df_cli_mas = leer_tabla("clientes", COLUMNAS_CLI)
        df_inv_mas = leer_tabla("inventario", COLUMNAS_INV)
        c_m1, c_m2 = st.columns(2)
        
        with c_m1:
            st.subheader("1. Congelar Cuenta")
            mat_act = df_inv_mas[df_inv_mas["Estado"] == "Ocupado"][["Plataforma", "Correo"]].drop_duplicates()
            
            if not mat_act.empty:
                opc_caidas = mat_act.apply(lambda r: f"{r['Plataforma']} | {r['Correo']}", axis=1).tolist()
                mat_cai = st.selectbox("Selecciona la cuenta caída:", ["--- Seleccione ---"] + opc_caidas, key="sop_caida")
                
                if mat_cai and mat_cai != "--- Seleccione ---" and st.button("💥 Declarar Caída", type="primary", key="btn_caida"):
                    p_cai, c_cai = mat_cai.split(" | ")
                    hoy_str = str(date.today())
                    
                    m_cli = (df_cli_mas["Plataforma"] == p_cai) & (df_cli_mas["Correo"] == c_cai)
                    df_cli_mas.loc[m_cli, "Estado_Servicio"] = "Congelado"
                    df_cli_mas.loc[m_cli, "Fecha_Congelamiento"] = hoy_str
                    
                    m_inv = (df_inv_mas["Plataforma"] == p_cai) & (df_inv_mas["Correo"] == c_cai)
                    df_inv_mas.loc[m_inv, "Estado"] = "🔴 En Revisión"
                    
                    guardar_tabla("clientes", df_cli_mas, COLUMNAS_CLI)
                    guardar_tabla("inventario", df_inv_mas, COLUMNAS_INV)
                    st.success("¡Clientes Congelados!")
                    st.rerun()
            else:
                st.write("Sin cuentas activas en uso.")
            
        with c_m2:
            st.subheader("2. Reactivar Cuenta")
            cong = df_cli_mas[df_cli_mas["Estado_Servicio"] == "Congelado"]
            
            if not cong.empty:
                opc_lev = cong[["Plataforma", "Correo"]].drop_duplicates().apply(lambda r: f"{r['Plataforma']} | {r['Correo']}", axis=1).tolist()
                mat_lev = st.selectbox("Selecciona a reactivar:", ["--- Seleccione ---"] + opc_lev, key="sop_lev")
                
                if mat_lev and mat_lev != "--- Seleccione ---" and st.button("▶️ Levantar Servicio", key="btn_lev"):
                    p_lev, c_lev = mat_lev.split(" | ")
                    hoy_d = date.today()
                    afect = cong[(cong["Plataforma"] == p_lev) & (cong["Correo"] == c_lev)]
                    
                    for idx, row in afect.iterrows():
                        try:
                            f_c_d = datetime.strptime(row["Fecha_Congelamiento"], "%Y-%m-%d").date()
                        except:
                            f_c_d = hoy_d
                            
                        d_p = max(0, (hoy_d - f_c_d).days)
                        
                        try:
                            f_c_v = datetime.strptime(row["Fecha_Corte"], "%Y-%m-%d").date()
                        except:
                            f_c_v = hoy_d
                        
                        df_cli_mas.at[idx, "Fecha_Corte"] = str(f_c_v + timedelta(days=d_p))
                        df_cli_mas.at[idx, "Estado_Servicio"] = "Activo"
                        df_cli_mas.at[idx, "Fecha_Congelamiento"] = ""
                        
                        m_i = df_inv_mas[(df_inv_mas["Plataforma"] == p_lev) & (df_inv_mas["Correo"] == c_lev) & (df_inv_mas["Perfil_Pantalla"] == row["Perfil_Pantalla"])]
                        if not m_i.empty:
                            df_inv_mas.at[m_i.index[0], "Estado"] = "Ocupado"
                            
                    guardar_tabla("clientes", df_cli_mas, COLUMNAS_CLI)
                    guardar_tabla("inventario", df_inv_mas, COLUMNAS_INV)
                    st.success("¡Servicios Reactivados!")
                    st.rerun()
            else:
                st.write("Sin cuentas congeladas actualmente.")

    elif opcion_soporte == "🔑 Actualizar Credenciales Matrices":
        st.info("🔑 Actualiza el correo, contraseña o el costo de inversión de la cuenta.")
        df_inv_cred = leer_tabla("inventario", COLUMNAS_INV)
        df_cli_cred = leer_tabla("clientes", COLUMNAS_CLI)
        
        if not df_inv_cred.empty:
            c_mat = df_inv_cred[["Plataforma", "Correo"]].drop_duplicates()
            l_opc = c_mat.apply(lambda r: f"{r['Plataforma']} | {r['Correo']}", axis=1).tolist()
            
            matriz_a_editar = st.selectbox("Selecciona la cuenta matriz a modificar:", ["--- Seleccione ---"] + l_opc, key="sop_mat_edit")
            
            if matriz_a_editar and matriz_a_editar != "--- Seleccione ---":
                plat_sel, corr_sel = matriz_a_editar.split(" | ")
                datos_act = df_inv_cred[(df_inv_cred["Plataforma"] == plat_sel) & (df_inv_cred["Correo"] == corr_sel)].iloc[0]
                
                with st.form("form_update_cred"):
                    nuevo_correo = st.text_input("Nuevo Correo (Déjalo igual si no cambió)", value=datos_act["Correo"], key=f"sop_new_corr_{corr_sel}")
                    nueva_clave = st.text_input("Nueva Contraseña", value=datos_act["Clave"], key=f"sop_new_pass_{corr_sel}")
                    
                    costo_actual = to_float(datos_act.get("Costo_Matriz", 0.0))
                    nuevo_costo = st.number_input("Costo de la Cuenta ($) (Por si subió o bajó de precio)", min_value=0.0, value=float(costo_actual), step=0.5, key=f"sop_new_cost_{corr_sel}")
                    
                    if st.form_submit_button("💾 Actualizar Cuenta", type="primary"):
                        if nuevo_correo.strip() == "" or nueva_clave.strip() == "":
                            st.error("⚠️ El correo y la contraseña no pueden estar en blanco.")
                        else:
                            mask_inv = (df_inv_cred["Plataforma"] == plat_sel) & (df_inv_cred["Correo"] == corr_sel)
                            df_inv_cred.loc[mask_inv, "Correo"] = nuevo_correo
                            df_inv_cred.loc[mask_inv, "Clave"] = nueva_clave
                            df_inv_cred.loc[mask_inv, "Costo_Matriz"] = str(nuevo_costo)
                            mask_ext = (df_inv_cred["Plataforma"] == plat_sel) & (df_inv_cred["IP_Region"] == f"EXTRA de {corr_sel}")
                            df_inv_cred.loc[mask_ext, "IP_Region"] = f"EXTRA de {nuevo_correo}"
                            
                            mask_cli = (df_cli_cred["Plataforma"] == plat_sel) & (df_cli_cred["Correo"] == corr_sel)
                            df_cli_cred.loc[mask_cli, "Correo"] = nuevo_correo
                            
                            guardar_tabla("inventario", df_inv_cred, COLUMNAS_INV)
                            guardar_tabla("clientes", df_cli_cred, COLUMNAS_CLI)
                            
                            st.success(f"¡Éxito! Todas las pantallas vinculadas a {matriz_a_editar} fueron actualizadas en la nube.")
                            st.rerun()

# ==============================================================================
# MÓDULO 6: CONFIGURACIÓN Y BACKUPS
# ==============================================================================
elif menu == "⚙️ Configuración":
    st.header("⚙️ Editor Maestro de Mensajes")
    st.info("💡 **Etiquetas:** `[cliente]`, `[servicios]`, `[monto_usd]`, `[monto_bs]`, `[plataforma]`, `[correo]`, `[clave]`, `[perfil]`, `[pin]`, `[fecha_corte]`.")
    
    try:
        with open(ARCHIVO_PLANTILLAS, 'r', encoding='utf-8') as f:
            plantillas = json.load(f)
    except:
        plantillas = {}
        
    with st.form("form_plantillas"):
        t_cobro = st.text_area("🟢 1. Cobro Diario", value=plantillas.get("cobro", ""), height=150, key="cfg_cobro")
        t_cot = st.text_area("📋 2. Cotización (Pago Móvil)", value=plantillas.get("cotizacion", ""), height=250, key="cfg_cot")
        t_ven = st.text_area("🛒 3. Venta Exitosa", value=plantillas.get("venta", ""), height=120, key="cfg_ven")
        t_sop = st.text_area("🛠️ 4. Soporte Técnico (Swap)", value=plantillas.get("soporte", ""), height=150, key="cfg_sop")
        
        if st.form_submit_button("💾 Guardar Plantillas", type="primary"):
            with open(ARCHIVO_PLANTILLAS, 'w', encoding='utf-8') as f:
                json.dump({"cobro": t_cobro, "cotizacion": t_cot, "venta": t_ven, "soporte": t_sop}, f, ensure_ascii=False, indent=4)
            st.success("¡Plantillas actualizadas!")
            st.rerun()

    st.markdown("---")
    
    st.subheader("💽 Sistema de Backups (Copia de Seguridad)")
    st.info("Descarga un archivo .zip con todas tus bases de datos descargadas directamente desde la nube de Supabase hasta este preciso momento.")
    
    # CAMBIO: el ZIP solo se arma cuando presionas el botón
    if st.button("🗂️ Preparar Copia de Seguridad", type="secondary", key="btn_prep_backup"):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zip_file:
            df_i = leer_tabla("inventario", COLUMNAS_INV)
            zip_file.writestr("inventario.csv", df_i.to_csv(index=False))
            
            df_c = leer_tabla("clientes", COLUMNAS_CLI)
            zip_file.writestr("clientes.csv", df_c.to_csv(index=False))
            
            df_p = leer_tabla("precios", COLUMNAS_PRE)
            zip_file.writestr("precios.csv", df_p.to_csv(index=False))
            
            df_pg = leer_tabla("pagos", COLUMNAS_PAG)
            zip_file.writestr("pagos.csv", df_pg.to_csv(index=False))
            
            if os.path.exists(ARCHIVO_PLANTILLAS):
                zip_file.write(ARCHIVO_PLANTILLAS)
        st.session_state.backup_zip = buffer.getvalue()
    
    if "backup_zip" in st.session_state:
        st.download_button(
            label="📦 Descargar Copia de Seguridad ahora",
            data=st.session_state.backup_zip,
            file_name=f"Backup_Streaming_Nube_{date.today()}.zip",
            mime="application/zip",
            type="primary",
            key="btn_backup"
        )
