import requests
import pyautogui
import pyttsx3
import speech_recognition as sr
import keyboard
import os
import imdb
import wolframalpha
import subprocess as sp
from datetime import datetime
from decouple import config
from random import choice
from conv import random_text
from online import (find_my_ip, search_on_google, search_on_wikipedia, get_news, #weather_forecast,
                    youtube_video, open_website, open_schoology, open_youtube, send_email)
from PIL import Image
from io import BytesIO


engine = pyttsx3.init('sapi5')  # Microsoft Speech API
engine.setProperty('volume', 1.3)  # volume of AI
engine.setProperty('rate', 215)  # speak rate of AI
voices = engine.getProperty('voices')  # includes the voice modules of py library
engine.setProperty('voice', voices[1].id)  # 1 for female and 0 for male voice
USER = config('USER')
HOSTNAME = config('BOT')

def speak(text):
    engine.say(text)
    engine.runAndWait()

# for greetings
def greet_me():
    hour = datetime.now().hour
    if (hour >= 6) and (hour < 12):
        speak(f"time") # Good morning {USER}
    elif (hour >= 12) and (hour <= 16):
        speak(f"time") # Good afternoon {USER}
    elif (hour >= 16) and (hour < 19):
        speak(f"time") # Good evening {USER}
    speak(f"testing") # I am {HOSTNAME}. How may I assist you, {USER}

listening = False

def start_listening():
    global listening
    listening = True
    print("Started Listening")

def pause_listening():
    global listening
    listening = False
    print("Stopped Listening")

keyboard.add_hotkey('ctrl+alt+k', start_listening)
keyboard.add_hotkey('ctrl+alt+p', pause_listening)

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1  # wait for user statement
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en')
        print(query)
        if "stop" not in query and "exit" not in query and "quit" not in query:
            speak(choice(random_text))
        else:
            hour = datetime.now().hour
            if hour >= 21 and hour < 6:
                speak("end") # Good night, take care!
            else:
                speak("end") # Have a good day!
            exit()

    except Exception:
        speak("repeat") # Sorry I couldn't understand. Could you please repeat that?
        query = 'None'
    return query


def get_weather(city):
    API_KEY = "a890a280a26ee308371d266bdf1b63fd"  # OpenWeatherMap API key
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

    try:
        # Make API request
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"  # To get temperature in Celsius
        }
        response = requests.get(BASE_URL, params=params)
        weather_data = response.json()

        if weather_data["cod"] != 200:
            speak("I couldn't fetch the weather for that location. Please try again.")
            return None

        # Parse Weather Data
        temperature = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        description = weather_data["weather"][0]["description"].capitalize()

        # Generate Weather Report
        weather_report = (
            f"The current temperature in {city} is {temperature}°C. "
            f"\nIt feels like {feels_like}°C. "
            f"\nThe weather is described as {description}."
        )
        speak(weather_report)
        print(weather_report)
        return weather_report
    except Exception as e:
        speak("Something went wrong while fetching the weather.")
        print("Error:", e)
        return None


def fetch_movie_info():
    try:
        # Initialize IMDb API
        movies_db = imdb.IMDb()
        speak("Please tell me the name of the movie.")
        print("Listening for movie name...")
        movie_name = take_command()

        if not movie_name:
            speak("I couldn't hear the movie name. Please try again.")
            return None

        # Search for the movie
        speak(f"Searching for {movie_name}...")
        movies = movies_db.search_movie(movie_name)

        if not movies:
            speak("No movies found with that name. Please try again.")
            return None

        # List top 5 search results
        speak("I found these movies. Please select one.")
        for idx, movie in enumerate(movies[:5]):
            title = movie.get('title', 'Unknown title')
            year = movie.get('year', 'Unknown year')
            speak(f"{idx + 1}. {title}, released in {year}")

        # Ask the user to choose a movie
        speak("Please tell me the number of the movie you are interested in.")
        print("Waiting for choice...")
        choice = input("Please choose a number according to the movies: ")

        if not choice.isdigit() or int(choice) not in range(1, len(movies[:5]) + 1):
            speak("Invalid choice. Please try again.")
            return None

        selected_movie = movies[int(choice) - 1]
        movie_id = selected_movie.getID()
        movie_info = movies_db.get_movie(movie_id)

        # Extract details
        title = movie_info.get('title', 'Unknown title')
        year = movie_info.get('year', 'Unknown year')
        rating = movie_info.get('rating', 'No rating available')
        genres = ", ".join(movie_info.get('genres', []))
        directors = ", ".join(director['name'] for director in movie_info.get('directors', []))
        plot = movie_info.get('plot outline', 'Plot summary not available')
        cast = ", ".join(actor['name'] for actor in movie_info.get('cast', [])[:5]) or "No cast information available"

        # Speak and Print Details
        movie_details = (
            f"{title} was released in {year}. It has an IMDb rating of {rating}. "
            f"The genres are {genres}. Directed by {directors}. The main cast includes {cast}. "
            f"Here is the plot summary: {plot}"
        )
        speak(movie_details)
        print(movie_details)
        return movie_details

    except Exception as e:
        speak("An error occurred while fetching the movie details.")
        print("Error:", e)
        return None


