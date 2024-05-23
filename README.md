---

# Phone Number Information Gatherer

Welcome to the Phone Number Information Gatherer project! This tool aims to provide comprehensive information about a given mobile phone number. By inputting a phone number, users can access valuable insights such as the Truecaller name associated with the number, any leaked names, country prefix, country code, local, international, and national formats, line type (e.g., mobile), time zone, carrier information (e.g., Airtel), and country name. 

## Features

- **Comprehensive Information**: Obtain detailed information about a phone number, including Truecaller name, country details, line type, carrier, and more.
- **Easy to Use**: Simple and intuitive interface for entering phone numbers and retrieving information.
- **Fast and Efficient**: Quickly fetch information about a phone number without hassle.

## Usage

To use the Phone Number Information Gatherer, simply input the desired phone number and wait for the tool to fetch the information. Here's a sample command and its output:

```
python mobileinfoga.py
```

Output:

```
[!] Fetching Phone Number: +911234567890 
[+] Valid: True 
[+] Truecaller Name: hello 
[+] Leaked Name: Hello 
[+] Country Prefix: +91 
[+] Country Code: IN 
[+] Local Format: 1234567890 
[+] International Format: +91 1234567890 
[+] National Format: 0123456789 
[+] Line Type: Mobile 
[+] Time Zone: ('Asia/Calcutta',) 
[+] Carrier: Airtel 
[+] Country Name: India 
[+] Location: India
```

## Installation

To install the Phone Number Information Gatherer, simply clone the repository and install the required dependencies:

```
git clone https://github.com/Bineesh627/MobileInfoga.git
cd MobileInfoga
pip install -r requirements.txt
```

## Contribution

Contributions are welcome! If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

---