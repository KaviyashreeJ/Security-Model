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
SENDGRID_API_KEY = AC84e2d75670ff64f058b87794cde8adef
TWILIO_ACCOUNT_SID = AC43929220433ca57bec69edce522c5a8d
TWILIO_AUTH_TOKEN = 524e6e01b962dc4851fe1da43da7eaee
ALERT_EMAIL = os.getenv("ALERT_EMAIL")
ALERT_PHONE = os.getenv("ALERT_PHONE")

# Function to send email alert
def send_email_alert(message):
    sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
    email = Mail(
        from_email="kaviyashreejawahar@gmail.com",
        to_emails=ALERT_EMAIL,
        subject="Security Alert",
        plain_text_content=message
    )
    sg.send(email)

# Function to send SMS alert
def send_sms_alert(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_="+91 9940141132",  # My Twilio number
        to=ALERT_PHONE
    )

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json  # Parse JSON request body

        # Check if the data is a list or a dictionary
        if isinstance(data, list):
            data = data[0]  # Extract first element if it's a list

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
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "Flask API is running!"

if __name__ == "__main__":
    app.run(debug=True)
