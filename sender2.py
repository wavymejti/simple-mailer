import smtplib
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import messagebox, simpledialog, StringVar, OptionMenu
from cryptography.fernet import Fernet

CONFIG_FILE = "config.json"
TEMPLATES_FILE = "templates.json"
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

def load_templates():
    try:
        with open(TEMPLATES_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_templates(templates):
    with open(TEMPLATES_FILE, "w") as file:
        json.dump(templates, file)

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

def save_template():
    template_name = simpledialog.askstring("Nazwa szablonu", "Podaj nazwę szablonu:")
    if template_name:
        templates = load_templates()
        body = text_body.get("1.0", tk.END)
        templates[template_name] = body
        save_templates(templates)
        update_template_list()
        messagebox.showinfo("Sukces", f"Szablon '{template_name}' został zapisany.")

def load_template(template_name):
    templates = load_templates()
    if template_name in templates:
        body = templates[template_name]
        text_body.delete("1.0", tk.END)
        text_body.insert(tk.END, body)
        messagebox.showinfo("Sukces", f"Szablon '{template_name}' został załadowany.")
    else:
        messagebox.showerror("Błąd", f"Szablon '{template_name}' nie istnieje.")

def update_template_list():
    templates = load_templates()
    template_names = list(templates.keys())
    template_var.set(template_names[0] if template_names else "")
    template_menu['menu'].delete(0, 'end')
    for name in template_names:
        template_menu['menu'].add_command(label=name, command=tk._setit(template_var, name))

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

save_template_button = tk.Button(root, text="Zapisz szablon", command=save_template)
save_template_button.grid(row=6, column=0, pady=10)

template_var = StringVar(root)
template_menu = OptionMenu(root, template_var, "")
template_menu.grid(row=6, column=1, pady=10)

load_template_button = tk.Button(root, text="Załaduj szablon", command=lambda: load_template(template_var.get()))
load_template_button.grid(row=6, column=2, pady=10)

load_saved_data()
update_template_list()

root.mainloop()