def calculate_or_plot(query):
    # WolframAlpha App ID
    app_math_id = "YK8TKJ-HY2WL44XQP"
    client = wolframalpha.Client(app_math_id)

    # Determine if the query is for a graph or calculation
    if "draw" in query or "plot" in query:
        query = query.replace("draw", "").replace("plot", "").strip()
        try:
            # WolframAlpha Simple API for plots
            url = f"http://api.wolframalpha.com/v1/simple?appid={app_math_id}&i={query}"
            response = requests.get(url)

            if response.status_code == 200:
                # Display the plot image
                image = Image.open(BytesIO(response.content))
                image.show()
                speak("Here's the graph.")
                print("Graph displayed successfully.")
            else:
                speak("I'm sorry, I couldn't generate the plot. Please try again.")
                print(f"Error: Received status code {response.status_code} from WolframAlpha.")
        except Exception as e:
            speak("There was an error retrieving the graph. Please try again.")
            print("Graph Error:", e)
    else:
        try:
            # Query WolframAlpha for calculations
            result = client.query(query)

            # Extract the answer
            answer = next(result.results).text
            speak(f"The answer is: {answer}")
            print(f"The answer is: {answer}")
        except StopIteration:
            # Handle cases where no result is found
            speak("I couldn't find an answer to your query. Please try again.")
            print("No results found.")
        except Exception as e:
            # General error handling
            speak("There was an error processing your query. Please try again.")
            print("Calculation Error:", e)

