from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    long_description = file.read()

setup(
    name='mobileinfoga',
    version='1.0.0',
    author='Bineesh',
    description='This tool gathers information from a phone number.',
    long_description=long_description,
    license="GNU",
    url='https://github.com/Bineesh627/MobileInfoga',
    packages=find_packages(),
    install_requires=[
        'phonenumbers',
        'requests',
        'telethon',
    ],
)
