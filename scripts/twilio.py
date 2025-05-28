from twilio.rest import Client

# Twilio credentials (replace with your actual credentials)
# USE ENVIRONMENT VARIABLES INSTEAD (twil.io/secure)
ACCOUNT_SID = 'ACe2b4cdd22b1f4c2041593660661ab9bc'
AUTH_TOKEN = '4047d4c0769927f9e1b3fed6a32a79e0'
TWILIO_PHONE_NUMBER = '+18774552519'  # Replace with your Twilio number
TO_PHONE_NUMBER = '+16697997334'     # Replace with the recipient's phone number

# Create Twilio client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Message content
message_body = "Hello! This is a test message from your Twilio API integration."

try:
    # Send the SMS
    message = client.messages.create(
        body=message_body,
        from_=TWILIO_PHONE_NUMBER,
        to=TO_PHONE_NUMBER
    )
    print(f"Message sent successfully! SID: {message.sid}")
except Exception as e:
    print(f"Failed to send message: {e}")
