import socket
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
from tkinter import ttk
from datetime import datetime

# Server configuration
HOST = '192.168.1.237'
PORT = 12345
BUFFER_SIZE = 1024
ACCOUNT_DIRECTORY = 'server_accounts'  # Directory where all accounts will be stored

# Global server variables
server_socket = None
server_running = True
log_path = 'server_activity.log'

# Utility function for logging
def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"{timestamp} - {message}"
    log_textbox.insert(tk.END, full_message + '\n')
    log_textbox.see(tk.END)
    save_log(full_message)

def save_log(message):
    with open(log_path, 'a') as log_file:
        log_file.write(message + '\n')

# Create an account folder and a welcome file
def create_account_folder(account_name):
    account_path = os.path.join(ACCOUNT_DIRECTORY, account_name)
    os.makedirs(account_path, exist_ok=True)
    welcome_file = os.path.join(account_path, 'new_email.txt')
    with open(welcome_file, 'w') as f:
        f.write("Thank you for using this service. We hope that you will feel comfortable............")
    log(f"Created account for: {account_name}")

# Handle receiving emails and saving them to the correct account folder
def save_email_to_account(account_name, email_content):
    account_path = os.path.join(ACCOUNT_DIRECTORY, account_name)
    if os.path.exists(account_path):
        email_file = os.path.join(account_path, f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(email_file, 'w') as f:
            f.write(email_content)
        log(f"Saved email for account: {account_name}")
    else:
        log(f"Account not found: {account_name}")

# Send all file names in the account folder to the client
def send_account_files(account_name, client_address):
    account_path = os.path.join(ACCOUNT_DIRECTORY, account_name)
    if os.path.exists(account_path):
        files = os.listdir(account_path)
        file_list = ','.join(files)
        server_socket.sendto(file_list.encode(), client_address)
        log(f"Sent file list to {client_address[0]}:{client_address[1]} for account {account_name}")
    else:
        error_message = "Account not found"
        server_socket.sendto(error_message.encode(), client_address)
        log(f"Account not found for {client_address[0]}:{client_address[1]}")

# Handle incoming requests
def handle_requests():
    global server_socket
    while server_running:
        try:
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            message = data.decode().split(':')
            
            if message[0] == "CREATE_ACCOUNT":
                account_name = message[1]
                create_account_folder(account_name)
                log(f"Account created for: {account_name}")
            
            elif message[0] == "SEND_EMAIL":
                account_name = message[1]
                email_content = message[2]
                save_email_to_account(account_name, email_content)
            
            elif message[0] == "LOGIN":
                account_name = message[1]
                send_account_files(account_name, client_address)
            
        except OSError as e:
            if server_running:
                log(f"Socket error: {e}")
            break

# Start the server
def start_server():
    global server_socket
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((HOST, PORT))
        log(f"Server started on {HOST}:{PORT}")
        Thread(target=handle_requests, daemon=True).start()
    except OSError as e:
        log(f"Failed to start server: {e}")

# Tkinter UI Setup
root = tk.Tk()
root.title("UDP File Server")
root.geometry('600x500')

# Modern theme
style = ttk.Style()
style.theme_use('clam')

# Create a frame for the file list
file_frame = ttk.Frame(root)
file_frame.pack(pady=10, padx=10, fill='both', expand=True)

# Label for file list
file_list_label = ttk.Label(file_frame, text="Available Files")
file_list_label.pack(anchor='w')

# Log display
log_frame = ttk.Frame(root)
log_frame.pack(pady=10, padx=10, fill='both', expand=True)

log_label = ttk.Label(log_frame, text="Server Log")
log_label.pack(anchor='w')

log_textbox = tk.Text(log_frame, height=10, width=60)
log_textbox.pack(fill='both', expand=True)

# Start the server on a separate thread
start_server_thread = Thread(target=start_server, daemon=True)
start_server_thread.start()

# Handle window closing
def on_closing():
    global server_running
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        server_running = False
        if server_socket:
            server_socket.close()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
