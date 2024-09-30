import socket
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from threading import Thread
import datetime

# Client configuration
BUFFER_SIZE = 1024
CURRENT_DIRECTORY = os.getcwd()
os.makedirs(os.path.join(CURRENT_DIRECTORY, 'client_files'), exist_ok=True)
DOWNLOAD_DIRECTORY = os.path.join(CURRENT_DIRECTORY, 'client_files')
LOG_FILE = 'client_activity.log'

# Log function
def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"{timestamp} - {message}"
    log_textbox.insert(tk.END, formatted_message + '\n')
    log_textbox.see(tk.END)  # Auto-scroll to the bottom

    # Save log to file
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(formatted_message + '\n')

# Handle receiving a list of files (emails) in the account
def receive_file_list():
    try:
        data, _ = client_socket.recvfrom(BUFFER_SIZE)
        file_list = data.decode().split(',')
        log(f"Received files: {', '.join(file_list)}")
    except Exception as e:
        log(f"Error receiving file list: {e}")

# Create a new account
def create_account():
    try:
        account_name = account_entry.get()
        if not account_name:
            messagebox.showwarning("Input Error", "Please enter an account name.")
            return

        log(f"Creating account '{account_name}'...")

        server_ip = server_ip_entry.get()
        server_port = int(server_port_entry.get())

        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(f"CREATE_ACCOUNT:{account_name}".encode(), (server_ip, server_port))
        
        log(f"Account '{account_name}' created successfully.")
    except Exception as e:
        log(f"Error creating account: {e}")

# Log in to an account and receive list of files
def login_account():
    try:
        account_name = account_entry.get()
        if not account_name:
            messagebox.showwarning("Input Error", "Please enter an account name.")
            return

        log(f"Logging into account '{account_name}'...")

        server_ip = server_ip_entry.get()
        server_port = int(server_port_entry.get())

        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(f"LOGIN:{account_name}".encode(), (server_ip, server_port))

        # Receive the list of files (emails)
        receive_file_list()
    except Exception as e:
        log(f"Error logging in: {e}")

# Send an email to another account
def send_email():
    try:
        recipient_account = recipient_entry.get()
        email_content = email_entry.get("1.0", tk.END).strip()

        if not recipient_account or not email_content:
            messagebox.showwarning("Input Error", "Please enter recipient account and email content.")
            return

        log(f"Sending email to '{recipient_account}'...")

        server_ip = server_ip_entry.get()
        server_port = int(server_port_entry.get())

        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(f"SEND_EMAIL:{recipient_account}:{email_content}".encode(), (server_ip, server_port))

        log(f"Email sent to '{recipient_account}'.")
    except Exception as e:
        log(f"Error sending email: {e}")

# Initialize the UI
root = tk.Tk()
root.title("UDP Email Client")
root.style = ttk.Style()
root.style.theme_use('clam')

# Server IP entry
server_ip_label = ttk.Label(root, text="Server IP:")
server_ip_label.pack(pady=5)

server_ip_entry = ttk.Entry(root)
server_ip_entry.pack(pady=5)

# Server port entry
server_port_label = ttk.Label(root, text="Server Port:")
server_port_label.pack(pady=5)

server_port_entry = ttk.Entry(root)
server_port_entry.pack(pady=5)

# Account name entry
account_label = ttk.Label(root, text="Account Name:")
account_label.pack(pady=5)

account_entry = ttk.Entry(root)
account_entry.pack(pady=5)

# Buttons for account actions
account_frame = ttk.Frame(root)
account_frame.pack(pady=10)

create_account_button = ttk.Button(account_frame, text="Create Account", command=lambda: Thread(target=create_account).start())
create_account_button.pack(side=tk.LEFT, padx=5)

login_button = ttk.Button(account_frame, text="Login", command=lambda: Thread(target=login_account).start())
login_button.pack(side=tk.LEFT, padx=5)

# Recipient entry for sending emails
recipient_label = ttk.Label(root, text="Recipient Account:")
recipient_label.pack(pady=5)

recipient_entry = ttk.Entry(root)
recipient_entry.pack(pady=5)

# Email content entry
email_label = ttk.Label(root, text="Email Content:")
email_label.pack(pady=5)

email_entry = tk.Text(root, height=5, width=40)
email_entry.pack(pady=5)

# Button to send email
send_email_button = ttk.Button(root, text="Send Email", command=lambda: Thread(target=send_email).start())
send_email_button.pack(pady=10)

# Log display
log_label = ttk.Label(root, text="Client Status")
log_label.pack(pady=5)

log_textbox = tk.Text(root, height=15, width=50)
log_textbox.pack(pady=5)

# Button to open log file
open_log_button = ttk.Button(root, text="Open Log File", command=lambda: os.startfile(LOG_FILE))
open_log_button.pack(pady=10)

# Start the Tkinter main loop
root.mainloop()
