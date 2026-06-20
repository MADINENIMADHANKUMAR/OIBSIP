import speech_recognition as sr
import pyttsx3
import datetime
import requests
import pywhatkit
import webbrowser
import os
import psutil
import pyautogui
import speedtest
import socket
import subprocess
import smtplib
from email.message import EmailMessage
from urllib.parse import quote
import google.generativeai as genai
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
def speak(text):
    try:
        print("\nAssistant:", text)
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        if len(voices) > 2:
            engine.setProperty("voice", voices[2].id)
        elif len(voices) > 0:
            engine.setProperty("voice", voices[0].id)      
        engine.setProperty("rate", 160)
        engine.setProperty("volume", 1.0)
        engine.say(str(text))
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print("Speech Error:", e)
def speak_long(text):
    sentences = text.split(". ")
    for sentence in sentences[:3]:
        sentence = sentence.strip()
        if sentence:
            speak(sentence)
def listen():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not understand.")
        return ""
    except sr.WaitTimeoutError:
        return ""
    except Exception as e:
        print("Error:", e)
        return ""
def get_user_name():
    speak("Hello. What is your name?")
    while True:
        name = listen()
        if name != "":
            name = name.title()
            speak(f"Nice to meet you {name}")
            return name
def tell_time():
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The time is {current_time}")
def tell_date():
    current_date = datetime.datetime.now().strftime("%d %B %Y")
    speak(f"Today's date is {current_date}")
