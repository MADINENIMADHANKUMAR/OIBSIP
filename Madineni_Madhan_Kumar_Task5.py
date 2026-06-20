import tkinter as tk
from tkinter import messagebox
import socket
import threading
import sqlite3
import json

def encrypt(text):
    return "".join(chr(ord(c) + 5) for c in text)

def decrypt(text):
    return "".join(chr(ord(c) - 5) for c in text)

def start_server():
    print("Starting Server...")
    conn_db = sqlite3.connect("chat_data.db", check_same_thread=False)
    c = conn_db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS history (message TEXT)")
    conn_db.commit()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 5555))
    server.listen()
    print("Server listening on port 5555...")

    clients = []

    def handle_client(client_socket):
        buffer = ""
        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    req = json.loads(line)
                    action = req.get("action")

                    if action == "register":
                        user = req["username"]
                        pwd = req["password"]
                        c.execute("SELECT * FROM users WHERE username=?", (user,))
                        if c.fetchone():
                            client_socket.send((json.dumps({"status": "error", "msg": "User exists"}) + "\n").encode())
                        else:
                            c.execute("INSERT INTO users VALUES (?, ?)", (user, pwd))
                            conn_db.commit()
                            client_socket.send((json.dumps({"status": "success", "msg": "Registered"}) + "\n").encode())
                    
                    elif action == "login":
                        user = req["username"]
                        pwd = req["password"]
                        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
                        if c.fetchone():
                            clients.append(client_socket)
                            client_socket.send((json.dumps({"status": "success", "msg": "Logged in"}) + "\n").encode())
                            
                            c.execute("SELECT message FROM history")
                            for row in c.fetchall():
                                client_socket.send((json.dumps({"action": "msg", "text": row[0]}) + "\n").encode())
                        else:
                            client_socket.send((json.dumps({"status": "error", "msg": "Invalid credentials"}) + "\n").encode())
                            
                    elif action == "msg":
                        msg = req["text"]
                        c.execute("INSERT INTO history VALUES (?)", (msg,))
                        conn_db.commit()
                        
                        for client in clients:
                            try:
                                client.send((json.dumps({"action": "msg", "text": msg}) + "\n").encode())
                            except:
                                clients.remove(client)
            except:
                break
        client_socket.close()

    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,)).start()


class ChatClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Secure Chat App")
        self.root.geometry("400x500")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect(("127.0.0.1", 5555))
        except:
            messagebox.showerror("Error", "Server is not running!")
            self.root.destroy()
            return

        self.username = ""
        self.build_login_screen()
        self.root.mainloop()

    def build_login_screen(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=50)

        tk.Label(self.login_frame, text="Username:", font=("Arial", 12)).pack()
        self.user_entry = tk.Entry(self.login_frame, font=("Arial", 12))
        self.user_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Password:", font=("Arial", 12)).pack()
        self.pwd_entry = tk.Entry(self.login_frame, show="*", font=("Arial", 12))
        self.pwd_entry.pack(pady=5)

        tk.Button(self.login_frame, text="Login", command=lambda: self.auth("login"), bg="lightblue").pack(pady=5, fill="x")
        tk.Button(self.login_frame, text="Register", command=lambda: self.auth("register")).pack(pady=5, fill="x")

    def auth(self, action):
        user = self.user_entry.get().strip()
        pwd = self.pwd_entry.get().strip()
        if not user or not pwd:
            messagebox.showerror("Error", "Fill all fields")
            return

        req = json.dumps({"action": action, "username": user, "password": pwd}) + "\n"
        self.socket.send(req.encode())
        
        data = ""
        while "\n" not in data:
            data += self.socket.recv(1024).decode()
        
        res = json.loads(data.split("\n")[0])
        
        if res["status"] == "success":
            if action == "login":
                self.username = user
                self.login_frame.destroy()
                self.build_chat_screen()
                threading.Thread(target=self.receive_messages, daemon=True).start()
            else:
                messagebox.showinfo("Success", "Registered! You can now login.")
        else:
            messagebox.showerror("Error", res["msg"])

    def build_chat_screen(self):
        self.chat_area = tk.Text(self.root, state="disabled", font=("Arial", 11))
        self.chat_area.pack(padx=10, pady=10, fill="both", expand=True)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        self.msg_entry = tk.Entry(bottom_frame, font=("Arial", 12))
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(bottom_frame, text="😀", command=lambda: self.msg_entry.insert(tk.END, "😀")).pack(side="left")
        tk.Button(bottom_frame, text="👍", command=lambda: self.msg_entry.insert(tk.END, "👍")).pack(side="left")
        
        tk.Button(bottom_frame, text="Send", command=self.send_message, bg="lightgreen").pack(side="left", padx=5)
        self.root.bind("<Return>", lambda event: self.send_message())

    def send_message(self):
        text = self.msg_entry.get().strip()
        if not text:
            return
        
        formatted_msg = f"{self.username}: {text}"
        encrypted_msg = encrypt(formatted_msg)
        
        req = json.dumps({"action": "msg", "text": encrypted_msg}) + "\n"
        self.socket.send(req.encode())
        self.msg_entry.delete(0, tk.END)

    def receive_messages(self):
        buffer = ""
        while True:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    req = json.loads(line)
                    
                    if req.get("action") == "msg":
                        decrypted_msg = decrypt(req["text"])
                        self.chat_area.config(state="normal")
                        self.chat_area.insert(tk.END, decrypted_msg + "\n")
                        self.chat_area.config(state="disabled")
                        self.chat_area.yview(tk.END)
            except:
                break

if __name__ == "__main__":
    mode = input("Run as (S)erver or (C)lient? ").strip().lower()
    if mode == 's':
        start_server()
    elif mode == 'c':
        ChatClient()
    else:
        print("Invalid choice. Run again and type S or C.")