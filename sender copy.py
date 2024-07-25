import smtplib
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet

CONFIG_FILE = "config.json"
KEY_FILE = "secret.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)

def load_key():
    return open(KEY_FILE, "rb").read()

def encrypt_password(password, key):
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    return base64.urlsafe_b64encode(encrypted_password).decode()

def decrypt_password(encrypted_password, key):
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(base64.urlsafe_b64decode(encrypted_password.encode())).decode()
    return decrypted_password

def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)

def send_email(sender_email, sender_password, receiver_email, subject, body):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        messagebox.showinfo("Sukces", "Email został wysłany pomyślnie!")
    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

def on_send_button_click():
    sender_email = entry_sender_email.get()
    sender_password = entry_sender_password.get()
    receiver_email = entry_receiver_email.get()
    subject = entry_subject.get()
    body = text_body.get("1.0", tk.END)
    send_email(sender_email, sender_password, receiver_email, subject, body)
    
    key = load_key()
    encrypted_password = encrypt_password(sender_password, key)

    config = {
        "sender_email": sender_email,
        "sender_password": encrypted_password,
        "receiver_email": receiver_email,
        "subject": subject
    }
    save_config(config)

def load_saved_data():
    config = load_config()
    entry_sender_email.insert(0, config.get("sender_email", ""))
    if "sender_password" in config:
        key = load_key()
        decrypted_password = decrypt_password(config["sender_password"], key)
        entry_sender_password.insert(0, decrypted_password)
    entry_receiver_email.insert(0, config.get("receiver_email", ""))
    entry_subject.insert(0, config.get("subject", ""))

# Tworzenie klucza, jeśli nie istnieje
try:
    open(KEY_FILE, "rb")
except FileNotFoundError:
    generate_key()

# Tworzenie GUI za pomocą tkinter
root = tk.Tk()
root.title("Wysyłanie e-maili")

tk.Label(root, text="Adres e-mail nadawcy:").grid(row=0, column=0)
entry_sender_email = tk.Entry(root, width=50)
entry_sender_email.grid(row=0, column=1)

tk.Label(root, text="Hasło nadawcy:").grid(row=1, column=0)
entry_sender_password = tk.Entry(root, show="*", width=50)
entry_sender_password.grid(row=1, column=1)

tk.Label(root, text="Adres e-mail odbiorcy:").grid(row=2, column=0)
entry_receiver_email = tk.Entry(root, width=50)
entry_receiver_email.grid(row=2, column=1)

tk.Label(root, text="Temat:").grid(row=3, column=0)
entry_subject = tk.Entry(root, width=50)
entry_subject.grid(row=3, column=1)

tk.Label(root, text="Treść wiadomości:").grid(row=4, column=0)
text_body = tk.Text(root, width=50, height=10)
text_body.grid(row=4, column=1)

send_button = tk.Button(root, text="Wyślij", command=on_send_button_click)
send_button.grid(row=5, column=1, pady=10)

load_saved_data()

root.mainloop()