def search_person(query):
    try:
        query = quote(query)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        headers = {"User-Agent": "VoiceAssistant/1.0"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            speak("Information not found.")
            return
        data = response.json()
        if "extract" in data:
            result = data["extract"]
            print("\nWikipedia Response:")
            print(result)
            speak("Here is what I found.")
            speak_long(result)
        else:
            speak("No information found.")
    except Exception as e:
        print("Wikipedia Error:", e)
        speak("Error searching information.")
def get_weather(city):
    if OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY":
        speak("Please set your OpenWeather API key first.")
        return
    if not city:
        speak("Please tell me the city name.")
        return
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            speak(f"The temperature in {city} is {temp} degrees Celsius with {desc}")
        else:
            print(f"\n[Debug] OpenWeather API Error ({response.status_code}):", data)
            speak("City not found or API error.")
    except Exception as e:
        print("Weather Error:", e)
        speak("Error fetching weather.")
def open_notepad():
    try:
        os.startfile("notepad.exe")
    except Exception:
        speak("Failed to open Notepad.")
def open_calculator():
    try:
        os.system("calc")
    except Exception:
        speak("Failed to open Calculator.")
def save_reminder(text):
    with open("reminders.txt", "a") as file:
        file.write(text + "\n")
    speak("Reminder saved")
def read_reminders():
    try:
        with open("reminders.txt", "r") as file:
            data = file.read()
            if data.strip():
                speak(data)
            else:
                speak("No reminders found")
    except FileNotFoundError:
        speak("No reminders found")
def battery_status():
    battery = psutil.sensors_battery()
    if battery:
        speak(f"Battery percentage is {battery.percent}")
    else:
        speak("Battery status unavailable.")
def screenshot():
    img = pyautogui.screenshot()
    img.save("screenshot.png")
    speak("Screenshot captured")
def check_speed():
    speak("Checking speed, this may take a moment.")
    try:
        st = speedtest.Speedtest()
        download = round(st.download() / 1000000, 2)
        speak(f"Download speed is {download} megabits per second")
    except Exception as e:
        print("Speedtest Error:", e)
        speak("Failed to check internet speed.")
def system_status():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    speak(f"CPU usage is {cpu} percent and RAM usage is {ram} percent")
def open_google():
    webbrowser.open("https://www.google.com")
    speak("Opening Google")
def open_youtube():
    webbrowser.open("https://www.youtube.com")
    speak("Opening YouTube")
def open_gmail():
    webbrowser.open("https://mail.google.com")
    speak("Opening Gmail")
def dns_lookup(domain):
    try:
        ip = socket.gethostbyname(domain)
        speak(f"The IP address of {domain} is {ip}")
    except socket.gaierror:
        speak(f"Could not resolve the IP for {domain}")
def ping_host(host):
    speak(f"Pinging {host}")
    try:
        subprocess.run(["ping", host, "-n", "4"], capture_output=True, text=True)
        speak("Ping completed")
    except Exception as e:
        print("Ping error:", e)
def ask_ai(question):
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        speak("Please set your Gemini API key first.")
        return
    try:
        response = model.generate_content(question)
        answer = response.text
        print("\nAI Response:")
        print(answer)
        speak(answer[:500])
    except Exception as e:
        print("AI Error:", e)
        speak("I am unable to connect to the AI service.")
def send_email():
    if EMAIL_ADDRESS == "your_email@gmail.com":
        speak("Please configure your email credentials in the code first.")
        return
    speak("Who should I send the email to? Please type it in the console to avoid spelling errors.")
    recipient = input("Enter recipient email: ")
    speak("What should the subject be?")
    subject = listen()
    speak("What is the message?")
    message = listen()
    if not recipient or not message:
        speak("Email cancelled due to missing information.")
        return
    try:
        msg = EmailMessage()
        msg.set_content(message)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        speak("Email has been sent successfully.")
    except Exception as e:
        print("Email Error:", e)
        speak("Failed to send email. Check your app password and settings.")
def control_smart_home(command):
    if "on" in command:
        speak("Turning on the smart lights.")
        print("[Simulated] Smart Home: Lights ON")
    elif "off" in command:
        speak("Turning off the smart lights.")
        print("[Simulated] Smart Home: Lights OFF")
    else:
        speak("I'm not sure what you want me to do with the smart home devices.")
if __name__ == "__main__":
    speak("Voice Assistant Started")
    USER_NAME = get_user_name()
    while True:
        command = listen()
        if command == "":
            continue
        if "hello" in command:
            speak(f"Hello {USER_NAME}. How can I help you?")
        elif "time" in command:
            tell_time()
        elif "date" in command:
            tell_date()
        elif "open google" in command:
            open_google()
        elif "open youtube" in command:
            open_youtube()
        elif "open gmail" in command:
            open_gmail()
        elif "send email" in command:
            send_email()
        elif "lights on" in command or "turn on the lights" in command:
            control_smart_home("on")
        elif "lights off" in command or "turn off the lights" in command:
            control_smart_home("off")
        elif "search" in command:
            query = command.replace("search", "").strip()
            if query:
                speak(f"Searching {query}")
                pywhatkit.search(query)
        elif "who is" in command:
            query = command.replace("who is", "").strip()
            search_person(query)
        elif "what is" in command:
            query = command.replace("what is", "").strip()
            search_person(query)
        elif "weather in" in command:
            city = command.replace("weather in", "").strip()
            get_weather(city)
        elif "open notepad" in command:
            speak("Opening Notepad")
            open_notepad()
        elif "open calculator" in command:
            speak("Opening Calculator")
            open_calculator()
        elif "open vscode" in command:
            os.system("code")
        elif "open chrome" in command:
            try:
                os.startfile(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
            except Exception:
                speak("Chrome not found at the specified path.")
        elif "play" in command:
            song = command.replace("play", "").strip()
            speak(f"Playing {song}")
            pywhatkit.playonyt(song)
        elif "remember" in command:
            reminder = command.replace("remember", "").strip()
            save_reminder(reminder)
        elif "show reminders" in command:
            read_reminders()
        elif "battery" in command:
            battery_status()
        elif "internet speed" in command:
            check_speed()
        elif "take screenshot" in command:
            screenshot()
        elif "system status" in command:
            system_status()
        elif "ip address of" in command:
            domain = command.replace("ip address of", "").strip()
            dns_lookup(domain)
        elif "ping" in command:
            host = command.replace("ping", "").strip()
            ping_host(host)
        elif "stop" in command or "exit" in command or "goodbye" in command:
            speak("Goodbye. Have a nice day.")
            break
        elif len(command.split()) <= 3:
            search_person(command)
        else:
            ask_ai(command)