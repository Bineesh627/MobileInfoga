import phonenumbers
from time import sleep
from modules.telethon_bot import TelethonBot
from phonenumbers import carrier, geocoder, timezone

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
    def validate_phone_number(input_number):
        # Check if input is an integer
        if not input_number.isdigit():
            print("Please enter only integer digits.")
            return False

        # Check if the number has a valid length
        if len(input_number) <= 10:
            print("Phone number must be 10 digits long.")
            return False

        return True

        # Check if the number is valid
        if not phonenumbers.is_valid_number(parsed_number):
            print("Invalid phone number.")
            return

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
        self.phone_number = phonenumbers.parse(self.formatted_number)
        self.phone_number_national = phonenumbers.format_number(self.phone_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        self.phone_number_international = phonenumbers.format_number(self.phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        self.carrier = carrier.name_for_number(self.phone_number, 'en')
        self.time_zone = timezone.time_zones_for_number(self.phone_number)
        self.location = geocoder.description_for_number(self.phone_number, "en")
        self.country_name = geocoder.country_name_for_number(self.phone_number, "en")
        self.country_prefix = self.phone_number.country_code
        region_code = self.country_prefix
        self.country_code = phonenumbers.region_code_for_country_code(region_code)
        self.valid = phonenumbers.is_valid_number(self.phone_number)
        self.local_format = self.phone_number.national_number
    
    def run_telegram_bot(self):
        bot = TelethonBot()
        bot.message = self.formatted_number
        bot.run()
        return bot.process_data()
        
    def output(self):
        print()
        sleep(0.1)
        print(f"[!] Fetching Phone Number  : {self.formatted_number}")
        sleep(0.1)
        print(f"[+] Valid                  : {self.valid}")
        sleep(0.1)
        print(self.run_telegram_bot())
        sleep(0.1)
        print(f"[+] Country Prefix         : +{self.country_prefix}")
        sleep(0.1)
        print(f"[+] Country Code           : {self.country_code}")
        sleep(0.1)
        print(f"[+] Local Format           : {self.local_format}")
        sleep(0.1)
        print(f"[+] International Format   : {self.phone_number_international}")        
        sleep(0.1)
        print(f"[+] National Format        : {self.phone_number_national}")        
        sleep(0.1)
        print(f"[+] Line Type              : {self.get_line_type()}")
        sleep(0.1)
        print(f"[+] Time Zone              : {self.time_zone}")
        sleep(0.1)
        print(f"[+] Carrier                : {self.carrier}")
        sleep(0.1)
        print(f"[+] Country Name           : {self.country_name}")
        sleep(0.1)
        print(f"[+] Location               : {self.location}")
        print()
        
if __name__ == "__main__":
    program = OsintNumber()
    number = input("Enter the number without (+), space: ").strip()
    
    if program.validate_phone_number(number):
        # Assuming the country code is +1 for US
        program.formatted_number = "+" + number
        program.grab_data()
        program.output()
    else:
        print("Invalid phone number format.")
