import json
import aiohttp
import requests
from .base import NotificationChannel
import os


class WhatsAppNotificationChannel(NotificationChannel):
    def send(self, recipients, **kwargs):
        message = kwargs.get('message')
        if not message:
            raise ValueError("WhatsApp requires a message")

        for recipient in recipients:
            # Call WhatsApp API
            print(f"Sending WhatsApp to {recipient}")
            message_data = self.get_text_message_input(recipient, message)
            self.send_message(message_data)

    def send_message(self, data):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv("ACCESS_TOKEN")}",
        }

        url = f"https://graph.facebook.com/{os.getenv("VERSION")}/{
            os.getenv("PHONE_NUMBER_ID")}/messages"
        try:
            response = requests.post(url, data=data, headers=headers)
            if response.status_code == 200:
                print("Message sent successfully",
                      response.status_code, response.text)
            else:
                print("Failed to send message",
                      response.status_code, response.text)
        except Exception as e:
            print("Connection Error:", e)

    def get_text_message_input(self, recipient, text):
        return json.dumps({
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {
                "body": text
            }
        })
