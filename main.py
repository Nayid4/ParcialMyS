from flask import Flask, render_template, request, redirect, url_for
import folium
import pandas as pd
import os
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
UPLOAD_FOLDER = 'static/data'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        # Verificar si el archivo está presente en la solicitud
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # Si el usuario no selecciona ningún archivo, se devuelve a la página de carga
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Cargar el archivo CSV en un DataFrame de pandas
            df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Obtener la lista de variables
            variables = df.columns.tolist()
            # Estadísticas descriptivas
            stats = df.describe() if not df.empty else pd.DataFrame()  # Inicializar stats con un DataFrame vacío si df está vacío
            # Histograma
            plt.figure(figsize=(10, 6))
            df.hist()
            plt.tight_layout()
            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            histogram_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
            # Crear el mapa de Colombia con Folium
            colombia_map = folium.Map(location=[4.5709, -74.2973], zoom_start=6)
            # Guardar el mapa de Colombia como un archivo HTML
            colombia_map.save('static/colombia_map.html')  # Cambio la ruta de guardado a 'static'
            # Renderizar la plantilla HTML con los datos y el mapa
            return render_template('dashboard.html', variables=variables, stats=stats, histogram_url=histogram_url)

    return render_template('dashboard.html')


if __name__ == "__main__":
    app.run(debug=True)

