import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Presupuestador Malacara", page_icon="❄️")

# --- BASE DE DATOS DE PRECIOS ---
PRECIOS_ALQUILER = {
    "Esquís Gama Bronce": {
        "Equipo Completo": [21.00, 38.50, 49.00, 58.00, 67.50],
        "Equipo Completo + Casco": [27.50, 47.50, 62.00, 73.00, 83.50],
        "Esquís + Bastones": [18.50, 34.00, 46.00, 55.50, 63.50],
        "Botas Esquí": [9.00, 15.50, 21.00, 26.00, 28.00]
    },
    "Esquís Gama Plata": {
        "Equipo Completo": [26.00, 46.50, 66.00, 83.50, 99.50],
        "Equipo Completo + Casco": [32.00, 55.50, 78.50, 98.50, 114.50],
        "Esquís + Bastones": [23.50, 44.00, 63.50, 81.00, 97.00],
        "Botas Esquí": [13.00, 24.00, 34.50, 42.50, 49.00]
    },
    "Esquís Gama Oro": {
        "Equipo Completo": [35.50, 65.00, 92.00, 120.00, 138.00],
        "Equipo Completo + Casco": [42.00, 75.50, 106.00, 136.00, 155.50],
        "Esquís + Bastones": [31.50, 53.00, 72.00, 90.50, 107.50],
        "Botas Esquí": [14.50, 26.00, 36.00, 44.00, 50.50]
    },
    "Esquís de Travesía": {
        "Equipo Completo": [35.50, 65.00, 92.00, 120.00, 138.00],
        "Equipo Completo + Casco": [42.00, 75.50, 106.00, 136.00, 155.50],
        "Esquís + Bastones": [31.50, 53.00, 72.00, 90.50, 107.50],
        "Botas Travesía": [14.50, 26.00, 36.00, 44.00, 50.50]
    },
    "Esquís Infantil (<= 13 Años)": {
        "Equipo Completo": [17.00, 30.50, 38.50, 50.00, 54.50],
        "Equipo Completo + Casco": [23.50, 40.00, 51.50, 65.00, 71.50],
        "Esquís + Bastones": [14.50, 24.00, 34.00, 40.00, 45.00],
        "Botas Esquí": [7.50, 11.50, 14.50, 17.00, 19.50]
    },
    "Esquís Infantil Oro (<= 13 Años)": {
        "Equipo Completo": [23.50, 42.50, 54.00, 69.00, 76.00],
        "Equipo Completo + Casco": [29.00, 51.50, 66.00, 83.50, 92.00],
        "Esquís + Bastones": [22.00, 41.00, 52.00, 67.50, 74.50],
        "Botas Esquí": [10.00, 16.00, 22.00, 26.50, 30.50]
    },
    "Snowboard Progresión": {
        "Tabla + Botas": [27.50, 49.00, 68.00, 84.50, 98.00],
        "Tabla + Botas + Casco": [34.00, 58.50, 82.00, 100.00, 115.50],
        "Tabla Sola": [20.00, 36.00, 52.00, 66.00, 79.50],
        "Botas Snowboard": [10.50, 18.50, 26.00, 32.00, 38.50]
    },
    "Snowboard Experto": {
        "Tabla + Botas": [32.00, 58.50, 75.50, 93.00, 100.00],
        "Tabla + Botas + Casco": [37.00, 66.50, 86.00, 106.00, 114.00],
        "Tabla Sola": [27.50, 48.00, 66.50, 82.00, 87.50],
        "Botas Snowboard": [11.50, 19.50, 26.50, 33.00, 39.50]
    },
    "Snowboard Niño": {
        "Tabla + Botas": [22.00, 37.00, 51.50, 65.00, 74.50],
        "Tabla + Botas + Casco": [28.00, 46.00, 65.00, 80.00, 93.00],
        "Tabla Sola": [18.00, 32.00, 45.00, 57.00, 71.50],
        "Botas Snowboard": [7.50, 11.50, 14.50, 17.00, 19.50]
    }
}

