from flask import Flask, request, jsonify
import joblib
import numpy as np
import sendgrid
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
import os

app = Flask(__name__)

# Load trained model
model = joblib.load("model.pkl")

# Load environment variables (for security)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")
ALERT_PHONE = os.getenv("ALERT_PHONE")

def send_email_alert(message):
    sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
    email = Mail(
        from_email="kaviyashree2673@example.com",
        to_emails=ALERT_EMAIL,
        subject="Security Alert",
        plain_text_content=message
    )
    sg.send(email)

def send_sms_alert(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_="+91 9940141132",  # Your Twilio number
        to=ALERT_PHONE
    )

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return jsonify({"message": "GET request received"}), 200

    try:
        data = request.json
        features = np.array(data["features"]).reshape(1, -1)
        prediction = model.predict(features)

        if prediction[0] == -1:  # Anomaly detected
            alert_message = "Suspicious activity detected!"
            send_email_alert(alert_message)
            send_sms_alert(alert_message)
            return jsonify({"status": "alert", "message": alert_message}), 200
        
        return jsonify({"status": "normal", "message": "No threats detected"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "Flask API is running!"

if __name__ == "__main__":
    app.run(debug=True)
