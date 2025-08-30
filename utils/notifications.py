from twilio.rest import Client
from config import Config

client = Client(Config.TWILIO_SID, Config.TWILIO_AUTH_TOKEN)

def send_notification(target, message, user_id=None):
    # Simplified: Send SMS (extend for in-app, WhatsApp)
    # Fetch user phone by user_id if needed
    phone = '+1234567890'  # Mock
    client.messages.create(to=phone, from_=Config.TWILIO_PHONE, body=message)
    print(f'Notification sent: {message}')  # For logging