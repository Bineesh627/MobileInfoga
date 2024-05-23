from telethon import events, sync
from telethon.tl.types import InputPeerUser
from config import API_HASH, API_ID, PHONE
import asyncio
import json
import re
import os

class TelethonBot:
    def __init__(self):
        self.client = None
        self.username = '@TrueCaller_Z_Bot'
        self.user_entity = None

    def authenticate(self):
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
            message_text = re.sub(r'[*`\ufe0f]', '', message_text)
            lines = message_text.split('\n')  # Define lines here
        for line in lines:
            line = line.strip()

            elif line.startswith('Name:') and not unknown_name_found:
                extracted_data['name'] = line.split(':')[1].strip()
            elif line.startswith('🔍 Unknown Says:'):
                extracted_data['unknown'] = {}
                unknown_name_found = True
            elif line.startswith('Name:') and unknown_name_found:
                extracted_data['unknown']['name'] = line.split(':')[1].strip()
            client.disconnect()

        # This is the JSON file path to store the response from the Truecaller data.
        FILE_PATH = 'output/response.json'
        # Check if the file exists
        if os.path.exists(FILE_PATH):
            # Read existing JSON data from the file
            with open(FILE_PATH, 'r') as file:
                existing_data = json.load(file)
            # Update existing data with new data
            existing_data.append(extracted_data)
        else:
            existing_data = [extracted_data]  # Create a new list if the file doesn't exist

        # Write the updated JSON data back to the file
        with open(FILE_PATH, 'w') as file:
            json.dump(existing_data, file, indent=4)

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
