import requests
import os
import shutil
import zipfile
import configparser
import subprocess

def fetch_latest_release(user, repo):
    url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def download_archive(download_url, file_name):
    response = requests.get(download_url)
    response.raise_for_status()
    with open(file_name, 'wb') as file:
        file.write(response.content)
    return file_name

def extract_files(zip_path, extract_to, specific_subfolder=None):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        if specific_subfolder:
            subfolder_path = None
            for member in zip_ref.infolist():
                if specific_subfolder in member.filename:
                    subfolder_path = member.filename
                    break
            if subfolder_path:
                subfolder_root = os.path.commonprefix([m.filename for m in zip_ref.infolist() if m.filename.startswith(subfolder_path)])
                for member in zip_ref.infolist():
                    if member.filename.startswith(subfolder_root):
                        member_path = os.path.relpath(member.filename, subfolder_root)
                        target_path = os.path.join(extract_to, member_path)
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        if member.filename.endswith('/'):
                            os.makedirs(target_path, exist_ok=True)
                        else:
                            with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
        else:
            for member in zip_ref.infolist():
                target_path = os.path.join(extract_to, member.filename)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                if member.filename.endswith('/'):
                    os.makedirs(target_path, exist_ok=True)
                else:
                    with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
    os.remove(zip_path)

def check_and_update_version(repo_info, config, version_section, extract_to):
    user = repo_info['user']
    repo = repo_info['repo']
    latest_release = fetch_latest_release(user, repo)
    latest_version = latest_release['tag_name']

    last_version = config[version_section].get(repo_info['config_key'], None)

    if last_version != latest_version:
        if repo == "GW2-Elite-Insights-Parser":
            download_url = f"https://github.com/{user}/{repo}/releases/download/{latest_version}/GW2EI.zip"
            zip_file = download_archive(download_url, f"GW2EI-{latest_version}.zip")
            extract_files(zip_file, extract_to)

        elif repo in ["arcdps_top_stats_parser", "fear-wvw-helper"]:
            download_url = f"https://github.com/{user}/{repo}/archive/refs/tags/{latest_version}.zip"
            zip_file = download_archive(download_url, f"{repo}-{latest_version}.zip")
            specific_subfolder = repo if repo == "arcdps_top_stats_parser" else "wvw_dps_report"
            extract_files(zip_file, extract_to, specific_subfolder=specific_subfolder)
        
        config[version_section][repo_info['config_key']] = latest_version
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

def main():
    config = configparser.ConfigParser()
    config.read('settings.ini')

    if 'Versions' not in config:
        config['Versions'] = {}

    repos = [
        {'user': 'baaron4', 'repo': 'GW2-Elite-Insights-Parser', 'extract_to': 'parser', 'config_key': 'EI'},
        {'user': 'Drevarr', 'repo': 'arcdps_top_stats_parser', 'extract_to': 'wvw_parser', 'config_key': 'WvW_parser'},
        {'user': 'lrdjdgmnt', 'repo': 'fear-wvw-helper', 'extract_to': 'c:/wvw_dps_report', 'config_key': 'helper'}
    ]
    for repo_info in repos:
        check_and_update_version(repo_info, config, 'Versions', repo_info['extract_to'])
        
    # Run the logs
    subprocess.run(["python", "logs.py"], shell=False)

if __name__ == "__main__":
    main()
