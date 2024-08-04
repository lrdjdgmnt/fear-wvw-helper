import os
import subprocess
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Function to find files based on creation time
def find_files(directory, extension, after_time):
    found_files = []
    # Walk through all directories and files in the path
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                file_path = os.path.join(root, file)
                # Get the creation time of the file
                creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if creation_time > after_time:
                    found_files.append(file_path)
    return found_files

# Paths for parsers and output
logpath = os.path.join(os.path.expanduser('~'), 'Documents', 'Guild Wars 2', 'addons', 'arcdps', 'arcdps.cbtlogs', 'WvW (1)')
parserpath = os.path.join('C:\\', 'wvw_dps_report', 'parser', 'GuildWars2EliteInsights.exe')
configpath = os.path.join('C:\\', 'wvw_dps_report', 'config.conf')
outputpath = os.path.join('C:\\', 'wvw_dps_report', 'logs_output')
wvwparser = os.path.join('C:\\', 'wvw_dps_report', 'wvw_parser', 'TW5_parse_top_stats_detailed.py')

# Delete all previous .tid files in the output path
for filename in os.listdir(outputpath):
    if filename.endswith('.tid'):
        os.remove(os.path.join(outputpath, filename))
        print(f"Deleted: {filename}")
        
# Function to handle GUI input and set the after_time variable
def get_start_time():
    def on_submit():
        try:
            # Get the values from the GUI inputs
            start_hour = int(hour_entry.get())
            start_minute = int(minute_entry.get())
            am_pm = am_pm_var.get()
    
            # Convert AM/PM format to 24-hour format
            if am_pm == 'PM' and start_hour < 12:
                start_hour += 12
            elif am_pm == 'AM' and start_hour == 12:
                start_hour = 0
    
            # Validate the input time
            if start_hour < 0 or start_hour > 23 or start_minute < 0 or start_minute > 59:
                raise ValueError("Invalid time format.")
    
            # Set the after_time variable based on the input
            selected_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    
            # Adjust the date if the selected time is later than the current time
            if selected_time > now:
                selected_time -= timedelta(days=1)
    
            # Close the GUI window
            root.destroy()

            # Proceed with the rest of the script using after_time
            process_files(selected_time)
        except ValueError as e:
            messagebox.showerror("Error", str(e))


    # Create the GUI window
    root = tk.Tk()
    root.title("Enter Raid Start Time")

    # Hour selection dropdown
    hour_label = ttk.Label(root, text="Hour:")
    hour_label.grid(row=0, column=0, padx=10, pady=5)
    hour_entry = ttk.Combobox(root, values=[str(i) for i in range(1, 13)])
    hour_entry.grid(row=0, column=1, padx=10, pady=5)
    hour_entry.current(0)

    # Minute selection dropdown
    minute_label = ttk.Label(root, text="Minute:")
    minute_label.grid(row=1, column=0, padx=10, pady=5)
    minute_entry = ttk.Combobox(root, values=[str(i).zfill(2) for i in range(0, 60)])
    minute_entry.grid(row=1, column=1, padx=10, pady=5)
    minute_entry.current(0)

    # AM/PM selection dropdown
    am_pm_var = tk.StringVar()
    am_pm_label = ttk.Label(root, text="AM/PM:")
    am_pm_label.grid(row=2, column=0, padx=10, pady=5)
    am_pm_combobox = ttk.Combobox(root, textvariable=am_pm_var, values=["AM", "PM"])
    am_pm_combobox.grid(row=2, column=1, padx=10, pady=5)
    am_pm_combobox.current(0)

    # Submit button
    submit_button = ttk.Button(root, text="Submit", command=on_submit)
    submit_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    root.mainloop()

# Function to process files based on the after_time
def process_files(after_time):
    # Search for files within the specified time range
    files_to_process = find_files(logpath, '.zevtc', after_time)

    # Run the parser with the found files if any
    if files_to_process:
        command = [parserpath, '-c', configpath] + files_to_process
        subprocess.run(command, shell=False)
    else:
        print(f"No .zevtc files found starting from {after_time}.")

# Get the current time
now = datetime.now()

# Call the function to get the raid start time
get_start_time()

print("Grabbing the attendence numbers and updatign the spread sheet please wait")

# Run the attendence numbers
subprocess.run (["python", "attendence.py"], shell=False)

# Run Drevarrs parser script
subprocess.run(["python", wvwparser, outputpath], shell=False)

# Clean up the output path by removing non-.tid files
for filename in os.listdir(outputpath):
    if not filename.endswith('.tid'):
        os.remove(os.path.join(outputpath, filename))
        print(f"Deleted: {filename}")

# Post the link to discord
subprocess.run(["python", "discord.py"], shell=False)