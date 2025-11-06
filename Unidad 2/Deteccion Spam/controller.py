import tkinter as tk                                # Tkinter para la GUI.
import pandas as pd                                 # Manejo de DataFrames.
from model import load_model_or_train, load_data    # Funciones del modelo y datos.

# En este modulo se realiza lo siguiente:
# - Definir la clase del controlador que conecta la vista y el modelo.
# - Proveer métodos para manejar eventos (botón, selección en tabla).
# - Cargar el modelo y los datos al iniciar.
# - Ejecuta una evaluación sobre todo el dataset (si está disponible).
# - Rellena la tabla de la vista y enlaza los handlers (botón y selección).

class SpamDetectorController:
    def __init__(self, root, view):
        self.view = view
        self.root = root

        # Carga el modelo y los datos, intentará cargar un .pkl si existe o reentrenara.
        self.model = load_model_or_train()
        # Buscará el CSV (Emails.csv) en rutas probables (cwd, data/).
        self.df = load_data()

        # Evalua el modelo con todo el dataset cargado y muestra % acierto.
        try:
            self.evaluate_on_dataset()
        except Exception as e:
            # 
            print(f"Advertencia: No se pudo evaluar el dataset: {e}")

        # Rellena el TreeView con las primeras filas del DataFrame (vista).
        self.view.populate_tree(self.df)

        # Botón de analizar -> analyze_email.
        self.view.set_analyze_command(self.analyze_email)
        # Selección de fila en la tabla -> on_tree_select.
        self.view.bind_tree_select(self.on_tree_select)

    # Handlers y métodos del controlador.
    def analyze_email(self):
        # Obtiene textos de la vista.
        asunto, mensaje = self.view.get_input_texts()
        # Concatenamos asunto y mensaje para la predicción como en el entrenamiento.
        full_text = f"{asunto.lower()} {mensaje.lower()}"

        if not full_text.strip():
            # Muestra un aviso al usuario por texto faltante.
            self.view.set_result_text("Ingrese Asunto y Mensaje", 'orange')
            return

        try:
            # El modelo espera una lista de strings.
            prediction = self.model.predict([full_text])[0]
            if prediction == 1:
                self.view.set_result_text("¡SPAM DETECTADO!", 'red')
            else:
                self.view.set_result_text("CORREO LEGÍTIMO", 'green')
        except Exception as e:
            # Si hay un error en la predicción, lo mostramos.
            self.view.set_result_text(f"Error en el análisis: {e}", 'gray')

    # Handler para cuando el usuario selecciona una fila en el TreeView.
    def on_tree_select(self, event):
        # Obtiene el id (iid) de la fila seleccionada.
        selection = event.widget.selection()
        if not selection:
            return
        iid = selection[0]

        # Intenta recuperar la fila del DataFrame por índice.
        try:
            df_row = self.df.loc[int(iid)]
        except Exception:
            try:
                df_row = self.df.loc[iid]
            except Exception:
                # Si no se puede localizar la fila, salimos sin hacer nada.
                return

        # Extrae campos con tolerancia a distintos tipos de estructuras de fila.
        remitente = df_row.get('Correo', '') if hasattr(df_row, 'get') else df_row['Correo'] if 'Correo' in df_row else ''
        asunto = df_row.get('Asunto', '') if hasattr(df_row, 'get') else df_row['Asunto'] if 'Asunto' in df_row else ''
        mensaje = df_row.get('Message', '') if hasattr(df_row, 'get') else df_row['Message'] if 'Message' in df_row else ''

        # Rellena la vista con los datos completos de la fila seleccionada.
        self.view.fill_fields(remitente=remitente, asunto=asunto, mensaje=mensaje)

    # Evalúa el modelo usando todas las filas etiquetadas del DataFrame.
    def evaluate_on_dataset(self):
        # Caso sin datos
        if self.df is None or self.df.empty:
            print("Evaluación: no hay datos para evaluar.")
            return

        # Verificar que el dataset tenga las columnas necesarias.
        if 'Categoría' not in self.df.columns or 'Message' not in self.df.columns:
            print("Evaluación: columnas requeridas ('Categoría', 'Message') no encontradas en el dataset.")
            return

        # Prepara las listas de textos y etiquetas verdaderas.
        texts = []
        y_true = []
        for _, row in self.df.iterrows():
            # Recupera la etiqueta y salta si es NaN.
            label = row.get('Categoría')
            if pd.isna(label):
                continue

            # Mapea etiquetas conocidas a 0/1. Aceptamos también '0'/'1' por si el CSV.
            if str(label).lower() in ('spam', '1'):
                y = 1
            elif str(label).lower() in ('ham', '0'):
                y = 0
            else:
                # Etiqueta desconocida -> ignorar fila.
                continue

            # Construye el texto de entrada igual que en la UI.
            asunto = str(row.get('Asunto', ''))
            mensaje = str(row.get('Message', ''))
            full = f"{asunto.lower()} {mensaje.lower()}".strip()

            # Si no hay texto útil, ignorar la fila.
            if not full:
                continue

            # Añade a las listas.
            texts.append(full)
            y_true.append(y)

        # Si no hay filas válidas para evaluar, notifica.
        if not texts:
            print("Evaluación: no se encontraron filas etiquetadas válidas para evaluar.")
            return

        # Predice en batch y calcula aciertos.
        try:
            preds = self.model.predict(texts)
        except Exception as e:
            print(f"Evaluación: error al predecir sobre el dataset: {e}")
            return

        # Calcula y muestra el porcentaje de aciertos.
        total = len(y_true)
        correct = int(sum(1 for a, b in zip(preds, y_true) if int(a) == int(b)))
        pct = (correct / total) * 100.0
        print(f"Evaluación del detector sobre {total} correos etiquetados: {correct}/{total} correctos -> {pct:.2f}% de acierto")
