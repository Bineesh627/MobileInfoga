from telethon import events, sync
from modules.extract_data import DataConverter
from telethon.tl.types import InputPeerUser
from modules.config import API_HASH, API_ID, PHONE
import asyncio
import json
import re
import os

class TelethonBot:
    def __init__(self):
        self.client = None
        self.username = '@TrueCaller1Bot'
        self.user_entity = None
        self.message = None

    def authenticate(self):
        os.makedirs('session', exist_ok=True)
        self.client = sync.TelegramClient('session/session', API_ID, API_HASH)
        self.client.connect()
        if not self.client.is_user_authorized():
            self.client.send_code_request(PHONE)
            self.client.sign_in(PHONE, input('Enter the OTP code: '))

    def get_user_entity(self, username):
        self.username = username
        self.user_entity = self.client.get_entity(username)

    def send_message_to_user(self, message):
        user_id = self.user_entity.id
        user_hash = self.user_entity.access_hash
        receiver = InputPeerUser(user_id, user_hash)
        self.client.send_message(receiver, message, parse_mode='html')

    def start_event_loop(self):
        self.client.start()
        self.client.run_until_disconnected()

    async def extract_data(self, event):
        extracted_data = {}
        unknown_name_found = False  # Initialize the variable here
        if event.is_reply:
            message_text = event.message.text
            converter = DataConverter(message_text)
            os.makedirs('output', exist_ok=True)
            converter.process('output/output.json')
            print(converter.convert_to_json())
        self.client.disconnect()

    def run(self):
        try:
            self.authenticate()
            self.get_user_entity(self.username)
            self.send_message_to_user(self.message)
            self.client.add_event_handler(self.extract_data, events.MessageEdited(from_users=self.user_entity.id, incoming=True))
            self.start_event_loop()
        except KeyboardInterrupt:
            print("Program terminated by user.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if self.client:
                self.client.disconnect()
