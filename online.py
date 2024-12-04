import requests
import wikipedia
import pywhatkit as kit  # online tool
import webbrowser
import smtplib

from email.message import EmailMessage
from decouple import config
from pywhatkit.core.core import send_message

EMAIL = "Email Address"
PASSKEY= "Passkey from Google Account"

def find_my_ip():
    ip_address = requests.get('URL?format=json').json()
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
    browser_path = ""  # brave path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    webbrowser.register('brave', None, webbrowser.BackgroundBrowser(browser_path))
    webbrowser.get('brave').open_new_tab(url)

def send_email(receive_add, subject, message):
    try:
        email = EmailMessage() # Core Function
        email['To'] = receive_add
        email['Subject'] = subject
        email['From'] = EMAIL

        email.set_content(message)
        s = smtplib.SMTP("smtp.gmail.com",587)
        s.starttls()
        s.login(EMAIL, PASSKEY)
        s.send_message(email)
        s.close()
        return True

    except Exception as e:
        print(e)
        return False

def get_news():
    news_headline = []
    result = requests.get(f"URL&"
                          f"apiKey=API").json()
                          # change the country to us if it nz doesn't have news
    articles = result["articles"]
    for article in articles:
        news_headline.append(article["title"])
    return news_headline[:6]


