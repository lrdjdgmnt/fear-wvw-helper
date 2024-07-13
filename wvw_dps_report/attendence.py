import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime
import time

# Google Sheet setup
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('guild-attendence-51513f448822.json', scope)
client = gspread.authorize(creds)
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1uAKGzdM36mqYyoW_G1tT5u3j8nwvn3JKq6btgdEWxEU/edit?gid=0').sheet1

# Fetch guild roster
guild_url = 'https://api.guildwars2.com/v2/guild/67740789-764C-EA11-81A8-C983E8889009/members?access_token=B7B225A2-5F45-524A-828D-E4D9A21B425DEFB5424E-C239-4D1A-9767-A28ACE7B03C5'
response = requests.get(guild_url)
guild_members = {member['name'] for member in response.json()}  # Set for faster lookups

# Process JSON files
attendance = {}
directory = 'logs_output'

for filename in os.listdir(directory):
    if filename.endswith('.json'):
        path = os.path.join(directory, filename)
        date_str = filename.split('_')[0]  # Extract the date portion
        date_obj = datetime.strptime(date_str, '%Y%m%d-%H%M%S')
        readable_date = date_obj.strftime('%m/%d/%Y')
        
        with open(path, 'r', encoding='utf-8') as file:  # Specifying encoding here
            data = json.load(file)
            for player in data['players']:
                account_name = player['account']
                if account_name in guild_members:
                    if account_name in attendance:
                        attendance[account_name]['fights'] += 1
                        attendance[account_name]['last_seen'] = readable_date
                    else:
                        attendance[account_name] = {'fights': 1, 'member': 'Yes', 'last_seen': readable_date}

# Fetch existing data from the Google Sheet
existing_data = sheet.get_all_records()
existing_players = {row['Player']: {'fights': int(row['Fights Attended']), 'member': row['Member'], 'last_seen': row.get('Last Seen', '')} for row in existing_data}

# Update the attendance with existing data
for account, data in existing_players.items():
    if account not in attendance:
        attendance[account] = {'fights': data['fights'], 'member': 'No' if account not in guild_members else 'Yes', 'last_seen': data['last_seen']}
    else:
        attendance[account]['fights'] += data['fights']

# Find column indices dynamically with case-insensitive search
header = sheet.row_values(1)
header_lower = [h.lower() for h in header]
player_col = header_lower.index('player') + 1
fights_col = header_lower.index('fights attended') + 1
member_col = header_lower.index('member') + 1
last_seen_col = header_lower.index('last seen') + 1

# Update the sheet without clearing it
sheet_data = sheet.get_all_records()
players_row = [row['Player'] for row in sheet_data]

# Batch update to reduce API calls
batch_update_requests = []
for account, data in attendance.items():
    if account in players_row:
        row_index = players_row.index(account) + 2  # Adjusting for header row
        batch_update_requests.append({
            'range': f'{chr(64 + fights_col)}{row_index}',
            'values': [[data['fights']]]
        })
        batch_update_requests.append({
            'range': f'{chr(64 + member_col)}{row_index}',
            'values': [[data['member']]]
        })
        batch_update_requests.append({
            'range': f'{chr(64 + last_seen_col)}{row_index}',
            'values': [[data['last_seen']]]
        })
    else:
        new_row = [''] * len(header)  # Initialize a new row with empty strings
        new_row[player_col - 1] = account
        new_row[fights_col - 1] = data['fights']
        new_row[member_col - 1] = data['member']
        new_row[last_seen_col - 1] = data['last_seen']
        sheet.append_row(new_row)
        time.sleep(1)  # Sleep to avoid hitting the API rate limit

# Execute batch update
for i in range(0, len(batch_update_requests), 10):  # Batch size of 10 to stay within the rate limit
    sheet.batch_update(batch_update_requests[i:i + 10])
    time.sleep(1)  # Sleep to avoid hitting the API rate limit

print('Google Sheet updated successfully. Parsing Logs:')
