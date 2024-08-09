import requests
import subprocess
import configparser
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import re
import os
import glob

def send_to_discord(webhook_url, message, botname):
    """
    Send a message to a Discord channel via webhook.
    """
    # Create a root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.attributes("-topmost", True)  # Ensure the message box is always on top
    
    data = {
        "content": message,
        "username": botname
    }
    response = requests.post(webhook_url, json=data)
    response.raise_for_status()  # This will raise an exception for HTTP errors.
    print("Message sent to Discord")

def extract_datetime_from_title(file_path):
    """
    Extract the datetime from the title in the .tid file.
    """
    with open(file_path, 'r') as file:
        content = file.read()
        match = re.search(r'title: (\d{12})-WvW-Log-Review', content)
        if match:
            return match.group(1)
    return None

def generate_url(base_url, file_path):
    """
    Generate a URL that includes the datetime extracted from the .tid file.
    """
    datetime_str = extract_datetime_from_title(file_path)
    if datetime_str:
        return f"{base_url}/#{datetime_str}-WvW-Log-Review"
    else:
        raise ValueError("Datetime not found in the file title.")

def find_latest_tid_file(log_folder, base_name):
    """
    Find the latest .tid file in the specified folder that matches the base name pattern.
    """
    search_pattern = os.path.join(log_folder, f"{base_name}*.tid")
    files = glob.glob(search_pattern)
    if not files:
        raise FileNotFoundError(f"No files matching pattern {search_pattern} found.")
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def confirm_upload(webhook_url, config):
    """
    Create a pop-up to confirm whether the logs have been uploaded.
    """
    # Create a root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.attributes("-topmost", True)  # Ensure the message box is always on top

    answer = messagebox.askyesno("Confirm Upload", "Are we uploading the logs for this WvW Session?", parent=root)
    if answer:
        subprocess.run(["python", "upload.py"], shell=False)
        log_folder = "logs_output"
        base_name = "TW5_top_stats_detailed"
        file_path = find_latest_tid_file(log_folder, base_name)
        message = f"{config['Discord']['message']} {generate_url(config['URLs']['WikiURL'], file_path)}"
        send_to_discord(webhook_url, message, config['Discord']['botname'])
        messagebox.showinfo("Done", "The message has been posted to Discord.", parent=root)
    else:
        messagebox.showinfo("No Upload", "No Log upload tonight! I hope you had fun!", parent=root)

    root.destroy()

def main():
    # Load configuration settings
    config = configparser.ConfigParser()
    config.read('settings.ini')

    # Get webhook URL and bot name from config
    webhook_url = config['Discord']['WebhookURL']
    botname = config['Discord']['botname']
    confirm_upload(webhook_url, config)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    main()