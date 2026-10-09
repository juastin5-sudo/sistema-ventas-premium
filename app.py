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

def _texto_excel(v):
    """Normaliza valores leídos de Excel sin mostrar nan/nat como texto."""
    if pd.isna(v):
        return ""
    if isinstance(v, (datetime, date, pd.Timestamp)):
        return pd.to_datetime(v).strftime("%Y-%m-%d")
    texto = str(v).strip()
    return "" if texto.lower() in {"nan", "nat", "none"} else texto


def _fecha_excel(v):
    """Convierte fechas de Excel (incluidos números seriales) a YYYY-MM-DD."""
    if pd.isna(v) or str(v).strip() == "":
        return ""
    try:
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            # Fechas guardadas por Excel como número de serie.
            if 20000 <= float(v) <= 80000:
                return (pd.Timestamp("1899-12-30") + pd.to_timedelta(float(v), unit="D")).strftime("%Y-%m-%d")
        return pd.to_datetime(v, errors="raise").strftime("%Y-%m-%d")
    except Exception:
        return ""


def _correo_excel(v):
    """Limpia saltos de línea y texto adicional que algunas celdas tienen junto al correo."""
    texto = _texto_excel(v)
    if not texto:
        return ""
    lineas = [x.strip() for x in texto.splitlines() if x.strip()]
    for linea in lineas:
        if "@" in linea:
            return linea
    return lineas[0] if lineas else ""


def preparar_importacion_excel(archivo):
    """Lee el Excel y prepara inventario/clientes. No escribe nada en Supabase."""
    # Índices de columna verificados contra los encabezados del libro compartido.
    # La fila 4 de Excel contiene encabezados; los datos empiezan en la fila 5.
    mapas = {
        "NETFLIX":     {"email": 6, "clave": 7, "slot": 8, "pin": 9, "cliente": 11, "inicio": 12, "corte": 14, "fecha_pago": 3, "costo": 0, "monto": 17},
        "NETFLIX PE":  {"email": 6, "clave": 7, "slot": 8, "pin": 9, "cliente": 11, "inicio": 12, "corte": 14, "fecha_pago": 3, "costo": 0, "monto": 17},
        "SPOTIFY":     {"email": 7, "clave": 8, "slot": 9, "pin": None, "cliente": 11, "inicio": 12, "corte": 14, "fecha_pago": 3, "costo": 0, "monto": 17},
        "DISNEY":      {"email": 5, "clave": 6, "slot": 7, "pin": 8, "cliente": 10, "inicio": 11, "corte": 13, "fecha_pago": 3, "costo": 0, "monto": 16},
        "HBO MAX":     {"email": 5, "clave": 6, "slot": 7, "pin": 8, "cliente": 11, "inicio": 12, "corte": 14, "fecha_pago": 3, "costo": 0, "monto": 17},
        "AMAZON":      {"email": 6, "clave": 7, "slot": 8, "pin": 9, "cliente": 11, "inicio": 12, "corte": 14, "fecha_pago": 3, "costo": 0, "monto": 17},
        "CRUNCHY":     {"email": 6, "clave": 7, "slot": 8, "pin": None, "cliente": 10, "inicio": 11, "corte": 13, "fecha_pago": 3, "costo": 0, "monto": 16},
        "PARAMOUNT +": {"email": 6, "clave": 7, "slot": 8, "pin": None, "cliente": 10, "inicio": 11, "corte": 13, "fecha_pago": 3, "costo": 0, "monto": 16},
    }
    inventario, clientes, avisos = [], [], []
    contenido = archivo.getvalue() if hasattr(archivo, "getvalue") else archivo.read()
    libro = pd.ExcelFile(io.BytesIO(contenido))

    for hoja in libro.sheet_names:
        nombre_hoja = str(hoja).strip().upper()
        mapa = mapas.get(nombre_hoja)
        if not mapa:
            avisos.append(f"Hoja no reconocida; no se importó: {hoja}")
            continue
        df = libro.parse(sheet_name=hoja, header=None, dtype=object)
        if df.shape[0] <= 4:
            avisos.append(f"La hoja {hoja} no contiene filas de datos.")
            continue

        correo_actual, clave_actual = "", ""
        fecha_pago_actual, costo_actual = "", "0"
        numero_perfil = {}
        filas_sin_correo = 0

        for pos in range(4, len(df)):
            fila = df.iloc[pos]

            def celda(indice):
                return fila.iloc[indice] if indice is not None and indice < len(fila) else None

            correo_fila = _correo_excel(celda(mapa["email"]))
            clave_fila = _texto_excel(celda(mapa["clave"]))

            # Al comenzar una cuenta nueva, no reutilizar por error la clave de la anterior.
            if correo_fila and correo_fila.casefold() != correo_actual.casefold():
                correo_actual = correo_fila
                clave_actual = clave_fila
                fecha_pago_actual = _fecha_excel(celda(mapa["fecha_pago"]))
                costo_actual = _texto_excel(celda(mapa["costo"])) or "0"
            else:
                if clave_fila:
                    clave_actual = clave_fila
                fecha_pago_fila = _fecha_excel(celda(mapa["fecha_pago"]))
                if fecha_pago_fila:
                    fecha_pago_actual = fecha_pago_fila
                costo_fila = _texto_excel(celda(mapa["costo"]))
                if costo_fila:
                    costo_actual = costo_fila

            correo = correo_actual
            clave = clave_actual
            cliente = _texto_excel(celda(mapa["cliente"]))
            fecha_inicio = _fecha_excel(celda(mapa["inicio"]))
            fecha_corte = _fecha_excel(celda(mapa["corte"]))
            monto_cliente = _texto_excel(celda(mapa["monto"])) or "0"
            valor_slot = _texto_excel(celda(mapa["slot"]))
            pin = _texto_excel(celda(mapa["pin"])) if mapa["pin"] is not None else "N/A"

            if cliente.upper() in {"TOTAL", "TOTALES", "GANANCIA", "PRECIO DE CUENTA EN BS."}:
                continue
            # No importar filas de resumen ni inventar una cuenta cuando no se conoce el correo.
            if not any([cliente, fecha_inicio, fecha_corte, valor_slot, pin if pin != "N/A" else ""]):
                continue
            if not correo:
                filas_sin_correo += 1
                continue

            key_cuenta = (nombre_hoja, correo.casefold())
            numero_perfil[key_cuenta] = numero_perfil.get(key_cuenta, 0) + 1
            if nombre_hoja == "SPOTIFY":
                # La app identifica los cupos Spotify por correo del cliente.
                slot_label = correo
            elif valor_slot:
                slot_label = valor_slot if valor_slot.lower().startswith(("perfil", "cupo", "principal")) else f"Perfil {valor_slot}"
            else:
                slot_label = f"Perfil {numero_perfil[key_cuenta]}"

            plataforma = "CRUNCHY ROLL" if nombre_hoja == "CRUNCHY" else ("NETFLIX" if nombre_hoja == "NETFLIX PE" else nombre_hoja)
            es_extra_pendiente = nombre_hoja == "NETFLIX PE"
            # La relación con la matriz de los perfiles extra no se adivina.
            ip_region = "EXTRA PENDIENTE DE ASIGNAR" if es_extra_pendiente else ""
            # En Spotify la columna "Precio cuenta" no permite saber con seguridad el coste
            # de cada invitación individual; se deja en cero para no inflar los gastos.
            costo_inv = "0" if nombre_hoja == "SPOTIFY" else (costo_actual or "0")

            inventario.append({
                "Plataforma": plataforma, "Correo": correo, "Clave": clave,
                "Perfil_Pantalla": slot_label, "PIN": pin,
                "Estado": "Ocupado" if cliente else "Disponible",
                "Fecha_Pago": fecha_pago_actual, "IP_Region": ip_region,
                "Costo_Matriz": costo_inv
            })

            if cliente:
                if fecha_corte:
                    try:
                        estado = "Activo" if pd.to_datetime(fecha_corte).date() >= date.today() else "Pendiente"
                    except Exception:
                        estado = "Pendiente"
                else:
                    estado = "Pendiente"
                clientes.append({
                    "Cliente": cliente, "Telefono": "", "Plataforma": plataforma,
                    "Correo": correo, "Perfil_Pantalla": slot_label,
                    "Fecha_Inicio": fecha_inicio, "Fecha_Corte": fecha_corte,
                    "Metodo_Pago": "", "Monto": monto_cliente,
                    "Clave_Spotify": clave if nombre_hoja == "SPOTIFY" else "",
                    "Estado_Servicio": estado, "Fecha_Congelamiento": "",
                    "Meses_Contratados": "1"
                })

        if filas_sin_correo:
            avisos.append(f"{hoja}: {filas_sin_correo} fila(s) con datos de perfil/cliente se omitieron porque no tenían correo de cuenta identificable. Revísalas en el Excel antes de importarlas manualmente.")

    df_inv = pd.DataFrame(inventario, columns=COLUMNAS_INV).fillna("").astype(str)
    df_cli = pd.DataFrame(clientes, columns=COLUMNAS_CLI).fillna("").astype(str)
    if not df_inv.empty:
        df_inv = df_inv.drop_duplicates(subset=["Plataforma", "Correo", "Perfil_Pantalla"])
    if not df_cli.empty:
        df_cli = df_cli.drop_duplicates(subset=["Plataforma", "Correo", "Cliente", "Fecha_Inicio", "Fecha_Corte"])
    return df_inv, df_cli, avisos

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

