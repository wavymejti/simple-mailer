import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import messagebox

def send_email(sender_email, sender_password, receiver_email, subject, body):
    # Utworzenie wiadomości e-mail
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Dodanie treści e-maila
    message.attach(MIMEText(body, "plain"))

    # Połączenie z serwerem SMTP Outlooka i wysłanie e-maila
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

root.mainloop()
