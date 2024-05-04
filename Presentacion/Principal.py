import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import geopandas as gpd
import folium
from folium.plugins import HeatMap

def select_dataset():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        dataset_entry.delete(0, tk.END)
        dataset_entry.insert(0, file_path)

def select_geojson():
    file_path = filedialog.askopenfilename(filetypes=[("GeoJSON files", "*.geojson")])
    if file_path:
        try:
            # Cargar el archivo GeoJSON de los departamentos de Colombia
            gdf = gpd.read_file(file_path)
            update_map(gdf)
            print("Archivo GeoJSON cargado con éxito.")
        except Exception as e:
            print("Error al cargar el archivo GeoJSON:", e)

def load_dataset():
    file_path = dataset_entry.get()
    if file_path:
        try:
            dataset = pd.read_csv(file_path)

            # Lista de columnas que necesitan corrección
            columns_to_correct = ['DANE', 'Codigo.DANE.periodo', 'Codigo.DANE.year']

            # Verificar y corregir los números de 4 dígitos en las columnas específicas
            for column in columns_to_correct:
                dataset[column] = dataset[column].apply(lambda x: str(x).zfill(5) if len(str(x)) == 4 else x)

            # Listar las variables cargadas
            variables_label.config(text="Variables del Dataset: " + ", ".join(dataset.columns))
            
            # Calcular estadísticas descriptivas
            descriptive_stats = dataset.describe()

            # Mostrar estadísticas descriptivas
            stats_text.config(state=tk.NORMAL)
            stats_text.delete('1.0', tk.END)
            stats_text.insert(tk.END, descriptive_stats)
            stats_text.config(state=tk.DISABLED)

            # Calcular histogramas
            plt.figure(figsize=(6, 4))
            for column in dataset.columns:
                if dataset[column].dtype in ['int64', 'float64']:
                    plt.hist(dataset[column], bins=20, alpha=0.5, label=column)
                    plt.xlabel(column)
                    plt.ylabel('Frecuencia')
                    plt.title('Histograma de Distribución')
                    plt.legend()
            plt.tight_layout()
            plt_canvas = FigureCanvasTkAgg(plt.gcf(), master=graph_frame)
            plt_canvas.draw()
            plt_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            print("Dataset cargado con éxito.")
        except Exception as e:
            print("Error al cargar el dataset:", e)
    else:
        print("Por favor, selecciona un archivo CSV.")

def update_map(gdf):
    global merged_data
    if 'DPTO_CCDGO' in gdf.columns:
        # Agrupar los datos por departamento y calcular la intensidad de casos de dengue
        grouped_data = dataset.groupby('DANE')['cases_all'].sum().reset_index()
        merged_data = pd.merge(gdf, grouped_data, left_on='DPTO_CCDGO', right_on='DANE', how='left')
        merged_data = merged_data[['DPTO_CNMBR', 'geometry', 'cases_all']].dropna()
        
        # Crear el mapa de calor
        m = folium.Map(location=[4.5709, -74.2973], zoom_start=6, tiles='cartodbpositron')
        HeatMap(data=merged_data[['geometry', 'cases_all']], radius=15).add_to(m)
        folium.GeoJson(merged_data, name='geojson').add_to(m)
        
        # Mostrar el mapa interactivo
        map_canvas = FigureCanvasTkAgg(m, master=map_frame)
        map_canvas.draw()
        map_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    else:
        print("El archivo GeoJSON no contiene la columna 'DPTO_CCDGO'.")

# Crear la ventana principal
root = tk.Tk()
root.title("Dashboard de Análisis de Datos")
root.configure(bg='#f0f0f0')

# Crear un marco para el título
title_frame = tk.Frame(root, bg='#333')
title_frame.pack(fill=tk.X)

# Etiqueta para el título
title_label = tk.Label(title_frame, text="Dashboard de Análisis de Datos", fg='white', bg='#333', font=('Helvetica', 16, 'bold'))
title_label.pack(pady=10)

# Crear un marco para el contenido principal
content_frame = tk.Frame(root, bg='#f0f0f0')
content_frame.pack(pady=10)

# Crear un botón para seleccionar el dataset
select_button = tk.Button(content_frame, text="Seleccionar Dataset", command=select_dataset)
select_button.grid(row=0, column=0, padx=10, pady=10)

# Entrada para mostrar la ruta del archivo seleccionado
dataset_entry = tk.Entry(content_frame, width=50)
dataset_entry.grid(row=0, column=1, padx=10, pady=10)

# Botón para cargar el dataset
load_button = tk.Button(content_frame, text="Cargar Dataset", command=load_dataset)
load_button.grid(row=0, column=2, padx=10, pady=10)

# Botón para seleccionar el archivo GeoJSON
select_geojson_button = tk.Button(content_frame, text="Seleccionar GeoJSON", command=select_geojson)
select_geojson_button.grid(row=0, column=3, padx=10, pady=10)

# Marco para mostrar el gráfico
graph_frame = tk.Frame(content_frame, bg='white', width=600, height=400)
graph_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

# Marco para mostrar el mapa interactivo
map_frame = tk.Frame(content_frame, bg='white', width=600, height=400)
map_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

# Etiqueta para mostrar las variables del dataset
variables_label = tk.Label(content_frame, text="Variables del Dataset:", bg='#f0f0f0', font=('Helvetica', 12, 'bold'))
variables_label.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

# Área de texto para mostrar estadísticas descriptivas
stats_text = tk.Text(content_frame, height=10, width=100)
stats_text.grid(row=4, column=0, columnspan=4, padx=10, pady=10)
stats_text.config(state=tk.DISABLED)

# Ejecutar el bucle principal de la ventana
root.mainloop()