def buscar_fila_inv(df_inv, fila_cli):
    """Índice de la pantalla del inventario que usa un servicio de cliente (o None)."""
    if fila_cli["Plataforma"] == "SPOTIFY":
        m = df_inv[(df_inv["Plataforma"] == "SPOTIFY") & (df_inv["Perfil_Pantalla"] == fila_cli["Perfil_Pantalla"])]
    else:
        m = df_inv[(df_inv["Plataforma"] == fila_cli["Plataforma"]) & (df_inv["Correo"] == fila_cli["Correo"]) & (df_inv["Perfil_Pantalla"] == fila_cli["Perfil_Pantalla"])]
    return m.index[0] if not m.empty else None

def matriz_de_servicio(df_inv, fila_cli):
    """(plataforma, correo de la cuenta que respalda el servicio). En Spotify el cliente usa su propio correo."""
    plat = fila_cli["Plataforma"]
    if plat == "SPOTIFY":
        i = buscar_fila_inv(df_inv, fila_cli)
        return plat, (df_inv.loc[i, "Correo"] if i is not None else None)
    return plat, fila_cli["Correo"]

def pantallas_huerfanas(df_inv, df_cli):
    """Pantallas que no salen para vender y que ningún cliente tiene."""
    usados = set()
    for _, r in df_cli.iterrows():
        i = buscar_fila_inv(df_inv, r)
        if i is not None:
            usados.add(i)
    filas, idxs = [], []
    for i, r in df_inv.iterrows():
        est = r["Estado"]
        if est == "Ocupado" and i not in usados:
            motivo = "Está Ocupada pero ningún cliente la tiene"
        elif est not in ("Disponible", "Ocupado", "🔴 En Revisión"):
            motivo = f"Estado raro: '{est}'"
        else:
            continue
        filas.append({"Plataforma": r["Plataforma"], "Correo": r["Correo"], "Perfil_Pantalla": r["Perfil_Pantalla"], "Estado": est, "Motivo": motivo})
        idxs.append(i)
    return pd.DataFrame(filas, index=idxs) if filas else pd.DataFrame()

def es_spotify_con_correo_cliente(fila_cli):
    return fila_cli["Plataforma"] == "SPOTIFY" and str(fila_cli["Perfil_Pantalla"]) == str(fila_cli["Correo"])

def reasignar_servicio(df_c, df_inv, idx_c, nuevo_i, correo_cli, ant_revision):
    """Mueve un servicio de cliente a otra pantalla del inventario y libera la anterior."""
    fila = df_c.loc[idx_c]
    i_old = buscar_fila_inv(df_inv, fila)
    spot_cli = es_spotify_con_correo_cliente(fila)
    if i_old is not None:
        df_inv.at[i_old, "Estado"] = "🔴 En Revisión" if ant_revision else "Disponible"
        if spot_cli:
            df_inv.at[i_old, "Perfil_Pantalla"] = "Cupo libre"
    df_inv.at[nuevo_i, "Estado"] = "Ocupado"
    if spot_cli:
        corr = str(correo_cli).strip() or str(fila["Correo"])
        df_inv.at[nuevo_i, "Perfil_Pantalla"] = corr
        df_c.at[idx_c, "Correo"] = corr
        df_c.at[idx_c, "Perfil_Pantalla"] = corr
    else:
        df_c.at[idx_c, "Correo"] = df_inv.at[nuevo_i, "Correo"]
        df_c.at[idx_c, "Perfil_Pantalla"] = df_inv.at[nuevo_i, "Perfil_Pantalla"]
    return df_c, df_inv

