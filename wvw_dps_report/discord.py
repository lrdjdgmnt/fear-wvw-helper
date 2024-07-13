import requests
import subprocess
import configparser
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

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

def generate_url(base_url):
    """
    Generate a URL that includes the current date in YYYYMMDD format.
    """
    current_date = datetime.now().strftime("%Y%m%d")
    return f"{base_url}/#{current_date}-WvW-Log-Review"

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
        message = f"{config['Discord']['message']} {generate_url(config['URLs']['WikiURL'])}"
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
