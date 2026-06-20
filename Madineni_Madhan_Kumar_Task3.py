import tkinter as tk
from tkinter import messagebox
import string
import secrets
class PasswordGenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("350x450")
        tk.Label(root, text="Password Length:", font=("Arial", 10, "bold")).pack(pady=10)
        self.length_var = tk.IntVar(value=16)
        tk.Entry(root, textvariable=self.length_var, width=10, justify="center").pack()
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.num_var = tk.BooleanVar(value=True)
        self.sym_var = tk.BooleanVar(value=True)
        tk.Checkbutton(root, text="Uppercase Letters", variable=self.upper_var).pack(anchor="w", padx=50, pady=2)
        tk.Checkbutton(root, text="Lowercase Letters", variable=self.lower_var).pack(anchor="w", padx=50, pady=2)
        tk.Checkbutton(root, text="Numbers", variable=self.num_var).pack(anchor="w", padx=50, pady=2)
        tk.Checkbutton(root, text="Symbols", variable=self.sym_var).pack(anchor="w", padx=50, pady=2)
        tk.Label(root, text="Exclude Characters:").pack(pady=5)
        self.exclude_var = tk.StringVar()
        tk.Entry(root, textvariable=self.exclude_var, width=15).pack()
        tk.Button(root, text="Generate Password", command=self.generate_pwd, bg="lightblue").pack(pady=20)
        self.result_var = tk.StringVar()
        tk.Entry(root, textvariable=self.result_var, font=("Courier", 12), state="readonly", justify="center").pack(fill="x", padx=20)
        tk.Button(root, text="Copy to Clipboard", command=self.copy_clipboard).pack(pady=10)
    def generate_pwd(self):
        try:
            length = self.length_var.get()
        except Exception:
            messagebox.showerror("Error", "Enter a valid number for length")
            return
        if length < 4:
            messagebox.showerror("Error", "Length must be at least 4")
            return
        exclude = set(self.exclude_var.get())
        chars = ""
        guaranteed = []
        if self.upper_var.get():
            pool = [c for c in string.ascii_uppercase if c not in exclude]
            if pool:
                chars += "".join(pool)
                guaranteed.append(secrets.choice(pool))
        if self.lower_var.get():
            pool = [c for c in string.ascii_lowercase if c not in exclude]
            if pool:
                chars += "".join(pool)
                guaranteed.append(secrets.choice(pool))
        if self.num_var.get():
            pool = [c for c in string.digits if c not in exclude]
            if pool:
                chars += "".join(pool)
                guaranteed.append(secrets.choice(pool))
        if self.sym_var.get():
            pool = [c for c in string.punctuation if c not in exclude]
            if pool:
                chars += "".join(pool)
                guaranteed.append(secrets.choice(pool))
        if not chars:
            messagebox.showerror("Error", "Select at least one character type")
            return
        if length < len(guaranteed):
            messagebox.showerror("Error", "Length is too short to include all chosen types")
            return
        password = list(guaranteed)
        while len(password) < length:
            password.append(secrets.choice(chars))
        secrets.SystemRandom().shuffle(password)
        self.result_var.set("".join(password))
    def copy_clipboard(self):
        pwd = self.result_var.get()
        if pwd:
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            self.root.update()
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenApp(root)
    root.mainloop()