def cambiar_correo_spotify(df_c, df_inv, idx_c, nuevo_correo):
    """Cambia el correo del cliente de Spotify y el nombre de su cupo en el inventario."""
    fila = df_c.loc[idx_c]
    nuevo = str(nuevo_correo).strip()
    if not es_spotify_con_correo_cliente(fila) or not nuevo or nuevo == str(fila["Correo"]):
        return df_c, df_inv
    i_old = buscar_fila_inv(df_inv, fila)
    if i_old is not None:
        df_inv.at[i_old, "Perfil_Pantalla"] = nuevo
    df_c.at[idx_c, "Correo"] = nuevo
    df_c.at[idx_c, "Perfil_Pantalla"] = nuevo
    return df_c, df_inv

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
    ["📌 Panel Diario", "📦 Registrar Cuentas", "🛒 Vender Perfiles", "📥 Importar Excel", "🗃️ Base de Datos", "💰 Finanzas", "🛠️ Soportes", "⚙️ Configuración"],
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

    n_pin = int((df_inv_res["Estado"] == "🔴 En Revisión").sum()) if not df_inv_res.empty else 0
    r1, r2, r3, r4, r5, r6 = st.columns(6)
    r1.metric("Clientes vencidos", n_venc)
    r2.metric("Cobran hoy", n_hoy)
    r3.metric("Próximos 3 días", n_prox)
    r4.metric("Por cobrar (USD)", f"${por_cobrar:,.2f}")
    r5.metric("Matrices por pagar", n_mat)
    r6.metric("PINs por cambiar", n_pin)

    if avisos_mat:
        st.warning(
            f"⚠️ **Paga estas cuentas matrices para que no se caigan (aviso {DIAS_AVISO_MATRIZ} días antes):**\n\n"
            + "\n".join(avisos_mat)
            + f"\n\n**Total a pagar: ${total_mat:,.2f} | {total_mat * st.session_state.tasa_cambio:,.2f} Bs**"
        )

    if "aviso_corte" in st.session_state:
        st.success(st.session_state.pop("aviso_corte"))

    en_rev_top = df_inv_res[df_inv_res["Estado"] == "🔴 En Revisión"] if not df_inv_res.empty else df_inv_res
    if not en_rev_top.empty:
        st.error(f"🔑 **{len(en_rev_top)} pantalla(s) por limpiar.** Cambia el PIN en la plataforma (en Spotify, saca al cliente del plan), anótalo aquí y pulsa Reactivar para volver a ponerla a la venta.")
        for idx_r, row_r in en_rev_top.iterrows():
            es_spot_r = row_r["Plataforma"] == "SPOTIFY"
            with st.container():
                st.markdown(f"🔴 **{row_r['Plataforma']}** | Perfil anterior: **{row_r['Perfil_Pantalla']}**")
                cr1, cr2, cr3 = st.columns(3)
                with cr1:
                    st.code(row_r["Correo"], language="markdown")
                with cr2:
                    st.code(row_r["Clave"], language="markdown")
                with cr3:
                    if es_spot_r:
                        nombre_cupo = st.text_input("Nombre del cupo libre:", value="Cupo libre" if "@" in str(row_r["Perfil_Pantalla"]) else str(row_r["Perfil_Pantalla"]), key=f"rn_{idx_r}")
                        if st.button("✅ Reactivar", key=f"rbs_{idx_r}", type="primary"):
                            df_inv_res.at[idx_r, "Estado"] = "Disponible"
                            df_inv_res.at[idx_r, "Perfil_Pantalla"] = nombre_cupo.strip() or "Cupo libre"
                            guardar_tabla("inventario", df_inv_res, COLUMNAS_INV)
                            st.rerun()
                    else:
                        nuevo_pin_r = st.text_input("NUEVO PIN:", value=str(row_r["PIN"]), key=f"rp_{idx_r}")
                        if st.button("✅ Reactivar", key=f"rb_{idx_r}", type="primary"):
                            df_inv_res.at[idx_r, "Estado"] = "Disponible"
                            df_inv_res.at[idx_r, "PIN"] = str(nuevo_pin_r)
                            guardar_tabla("inventario", df_inv_res, COLUMNAS_INV)
                            st.rerun()
        st.markdown("---")

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
                orden_cli = df_vencidos.assign(D=(df_vencidos["Fecha_Real"] - hoy_pd).dt.days).groupby("Cliente")["D"].min().sort_values(kind="stable")
                grupo_actual = None
                for cli in orden_cli.index.tolist():
                    d_grupo = int(orden_cli[cli])
                    g_nuevo = "venc" if d_grupo < 0 else ("hoy" if d_grupo == 0 else "prox")
                    if g_nuevo != grupo_actual:
                        grupo_actual = g_nuevo
                        st.markdown({"venc": "#### 🔴 Vencidos", "hoy": "#### 🟡 Cobran hoy", "prox": "#### 🔵 Próximos a vencer"}[g_nuevo])
                    df_cli_actual = df_vencidos[df_vencidos["Cliente"] == cli].sort_values("Fecha_Real")
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
                                        i_inv_nr = buscar_fila_inv(df_full_inv, r_d)
                                        if i_inv_nr is not None:
                                            df_full_inv.at[i_inv_nr, "Estado"] = "🔴 En Revisión"
                                        i_borrar.append(idx_row)
                                    guardar_tabla("clientes", df_full_cli.drop(i_borrar), COLUMNAS_CLI)
                                    guardar_tabla("inventario", df_full_inv, COLUMNAS_INV)
                                    st.session_state.aviso_corte = f"✂️ Cortaste {len(i_borrar)} servicio(s). Revisa abajo la sección '🔑 pantallas por limpiar' para cambiar el PIN."
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
                
                usar_fecha_manual = st.checkbox("📅 Cliente que ya tenía el servicio: poner la fecha de corte a mano", value=False, key=f"frm_usar_fecha_{cart_len}")
                fecha_corte_manual = st.date_input("Fecha de corte (solo se usa si marcaste la casilla de arriba)", value=date.today(), key=f"frm_fecha_corte_{cart_len}")
                st.caption("Si marcas la casilla, la fecha de inicio se calcula hacia atrás según los meses contratados, y el pago queda anotado en esa fecha (no en el mes de hoy).")
                
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
                            if usar_fecha_manual and act_ya:
                                f_c = fecha_corte_manual
                                f_ini = sumar_meses(fecha_corte_manual, -int(i["Meses"]))
                                tipo_pago = "Importado"
                            else:
                                f_c = sumar_meses(f_base, i["Meses"])
                                f_ini = f_base
                                tipo_pago = "Venta"
                            f_nuevas.append({
                                "Cliente": cli, "Telefono": tel, "Plataforma": i["Plataforma"], 
                                "Correo": i["Correo_Matriz"] if not i["Correo_Cliente"] else i["Correo_Cliente"], 
                                "Perfil_Pantalla": i["Perfil_Pantalla"], "Fecha_Inicio": str(f_ini), "Fecha_Corte": str(f_c), 
                                "Metodo_Pago": met, "Monto": str(m_div), "Clave_Spotify": i["Clave_Cliente"], 
                                "Estado_Servicio": e_ini, "Fecha_Congelamiento": "", "Meses_Contratados": str(i["Meses"])
                            })
                            
                            p_nuevos.append({
                                "Fecha": str(f_ini), "Cliente": cli, "Plataforma": i["Plataforma"],
                                "Correo": i["Correo_Matriz"] if not i["Correo_Cliente"] else i["Correo_Cliente"],
                                "Perfil_Pantalla": i["Perfil_Pantalla"], "Monto": str(m_div),
                                "Metodo_Pago": met, "Meses": str(i["Meses"]), "Tipo": tipo_pago
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

# ================================================================================
# MÓDULO DE IMPORTACIÓN DESDE EXCEL
# ================================================================================
elif menu == "📥 Importar Excel":
    st.header("📥 Importar registros desde Excel")
    st.write("Carga el archivo .xlsx original. No necesitas convertirlo a CSV.")
    st.warning("La importación es aditiva: no borra tablas ni reemplaza datos. Revisa la vista previa antes de guardar. No se crean pagos históricos ni se inventan costes de Spotify. Los perfiles extra de NETFLIX PE quedan pendientes de asignar a su matriz.")
    archivo_excel = st.file_uploader("Selecciona tu Excel de plataformas", type=["xlsx"], key="subir_excel_registros")
    if archivo_excel is not None:
        try:
            df_import_inv, df_import_cli, avisos_import = preparar_importacion_excel(archivo_excel)
            # No continuar si no se puede leer Supabase: hacerlo podría causar duplicados.
            try:
                inv_actual = _leer_tabla_cache("inventario", COLUMNAS_INV)
                cli_actual = _leer_tabla_cache("clientes", COLUMNAS_CLI)
            except Exception as e_db:
                st.error(f"No se pudo leer Supabase para comprobar duplicados. No se importó nada. Detalle: {e_db}")
                st.stop()
            if not inv_actual.empty:
                claves_inv = set((inv_actual["Plataforma"].str.upper().str.strip() + "|" + inv_actual["Correo"].str.lower().str.strip() + "|" + inv_actual["Perfil_Pantalla"].str.lower().str.strip()).tolist())
                df_import_inv = df_import_inv[~(df_import_inv["Plataforma"].str.upper().str.strip() + "|" + df_import_inv["Correo"].str.lower().str.strip() + "|" + df_import_inv["Perfil_Pantalla"].str.lower().str.strip()).isin(claves_inv)]
            if not cli_actual.empty:
                def clave_cliente(df):
                    return (df["Plataforma"].str.upper().str.strip() + "|" + df["Correo"].str.lower().str.strip() + "|" + df["Cliente"].str.lower().str.strip() + "|" + df["Fecha_Inicio"].str.strip() + "|" + df["Fecha_Corte"].str.strip())
                claves_cli = set(clave_cliente(cli_actual).tolist())
                df_import_cli = df_import_cli[~clave_cliente(df_import_cli).isin(claves_cli)]
            st.subheader("Resumen de la vista previa")
            m1, m2, m3 = st.columns(3)
            m1.metric("Cuentas/perfiles nuevos", len(df_import_inv))
            m2.metric("Clientes nuevos", len(df_import_cli))
            m3.metric("Hojas leídas", len(pd.ExcelFile(archivo_excel).sheet_names))
            if avisos_import:
                for aviso in avisos_import:
                    st.info(aviso)
            with st.expander("Revisar inventario que se agregará", expanded=False):
                st.dataframe(df_import_inv.drop(columns=["Clave"], errors="ignore"), use_container_width=True, hide_index=True)
            with st.expander("Revisar clientes que se agregarán", expanded=True):
                st.dataframe(df_import_cli.drop(columns=["Clave_Spotify"], errors="ignore"), use_container_width=True, hide_index=True)
            st.caption("Por seguridad, las contraseñas no se muestran en las vistas previas. Fecha de inicio, fecha de corte y monto del cliente se leen de las columnas del Excel. El costo de Spotify queda en 0 hasta confirmar cómo repartir el costo familiar. Los perfiles extra quedan sin matriz asignada hasta revisarlos.")
            confirmar_importacion = st.checkbox("Confirmo que revisé la vista previa y quiero agregar solo los registros nuevos.", key="confirmar_import_excel")
            if st.button("🚀 Importar registros a Supabase", type="primary", disabled=not confirmar_importacion, key="btn_importar_excel_supabase"):
                if len(df_import_inv) == 0 and len(df_import_cli) == 0:
                    st.info("No hay registros nuevos para importar.")
                else:
                    ok_inv = True if df_import_inv.empty else agregar_filas("inventario", df_import_inv, COLUMNAS_INV)
                    ok_cli = True if df_import_cli.empty else agregar_filas("clientes", df_import_cli, COLUMNAS_CLI)
                    if ok_inv and ok_cli:
                        st.success(f"Importación terminada. Se agregaron {len(df_import_inv)} registros de inventario y {len(df_import_cli)} clientes. No se eliminaron datos existentes.")
                        st.cache_data.clear()
                    else:
                        st.error("La importación no terminó completamente. Revisa los errores mostrados y verifica en Supabase qué tabla recibió los datos antes de volver a intentar.")
        except Exception as e:
            st.error(f"No se pudo leer el Excel: {e}")
            st.caption("Comprueba que sea un archivo .xlsx válido y que sus hojas sigan el formato del libro original.")

# ================================================================================
# MÓDULO 3: BASE DE DATOS
# ================================================================================
elif menu == "🗃️ Base de Datos":
    st.header("🗃️ Gestor de Bases de Datos")
    if "aviso_bd" in st.session_state:
        st.success(st.session_state.pop("aviso_bd"))
    
    opcion_bd = st.radio("Selecciona la Base de Datos a visualizar:", ["👥 Base de Clientes Activos", "📦 Inventario Completo de Cuentas"], horizontal=True, label_visibility="collapsed", key="bd_radio")
    st.markdown("---")
    
    if opcion_bd == "👥 Base de Clientes Activos":
        st.subheader("Clientes y Fechas")
        df_c = leer_tabla("clientes", COLUMNAS_CLI)
        
        if not df_c.empty:
            busq_cli = st.text_input("🔍 Buscar (nombre, teléfono, correo, plataforma, perfil...)", key="busq_cli", placeholder="Escribe y la lista se filtra")
            if busq_cli.strip():
                _t = busq_cli.strip().lower()
                df_vista_c = df_c[df_c.apply(lambda r: _t in " ".join(r.astype(str)).lower(), axis=1)]
            else:
                df_vista_c = df_c
            st.caption(f"Mostrando {len(df_vista_c)} de {len(df_c)} servicios")
            st.dataframe(df_vista_c, hide_index=True)
            
            st.markdown("---")
            st.subheader("✏️ Editar o Eliminar Cliente")
            
            clientes_vista = sorted(df_vista_c["Cliente"].unique().tolist())
            cli_a_editar = st.selectbox("1. Selecciona el cliente:", ["---"] + clientes_vista, index=1 if len(clientes_vista) == 1 else 0, key="edit_cli_sel")
            
            if cli_a_editar != "---":
                filas_cli = df_c[df_c["Cliente"] == cli_a_editar]
                opciones_pantalla = filas_cli.apply(lambda r: f"{r['Plataforma']} - {r['Correo']} ({r['Perfil_Pantalla']})", axis=1).tolist()
                
                pantalla_a_editar = st.selectbox("2. Selecciona el servicio a editar:", opciones_pantalla, key="edit_cli_pant")
                
                if pantalla_a_editar:
                    filtro_busqueda = filas_cli.apply(lambda r: f"{r['Plataforma']} - {r['Correo']} ({r['Perfil_Pantalla']})", axis=1) == pantalla_a_editar
                    idx_real = filas_cli.index[filtro_busqueda].tolist()[0]
                    datos_fila = df_c.loc[idx_real]
                    
                    df_inv_ed = leer_tabla("inventario", COLUMNAS_INV)
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
                        
                        st.markdown("**🔑 Datos de acceso y pantalla**")
                        spot_cli_e = es_spotify_con_correo_cliente(datos_fila)
                        if spot_cli_e:
                            ea1, ea2 = st.columns(2)
                            n_corr_cli = ea1.text_input("Correo del cliente (Spotify)", value=str(datos_fila["Correo"]))
                            n_clave_cli = ea2.text_input("Contraseña del cliente (Spotify)", value=str(datos_fila["Clave_Spotify"]))
                        else:
                            n_corr_cli = str(datos_fila["Correo"])
                            n_clave_cli = str(datos_fila["Clave_Spotify"])
                            st.caption(f"Está en la pantalla: **{datos_fila['Correo']}** | Perfil: **{datos_fila['Perfil_Pantalla']}**. El correo y la clave de esa cuenta se cambian en Soportes > Actualizar Credenciales. Si lo registraste en la pantalla equivocada, muévelo aquí abajo.")
                        n_monto = st.number_input("Monto del servicio ($)", min_value=0.0, step=0.5, value=float(to_float(datos_fila["Monto"])))
                        disp_e = df_inv_ed[(df_inv_ed["Plataforma"] == datos_fila["Plataforma"]) & (df_inv_ed["Estado"] == "Disponible")]
                        opc_reasig = {"(Dejarlo en su pantalla actual)": None}
                        for i_d, r_d in disp_e.iterrows():
                            opc_reasig[f"{r_d['Correo']} - {r_d['Perfil_Pantalla']}"] = i_d
                        sel_reasig = st.selectbox("Mover a otra pantalla libre (si lo registraste en la equivocada)", list(opc_reasig.keys()))
                        ant_revision = st.checkbox("Si lo muevo: la pantalla anterior queda 🔴 En Revisión (marca esto solo si el cliente sí la llegó a usar). Si no, vuelve a Disponible.", value=False)
                        
                        liberar_pant = st.checkbox("Al eliminar, liberar su pantalla (queda 🔴 En Revisión para cambiar el PIN)", value=True)
                        col_btn1, col_btn2 = st.columns(2)
                        if col_btn1.form_submit_button("💾 Guardar Cambios", type="primary"):
                            df_c.at[idx_real, "Telefono"] = str(n_tel)
                            df_c.at[idx_real, "Fecha_Corte"] = str(n_f_corte)
                            df_c.at[idx_real, "Estado_Servicio"] = str(n_est)
                            df_c.at[idx_real, "Monto"] = str(round(n_monto, 2))
                            inv_cambio = False
                            nuevo_i_sel = opc_reasig[sel_reasig]
                            if nuevo_i_sel is not None:
                                df_c, df_inv_ed = reasignar_servicio(df_c, df_inv_ed, idx_real, nuevo_i_sel, n_corr_cli if spot_cli_e else "", ant_revision)
                                inv_cambio = True
                            elif spot_cli_e:
                                df_c, df_inv_ed = cambiar_correo_spotify(df_c, df_inv_ed, idx_real, n_corr_cli)
                                inv_cambio = True
                            if spot_cli_e:
                                df_c.at[idx_real, "Clave_Spotify"] = str(n_clave_cli)
                            guardar_tabla("clientes", df_c, COLUMNAS_CLI)
                            if inv_cambio:
                                guardar_tabla("inventario", df_inv_ed, COLUMNAS_INV)
                            st.session_state.aviso_bd = "¡Cliente actualizado en la nube!" + (" Cambié también su pantalla en el inventario." if nuevo_i_sel is not None else "")
                            st.rerun()
                            
                        if col_btn2.form_submit_button("🗑️ Eliminar Registro de la Nube"): 
                            if liberar_pant:
                                df_inv_lib = leer_tabla("inventario", COLUMNAS_INV)
                                i_lib = buscar_fila_inv(df_inv_lib, datos_fila)
                                if i_lib is not None:
                                    df_inv_lib.at[i_lib, "Estado"] = "🔴 En Revisión"
                                    guardar_tabla("inventario", df_inv_lib, COLUMNAS_INV)
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
            df_c_orf = leer_tabla("clientes", COLUMNAS_CLI)
            df_orf = pantallas_huerfanas(df_i, df_c_orf)
            n_rev_i = int((df_i["Estado"] == "🔴 En Revisión").sum())
            if not df_orf.empty:
                st.warning(f"🔎 Encontré {len(df_orf)} pantalla(s) que no te salen para vender y que ningún cliente tiene:")
                st.dataframe(df_orf, hide_index=True)
                if st.button("🔓 Liberar estas pantallas (pasan a Disponible)", key="btn_liberar_orf", type="primary"):
                    df_i.loc[df_orf.index, "Estado"] = "Disponible"
                    guardar_tabla("inventario", df_i, COLUMNAS_INV)
                    st.session_state.aviso_bd = f"¡Listo! {len(df_orf)} pantalla(s) volvieron a Disponible."
                    st.rerun()
            else:
                st.success("✅ Todas las pantallas Ocupadas tienen un cliente asignado.")
            if n_rev_i:
                st.caption(f"Además hay {n_rev_i} pantalla(s) en 🔴 En Revisión: no salen para vender hasta que las reactives en el Panel Diario.")
            busq_inv = st.text_input("🔍 Buscar (plataforma, correo, perfil, región, estado...)", key="busq_inv", placeholder="Escribe y la lista se filtra")
            if busq_inv.strip():
                _ti = busq_inv.strip().lower()
                df_vista_i = df_i[df_i.apply(lambda r: _ti in " ".join(r.astype(str)).lower(), axis=1)]
            else:
                df_vista_i = df_i
            st.caption(f"Mostrando {len(df_vista_i)} de {len(df_i)} pantallas")
            st.dataframe(df_vista_i, hide_index=True)
            
            st.markdown("---")
            st.subheader("✏️ Editar o Eliminar Inventario")
            
            opciones_inv = [f"{r['Plataforma']} | {r['Correo']} - Perfil: {r['Perfil_Pantalla']}" for _, r in df_vista_i.iterrows()]
            inv_a_editar = st.selectbox("Selecciona la pantalla exacta a modificar:", ["---"] + opciones_inv, index=1 if len(opciones_inv) == 1 else 0, key="edit_inv_sel")
            
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

            st.markdown("---")
            st.subheader("🗑️ Eliminar una cuenta completa")
            st.caption("Borra la cuenta con todos sus perfiles de una sola vez. Antes de hacerlo, descarga una copia de seguridad en Configuración.")
            mats_del = df_i[~df_i["IP_Region"].str.startswith("EXTRA")].drop_duplicates(subset=["Plataforma", "Correo"])
            opc_del = mats_del.apply(lambda r: f"{r['Plataforma']} | {r['Correo']}", axis=1).tolist()
            cta_del = st.selectbox("Selecciona la cuenta matriz a eliminar:", ["--- Seleccione ---"] + opc_del, key="del_cta_sel")

            if cta_del != "--- Seleccione ---":
                plat_del, corr_del = cta_del.split(" | ", 1)
                n_perf_del = len(df_i[(df_i["Plataforma"] == plat_del) & (df_i["Correo"] == corr_del)])
                extras_del = df_i[(df_i["Plataforma"] == plat_del) & (df_i["IP_Region"] == f"EXTRA de {corr_del}")]
                df_c_del = leer_tabla("clientes", COLUMNAS_CLI)
                cli_del = df_c_del[(df_c_del["Plataforma"] == plat_del) & (df_c_del["Correo"] == corr_del)]
                st.info(f"Esta cuenta tiene **{n_perf_del} perfiles**, **{len(extras_del)} perfil(es) extra** vinculados y **{cli_del['Cliente'].nunique()} cliente(s)** ({len(cli_del)} servicios).")

                accion_cli = st.radio("¿Qué hacemos con los clientes de esta cuenta?", ["Conservar a los clientes (solo se borra la cuenta)", "Eliminar también a sus clientes"], key="del_cta_cli")
                if plat_del == "SPOTIFY":
                    st.caption("En Spotify los clientes se registran con su propio correo, así que no se eliminan automáticamente. Búscalos en la base de clientes.")

                borrar_extras = False
                if len(extras_del) > 0:
                    borrar_extras = st.checkbox(f"Eliminar también sus {len(extras_del)} perfil(es) extra (si no, quedan como cuentas independientes)", value=True, key="del_cta_ext")

                conf_del = st.checkbox("Entiendo que esto no se puede deshacer", key="del_cta_conf")
                if st.button("🗑️ Eliminar cuenta completa", type="primary", key="btn_del_cta"):
                    if not conf_del:
                        st.error("⚠️ Marca la casilla de confirmación.")
                    else:
                        mask_cta = (df_i["Plataforma"] == plat_del) & (df_i["Correo"] == corr_del)
                        mask_ext = (df_i["Plataforma"] == plat_del) & (df_i["IP_Region"] == f"EXTRA de {corr_del}")
                        a_borrar = (mask_cta | mask_ext) if borrar_extras else mask_cta
                        if not borrar_extras:
                            df_i.loc[mask_ext, "IP_Region"] = "Independiente"
                        guardar_tabla("inventario", df_i[~a_borrar], COLUMNAS_INV)

                        if "Eliminar también" in accion_cli:
                            correos_cli = [corr_del] + (extras_del["Correo"].unique().tolist() if borrar_extras else [])
                            mask_cl = (df_c_del["Plataforma"] == plat_del) & (df_c_del["Correo"].isin(correos_cli))
                            guardar_tabla("clientes", df_c_del[~mask_cl], COLUMNAS_CLI)
                        st.success("¡Cuenta eliminada!")
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

    # ---------- CUENTAS: costo, región y ganancia mensual esperada ----------
    st.markdown("### 💼 Tus cuentas: costo, región y ganancia mensual")
    st.info("💡 **Ingreso mensual** = lo que pagan hoy tus clientes activos, llevado a 1 mes (si alguien pagó 3 meses, se divide entre 3). **Costo** = lo que pagas por la cuenta más sus perfiles extra cada 31 días. Edita la **Región** o el **Costo** directamente en la tabla y pulsa Guardar.")

    inv_padre = {}
    for _, r_i in df_inv.iterrows():
        ip_i = str(r_i["IP_Region"])
        inv_padre[(r_i["Plataforma"], r_i["Correo"])] = ip_i[len("EXTRA de "):] if ip_i.startswith("EXTRA de ") else r_i["Correo"]

    ing_cuenta = {}
    ing_plat_mes = {}
    for _, r_c in df_cli[df_cli["Estado_Servicio"].isin(["Activo", "Congelado"])].iterrows():
        meses_c = max(to_float(r_c["Meses_Contratados"]), 1.0)
        mensual_c = to_float(r_c["Monto"]) / meses_c
        plat_c, corr_c = matriz_de_servicio(df_inv, r_c)
        ing_plat_mes[plat_c] = ing_plat_mes.get(plat_c, 0.0) + mensual_c
        if corr_c is not None:
            k_c = (plat_c, inv_padre.get((plat_c, corr_c), corr_c))
            ing_cuenta[k_c] = ing_cuenta.get(k_c, 0.0) + mensual_c

    filas_cta = []
    if not df_inv.empty:
        mats_f = df_inv[~df_inv["IP_Region"].str.startswith("EXTRA")].drop_duplicates(subset=["Plataforma", "Correo"])
        for _, r_m in mats_f.iterrows():
            plat_m, corr_m = r_m["Plataforma"], r_m["Correo"]
            perf_m = df_inv[(df_inv["Plataforma"] == plat_m) & (df_inv["Correo"] == corr_m)]
            c_base = to_float(r_m["Costo_Matriz"])
            c_tot, c_ext, n_ext = costo_con_extras(df_inv, plat_m, corr_m, c_base)
            ing_m = ing_cuenta.get((plat_m, corr_m), 0.0)
            _fp = pd.to_datetime(r_m["Fecha_Pago"], errors="coerce")
            if pd.isna(_fp):
                f_pago_m, txt_vence = pd.NaT, "Sin fecha"
            else:
                f_pago_m = _fp.normalize()
                d_pago = (f_pago_m.date() - date.today()).days
                txt_vence = f"Vencida hace {abs(d_pago)} d" if d_pago < 0 else ("Hoy" if d_pago == 0 else f"En {d_pago} d")
            filas_cta.append({
                "Plataforma": plat_m, "Correo": corr_m, "Región": r_m["IP_Region"], "Fecha de pago": f_pago_m, "Vence": txt_vence,
                "Costo cuenta ($)": float(c_base), "Extras": int(n_ext), "Costo extras ($)": float(c_ext),
                "Costo total ($)": round(c_tot, 2), "Vendidos": f"{int((perf_m['Estado'] == 'Ocupado').sum())}/{len(perf_m)}",
                "Ingreso mensual ($)": round(ing_m, 2), "Ganancia mensual ($)": round(ing_m - c_tot, 2)
            })

    if filas_cta:
        df_cuentas = pd.DataFrame(filas_cta)
        df_cuentas["Fecha de pago"] = pd.to_datetime(df_cuentas["Fecha de pago"], errors="coerce")
        ediciones = []
        for plat_x in df_cuentas["Plataforma"].unique().tolist():
            sub_o = df_cuentas[df_cuentas["Plataforma"] == plat_x].reset_index(drop=True)
            ing_x = float(sub_o["Ingreso mensual ($)"].sum())
            cos_x = float(sub_o["Costo total ($)"].sum())
            titulo_x = f"📺 {plat_x}  ·  {len(sub_o)} cuenta(s)  ·  Ingreso ${ing_x:,.2f}  ·  Costo ${cos_x:,.2f}  ·  Ganancia ${ing_x - cos_x:,.2f}"
            with st.expander(titulo_x, expanded=False):
                sub_n = st.data_editor(
                    sub_o, key=f"ed_cuentas_{plat_x}", hide_index=True,
                    disabled=[c for c in sub_o.columns if c not in ("Región", "Fecha de pago", "Costo cuenta ($)")],
                    column_config={
                        "Plataforma": None,
                        "Región": st.column_config.TextColumn("Región (editable)"),
                        "Fecha de pago": st.column_config.DateColumn("Fecha de pago (editable)", format="DD/MM/YYYY"),
                        "Costo cuenta ($)": st.column_config.NumberColumn("Costo cuenta ($) (editable)", min_value=0.0, step=0.5, format="%.2f"),
                    }
                )
            ediciones.append((sub_o, sub_n))

        if st.button("💾 Guardar cambios de cuentas", type="primary", key="btn_guardar_cuentas"):
            df_inv_g = df_inv.copy()
            hubo = False
            region_mala = False
            for sub_o, sub_n in ediciones:
                for pos in range(len(sub_o)):
                    orig = sub_o.iloc[pos]
                    nuevo = sub_n.iloc[pos]
                    n_costo = to_float(nuevo["Costo cuenta ($)"])
                    n_reg = "" if pd.isna(nuevo["Región"]) else str(nuevo["Región"]).strip()
                    if n_reg.upper().startswith("EXTRA"):
                        region_mala = True
                        continue
                    m_g = (df_inv_g["Plataforma"] == orig["Plataforma"]) & (df_inv_g["Correo"] == orig["Correo"])
                    m_ext_g = (df_inv_g["Plataforma"] == orig["Plataforma"]) & (df_inv_g["IP_Region"] == f"EXTRA de {orig['Correo']}")
                    if abs(n_costo - float(orig["Costo cuenta ($)"])) > 1e-9 or n_reg != str(orig["Región"]):
                        df_inv_g.loc[m_g, "Costo_Matriz"] = str(n_costo)
                        df_inv_g.loc[m_g, "IP_Region"] = n_reg
                        hubo = True
                    n_fecha = pd.to_datetime(nuevo["Fecha de pago"], errors="coerce")
                    o_fecha = pd.to_datetime(orig["Fecha de pago"], errors="coerce")
                    if (not pd.isna(n_fecha)) and (pd.isna(o_fecha) or n_fecha.date() != o_fecha.date()):
                        df_inv_g.loc[m_g | m_ext_g, "Fecha_Pago"] = str(n_fecha.date())
                        hubo = True
            if region_mala:
                st.error("⚠️ La región no puede empezar con la palabra EXTRA (esa palabra se usa para los perfiles extra).")
            elif hubo:
                guardar_tabla("inventario", df_inv_g, COLUMNAS_INV)
                st.success("¡Cuentas actualizadas!")
                st.rerun()
            else:
                st.info("No hiciste ningún cambio.")
    else:
        st.info("Todavía no hay cuentas registradas.")

    if not df_inv.empty:
        extras_f = df_inv[df_inv["IP_Region"].str.startswith("EXTRA de ")].drop_duplicates(subset=["Plataforma", "Correo"])
        if not extras_f.empty:
            with st.expander(f"➕ Perfiles extra ({len(extras_f)}): editar su costo"):
                df_extras = pd.DataFrame([{
                    "Plataforma": r_x["Plataforma"], "Correo": r_x["Correo"],
                    "Lo paga la matriz": str(r_x["IP_Region"])[len("EXTRA de "):], "Costo extra ($)": float(to_float(r_x["Costo_Matriz"]))
                } for _, r_x in extras_f.iterrows()])
                df_ex_ed = st.data_editor(
                    df_extras, key="ed_extras", hide_index=True,
                    disabled=["Plataforma", "Correo", "Lo paga la matriz"],
                    column_config={"Costo extra ($)": st.column_config.NumberColumn("Costo extra ($) (editable)", min_value=0.0, step=0.5, format="%.2f")}
                )
                if st.button("💾 Guardar costos de extras", key="btn_guardar_extras"):
                    df_inv_x = df_inv.copy()
                    hubo_x = False
                    for pos in range(len(df_extras)):
                        orig_x = df_extras.iloc[pos]
                        n_c = to_float(df_ex_ed.iloc[pos]["Costo extra ($)"])
                        if abs(n_c - float(orig_x["Costo extra ($)"])) > 1e-9:
                            m_x = (df_inv_x["Plataforma"] == orig_x["Plataforma"]) & (df_inv_x["Correo"] == orig_x["Correo"])
                            df_inv_x.loc[m_x, "Costo_Matriz"] = str(n_c)
                            hubo_x = True
                    if hubo_x:
                        guardar_tabla("inventario", df_inv_x, COLUMNAS_INV)
                        st.success("¡Costos de extras actualizados!")
                        st.rerun()
                    else:
                        st.info("No hiciste ningún cambio.")

    # Resumen mensual esperado (por plataforma y global)
    ingreso_rec = float(sum(ing_plat_mes.values()))
    costo_rec = float(sum([to_float(x) for x in df_inv.drop_duplicates(subset=["Plataforma", "Correo"])["Costo_Matriz"]])) if not df_inv.empty else 0.0
    ganancia_rec = ingreso_rec - costo_rec
    ts_rec = st.session_state.tasa_cambio

    st.markdown("### 📈 Ganancia mensual esperada (con tus clientes activos de hoy)")
    q1, q2, q3 = st.columns(3)
    q1.metric("💵 Ingreso mensual", f"${ingreso_rec:,.2f}")
    q2.metric("💵 Costo mensual", f"${costo_rec:,.2f}")
    q3.metric("💵 Ganancia mensual", f"${ganancia_rec:,.2f}")
    qb1, qb2, qb3 = st.columns(3)
    qb1.metric("🇻🇪 Ingreso Bs", f"{ingreso_rec * ts_rec:,.2f} Bs")
    qb2.metric("🇻🇪 Costo Bs", f"{costo_rec * ts_rec:,.2f} Bs")
    qb3.metric("🇻🇪 Ganancia Bs", f"{ganancia_rec * ts_rec:,.2f} Bs")

    filas_plat = []
    plats_todas = sorted(set(list(ing_plat_mes.keys()) + (df_inv["Plataforma"].unique().tolist() if not df_inv.empty else [])))
    for plat_r in plats_todas:
        costo_p = float(sum([to_float(x) for x in df_inv[df_inv["Plataforma"] == plat_r].drop_duplicates(subset=["Correo"])["Costo_Matriz"]])) if not df_inv.empty else 0.0
        ing_p = ing_plat_mes.get(plat_r, 0.0)
        if costo_p > 0 or ing_p > 0:
            filas_plat.append({"Plataforma": plat_r, "Ingreso mensual": f"${ing_p:.2f}", "Costo mensual": f"${costo_p:.2f}", "Ganancia mensual": f"${ing_p - costo_p:.2f}"})
    if filas_plat:
        st.table(pd.DataFrame(filas_plat))

    st.markdown("---")
    st.markdown("## 🧾 Lo cobrado realmente (historial de pagos)")
    st.caption("Esto suma los pagos anotados en cada mes. Los clientes que registraste con fecha antigua cuentan en su mes original, por eso este número puede verse bajo aunque tu ganancia mensual esperada (arriba) sea positiva.")

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

    st.markdown("### 📊 Cobrado por plataforma en el mes elegido")
    st.caption("Ingresos: pagos recibidos en el mes elegido. Costos: lo que cuestan hoy tus cuentas por mes (31 días).")
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
    
    st.markdown(f"### 💰 Flujo de caja del mes ({mes_sel}): cobrado vs. costos")
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
                    tipos_rep = ["--- Seleccione ---", "🔢 El PIN no coincide", "🔑 El correo o la clave no funcionan", "💳 La cuenta sale sin pago / suspendida", "📺 La pantalla falla o no abre", "⏳ Caída / tardé en responder (agregar días)"]
                    tipo_rep = st.selectbox("3. ❓ ¿Qué problema tiene?", tipos_rep, key="rep_tipo")

                    m_inv_rep = df_inv_rep[(df_inv_rep["Plataforma"] == d_rep["Plataforma"]) & (df_inv_rep["Correo"] == d_rep["Correo"]) & (df_inv_rep["Perfil_Pantalla"] == d_rep["Perfil_Pantalla"])]
                    st.markdown("---")

                    if tipo_rep == "⏳ Caída / tardé en responder (agregar días)":
                        try:
                            fc_rep = pd.to_datetime(d_rep["Fecha_Corte"]).date()
                        except:
                            fc_rep = None
                        if fc_rep is None:
                            st.error("Este servicio no tiene una fecha de corte válida. Corrígela en Base de Datos.")
                        else:
                            st.markdown(f"**Fecha de corte actual:** {fc_rep.strftime('%d/%m/%Y')}")
                            dias_perd = st.number_input("📅 Días perdidos a agregar (1 a 31)", min_value=1, max_value=31, value=1, step=1, key=f"rep_dias_{idx_rep}")
                            todos_serv = st.checkbox("Aplicar a todos los servicios de este cliente", value=False, key=f"rep_todos_{idx_rep}")
                            st.markdown(f"**Nueva fecha de corte:** {(fc_rep + timedelta(days=int(dias_perd))).strftime('%d/%m/%Y')}")
                            if st.button("➕ Agregar días y generar mensaje", type="primary", key=f"btn_rep_dias_{idx_rep}"):
                                filas_dias = df_f_rep.index.tolist() if todos_serv else [idx_rep]
                                for i_d in filas_dias:
                                    try:
                                        f_v = pd.to_datetime(df_cli_rep.at[i_d, "Fecha_Corte"]).date()
                                    except:
                                        continue
                                    df_cli_rep.at[i_d, "Fecha_Corte"] = str(f_v + timedelta(days=int(dias_perd)))
                                guardar_tabla("clientes", df_cli_rep, COLUMNAS_CLI)
                                nueva_fc = (fc_rep + timedelta(days=int(dias_perd))).strftime('%d/%m/%Y')
                                cuenta_serv = "tus servicios" if todos_serv else f"tu servicio de {d_rep['Plataforma']}"
                                st.session_state.m_reporte = f"¡Hola! Disculpa la demora y el inconveniente 🙏 Te agregué {int(dias_perd)} día(s) a {cuenta_serv} por el tiempo perdido. Tu nueva fecha de corte es el {nueva_fc}."
                                st.session_state.m_reporte_titulo = f"¡Listo! Se agregaron {int(dias_perd)} día(s). Mensaje para el cliente:"
                                st.rerun()

                    elif tipo_rep == "📺 La pantalla falla o no abre":
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
