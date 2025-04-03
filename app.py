from flask import Flask, request, jsonify
import joblib
import numpy as np
import sendgrid
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
import os
import logging

app = Flask(__name__)

# Load trained model
try:
    model = joblib.load("model.pkl")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    model = None  # Ensure the app does not crash

# Load environment variables (for security)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")
ALERT_PHONE = os.getenv("ALERT_PHONE")

# Validate API keys
if not SENDGRID_API_KEY:
    logging.warning("SENDGRID_API_KEY is missing!")
if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    logging.warning("Twilio credentials are missing!")

# Function to send email alert
def send_email_alert(message):
    if not SENDGRID_API_KEY:
        logging.error("SendGrid API Key is missing. Email alert not sent.")
        return

    try:
        sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
        email = Mail(
            from_email="kaviyashreejawahar@gmail.com",
            to_emails=ALERT_EMAIL,
            subject="Security Alert",
            plain_text_content=message
        )
        response = sg.send(email)
        logging.info(f"Email sent successfully: {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending email alert: {e}")

# Function to send SMS alert
def send_sms_alert(message):
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        logging.error("Twilio credentials missing. SMS alert not sent.")
        return

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_="+91 9940141132",  # Twilio number
            to=ALERT_PHONE
        )
        logging.info(f"SMS sent successfully: {message.sid}")
    except Exception as e:
        logging.error(f"Error sending SMS alert: {e}")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if not model:
            return jsonify({"error": "Model not loaded"}), 500

        data = request.json  # Parse JSON request body
        if isinstance(data, list):
            data = data[0]  # Handle list format

        if not isinstance(data, dict):
            return jsonify({"error": "Invalid input format. Expecting JSON dictionary."}), 400

        # Convert input data into a NumPy array
        features = np.array(list(data.values())).reshape(1, -1)

        # Get model prediction
        prediction = model.predict(features)

        if prediction[0] == -1:  # If anomaly detected
            alert_message = "Suspicious activity detected!"
            send_email_alert(alert_message)
            send_sms_alert(alert_message)
            return jsonify({"status": "alert", "message": alert_message}), 200
        
        return jsonify({"status": "normal", "message": "No threats detected"}), 200

    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "Flask API For Security Application in Cloud is running!"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Enable logging
    app.run(debug=True)
