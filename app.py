import streamlit as st
import re
import streamlit as st
import re
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import pytz

# Configuración simple
st.title("🛒 Lista de Compras Mercadito")


# Inicializar lista vacía
if 'productos' not in st.session_state:
    st.session_state.productos = []

def convertir_cantidad(texto):
    try:
        texto = str(texto).lower().replace(',', '.')
        
        # Caso fracción (ej: 1/4, 1 / 2)
        if '/' in texto:
            match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)', texto)
            if match:
                return float(match.group(1)) / float(match.group(2))
        
        # Caso número simple (ej: 3, 2.5, 3 kilos)
        match = re.search(r'\d+(?:\.\d+)?', texto)
        if match:
            return float(match.group(0))
            
        return None
    except:
        return None

def limpiar_formulario():
    st.session_state.nombre_input = ""
    st.session_state.cantidad_input = "1"
    st.session_state.costo_input = None

def create_pdf(productos, total):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Lista de Compras Mercadito', 0, 1, 'C')
            self.set_font('Arial', '', 10)
            peru_time = datetime.now(pytz.timezone('America/Lima'))
            self.cell(0, 10, f'Fecha: {peru_time.strftime("%d/%m/%Y %H:%M:%S")}', 0, 1, 'C')
            self.ln(5)

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Encabezados de tabla
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(10, 10, "No.", 1, 0, 'C')
    pdf.cell(70, 10, "Producto", 1)
    pdf.cell(40, 10, "Cant.", 1)
    pdf.cell(30, 10, "Precio", 1)
    pdf.cell(40, 10, "SubTotal", 1)
    pdf.ln()

    # Datos
    pdf.set_font("Arial", size=12)
    for i, p in enumerate(productos, 1):
        # Asegurar caracteres latinos
        nombre = p['nombre'].encode('latin-1', 'replace').decode('latin-1')
        cant = p.get('cantidad_texto', str(p['cantidad'])).encode('latin-1', 'replace').decode('latin-1')
        
        pdf.cell(10, 10, str(i), 1, 0, 'C')
        pdf.cell(70, 10, nombre, 1)
        pdf.cell(40, 10, cant, 1)
        pdf.cell(30, 10, f"S/. {p['costo']:.2f}", 1)
        pdf.cell(40, 10, f"S/. {p['subtotal']:.2f}", 1)
        pdf.ln()

    # Total
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(150, 10, "TOTAL A PAGAR:", 0, 0, 'R')
    pdf.cell(40, 10, f"S/. {total:.2f}", 0, 1)

    # Validar si output devuelve bytes (fpdf2) o string (fpdf)
    salida = pdf.output(dest='S')
    if isinstance(salida, str):
        return salida.encode('latin-1')
    return bytes(salida)

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
    costo = st.number_input("Precio Unitario", min_value=0.0, value=None, step=0.01, format="%.2f", key="costo_input")

col_btn1, col_btn2, _ = st.columns([2, 2, 5])
with col_btn1:
    agregar = st.button("Agregar a la lista")

with col_btn2:
    limpiar = st.button("Limpiar", on_click=limpiar_formulario)

# Botón para agregar
if agregar:
    if nombre and costo is not None:
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
                'cantidad_texto': cantidad_txt,
                'costo': costo,
                'subtotal': subtotal
            })
            st.success(f"✅ {nombre} agregados")

    else:
        if not nombre:
            st.warning("⚠️ Escribe el nombre del producto")
        elif costo is None:
            st.warning("⚠️ Ingresa el precio unitario")


# --- MOSTRAR LISTA ACTUAL ---
st.subheader("📋 Tu Lista de Compras")

if st.session_state.productos:
    # --- MOSTRAR COMO TABLA (DataFrame) ---
    # Convertir a DataFrame para visualización tipo tabla
    data_display = []
    for p in st.session_state.productos:
        cant_str = p.get('cantidad_texto', str(p['cantidad']))
        # Asegurarnos de que el texto de cantidad sea lo que se muestra
        data_display.append({
            "Producto": p['nombre'],
            "Cant.": cant_str,
            "PreUni": p['costo'],
            "SubTotal": p['subtotal'],
            "Eliminar": False
        })
    
    df = pd.DataFrame(data_display)
    # Ajustar índice para comenzar en 1
    df.index = range(1, len(df) + 1)

    column_config = {
        # "Nro" se maneja automáticamente pon el índice del DataFrame
        "Producto": st.column_config.TextColumn("Producto", width="medium"),
        "Cant.": st.column_config.TextColumn("Cant.", width="small"),
        "PreUni": st.column_config.NumberColumn("PreUni", format="S/. %.2f", width="small"),
        "SubTotal": st.column_config.NumberColumn("SubT.", format="S/. %.2f", width="small"),
        "Eliminar": st.column_config.CheckboxColumn("🗑️", width="small")
    }

    # Mostrar tabla editable
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        hide_index=False,
        use_container_width=True,
        key="editor_lista"
    )

    # Calcular y mostrar total
    total_general = sum(p['subtotal'] for p in st.session_state.productos)
    
    col_total1, col_total2 = st.columns([3, 1])
    with col_total1:
        # Botón para eliminar seleccionados (procesar cambios del editor)
        filas_a_eliminar = edited_df[edited_df["Eliminar"] == True].index.tolist()
        if filas_a_eliminar:
            if st.button(f"🗑️ Eliminar ({len(filas_a_eliminar)}) seleccionados"):
                # Eliminar items (desde el último para no afectar indices al borrar)
                for i in sorted(filas_a_eliminar, reverse=True):
                    st.session_state.productos.pop(i)
                st.rerun()

    with col_total2:
        st.markdown(f"### Total: S/. {total_general:.2f}")

    # Botón PDF
    pdf_bytes = create_pdf(st.session_state.productos, total_general)
    st.download_button(
        label="📄 Descargar PDF",
        data=pdf_bytes,
        file_name=f"lista_compras_{datetime.now(pytz.timezone('America/Lima')).strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )

    # Línea separadora
    st.markdown("---")
    
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
2. Pon la cantidad (ejem: 1 kilo, 1/2 pollo, 1/4 pollo, 1/8 pollo)
3. Pon el costo por unidad del producto
4. Haz clic en 'Agregar a la lista'
5. Usa ❌ para eliminar un producto de la lista

Creado por: Jenrry Soto Dextre\n
Correo: dextre1481@gmail.com\n
Pagina web: https://dextre.xyz\n
GitHub: https://github.com/jenrrysd\n
""")