# --- FUNCIONES AUXILIARES ---
def calcular_precio_clases(tipo, num_personas, num_dias_horas):
    """
    Colectiva: 55€ por persona/dia (bloque 3h).
    Particular: 50€ base (1 pax) + 5€ por cada pax extra, por hora.
    """
    if tipo == "Colectiva (3h/día)":
        precio_unitario = 55
        total = precio_unitario * num_personas * num_dias_horas
        descripcion = f"Cursillo Colectivo ({num_dias_horas} días)"
        detalle = f"{num_dias_horas} días x {num_personas} pers"
        return total, descripcion, detalle, precio_unitario
    else: # Particular
        # Lógica: Base 50€ + 5€ por cada persona adicional
        # Ejemplo: 1 pers = 50€/h. 2 pers = 55€/h. 3 pers = 60€/h.
        precio_hora = 50 + (max(0, num_personas - 1) * 5)
        total = precio_hora * num_dias_horas # Aquí num_dias_horas son Horas Totales
        descripcion = f"Clase Particular ({num_dias_horas} horas totales)"
        detalle = f"{num_dias_horas}h totales x {num_personas} pers"
        return total, descripcion, detalle, precio_hora

def calcular_precio_alquiler(gama, equipo, dias):
    if dias < 1: return 0
    if dias > 5: dias = 5 # Tope según tablas
    
    # Índice del array (dias - 1)
    try:
        precio = PRECIOS_ALQUILER[gama][equipo][dias-1]
        return precio
    except:
        return 0

