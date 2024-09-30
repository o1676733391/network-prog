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
def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"{timestamp} - {message}"
    log_textbox.insert(tk.END, formatted_message + '\n')
    log_textbox.see(tk.END)  # Auto-scroll to the bottom
    
    # Save log to file
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(formatted_message + '\n')

def receive_file(filename, server_address):
    try:
        file_path = os.path.join(DOWNLOAD_DIRECTORY, filename)
        os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)
        log(f"Saving file to: {file_path}")

        with open(file_path, 'wb') as file:
            while True:
                data, _ = client_socket.recvfrom(BUFFER_SIZE)
                
                if data.decode() == "END":
                    log("End of file transmission.")
                    break
                
                if data.decode() == "File not found":
                    log("File not found on the server.")
                    break
                
                log(f"Received packet: {data[:50]}...")
                file.write(data)
        
        log(f"Finished receiving file: {filename}")
    except Exception as e:
        log(f"An error occurred: {e}")

def request_file():
    try:
        server_ip = server_ip_entry.get()
        server_port = int(server_port_entry.get())
        filename = file_entry.get()

        if not server_ip or not server_port or not filename:
            messagebox.showwarning("Input Error", "Please enter all required fields.")
            return

        log(f"Requesting file '{filename}' from server {server_ip}:{server_port}...")
        
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(filename.encode(), (server_ip, server_port))

        receive_file(filename, (server_ip, server_port))

    except Exception as e:
        log(f"Error requesting file: {e}")

def open_log_file():
    os.startfile(LOG_FILE)

# Initialize the UI
root = tk.Tk()
root.title("UDP File Client")
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

# File name entry
file_label = ttk.Label(root, text="File Name:")
file_label.pack(pady=5)

file_entry = ttk.Entry(root)
file_entry.pack(pady=5)

# Request file button
request_file_button = ttk.Button(root, text="Request File", command=lambda: Thread(target=request_file).start())
request_file_button.pack(pady=10)

# Create a log display
log_label = ttk.Label(root, text="Client Status")
log_label.pack(pady=5)

log_textbox = tk.Text(root, height=15, width=50)
log_textbox.pack(pady=5)

# Button to open log file
open_log_button = ttk.Button(root, text="Open Log File", command=open_log_file)
open_log_button.pack(pady=10)

# Start the Tkinter main loop
root.mainloop()