if __name__ == '__main__':
    greet_me()
    while True:
        if listening:
            query = take_command().lower()
            if "how are you" in query:
                speak("I am absolutely fine! What about you?")

            elif "open command prompt" in query:
                speak("opening command prompt")
                os.system('start cmd')

            elif "close command prompt" in query:
                speak("Closing Command Prompt")
                os.system("taskkill /F /IM cmd.exe")

            elif "open camera" in query:
                speak("opening camera")
                sp.run('start microsoft.windows.camera:', shell=True)
                if "take a photo" in query:
                    speak("taking photo")
                    sp.run('start microsoft.windows.camera:', shell=True)
                    pyautogui.press('space')

            elif "close camera" in query:
                speak("Closing Camera")
                os.system("taskkill /F /IM WindowsCamera.exe")

            elif "open notepad" in query:
                speak("opening notepad")
                notepad_path = "C:\\mdmah\\New\\AppData\\Local\\Microsoft\\WindowsApps\\notepad.exe"
                os.startfile(notepad_path)

            elif "close notepad" in query:
                speak("Closing Notepad")
                sp.run(["taskkill", "/F", "/IM", "notepad.exe"])

            elif "open discord" in query:
                speak("opening discord")
                discord_path = "C:\\Users\\mdmah\\AppData\\Local\\Discord\\app-1.0.9168\\Discord.exe"
                os.startfile(discord_path)

            elif "close discord" in query:
                speak("Closing Discord")
                sp.run(["taskkill", "/F", "/IM", "Discord.exe"])

            elif "open vs code" in query:
                speak("opening VS code")
                vscode_path = "C:\\Users\\mdmah\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
                os.startfile(vscode_path)

            elif "close vs code" in query:
                speak("Closing VS Code")
                sp.run(["taskkill", "/F", "/IM", "Code.exe"])

            elif "open pycharm" in query:
                speak("opening pycharm")
                pycharm_path = "C:\\Program Files\\JetBrains\\PyCharm Community Edition 2024.2.4\\bin\\pycharm64.exe"
                os.startfile(pycharm_path)

            elif "close pycharm" in query:
                speak("Closing pycharm")
                sp.run(["taskkill", "/F", "/IM", "pycharm64.exe"])

            elif "open brave" in query:
                speak("opening brave")
                brave_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
                os.startfile(brave_path)

            elif "close brave" in query:
                speak("Closing Brave")
                sp.run(["taskkill", "/F", "/IM", "brave.exe"])

            elif "open chrome" in query:
                speak("opening chrome")
                chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                os.startfile(chrome_path)

            elif "close chrome" in query:
                speak("Closing Chrome")
                sp.run(["taskkill", "/F", "/IM", "chrome.exe"])

            elif "ip address" in query:
                ip_address = find_my_ip()
                speak(f"Your ip address is {ip_address}")
                print(f"Your IP address is {ip_address}")

            elif "play in youtube" in query:
                speak("What do you want to play on youtube?")
                video = take_command().lower()
                youtube_video(video)

            elif "open google" in query:
                speak("What do you want to search on google?")
                text = take_command().lower()
                if "search" in text:
                    url = text.split("search")[-1].strip()
                    search_on_google(url)
                    speak("Searching " + url)

            elif "open wikipedia" in query:
                speak("What do you want to wiki?")
                search = take_command().lower()
                results = search_on_wikipedia(search)
                speak(f"According to wikipedia, {results}")
                speak("I am printing the results out")
                print(results)

            elif "open schoology" in query:
                speak("opening schoology")
                open_schoology("https://schoology.burnside.school.nz/home")

            elif "open youtube" in query:
                speak("opening youtube")
                open_youtube("https://youtube.com")

            elif "open a website" in query or "open website" in query or "open another website" in query:
                speak("What website would you like to open?")
                text = take_command().lower()
                if "slash" in text:
                    text = text.replace("slash", "/")
                    # Check if a common domain suffix is already present; if not, add ".com"
                if not (text.endswith(".com") or text.endswith(".net") or text.endswith(".org") or text.endswith(
                        ".edu")):
                    text += ".com"
                if "open" in text:
                    url = text.split("open")[-1].strip()
                    open_website(url)
                    speak("Opening " + url)
                else:
                    speak("I'm sorry, I didn't understand your request.")

            elif "send an email" in query:
                speak("Who do you want to email to?. Please enter the email address")
                receiver_add = input("Email address:")
                speak("What should be the subject?")
                subject = take_command().capitalize()
                speak("What is the message ?")
                message = take_command().capitalize()
                if send_email(receiver_add, subject, message):
                    speak("I have sent the email")
                    print("I have sent the email")
                else:
                    speak("something went wrong! Please check the error log")

            elif "what's the news" in query:
                speak(f"I am reading out the latest headlines of today")
                speak(get_news())
                speak("I am printing it on screen")
                print(*get_news(), sep='\n')

            elif "weather" in query:
                speak("Please tell me the name of the city.")
                city = take_command()
                if city:
                    get_weather(city)
                else:
                    speak("I couldn't understand the city name. Please try again.")

            elif "movie" in query:
                fetch_movie_info()

            elif "calculate" in query or "draw" in query or "plot" in query:
                speak("Please tell me what you want to calculate or draw.")
                user_query = take_command()
                if user_query:
                    calculate_or_plot(user_query)
                else:
                    speak("I couldn't understand your query. Please try again.")

            elif "what is" in query or "who is" in query or "which is" in query:
                app_ans_id = "YK8TKJ-AAQH9PXPQJ"
                client = wolframalpha.Client(app_ans_id)
                try:
                    ind = query.lower().index("what is") if "what is" in query.lower() else \
                          query.lower().index('who is') if 'who is' in query.lower() else \
                          query.lower().index('which is') if 'which is' in query.lower() else None

                    if ind is not None:
                        text = query.split()[ind + 2:]
                        res = client.query(" ".join(text))
                        ans_txt = next(res.results).text
                        speak("The answer is " + ans_txt)
                        print("The answer is " + ans_txt)
                    else:
                        speak("I couldn't find that. Please try again.")
                except StopIteration:
                    speak("I couldn't find that. Please try again.")

            