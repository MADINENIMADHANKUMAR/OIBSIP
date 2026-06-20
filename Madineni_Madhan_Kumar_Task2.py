import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
def setup_database():
    conn = sqlite3.connect("bmi_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            bmi REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
class BMICalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced BMI Calculator")
        self.root.geometry("450x500")
        self.root.configure(padx=20, pady=20)
        self.root.resizable(False, False)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, font=('Helvetica', 10, 'bold'))
        style.configure("TLabel", font=('Helvetica', 11))
        title_label = ttk.Label(self.root, text="BMI Tracker Pro", font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        input_frame = ttk.LabelFrame(self.root, text="Enter Your Details", padding=(15, 10))
        input_frame.pack(fill="x", pady=10)
        ttk.Label(input_frame, text="User Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.name_var, width=25).grid(row=0, column=1, pady=5, padx=10)
        ttk.Label(input_frame, text="Weight (kg):").grid(row=1, column=0, sticky="w", pady=5)
        self.weight_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.weight_var, width=25).grid(row=1, column=1, pady=5, padx=10)
        ttk.Label(input_frame, text="Height (cm):").grid(row=2, column=0, sticky="w", pady=5)
        self.height_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.height_var, width=25).grid(row=2, column=1, pady=5, padx=10)
        calc_btn = ttk.Button(self.root, text="Calculate & Save BMI", command=self.calculate_bmi)
        calc_btn.pack(fill="x", pady=(15, 5))
        self.result_frame = ttk.Frame(self.root)
        self.result_frame.pack(fill="x", pady=10)
        self.bmi_label = ttk.Label(self.result_frame, text="BMI: --", font=('Helvetica', 14, 'bold'))
        self.bmi_label.pack()
        self.category_label = ttk.Label(self.result_frame, text="Category: --", font=('Helvetica', 12))
        self.category_label.pack()
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", pady=20)
        history_btn = ttk.Button(action_frame, text="View History", command=self.view_history)
        history_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        plot_btn = ttk.Button(action_frame, text="Show BMI Trend", command=self.show_trend)
        plot_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))
    def calculate_bmi(self):
        name = self.name_var.get().strip()
        weight_str = self.weight_var.get().strip()
        height_str = self.height_var.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Please enter a User Name.")
            return
        try:
            weight = float(weight_str)
            height_cm = float(height_str)
            if weight <= 0 or height_cm <= 0:
                raise ValueError("Values must be positive.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for weight and height.")
            return
        height_m = height_cm / 100
        bmi = round(weight / (height_m ** 2), 2)
        if bmi < 18.5:
            category = "Underweight"
            color = "blue"
        elif 18.5 <= bmi <= 24.9:
            category = "Normal weight"
            color = "green"
        elif 25.0 <= bmi <= 29.9:
            category = "Overweight"
            color = "orange"
        else:
            category = "Obese"
            color = "red"
        self.bmi_label.config(text=f"BMI: {bmi}")
        self.category_label.config(text=f"Category: {category}", foreground=color)
        self.save_to_database(name, weight, height_cm, bmi, category)
        messagebox.showinfo("Success", f"BMI for {name} calculated and saved successfully!")
    def save_to_database(self, name, weight, height, bmi, category):
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect("bmi_database.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_history (name, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name.title(), weight, height, bmi, category, current_date))
        conn.commit()
        conn.close()
    def view_history(self):
        name = self.name_var.get().strip().title()
        if not name:
            messagebox.showwarning("Warning", "Please enter a User Name to view history.")
            return
        conn = sqlite3.connect("bmi_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT date, weight, height, bmi, category FROM user_history WHERE name=?", (name,))
        records = cursor.fetchall()
        conn.close()
        if not records:
            messagebox.showinfo("No Data", f"No historical data found for '{name}'.")
            return
        history_win = tk.Toplevel(self.root)
        history_win.title(f"{name}'s BMI History")
        history_win.geometry("550x300")
        columns = ("Date", "Weight (kg)", "Height (cm)", "BMI", "Category")
        tree = ttk.Treeview(history_win, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        for row in records:
            tree.insert("", "end", values=row)
    def show_trend(self):
        name = self.name_var.get().strip().title()
        if not name:
            messagebox.showwarning("Warning", "Please enter a User Name to view trends.")
            return
        conn = sqlite3.connect("bmi_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT date, bmi FROM user_history WHERE name=? ORDER BY id", (name,))
        records = cursor.fetchall()
        conn.close()
        if len(records) < 2:
            messagebox.showinfo("Not Enough Data", "You need at least 2 saved records to plot a trend.")
            return
        dates = [row[0].split(" ")[0] for row in records]
        bmis = [row[1] for row in records]
        plot_win = tk.Toplevel(self.root)
        plot_win.title(f"{name}'s BMI Trend")
        plot_win.geometry("600x400")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(dates, bmis, marker='o', linestyle='-', color='b', label="BMI")
        ax.axhline(y=18.5, color='orange', linestyle='--', alpha=0.5)
        ax.axhline(y=24.9, color='green', linestyle='--', alpha=0.5, label="Normal Range")
        ax.axhline(y=29.9, color='red', linestyle='--', alpha=0.5)
        ax.set_title(f"BMI Progress for {name}")
        ax.set_xlabel("Date")
        ax.set_ylabel("BMI Value")
        ax.legend()
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=plot_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()