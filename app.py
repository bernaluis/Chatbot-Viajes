from flask import Flask, render_template, request, jsonify
import openai
import sqlite3

# Configuración de la API de OpenAI
openai.api_key = ""

app = Flask(__name__)

# Configurar la base de datos SQLite
DB_NAME = "travel_history.db"


def init_db():
    """Inicializa la base de datos."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin TEXT,
                destination TEXT,
                departure_date TEXT,
                return_date TEXT,
                activities TEXT,
                budget REAL,
                response TEXT
            )
        """)
        conn.commit()


@app.route('/recommend', methods=['POST'])
def recommend():
    """Recibe datos del frontend, consulta la API de ChatGPT y guarda el historial."""
    data = request.json

    # Extraer datos
    origin = data.get('origin')
    destinations = data.get('destinations')
    departure_date = data.get('departure_date')
    return_date = data.get('return_date')
    activities = data.get('activities', [])
    activities.reverse()
    budget = data.get('budget')

    # Crear mensaje para ChatGPT
    messages = [
        {"role": "system", "content": "Eres un agente de viajes virtual."},
        {"role": "user", "content": f"El cliente quiere viajar de {origin} a {destinations}. Fecha de salida: {departure_date}, Fecha de regreso: {return_date}. Las actividades que le interesan son: {', '.join(activities)}. Su presupuesto total es de ${budget}. ¿Qué vuelos y opciones de viaje puedo recomendarle?"}
    ]

    try:
        # Llamada a la API de ChatGPT utilizando la versión 1.55.1
        response = openai.chat.completions.create(
            model="gpt-4",  # o el modelo que prefieras
            messages=messages,
            temperature=0
        )
        chatgpt_response = response.choices[0].message.content

        # Guardar en SQLite
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO history (origin, destination, departure_date, return_date, activities, budget, response)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (origin, ', '.join(destinations), departure_date, return_date, ', '.join(activities), budget, chatgpt_response))
            conn.commit()

        # Respuesta al cliente
        return jsonify({
            'status': 'success',
            'response': chatgpt_response
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/history', methods=['GET'])
def history():
    """Devuelve el historial de búsquedas desde SQLite."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM history ORDER BY id DESC")
            rows = cursor.fetchall()

        history = [
            {
                'id': row[0],
                'origin': row[1],
                'destination': row[2],
                'departure_date': row[3],
                'return_date': row[4],
                'activities': row[5],
                'budget': row[6],
                'response': row[7]
            } for row in rows
        ]

        return jsonify({'status': 'success', 'history': history})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
