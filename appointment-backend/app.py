from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from twilio.rest import Client
from dotenv import load_dotenv
import os

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(to, subject, body):
    msg = MIMEMultipart()
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

    print("Email sent to:", to)


load_dotenv()

app = Flask(__name__)
CORS(app)

# -----------------------------
# Database Connection
# -----------------------------
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# -----------------------------
# SMS Function
# -----------------------------
def send_sms(to, message):
    try:
        client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH"))
        client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_NUMBER"),
            to=to
        )
        print("SMS sent successfully")
        
        return True
    except Exception as e:
        print("SMS Error:", e)
        return False

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    return "Appointment backend is running"

@app.route("/test")
def test():
    return "Test OK"

@app.route('/test-sms')
def test_sms():
    send_sms("+15103645765", "Test message from you system!")
    return "SMS sent!"
@app.route('/test-email')
def test_email():
    send_email(
        "pandu.chetan27@gmail.com", 
        "Test Email", 
        "This is a test email from your appointment backend."
    )
    return "Email sent!"



# -----------------------------
# CREATE Appointment
# -----------------------------
@app.route("/appointments", methods=["POST"])
def create_appointment():
    try:
        data = request.json

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO appointments (patient_name, patient_phone, provider_name, patient_email, appointment_time)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            data["patient_name"],
            data["patient_phone"],
            data["provider_name"],
            data["patient_email"],
            data["appointment_time"]
        )

        cursor.execute(sql, values)
        conn.commit()

        appointment_id = cursor.lastrowid

        # Send SMS AFTER DB commit
        send_sms(
            data["patient_phone"],
            f"Hello {data['patient_name']}, your appointment is confirmed for {data['appointment_time']}."
        )

        send_email(
        data['patient_email'],
        "Appointment Confirmation",
        f"Hello {data['patient_name']}, your appointment with {data['provider_name']} is confirmed for {data['appointment_time']}."
    )

        cursor.close()
        conn.close()

        return jsonify({"id": appointment_id, "message": "Appointment created"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# READ All Appointments
# -----------------------------
@app.route("/appointments", methods=["GET"])
def get_appointments():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM appointments ORDER BY appointment_time ASC")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(rows), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# READ Single Appointment
# -----------------------------
@app.route("/appointments/<int:id>", methods=["GET"])
def get_appointment(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM appointments WHERE id = %s", (id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            return jsonify(row), 200
        else:
            return jsonify({"message": "Appointment not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# UPDATE Appointment
# -----------------------------
@app.route("/appointments/<int:id>", methods=["PUT"])
def update_appointment(id):
    try:
        data = request.json

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE appointments
            SET patient_name=%s, patient_phone=%s, provider_name=%s, patient_email=%s, appointment_time=%s
            WHERE id=%s
        """

        values = (
            data["patient_name"],
            data["patient_phone"],
            data["provider_name"],
            data["patient_email"],
            data["appointment_time"],
            id
        )

        cursor.execute(sql, values)
        conn.commit()
        send_email(
        data['patient_email'],
        "Appointment updated Confirmation",
        f"Hello {data['patient_name']}, your appointment with {data['provider_name']} is confirmed for {data['appointment_time']}."
    )

        updated = cursor.rowcount  # check BEFORE closing cursor

        cursor.close()
        conn.close()

        if updated == 0:
            return jsonify({"message": "Appointment not found"}), 404

        # Send SMS
        send_sms(
            data["patient_phone"],
            f"Hello {data['patient_name']}, your appointment has been updated to {data['appointment_time']}."
        )

        return jsonify({"message": "Appointment updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# DELETE Appointment
# -----------------------------
@app.route("/appointments/<int:id>", methods=["DELETE"])
def delete_appointment(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get patient info BEFORE deleting
        cursor.execute("SELECT patient_name, patient_phone FROM appointments WHERE id = %s", (id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"message": "Appointment not found"}), 404

        patient_name = row["patient_name"]
        patient_phone = row["patient_phone"]

        cursor.execute("DELETE FROM appointments WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        # Send SMS
        send_sms(
            patient_phone,
            f"Hello {patient_name}, your appointment has been cancelled."
        )

        return jsonify({"message": "Appointment deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)