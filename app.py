import streamlit as st

# Configuración simple
st.title("🛒 Lista de Compras Mercadito")


# Inicializar lista vacía
if 'productos' not in st.session_state:
    st.session_state.productos = []


def convertir_cantidad(texto):
    try:
        texto = str(texto).replace(',', '.')
        if '/' in texto:
            num, den = texto.split('/')
            return float(num) / float(den)
        return float(texto)
    except:
        return None

def limpiar_formulario():
    st.session_state.nombre_input = ""
    st.session_state.cantidad_input = "1"
    st.session_state.costo_input = 0.0

# --- FORMULARIO SIMPLE PARA AGREGAR ---
st.subheader("➕ Agregar Producto")

# Entradas básicas en una sola línea
col1, col2, col3 = st.columns(3)
with col1:
    nombre = st.text_input("Producto", key="nombre_input")
with col2:
    # Corregir tipo de dato en session_state si viene de ejecución anterior
    if isinstance(st.session_state.get('cantidad_input'), (int, float)):
        st.session_state.cantidad_input = str(st.session_state.cantidad_input)
        
    cantidad_txt = st.text_input("Cantidad (ej: 1, 1/4, 2.5)", value="1", key="cantidad_input")
with col3:
    costo = st.number_input("Costo unitario", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="costo_input")

col_btn1, col_btn2, _ = st.columns([2, 2, 5])
with col_btn1:
    agregar = st.button("Agregar a la lista")

with col_btn2:
    limpiar = st.button("Limpiar", on_click=limpiar_formulario)

# Botón para agregar
if agregar:
    if nombre:
        cant_val = convertir_cantidad(cantidad_txt)
        
        if cant_val is None or cant_val <= 0:
            st.warning("⚠️ Cantidad inválida (usa números o fracciones como 1/4)")
        else:
            # Calcular subtotal
            subtotal = cant_val * costo
            
            # Agregar a la lista
            st.session_state.productos.append({
                'nombre': nombre,
                'cantidad': cant_val,
                'costo': costo,
                'subtotal': subtotal
            })
            st.success(f"✅ {nombre} agregado ({cant_val:.3f})")

        # st.session_state.nombre_input = ""
        # st.session_state.cantidad_input = 1
        # st.session_state.costo_input = 0.0  
    else:
        st.warning("⚠️ Escribe el nombre del producto")



# --- MOSTRAR LISTA ACTUAL ---
st.subheader("📋 Tu Lista de Compras")

if st.session_state.productos:
    # Mostrar cada producto
    total_general = 0
    
    for i, producto in enumerate(st.session_state.productos):
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
        
        with col1:
            st.write(f"**{producto['nombre']}**")
        with col2:
            st.write(f"{producto['cantidad']:.2f}")
        with col3:
            st.write(f"${producto['costo']:.2f}")
        with col4:
            st.write(f"${producto['subtotal']:.2f}")
        with col5:
            if st.button("❌", key=f"eliminar_{i}"):
                st.session_state.productos.pop(i)
                st.rerun()
        
        total_general += producto['subtotal']
    
    # Línea separadora
    st.markdown("---")
    
    # Mostrar total
    col_total1, col_total2 = st.columns([4, 1])
    with col_total1:
        st.write("**TOTAL A PAGAR:**")
    with col_total2:
        st.write(f"**${total_general:.2f}**")
    
    # Botón para limpiar todo
    if st.button("🗑️ Limpiar toda la lista"):
        st.session_state.productos = []
        st.rerun()

else:
    st.info("📭 La lista está vacía. Agrega productos arriba.")

# --- INSTRUCCIONES SIMPLES ---
st.markdown("---")
st.caption("""
**Instrucciones:**
1. Escribe el nombre del producto
2. Pon la cantidad (puedes usar 1, 1.5 o fracciones como un 1/4)
3. Pon el costo por unidad (Kilo)
4. Haz clic en 'Agregar a la lista'
5. Usa ❌ para eliminar un producto

Creado por: Jenrry Soto Dextre\n
Correo: dextre1481@gmail.com\n
Pagina web: https://dextre.xyz\n
GitHub: https://github.com/jenrrysd\n
""")

