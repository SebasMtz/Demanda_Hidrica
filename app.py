import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Modelo de Demanda Hídrica", page_icon="💧", layout="centered")

# Estilos personalizados para colores azules y texto visible
primaryColor = "#1f77b4"
backgroundColor = "#f0f8ff"
secondaryBackgroundColor = "#e6f2ff"
textColor = "#000000"  # Cambiado a negro para mejor visibilidad
font = "sans serif"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {backgroundColor};
        color: {textColor};
    }}
    .stButton>button {{
        background-color: {primaryColor};
        color: white;
    }}
    h1, h2, h3, h4, h5, h6, p, label {{
        color: {textColor};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("💧 Modelo Interactivo de Demanda Hídrica para Cultivos Agroforestales")

st.header("Parámetros de Entrada")

# Densidades por hectárea con valores iniciales
cacao_density = st.number_input("Densidad de cacao por hectárea (plantas/ha)", value=1280, min_value=0)
permanent_shade_density = st.number_input("Densidad de sombra permanente por hectárea (plantas/ha)", value=1500, min_value=0)
short_term_crop_density = st.number_input("Densidad de cultivos de corto plazo por hectárea (plantas/ha)", value=0, min_value=0)
temporary_shade_density = st.number_input("Densidad de sombra temporal por hectárea (plantas/ha)", value=0, min_value=0)

# Total de hectáreas con valor inicial
total_hectares = st.number_input("Total de hectáreas a sembrar", value=12, min_value=1)

# Años a simular
years_to_simulate = st.number_input("Número de años a simular", value=10, min_value=5)

st.subheader("Demanda de agua por planta para los primeros 5 años (litros/planta/año)")

def get_water_demand_input(crop_name, default_values):
    st.write(f"**{crop_name}:**")
    water_demand = []
    cols = st.columns(5)
    for i in range(5):
        demand = cols[i].number_input(f"Año {i+1}", key=f"{crop_name}_year_{i+1}", value=default_values[i], min_value=0)
        water_demand.append(demand)
    st.write("")  # Espacio adicional
    return water_demand

# Valores iniciales para demanda de agua por planta
cacao_default_demand = [300, 400, 600, 800, 1200]
permanent_shade_default_demand = [150, 250, 300, 400, 400]
short_term_crop_default_demand = [0, 0, 0, 0, 0]
temporary_shade_default_demand = [0, 0, 0, 0, 0]

# Ingresar demandas de agua para cada cultivo
cacao_water_demand = get_water_demand_input("Cacao", cacao_default_demand)
permanent_shade_water_demand = get_water_demand_input("Sombra Permanente", permanent_shade_default_demand)
short_term_crop_water_demand = get_water_demand_input("Cultivos de Corto Plazo", short_term_crop_default_demand)
temporary_shade_water_demand = get_water_demand_input("Sombra Temporal", temporary_shade_default_demand)

st.header("Resultados")

# Crear DataFrame para almacenar la demanda anual
years = np.arange(1, years_to_simulate + 1)
data = pd.DataFrame({'Año': years})

def calculate_water_demand(density, water_demand_list):
    demand_per_year = []
    for year in years:
        if year <= 5:
            demand = water_demand_list[year - 1] * density * total_hectares
        else:
            demand = water_demand_list[-1] * density * total_hectares  # Demanda estabilizada
        demand_per_year.append(demand)
    return demand_per_year

# Calcular demanda hídrica para cada cultivo
cacao_total_demand = calculate_water_demand(cacao_density, cacao_water_demand)
permanent_shade_total_demand = calculate_water_demand(permanent_shade_density, permanent_shade_water_demand)
short_term_crop_total_demand = calculate_water_demand(short_term_crop_density, short_term_crop_water_demand)
temporary_shade_total_demand = calculate_water_demand(temporary_shade_density, temporary_shade_water_demand)

# Agregar al DataFrame
data['Demanda Cacao (L)'] = cacao_total_demand
data['Demanda Sombra Permanente (L)'] = permanent_shade_total_demand
data['Demanda Cultivos Corto Plazo (L)'] = short_term_crop_total_demand
data['Demanda Sombra Temporal (L)'] = temporary_shade_total_demand
data['Demanda Total (L)'] = data[['Demanda Cacao (L)', 'Demanda Sombra Permanente (L)', 
                                  'Demanda Cultivos Corto Plazo (L)', 'Demanda Sombra Temporal (L)']].sum(axis=1)

# Mostrar tabla de demandas
st.subheader("Demanda Hídrica Anual por Cultivo")
st.dataframe(
    data.style.format({"Demanda Cacao (L)": "{:,.0f}", 
                       "Demanda Sombra Permanente (L)": "{:,.0f}",
                       "Demanda Cultivos Corto Plazo (L)": "{:,.0f}",
                       "Demanda Sombra Temporal (L)": "{:,.0f}",
                       "Demanda Total (L)": "{:,.0f}"})
    .set_properties(**{'background-color': '#e6f2ff', 'color': '#000000'}, subset=pd.IndexSlice[:, :])
)

# Graficar la demanda hídrica
st.subheader("Gráfica de Demanda Hídrica Anual")

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(data['Año'], data['Demanda Total (L)'], marker='o', color=primaryColor, label='Demanda Total')
ax.fill_between(data['Año'], data['Demanda Total (L)'], color=primaryColor, alpha=0.3)
ax.set_xlabel('Año')
ax.set_ylabel('Demanda de Agua (Litros)')
ax.set_title('Demanda Hídrica Anual', color=primaryColor)
ax.grid(True, linestyle='--', alpha=0.7)
ax.legend()
st.pyplot(fig)

# Calcular el volumen máximo de agua necesario
max_water_demand = data['Demanda Total (L)'].max()
st.write(f"**Demanda máxima de agua:** {max_water_demand:,.0f} litros")

# Calcular el área de la olla
pond_volume_m3 = max_water_demand / 1000  # Convertir litros a metros cúbicos
pond_area = pond_volume_m3 / 5  # Profundidad de 5 metros
st.write(f"**Área requerida de la olla:** {pond_area:,.2f} m²")
st.write(f"Esto equivale a **{pond_area / 10000:.4f} hectáreas**")
