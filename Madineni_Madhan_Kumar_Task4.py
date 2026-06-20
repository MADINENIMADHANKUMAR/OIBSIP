import tkinter as tk
from tkinter import messagebox
import requests
from io import BytesIO
from PIL import Image, ImageTk
from datetime import datetime

API_KEY = "ecacf197fd96c72e216a23d9d4ee6758"

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("400x550")
        
        self.unit = "metric"
        self.symbol = "°C"
        
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)
        
        self.city_input = tk.Entry(top_frame, font=("Arial", 12))
        self.city_input.pack(side="left", padx=5)
        
        tk.Button(top_frame, text="Search", command=self.fetch_weather).pack(side="left")
        tk.Button(top_frame, text="Auto-Detect", command=self.auto_detect).pack(side="left", padx=5)

        self.unit_btn = tk.Button(root, text="Change to °F", command=self.change_unit)
        self.unit_btn.pack()
        
        self.city_lbl = tk.Label(root, font=("Arial", 18, "bold"))
        self.city_lbl.pack(pady=10)
        
        self.icon_lbl = tk.Label(root)
        self.icon_lbl.pack()
        
        self.temp_lbl = tk.Label(root, font=("Arial", 28, "bold"))
        self.temp_lbl.pack()
        
        self.desc_lbl = tk.Label(root, font=("Arial", 14))
        self.desc_lbl.pack()
        
        self.details_lbl = tk.Label(root, font=("Arial", 11))
        self.details_lbl.pack(pady=10)

        tk.Label(root, text="Forecast", font=("Arial", 12, "bold")).pack(pady=5)
        self.forecast_frame = tk.Frame(root)
        self.forecast_frame.pack()

    def change_unit(self):
        if self.unit == "metric":
            self.unit = "imperial"
            self.symbol = "°F"
            self.unit_btn.config(text="Change to °C")
        else:
            self.unit = "metric"
            self.symbol = "°C"
            self.unit_btn.config(text="Change to °F")
        
        if self.city_input.get():
            self.fetch_weather()

    def auto_detect(self):
        try:
            data = requests.get("https://ipinfo.io/json", timeout=5).json()
            if "city" in data:
                self.city_input.delete(0, tk.END)
                self.city_input.insert(0, data["city"])
                self.fetch_weather()
            else:
                messagebox.showerror("Error", "Could not find location")
        except:
            messagebox.showerror("Error", "Network error")

    def fetch_weather(self):
        city = self.city_input.get().strip()
        if not city:
            messagebox.showerror("Error", "Enter a city")
            return
            
        if API_KEY == "YOUR_OPENWEATHER_API_KEY":
            messagebox.showerror("Error", "API Key missing in code")
            return

        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={self.unit}"
            data = requests.get(url).json()
            
            if data.get("cod") != 200:
                messagebox.showerror("Error", "City not found")
                return
            
            self.city_lbl.config(text=f"{data['name']}, {data['sys']['country']}")
            self.temp_lbl.config(text=f"{data['main']['temp']}{self.symbol}")
            self.desc_lbl.config(text=data['weather'][0]['description'].title())
            
            speed = data['wind']['speed']
            wind_str = "m/s" if self.unit == "metric" else "mph"
            hum = data['main']['humidity']
            self.details_lbl.config(text=f"Humidity: {hum}% | Wind: {speed} {wind_str}")
            
            icon = data['weather'][0]['icon']
            img_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
            img_data = requests.get(img_url).content
            img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
            
            self.icon_lbl.config(image=img)
            self.icon_lbl.image = img

            self.update_forecast(city)

        except:
            messagebox.showerror("Error", "Failed to get weather")

    def update_forecast(self, city):
        for w in self.forecast_frame.winfo_children():
            w.destroy()

        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={self.unit}"
        data = requests.get(url).json()
        
        if str(data.get("cod")) != "200":
            return

        for item in data["list"][:3]:
            time_str = datetime.fromtimestamp(item["dt"]).strftime("%I %p")
            temp_str = f"{item['main']['temp']}{self.symbol}"
            desc_str = item["weather"][0]["main"]
            
            box = tk.Frame(self.forecast_frame, bd=1, relief="ridge", padx=10, pady=5)
            box.pack(side="left", padx=5)
            
            tk.Label(box, text=time_str, font=("Arial", 10, "bold")).pack()
            tk.Label(box, text=temp_str).pack()
            tk.Label(box, text=desc_str, font=("Arial", 9)).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()