# --- CLASE PDF ---
class PDF(FPDF):
    def header(self):
        # Intentar poner logo si existe, si no, texto
        # self.image('logo.png', 10, 8, 33) 
        self.set_font('Arial', 'B', 24)
        self.set_text_color(220, 50, 50) # Rojo Malacara aprox
        self.cell(0, 10, 'Presupuesto', 0, 1, 'C')
        self.set_text_color(50, 50, 100)
        self.cell(0, 10, 'Malacara Esquí - Snowboard', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Generado automáticamente por Malacara App', 0, 0, 'C')

# --- INTERFAZ STREAMLIT ---
st.title("⛷️ Generador de Presupuestos Malacara")

# 1. DATOS DEL CLIENTE
with st.container():
    st.subheader("1. Detalles del Cliente")
    col1, col2 = st.columns(2)
    cliente_nombre = col1.text_input("Nombre del Cliente", "Iván Fernández")
    cliente_fechas = col2.text_input("Fechas (ej: 22/12 - 24/12)", "22/12 - 24/12")
    cliente_telefono = col1.text_input("Teléfono")
    cliente_email = col2.text_input("Email")
    fecha_solicitud = datetime.now().strftime("%d/%m/%Y")

# 2. CLASES
st.divider()
st.subheader("2. Clases de Esquí / Snowboard")
col_clase1, col_clase2, col_clase3 = st.columns(3)
tipo_clase = col_clase1.selectbox("Tipo de Clase", ["Ninguna", "Colectiva (3h/día)", "Particular"])
num_alumnos = col_clase2.number_input("Nº Alumnos", min_value=1, value=1)

if tipo_clase == "Colectiva (3h/día)":
    duracion_clase = col_clase3.number_input("Días de Clase", min_value=1, max_value=5, value=3)
    lbl_duracion = "días"
elif tipo_clase == "Particular":
    duracion_clase = col_clase3.number_input("Total Horas Contratadas", min_value=1, value=2)
    lbl_duracion = "horas"
else:
    duracion_clase = 0
    lbl_duracion = "-"

precio_clases = 0
desc_clases = ""
detalle_clases = ""
unitario_clases = 0

if tipo_clase != "Ninguna":
    precio_clases, desc_clases, detalle_clases, unitario_clases = calcular_precio_clases(tipo_clase, num_alumnos, duracion_clase)
    st.info(f"💰 Total Clases: {precio_clases}€ ({desc_clases})")

# 3. ALQUILER DE MATERIAL
st.divider()
st.subheader("3. Alquiler de Material")

# Inicializar lista de alquileres en session state si no existe
if 'alquileres' not in st.session_state:
    st.session_state['alquileres'] = []

# Formulario para añadir alquiler
with st.expander("Añadir Equipo", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    cat_select = c1.selectbox("Gama", list(PRECIOS_ALQUILER.keys()))
    equip_options = list(PRECIOS_ALQUILER[cat_select].keys())
    equip_select = c2.selectbox("Equipo", equip_options)
    dias_alq = c3.slider("Días", 1, 5, 3)
    cant_equip = c4.number_input("Cantidad", 1, 10, 1)
    
    if st.button("Añadir a la lista"):
        precio_unit = calcular_precio_alquiler(cat_select, equip_select, dias_alq)
        subtotal_linea = precio_unit * cant_equip
        st.session_state['alquileres'].append({
            "gama": cat_select,
            "tipo": equip_select,
            "dias": dias_alq,
            "cantidad": cant_equip,
            "precio_unit": precio_unit,
            "subtotal": subtotal_linea
        })

# Mostrar Tabla de Alquileres seleccionados
total_alquiler = 0
if len(st.session_state['alquileres']) > 0:
    df_alq = pd.DataFrame(st.session_state['alquileres'])
    st.dataframe(df_alq[["gama", "tipo", "dias", "cantidad", "subtotal"]])
    total_alquiler = df_alq["subtotal"].sum()
    
    if st.button("Borrar todo el material"):
        st.session_state['alquileres'] = []
        st.rerun()

st.write(f"**Subtotal Alquiler: {total_alquiler}€**")

# 4. DESCUENTOS Y TOTALES
st.divider()
st.subheader("4. Resumen y Descuentos")

subtotal_general = precio_clases + total_alquiler

col_d1, col_d2 = st.columns(2)
aplicar_descuento = col_d1.checkbox("Aplicar Descuento Manual")
tipo_desc = col_d2.radio("Tipo", ["Porcentaje (%)", "Cantidad Fija (€)"], disabled=not aplicar_descuento)
valor_desc = col_d1.number_input("Valor del descuento", min_value=0.0, value=0.0, disabled=not aplicar_descuento)
concepto_desc = col_d2.text_input("Motivo Descuento", "Descuento Comercial", disabled=not aplicar_descuento)

descuento_total = 0
if aplicar_descuento:
    if tipo_desc == "Porcentaje (%)":
        descuento_total = subtotal_general * (valor_desc / 100)
    else:
        descuento_total = valor_desc

total_final = subtotal_general - descuento_total

st.metric(label="TOTAL PRESUPUESTO", value=f"{total_final:.2f}€", delta=f"-{descuento_total:.2f}€" if descuento_total > 0 else None)

# 5. GENERAR PDF
def create_pdf():
    pdf = PDF()
    pdf.add_page()
    
    # Colores
    blue_header = (230, 240, 255)
    
    # Texto intro
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, "Gracias por contactar con Malacara Esquí y Snowboard. A continuación, encontrará su presupuesto personalizado.")
    pdf.ln(5)
    
    # BLOQUE CLIENTE
    pdf.set_fill_color(*blue_header)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Detalles del Cliente", 0, 1, 'L', fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 6, "Nombre:", 0, 0)
    pdf.set_font("Arial", '', 10)
    pdf.cell(50, 6, cliente_nombre, 0, 0)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 6, "Fecha Solicitud:", 0, 0)
    pdf.set_font("Arial", '', 10)
    pdf.cell(50, 6, fecha_solicitud, 0, 1)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 6, "Fechas viaje:", 0, 0)
    pdf.set_font("Arial", '', 10)
    pdf.cell(50, 6, cliente_fechas, 0, 0)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 6, "Teléfono:", 0, 0)
    pdf.set_font("Arial", '', 10)
    pdf.cell(50, 6, cliente_telefono, 0, 1)
    pdf.ln(5)
    
    # BLOQUE CLASES
    if tipo_clase != "Ninguna":
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "Presupuesto de Clases", 0, 1, 'L', fill=True)
        # Headers tabla
        pdf.set_font("Arial", 'B', 9)
        pdf.set_text_color(0, 51, 102) # Azul oscuro
        pdf.cell(70, 8, "Servicio", 1, 0, 'C')
        pdf.cell(30, 8, "Detalle", 1, 0, 'C')
        pdf.cell(30, 8, "Precio Unit.", 1, 0, 'C')
        pdf.cell(30, 8, "Total", 1, 1, 'C')
        
        # Rows
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 9)
        pdf.cell(70, 8, desc_clases, 1, 0)
        pdf.cell(30, 8, detalle_clases, 1, 0, 'C')
        pdf.cell(30, 8, f"{unitario_clases} eur", 1, 0, 'C')
        pdf.cell(30, 8, f"{precio_clases} eur", 1, 1, 'C')
        pdf.ln(5)

    # BLOQUE ALQUILER
    if len(st.session_state['alquileres']) > 0:
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0)
        pdf.cell(0, 8, "Presupuesto de Alquiler", 0, 1, 'L', fill=True)
        
        # Headers
        pdf.set_font("Arial", 'B', 9)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(60, 8, "Equipo / Gama", 1, 0, 'C')
        pdf.cell(25, 8, "Duración", 1, 0, 'C')
        pdf.cell(25, 8, "Precio Unit.", 1, 0, 'C')
        pdf.cell(25, 8, "Cantidad", 1, 0, 'C')
        pdf.cell(25, 8, "Subtotal", 1, 1, 'C')
        
        pdf.set_text_color(0)
        pdf.set_font("Arial", '', 8)
        
        for item in st.session_state['alquileres']:
            desc_item = f"{item['gama']} - {item['tipo']}"
            pdf.cell(60, 8, desc_item[:35], 1, 0) # Cortar si es muy largo
            pdf.cell(25, 8, f"{item['dias']} dias", 1, 0, 'C')
            pdf.cell(25, 8, f"{item['precio_unit']} eur", 1, 0, 'C')
            pdf.cell(25, 8, str(item['cantidad']), 1, 0, 'C')
            pdf.cell(25, 8, f"{item['subtotal']} eur", 1, 1, 'C')
        pdf.ln(5)

    # RESUMEN FINAL
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Resumen del Presupuesto", 0, 1, 'L', fill=True)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(140, 7, "Total Clases:", 0, 0, 'R')
    pdf.cell(40, 7, f"{precio_clases:.2f} eur", 0, 1, 'R')
    
    pdf.cell(140, 7, "Total Alquiler:", 0, 0, 'R')
    pdf.cell(40, 7, f"{total_alquiler:.2f} eur", 0, 1, 'R')
    
    if descuento_total > 0:
        pdf.set_text_color(200, 0, 0)
        pdf.cell(140, 7, f"Descuento ({concepto_desc}):", 0, 0, 'R')
        pdf.cell(40, 7, f"-{descuento_total:.2f} eur", 0, 1, 'R')
        pdf.set_text_color(0)
        
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(140, 10, "TOTAL PRESUPUESTO:", 0, 0, 'R')
    pdf.cell(40, 10, f"{total_final:.2f} eur", 0, 1, 'R')
    pdf.ln(5)
    
    # CONDICIONES Y CONTACTO
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(*blue_header)
    pdf.cell(0, 8, "Condiciones y Contacto", 0, 1, 'L', fill=True)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, "\n- Este presupuesto tiene una validez de 15 días.\n- Para confirmar la reserva, contacte con nosotros.\n- Cancelaciones con menos de 48h conllevan cargo.\n\nTeléfono: +34 697 96 44 40 | Email: info@malacaraesqui.com\n¡Esperamos verle pronto en las pistas de Astún y Candanchú!")

    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 GENERAR PDF"):
    pdf_bytes = create_pdf()
    nombre_archivo = f"Presupuesto_Malacara_{cliente_nombre.replace(' ', '_')}.pdf"
    
    st.download_button(
        label="Descargar PDF Final",
        data=pdf_bytes,
        file_name=nombre_archivo,
        mime='application/pdf'
    )
