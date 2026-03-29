from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Sarigama12@",
        database="clinic"
    )

@app.route("/")
def home():
    return "Appointment backend is running"
@app.route("/test")
def test():
    return "Test OK"

@app.route("/appointments", methods=["POST"])
def create_appointment():
    try:
        data = request.json

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO appointments (patient_name, patient_phone, provider_name, appointment_time)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            data["patient_name"],
            data["patient_phone"],
            data["provider_name"],
            data["appointment_time"]
        )

        cursor.execute(sql, values)
        conn.commit()

        appointment_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({"id": appointment_id, "message": "Appointment created"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)