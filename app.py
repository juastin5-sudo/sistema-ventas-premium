import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta

# ==============================================================================
# 1. CONFIGURACIÓN UI/UX (Mantenemos tu diseño)
# ==============================================================================
st.set_page_config(page_title="Gestión Premium (MODO PRUEBA LOCAL)", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0a0b10 !important; color: #f1f1f4 !important; }
        h1 { color: #00FF7F !important; }
        .stButton > button[kind="primary"] { background-color: #00FF7F !important; color: black !important; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. SISTEMA FALSO (SIN INTERNET NI SUPABASE)
# ==============================================================================
st.warning("⚠️ ESTÁS EN MODO PRUEBA LOCAL. NINGÚN DATO SE ESTÁ GUARDANDO EN SUPABASE NI CONSULTANDO A BINANCE.")

COLUMNAS_INV = ["Plataforma", "Correo", "Clave", "Perfil_Pantalla", "PIN", "Estado"]

# Creamos una tabla falsa en la memoria en vez de usar Supabase
if 'bd_falsa' not in st.session_state:
    st.session_state.bd_falsa = pd.DataFrame([
        {"Plataforma": "NETFLIX", "Correo": "prueba@test.com", "Clave": "123", "Perfil_Pantalla": "Perfil 1", "PIN": "1111", "Estado": "Disponible"},
        {"Plataforma": "SPOTIFY", "Correo": "musica@test.com", "Clave": "abc", "Perfil_Pantalla": "Principal", "PIN": "N/A", "Estado": "Ocupado"}
    ])

# ==============================================================================
# 3. NAVEGACIÓN
# ==============================================================================
st.sidebar.title("Navegación 🧭")
menu = st.sidebar.radio("Menú", ["📌 Panel Diario", "📦 1. Registrar Cuentas", "🛒 2. Vender Perfiles", "🗃️ 3. Base de Datos"])
st.title("Panel de Prueba")

# ==============================================================================
# MÓDULOS DE PRUEBA
# ==============================================================================
if menu == "📌 Panel Diario":
    st.header("Lo que tienes que hacer hoy 📝")
    st.success("La pestaña cargó perfectamente sin consultar internet.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cobros Simulados")
        if st.button("Probar botón de cobro", type="primary"):
            st.write("¡Clic registrado!")
            
    with col2:
        st.subheader("Pagos Simulados")
        st.info("Sin pagos por ahora.")

elif menu == "📦 1. Registrar Cuentas":
    st.subheader("Ingresar nueva cuenta")
    
    c1, c2 = st.columns(2)
    plat = c1.selectbox("Plataforma", ["NETFLIX", "SPOTIFY", "MAGIS TV"])
    corr = c1.text_input("Correo")
    clav = c1.text_input("Clave")
    
    if st.button("💾 Guardar (Simulado)", type="primary"):
        st.success(f"Si estuvieras conectado, la cuenta {corr} se habría guardado.")

elif menu == "🛒 2. Vender Perfiles":
    st.subheader("Armar Combo de Ventas")
    
    c1, c2 = st.columns(2)
    with c1:
        plat_v = st.selectbox("1. Plataforma", ["NETFLIX", "SPOTIFY"])
        p_sel = st.selectbox("2. Perfil", ["Perfil 1", "Perfil 2", "Perfil 3"])
        
    with c2:
        cli = st.text_input("Nombre Cliente")
        meses = st.number_input("Meses", 1, 12, 1)
        
    if st.button("🚀 Confirmar Venta Simulada", type="primary"):
        if cli:
            st.success("Venta procesada en la memoria local.")
        else:
            st.error("Pon un nombre.")

elif menu == "🗃️ 3. Base de Datos":
    st.header("🗃️ Base de Datos Local")
    st.write("Esta tabla viene de la memoria de tu app, no de Supabase.")
    st.table(st.session_state.bd_falsa)

st.markdown("---")
st.write("Haz clic en todas las pestañas rápido para ver si el servidor aguanta la carga visual.")
