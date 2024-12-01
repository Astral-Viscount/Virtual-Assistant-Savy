import requests
import wikipedia
import pywhatkit as kit  # online tool
import webbrowser
import smtplib

from email.message import EmailMessage
from decouple import config


Email = "Email Address"
Passkey= "Passkey from Google Account"

def find_my_ip():
    ip_address = requests.get('https://api.ipify.org?format=json').json()
    return ip_address["ip"]

def search_on_wikipedia(query):
    results = wikipedia.summary(query, sentences=2)
    return results

def search_on_google(query):
    kit.search(query)

def youtube_video(video):
    kit.playonyt(video)

def open_schoology(url):
    webbrowser.open(url)

def open_youtube(url):
    webbrowser.open(url)

def open_website(url):
    browser_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"  # brave path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    webbrowser.register('brave', None, webbrowser.BackgroundBrowser(browser_path))
    webbrowser.get('brave').open_new_tab(url)

