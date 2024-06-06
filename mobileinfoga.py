from telethon import events, sync
from telethon.tl.types import InputPeerUser
from config import API_HASH, API_ID, PHONE
import os
import json
import re
import asyncio
import phonenumbers
from time import sleep
from phonenumbers import carrier, geocoder, timezone

class DataConverter:
    def __init__(self, text_data):
        self.lines = text_data.split('\n')
        self.data = {
            "Number": "",
            "Country": "",
            "TrueCaller": {},
            "Unknown": {},
            "Unknown2": {},
            "WhatsApp": "",
            "Telegram": ""
        }

    def clean_line(self, line):
        line = re.sub(r"[*`\ufe0f]", '', line)
        return line.strip()

    def extract_links(self, line):
        # Extract contents within [] and ()
        links = re.findall(r'\[(.*?)\]\((.*?)\)', line)
        link_strings = [f"{text}: {url}" for text, url in links]
        return link_strings

    def parse_lines(self):
        current_section = None
        for line in self.lines:
            line = self.clean_line(line)
            links = self.extract_links(line)
            if line.startswith("Number:"):
                self.data["Number"] = line.split(": ", 1)[1]
            elif line.startswith("Country:"):
                self.data["Country"] = line.split(": ", 1)[1]
            elif line.startswith("🔍 TrueCaller Says:"):
                current_section = "TrueCaller"
            elif line.startswith("🔍 Unknown Says:"):
                current_section = "Unknown"
            elif line.startswith("🔍 Unknown2 Says:"):
                current_section = "Unknown2"
            elif current_section and ": " in line:
                key, value = line.split(": ", 1)
                self.data[current_section][key] = value
            for link in links:
                if link.startswith("WhatsApp:"):
                    self.data["WhatsApp"] = link.split(": ", 1)[1]
                elif link.startswith("Telegram:"):
                    self.data["Telegram"] = link.split(": ", 1)[1]

    def convert_to_json(self):
        return json.dumps(self.data, indent=4)

    def process(self):
        self.parse_lines()
        return self.convert_to_json()
        
class TelethonBot:
    def __init__(self):
        self.client = None
        self.username = '@TrueCaller1Bot'
        self.user_entity = None
        self.message = None
        self.message_text = None

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
        if event.is_reply:
            self.message_text = event.message.text
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
                
class OsintNumber:
    def __init__(self):
        self.formatted_number = None
        self.phone_number = None
        self.phone_number_national = None
        self.phone_number_international = None
        self.carrier = None
        self.country_prefix = None
        self.local_format = None
        self.time_zone = None
        self.country_name = None
        self.country_code = None
        self.location = None
        self.valid = False

    @staticmethod
    def validate_phone_number(input_number):  # Corrected the static method signature
        try:
            parsed_number = phonenumbers.parse(input_number, None)
            return phonenumbers.is_possible_number(parsed_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            print("Invalid phone number format.")
            return False

    def get_line_type(self):
        parsed_number = phonenumbers.parse(self.formatted_number)
        number_type = phonenumbers.number_type(parsed_number)
    
        if number_type == phonenumbers.PhoneNumberType.FIXED_LINE:
            return "Fixed Line"
        elif number_type == phonenumbers.PhoneNumberType.MOBILE:
            return "Mobile"
        elif number_type == phonenumbers.PhoneNumberType.TOLL_FREE:
            return "Toll Free"
        elif number_type == phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE:
            return "Fixed Line or Mobile"
        elif number_type == phonenumbers.PhoneNumberType.PREMIUM_RATE:
            return "Premium Rate"
        elif number_type == phonenumbers.PhoneNumberType.SHARED_COST:
            return "Shared Cost"
        elif number_type == phonenumbers.PhoneNumberType.VOIP:
            return "VoIP"
        elif number_type == phonenumbers.PhoneNumberType.PERSONAL_NUMBER:
            return "Personal Number"
        elif number_type == phonenumbers.PhoneNumberType.PAGER:
            return "Pager"
        elif number_type == phonenumbers.PhoneNumberType.UAN:
            return "Universal Access Number"
        else:
            return "Unknown"
        
    def grab_data(self):
        try:
            self.phone_number = phonenumbers.parse(self.formatted_number)
            self.phone_number_national = phonenumbers.format_number(self.phone_number, phonenumbers.PhoneNumberFormat.NATIONAL)
            self.phone_number_international = phonenumbers.format_number(self.phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            self.carrier = carrier.name_for_number(self.phone_number, 'en')
            self.time_zone = timezone.time_zones_for_number(self.phone_number)
            self.location = geocoder.description_for_number(self.phone_number, "en")
            self.country_name = geocoder.country_name_for_number(self.phone_number, "en")
            self.country_prefix = self.phone_number.country_code
            self.country_code = phonenumbers.region_code_for_country_code(self.country_prefix)
            self.valid = phonenumbers.is_valid_number(self.phone_number)
            self.local_format = self.phone_number.national_number
        except phonenumbers.phonenumberutil.NumberParseException as e:
            print(f"Error parsing phone number: {e}")
            self.valid = False

    def output(self):
        data = {
            "Fetching Phone Number": self.formatted_number,
            "Valid": self.valid,
            "Country Prefix": f"+{self.country_prefix}",
            "Country Code": self.country_code,
            "Local Format": self.local_format,
            "International Format": self.phone_number_international,
            "National Format": self.phone_number_national,
            "Line Type": self.get_line_type(),
            "Time Zone": self.time_zone,
            "Carrier": self.carrier,
            "Country Name": self.country_name,
            "Location": self.location
        }
        
        json_output = json.dumps(data, indent=4)
        return json_output
        
def Formating_data(osintData, telegramData):
    print(osintData)
    print(telegramData)
    
def convert_data(text_data):
    converter = DataConverter(text_data)
    return converter.process()
       
def run_telegram_bot(number):
    bot = TelethonBot()
    bot.message = number
    bot.run()
    text_data = bot.message_text
    convert = convert_data(text_data)
    return convert
    
def main():
    program = OsintNumber()
    number = input("Enter the number with country code (e.g., +1234567890): ").strip()

    if program.validate_phone_number(number):
        program.formatted_number = number
        program.grab_data()
        if program.valid:
            number = program.formatted_number
            telegramData = run_telegram_bot(number)
            osintData = program.output()
            Formating_data(osintData, telegramData)
        else:
            print("Invalid phone number.")
    else:
        print("Invalid phone number format.")


if __name__ == '__main__':
    main()