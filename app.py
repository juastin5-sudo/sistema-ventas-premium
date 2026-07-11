import streamlit as st
import pandas as pd
import os
import random
import calendar
import json
import zipfile
import io
import requests # Solo para Binance ahora
from datetime import date, datetime, timedelta
from supabase import create_client, Client

# ==============================================================================
# 1. CONFIGURACIÓN Y DISEÑO UI/UX
# ==============================================================================
st.set_page_config(page_title="Gestión Streaming Premium", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
        
        html, body, p, span, div, label, input, textarea, select, button { font-family: 'Inter', sans-serif; }
        h1, h2, h3, [data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif !important; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
        .stApp { background: radial-gradient(circle at 50% 0%, #1a1b26 0%, #0a0b10 80%) !important; color: #f1f1f4 !important; }
        [data-testid="stSidebar"] { background-color: #0e0f16 !important; border-right: 1px solid rgba(255, 255, 255, 0.04) !important; }
        h1 { background: linear-gradient(135deg, #00FF7F 0%, #00BFFF 100%); -webkit-background-clip: text; -webkit-background-color: transparent; -webkit-text-fill-color: transparent; font-weight: 800 !important; margin-bottom: 1.5rem !important; }
        div[data-testid="stForm"] { background-color: #141522 !important; border: 1px solid rgba(255, 255, 255, 0.05) !important; border-radius: 16px !important; padding: 2rem !important; }
        .stButton > button[kind="primary"] { background: linear-gradient(135deg, #00FF7F 0%, #00BFFF 100%) !important; color: #0a0b10 !important; border: none !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. SISTEMA DE BASE DE DATOS (CONEXIÓN OFICIAL SUPABASE)
# ==============================================================================
COLUMNAS_INV = ["Plataforma", "Correo", "Clave", "Perfil_Pantalla", "PIN", "Estado", "Fecha_Pago", "IP_Region", "Costo_Matriz"]
COLUMNAS_CLI = ["Cliente", "Telefono", "Plataforma", "Correo", "Perfil_Pantalla", "Fecha_Inicio", "Fecha_Corte", "Metodo_Pago", "Monto", "Clave_Spotify", "Estado_Servicio", "Fecha_Congelamiento", "Meses_Contratados"]
COLUMNAS_PRE = ["Plataforma", "Costo_Matriz", "Precio_Venta_Perfil"]
ARCHIVO_PLANTILLAS = "plantillas.json"

# Inicializar cliente oficial de Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase_client = init_connection()

def to_float(val):
    try:
        if pd.isna(val) or val == "" or val is None: return 0.0
        return float(str(val).replace(',', '.').replace('$', '').strip())
    except: return 0.0

@st.cache_data(ttl=300, show_spinner=False)
def leer_tabla(tabla, columnas):
    try:
        response = supabase_client.table(tabla).select("*").execute()
        df = pd.DataFrame(response.data)
        if df.empty: return pd.DataFrame(columns=columnas).astype(str)
        for col in columnas:
            if col not in df.columns: df[col] = ""
        return df[columnas].astype(str).fillna("")
    except Exception as e:
        return pd.DataFrame(columns=columnas).astype(str)

def guardar_tabla(tabla, df, columnas):
    try:
        # Borra todo lo que no sea igual a algo imposible (es decir, borra toda la tabla)
        supabase_client.table(tabla).delete().neq(columnas[0], "VALOR_INEXISTENTE").execute()
        if not df.empty:
            df_clean = df[columnas].fillna("").astype(str)
            records = df_clean.to_dict(orient="records")
            supabase_client.table(tabla).insert(records).execute()
        st.cache_data.clear()
    except Exception as e: st.error(f"Error guardando {tabla}: {e}")

def agregar_filas(tabla, df, columnas):
    try:
        if not df.empty:
            df_clean = df[columnas].fillna("").astype(str)
            records = df_clean.to_dict(orient="records")
            supabase_client.table(tabla).insert(records).execute()
        st.cache_data.clear()
    except Exception as e: st.error(f"Error agregando a {tabla}: {e}")

@st.cache_data(ttl=1800, show_spinner=False)
def obtener_tasa_binance():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    data = {"asset": "USDT", "fiat": "VES", "merchantCheck": False, "page": 1, "rows": 5, "tradeType": "BUY"}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=5)
        if resp.status_code == 200:
            anuncios = resp.json().get("data", [])
            if len(anuncios) >= 4: return round(float(anuncios[3]["adv"]["price"]) * 1.01, 2)
    except: pass
    return None

def sumar_meses(fecha_obj, meses):
    mes = fecha_obj.month - 1 + int(meses)
    anio = fecha_obj.year + mes // 12
    mes = mes % 12 + 1
    return date(anio, mes, min(fecha_obj.day, calendar.monthrange(anio, mes)[1]))

if 'pines_azar' not in st.session_state: st.session_state.pines_azar = [str(random.randint(1000, 9999)) for _ in range(50)]
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'tasa_cambio' not in st.session_state: 
    tasa_api = obtener_tasa_binance()
    st.session_state.tasa_cambio = tasa_api if tasa_api else 40.00

def inicializar_archivos():
    if not os.path.exists(ARCHIVO_PLANTILLAS):
        with open(ARCHIVO_PLANTILLAS, 'w', encoding='utf-8') as f:
            json.dump({
                "cobro": "¡Hola [cliente]! 👋 Paso por acá para recordarte que tus servicios están próximos a vencer:\n\n[servicios]\n*Total a transferir:* $[monto_usd] USD o su equivalente **[monto_bs] Bs**.\n\nMe avisas al realizar el pago para mantener tus pantallas activas sin interrupciones. ¡Muchas gracias! ✨",
                "cotizacion": "¡Hola! Aquí tienes el desglose y la cuenta de tus servicios:\n\n[servicios]\n💰 *Total:* $[monto_usd] USD / *[monto_bs] Bs*\n\n👇 *Puedes realizar tu pago móvil a cualquiera de estas cuentas:* \n\n*Monto a transferir = [monto_bs] bs*",
                "venta": "Plataforma: [plataforma]\n*Correo*: [correo]\n*Clave*: [clave]\n*Perfil*: [perfil] PIN: [pin]\n\n*Vence el*: [fecha_corte]",
                "soporte": "¡Hola! Para solucionar tu inconveniente rápidamente y que sigas disfrutando sin pausas, te he migrado a una pantalla nueva limpia. Aquí tienes los datos actualizados:\n\nPlataforma: [plataforma]\n*Correo*: [correo]\n*Clave*: [clave]\n*Perfil*: [perfil] PIN: [pin]\n\n*Nota: Tu fecha de corte mensual se mantiene igual ([fecha_corte]).*"
            }, f, ensure_ascii=False, indent=4)
            
    df_pre = leer_tabla("precios", COLUMNAS_PRE)
    if df_pre.empty:
        df_default = pd.DataFrame([
            {"Plataforma": "NETFLIX", "Costo_Matriz": "9.00", "Precio_Venta_Perfil": "3.00"},
            {"Plataforma": "SPOTIFY", "Costo_Matriz": "5.00", "Precio_Venta_Perfil": "1.50"}
        ]).astype(str)
        agregar_filas("precios", df_default, COLUMNAS_PRE)

def cargar_plantilla(tipo):
    try:
        with open(ARCHIVO_PLANTILLAS, 'r', encoding='utf-8') as f: return json.load(f).get(tipo, "")
    except: return ""

inicializar_archivos()

# ==============================================================================
# 3. NAVEGACIÓN LATERAL
# ==============================================================================
st.sidebar.title("Navegación 🧭")
menu = st.sidebar.radio("Menú", ["📌 Panel Diario", "📦 1. Registrar Cuentas", "🛒 2. Vender Perfiles", "🗃️ 3. Base de Datos", "💰 4. Finanzas", "🛠️ 5. Soportes", "⚙️ 6. Configuración"], label_visibility="collapsed")
st.title("Panel Central de Cuentas")

# ==============================================================================
# MÓDULO 0: PANEL DIARIO 
# ==============================================================================
if menu == "📌 Panel Diario":
    st.header("Lo que tienes que hacer hoy 📝")
    hoy_pd = pd.to_datetime("today").normalize()
    df_clientes_raw = leer_tabla("clientes", COLUMNAS_CLI)
    
    pendientes_activacion = df_clientes_raw[df_clientes_raw["Estado_Servicio"] == "Pendiente"]
    if not pendientes_activacion.empty:
        st.subheader("⏳ Pendientes por Activar")
        for idx, row in pendientes_activacion.iterrows():
            st.warning(f"🟡 **{row['Cliente']}** | {row['Plataforma']}")
            c1, c2 = st.columns(2)
            c1.code(row['Correo'])
            if c2.button("✅ Activar", key=f"act_{idx}", type="primary"):
                m = int(to_float(row.get('Meses_Contratados', 1)))
                df_clientes_raw.at[idx, "Fecha_Inicio"] = str(date.today())
                df_clientes_raw.at[idx, "Fecha_Corte"] = str(sumar_meses(date.today(), m if m > 0 else 1))
                df_clientes_raw.at[idx, "Estado_Servicio"] = "Activo"
                guardar_tabla("clientes", df_clientes_raw, COLUMNAS_CLI)
                st.rerun()
        st.markdown("---")
    
    col_cobros, col_pagos = st.columns(2)
    with col_cobros:
        st.subheader("🟢 Cobros a Clientes")
        activos = df_clientes_raw[df_clientes_raw["Estado_Servicio"] == "Activo"].copy()
        if not activos.empty:
            activos["Fecha_Real"] = pd.to_datetime(activos["Fecha_Corte"], errors="coerce")
            df_vencidos = activos[(activos["Fecha_Real"].notna()) & ((activos["Fecha_Real"] - hoy_pd).dt.days <= 3)]
            for cli in df_vencidos["Cliente"].unique():
                d_cli = df_vencidos[df_vencidos["Cliente"] == cli]
                dias = (d_cli["Fecha_Real"] - hoy_pd).dt.days.min()
                if dias < 0: st.error(f"🔴 Vencido: {cli}")
                elif dias == 0: st.warning(f"🟡 Cobra Hoy: {cli}")
                else: st.info(f"🔵 Próximo: {cli}")
                
                with st.form(key=f"fc_{cli}"):
                    tot_u, t_serv, chks = 0.0, "", []
                    for i, r in d_cli.iterrows():
                        if st.checkbox(f"• {r['Plataforma']} ({r['Perfil_Pantalla']}) | ${to_float(r.get('Monto',0)):.2f}", value=True, key=f"c_{i}"):
                            chks.append(i)
                            tot_u += to_float(r.get('Monto',0))
                            t_serv += f"- {r['Plataforma']} ({r['Perfil_Pantalla']})\n"
                    st.markdown(f"**Total: ${tot_u:.2f} | {tot_u * st.session_state.tasa_cambio:,.2f} Bs**")
                    with st.expander("📋 Ver Mensaje"):
                        st.code(cargar_plantilla("cobro").replace("[cliente]", cli).replace("[servicios]", t_serv.strip()).replace("[monto_usd]", f"{tot_u:.2f}").replace("[monto_bs]", f"{tot_u * st.session_state.tasa_cambio:,.2f}"))
                    c1, c2 = st.columns([1,2])
                    m_r = c1.number_input("Meses", 1, 12, 1, key=f"m_{cli}")
                    opc = c2.selectbox("Acción:", ["---", "✅ Sí Renovó", "❌ No Renovó"], key=f"o_{cli}")
                    if st.form_submit_button("Procesar", type="primary") and opc != "---" and chks:
                        df_inv = leer_tabla("inventario", COLUMNAS_INV)
                        if "Sí" in opc:
                            for i in chks: df_clientes_raw.at[i, "Fecha_Corte"] = str(sumar_meses(datetime.strptime(df_clientes_raw.loc[i, "Fecha_Corte"], "%Y-%m-%d").date(), m_r))
                        else:
                            for i in chks:
                                r = df_clientes_raw.loc[i]
                                m_i = df_inv[(df_inv["Correo"] == r["Correo"]) & (df_inv["Perfil_Pantalla"] == r["Perfil_Pantalla"])]
                                if not m_i.empty: df_inv.at[m_i.index[0], "Estado"] = "🔴 En Revisión"
                            df_clientes_raw = df_clientes_raw.drop(chks)
                            guardar_tabla("inventario", df_inv, COLUMNAS_INV)
                        guardar_tabla("clientes", df_clientes_raw, COLUMNAS_CLI)
                        st.rerun()
        else: st.success("Sin cobros.")

    with col_pagos:
        st.subheader("🔴 Pagos Matrices")
        df_inv = leer_tabla("inventario", COLUMNAS_INV)
        if not df_inv.empty:
            c_uni = df_inv.drop_duplicates(subset=["Correo", "Plataforma"]).copy()
            c_uni["Fecha_Real"] = pd.to_datetime(c_uni["Fecha_Pago"], errors="coerce")
            p_pend = c_uni[(c_uni["Fecha_Real"].notna()) & ((c_uni["Fecha_Real"] - hoy_pd).dt.days <= 5)]
            for idx, row in p_pend.sort_values(by="Fecha_Real").iterrows():
                dias = (row["Fecha_Real"] - hoy_pd).days
                c_mat = to_float(row.get("Costo_Matriz", 0.0))
                st.warning(f"**{row['Plataforma']}** | {'🚨 VENCIDA' if dias < 0 else '🔥 HOY' if dias == 0 else f'⏳ En {dias}d'}\n\nCosto: ${c_mat:.2f}")
                with st.expander("Ver Datos"):
                    st.code(row["Correo"] + "\n" + row["Clave"])
                    nf = st.date_input("Próximo pago:", value=row["Fecha_Real"].date(), key=f"f_{idx}")
                    if st.button("Guardar", key=f"b_{idx}"):
                        df_i = leer_tabla("inventario", COLUMNAS_INV)
                        df_i.loc[(df_i["Correo"] == row["Correo"]) & (df_i["Plataforma"] == row["Plataforma"]), "Fecha_Pago"] = str(nf)
                        guardar_tabla("inventario", df_i, COLUMNAS_INV)
                        st.rerun()
        
        en_rev = df_inv[df_inv["Estado"] == "🔴 En Revisión"]
        if not en_rev.empty:
            st.subheader("🛠️ Cuentas en Revisión")
            for idx, row in en_rev.iterrows():
                st.error(f"{row['Plataforma']} | Perfil: {row['Perfil_Pantalla']}")
                np = st.text_input("NUEVO PIN:", value=str(row["PIN"]), key=f"rp_{idx}")
                if st.button("✅ Reactivar", key=f"rb_{idx}"):
                    df_inv.at[idx, "Estado"] = "Disponible"
                    df_inv.at[idx, "PIN"] = str(np)
                    guardar_tabla("inventario", df_inv, COLUMNAS_INV)
                    st.rerun()

# ==============================================================================
# MÓDULO 1: REGISTRAR CUENTAS 
# ==============================================================================
elif menu == "📦 1. Registrar Cuentas":
    st.subheader("Ingresar nueva matriz")
    df_pre = leer_tabla("precios", COLUMNAS_PRE)
    l_plat = df_pre["Plataforma"].unique().tolist() or ["NETFLIX"]
    
    c1, c2 = st.columns(2)
    plat = c1.selectbox("Plataforma", l_plat)
    corr = c1.text_input("Correo")
    clav = c1.text_input("Clave")
    cost = c1.number_input("Costo de matriz ($)", 0.0, step=0.5)
    
    cant = 6 if plat == "SPOTIFY" else c2.number_input("Perfiles", 1, 15, 5)
    f_pago = c2.date_input("Día de pago")
    ip = c2.text_input("IP/Región")
    
    st.markdown("**Perfiles:**")
    perf = []
    for i in range(1, int(cant) + 1):
        ca, cb = st.columns(2)
        n = ca.text_input(f"Nombre {i}", "Principal" if plat=="SPOTIFY" and i==1 else f"Perfil {i}", disabled=plat=="SPOTIFY" and i==1, key=f"n_{i}")
        p = "N/A" if plat == "SPOTIFY" else cb.text_input(f"PIN {i}", st.session_state.pines_azar[i], key=f"p_{i}")
        perf.append({"n": n, "p": p})
        
    if st.button("💾 Guardar Matriz", type="primary") and corr and clav:
        n_p = [{"Plataforma": plat, "Correo": corr, "Clave": clav, "Perfil_Pantalla": i["n"], "PIN": str(i["p"]), "Estado": "Disponible", "Fecha_Pago": str(f_pago), "IP_Region": ip, "Costo_Matriz": str(cost)} for i in perf]
        agregar_filas("inventario", pd.DataFrame(n_p), COLUMNAS_INV)
        st.success("¡Guardado!")
        st.session_state.pines_azar = [str(random.randint(1000, 9999)) for _ in range(50)]
        st.rerun()

# ==============================================================================
# MÓDULO 2: VENTAS 
# ==============================================================================
elif menu == "🛒 2. Vender Perfiles":
    st.subheader("Armar Combo de Ventas")
    df_inv = leer_tabla("inventario", COLUMNAS_INV)
    df_pre = leer_tabla("precios", COLUMNAS_PRE)
    disp_tot = df_inv[df_inv["Estado"] == "Disponible"]
    
    c1, c2 = st.columns(2)
    with c1:
        plat_v = st.selectbox("1. Plataforma", disp_tot["Plataforma"].unique().tolist() if not disp_tot.empty else ["Agotado"])
        o_disp = disp_tot[disp_tot["Plataforma"] == plat_v] if plat_v != "Agotado" else pd.DataFrame()
        l_perf = o_disp.apply(lambda r: f"{r['Correo']} - {r['Perfil_Pantalla']}", axis=1).tolist() if not o_disp.empty else ["Agotado"]
        p_sel = st.selectbox("2. Perfil", l_perf)
        
    if p_sel != "Agotado":
        i_sel = o_disp.index[l_perf.index(p_sel)]
        dp = df_inv.loc[i_sel]
        with c2:
            cc = st.text_input("Correo Cliente") if plat_v == "SPOTIFY" else ""
            clc = st.text_input("Clave Cliente") if plat_v == "SPOTIFY" else ""
            nf = cc if cc else (st.text_input("Nombre", dp["Perfil_Pantalla"]) if plat_v != "SPOTIFY" else dp["Perfil_Pantalla"])
            pin = "N/A" if plat_v == "SPOTIFY" else st.text_input("PIN", dp["PIN"])
            meses = st.number_input("Meses", 1, 12, 1)
            mt = to_float(df_pre[df_pre["Plataforma"] == plat_v]["Precio_Venta_Perfil"].iloc[0]) if not df_pre[df_pre["Plataforma"] == plat_v].empty else 0.0
            ptot = st.number_input("Total ($)", value=float(mt * meses), step=0.5)
            
        if st.button("➕ Añadir"):
            st.session_state.carrito.append({"idx": i_sel, "Plat": plat_v, "C_Mat": dp["Correo"], "Cl_Mat": dp["Clave"], "Perf": nf, "PIN": pin, "Meses": meses, "Tot": ptot, "C_Cli": cc, "Cl_Cli": clc})
            st.rerun()

    if st.session_state.carrito:
        st.table(pd.DataFrame(st.session_state.carrito)[["Plat", "Perf", "Meses", "Tot"]])
        if st.button("❌ Vaciar"): st.session_state.carrito = []; st.rerun()
        
        with st.form("f_vta"):
            c1, c2, c3, c4 = st.columns(4)
            cli = c1.text_input("Cliente")
            tel = c2.text_input("WhatsApp", "+58")
            met = c3.selectbox("Pago", ["Binance", "Pago Móvil", "Zelle", "Efectivo"])
            mtot = c4.number_input("Total Combo ($)", value=sum([i["Tot"] for i in st.session_state.carrito]))
            act = st.checkbox("Entregado ya", True)
            
            if st.form_submit_button("🚀 Confirmar Venta") and cli:
                mdiv, uni = mtot / len(st.session_state.carrito), ""
                fn = []
                for i in st.session_state.carrito:
                    fc = sumar_meses(date.today(), i["Meses"])
                    fn.append({"Cliente": cli, "Telefono": tel, "Plataforma": i["Plat"], "Correo": i["C_Cli"] or i["C_Mat"], "Perfil_Pantalla": i["Perf"], "Fecha_Inicio": str(date.today()), "Fecha_Corte": str(fc), "Metodo_Pago": met, "Monto": str(mdiv), "Clave_Spotify": i["Cl_Cli"], "Estado_Servicio": "Activo" if act else "Pendiente", "Fecha_Congelamiento": "", "Meses_Contratados": str(i["Meses"])})
                    df_inv.at[i["idx"], "Estado"] = "Ocupado"
                    df_inv.at[i["idx"], "PIN"] = i["PIN"]
                    df_inv.at[i["idx"], "Perfil_Pantalla"] = i["Perf"]
                    uni += cargar_plantilla("venta").replace("[plataforma]", i["Plat"]).replace("[correo]", i["C_Cli"] or i["C_Mat"]).replace("[clave]", i["Cl_Mat"]).replace("[perfil]", i["Perf"]).replace("[pin]", i["PIN"]).replace("[fecha_corte]", str(fc)) + "\n\n"
                agregar_filas("clientes", pd.DataFrame(fn), COLUMNAS_CLI)
                guardar_tabla("inventario", df_inv, COLUMNAS_INV)
                st.session_state.carrito = []
                st.success("¡Venta Lista!"); st.code(uni)

# ==============================================================================
# MÓDULO 3: BASE DE DATOS Y MÓDULO 4: FINANZAS
# ==============================================================================
elif menu in ["🗃️ 3. Base de Datos", "💰 4. Finanzas"]:
    if menu == "🗃️ 3. Base de Datos":
        st.header("🗃️ Base de Datos")
        df_c = leer_tabla("clientes", COLUMNAS_CLI)
        df_i = leer_tabla("inventario", COLUMNAS_INV)
        t = st.radio("Ver", ["Clientes", "Inventario"], horizontal=True)
        if t == "Clientes": st.table(df_c)
        else: st.table(df_i)
    else:
        st.header("💰 Finanzas")
        st.metric("Tasa Binance", f"{st.session_state.tasa_cambio} Bs")
        df_p = leer_tabla("precios", COLUMNAS_PRE)
        df_c = leer_tabla("clientes", COLUMNAS_CLI)
        df_i = leer_tabla("inventario", COLUMNAS_INV)
        
        st.table(df_p[["Plataforma", "Precio_Venta_Perfil"]])
        
        ing = sum([to_float(x) for x in df_c[df_c["Estado_Servicio"] != "Pendiente"]["Monto"]]) if not df_c.empty else 0.0
        cost = sum([to_float(x.get("Costo_Matriz", 0)) for _, x in df_i.drop_duplicates(subset=["Correo", "Plataforma"]).iterrows()]) if not df_i.empty else 0.0
        c1, c2, c3 = st.columns(3)
        c1.metric("Ingresos", f"${ing:.2f}")
        c2.metric("Costos", f"${cost:.2f}")
        c3.metric("Ganancia", f"${ing - cost:.2f}")

# ==============================================================================
# MÓDULO 5: SOPORTES Y 6: CONFIG
# ==============================================================================
elif menu in ["🛠️ 5. Soportes", "⚙️ 6. Configuración"]:
    if menu == "🛠️ 5. Soportes":
        st.header("🛠️ Soporte")
        df_i = leer_tabla("inventario", COLUMNAS_INV)
        df_c = leer_tabla("clientes", COLUMNAS_CLI)
        st.subheader("🔑 Actualizar Credenciales Matrices")
        if not df_i.empty:
            opc = df_i[["Plataforma", "Correo"]].drop_duplicates().apply(lambda r: f"{r['Plataforma']} | {r['Correo']}", axis=1).tolist()
            sel = st.selectbox("Matriz:", ["---"] + opc)
            if sel != "---":
                p, c = sel.split(" | ")
                d = df_i[(df_i["Plataforma"] == p) & (df_i["Correo"] == c)].iloc[0]
                nc = st.text_input("Nuevo Correo", d["Correo"])
                ncl = st.text_input("Nueva Clave", d["Clave"])
                nco = st.number_input("Costo", value=float(to_float(d.get("Costo_Matriz",0))), step=0.5)
                if st.button("Guardar"):
                    df_i.loc[(df_i["Plataforma"] == p) & (df_i["Correo"] == c), ["Correo", "Clave", "Costo_Matriz"]] = [nc, ncl, str(nco)]
                    df_c.loc[(df_c["Plataforma"] == p) & (df_c["Correo"] == c), "Correo"] = nc
                    guardar_tabla("inventario", df_i, COLUMNAS_INV)
                    guardar_tabla("clientes", df_c, COLUMNAS_CLI)
                    st.success("¡Actualizado!")
                    st.rerun()
    else:
        st.header("⚙️ Configuración")
        st.write("Variables plantillas cargadas automáticamente. Backup ZIP generado al vuelo.")
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("inventario.csv", leer_tabla("inventario", COLUMNAS_INV).to_csv(index=False))
            z.writestr("clientes.csv", leer_tabla("clientes", COLUMNAS_CLI).to_csv(index=False))
        st.download_button("📦 Descargar Backup", data=buffer.getvalue(), file_name="Backup.zip", mime="application/zip")
