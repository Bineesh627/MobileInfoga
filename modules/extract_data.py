from modules.telethon_bot import TelethonBot
import json
import re

class DataConverter:
    def __init__(self):
        self.lines = self.text_data.split('\n')
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
        print(line)
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

    def save_json(self, output_file):
        json_data = self.convert_to_json()
        with open(output_file, 'w') as json_file:
            json_file.write(json_data)

    def bot_process(self, number):
        bot = TelethonBot()
        bot.message = number
        bot.run()
        self.text_data = bot.message_text

    def process(self, output_file):
        self.parse_lines()
        self.save_json(output_file)
