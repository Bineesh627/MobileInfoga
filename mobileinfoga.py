from telethon import events, sync
from telethon.tl.types import InputPeerUser
from config import API_HASH, API_ID, PHONE
import os
import json
import re
import phonenumbers
import mobile_codes
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
            "fetching_number": self.formatted_number,
            "valid": self.valid,
            "country_prefix": f"+{self.country_prefix}",
            "country_code": self.country_code,
            "local_format": self.local_format,
            "international_format": self.phone_number_international,
            "national_format": self.phone_number_national,
            "line_type": self.get_line_type(),
            "time_zone": self.time_zone,
            "carrier": self.carrier,
            "country_name": self.country_name,
            "location": self.location
        }

        json_output = json.dumps(data, indent=4)
        return json_output

def Formating_data(osintData, telegramData):
    try:
        if isinstance(telegramData, str):
            telegramData = json.loads(telegramData)
        if isinstance(osintData, str):
            osintData = json.loads(osintData)
        if not isinstance(telegramData, dict):
            raise ValueError("telegramData must be a dictionary after parsing JSON.")
        if not isinstance(osintData, dict):
            raise ValueError("osintData must be a dictionary after parsing JSON.")
        fetching_number = osintData['fetching_number']
        valid = osintData['valid']
        truecallerName = telegramData.get('TrueCaller', {}).get('Name')
        leaked_data1 = telegramData.get('Unknown', {}).get('Name')
        leaked_data2 = telegramData.get('Unknown2', {}).get('Name')
        country_prefix = osintData['country_prefix']
        country_code = osintData['country_code']
        local_format = osintData['local_format']
        international_format = osintData['international_format']
        national_format = osintData['national_format']
        line_type = osintData['line_type']
        time_zone = osintData['time_zone']
        carrier = osintData['carrier']
        location = telegramData.get('TrueCaller', {}).get('Location')
        whatsapp = telegramData.get('WhatsApp')
        telegram = telegramData.get('Telegram')

        mcc, mnc = mncmcc(country_code, location, carrier)
        plmn = EncodePLMN(mcc, mnc)

        print("Fetcing Phone Number : ", fetching_number)
        print("valid                : ", valid)
        print("Truecaller Name      : ", truecallerName)
        print("Leaked Name          : ", leaked_data1)
        print("Leaked Name          : ", leaked_data2)
        print("Country Prefix       : ", country_prefix)
        print("Country Code         : ", country_code)
        print("Local Format         : ", local_format)
        print("International Format : ", international_format)
        print("National Format      : ", national_format)
        print("Line Type            : ", line_type)
        print("Time Zone            : ", time_zone)
        print("Carrier              : ", carrier)
        print("Location             : ", location)
        print("WhatsApp Link        : ", whatsapp)
        print("Telegram Link        : ", telegram)
        print("MCC                  : ", mcc)
        print("MNC                  : ", mnc)
        print("PLMN Identifier      : ", plmn)

    except json.JSONDecodeError as e:
        print(f"Key error: {e}")
    except KeyError as e:
        print(f"Type error: {e}")
    except ValueError as e:
        print(f"Value error: {e}")

def Reverse(string):
    return string[::-1]

def EncodePLMN(mcc, mnc):
    if mcc is None or mnc is None:
        raise ValueError("MCC and MNC must not be None")
    
    mcc_reversed = Reverse(mcc)
    mnc_reversed = Reverse(mnc)

    plmn = list('XXXXXX')
    if len(mnc) == 2:
        plmn[0] = mcc_reversed[1]
        plmn[1] = mcc_reversed[2]
        plmn[2] = "f"
        plmn[3] = mcc_reversed[0]
        plmn[4] = mnc_reversed[0]
        plmn[5] = mnc_reversed[1]
    else:
        plmn[0] = mcc_reversed[1]
        plmn[1] = mcc_reversed[2]
        plmn[2] = mnc_reversed[0]
        plmn[3] = mcc_reversed[0]
        plmn[4] = mnc_reversed[1]
        plmn[5] = mnc_reversed[2]
    
    encoded_plmn = ''.join(plmn)
    return encoded_plmn

def mncmcc(country_code, location, carrier):
    country_code = country_code.strip().upper()
    location = location.strip().lower()
    carrier = carrier.strip().lower()

    info = mobile_codes.alpha2(country_code)
    if not info:
        raise ValueError(f"No information found for country code: {country_code}")

    mcc_list = info.mcc

    mcc_number = None
    mnc_number = None
    for mcc in mcc_list:
        operators = mobile_codes.operators(mcc)
        for operator in operators:
            if location in operator.operator.lower() and carrier in operator.brand.lower():
                mcc_number = operator.mcc
                mnc_number = operator.mnc
                
                return mcc_number, mnc_number
    return None, None

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
