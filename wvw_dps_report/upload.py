import os
import time
import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():
    # Load configuration settings
    config = configparser.ConfigParser()
    config.read('settings.ini')

    # Setup WebDriver
    driver_path = 'chromedriver-win64/chromedriver.exe'
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service)

    try:
        # Navigate to the login page
        driver.get(config['URLs']['LoginURL'])

        # Input credentials and log in
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'user_email')))
        driver.find_element(By.ID, 'user_email').send_keys(config['Credentials']['Email'])
        
        # Retrieve password from the configuration file
        if 'Credentials' in config and 'Password' in config['Credentials']:
            password = config['Credentials']['Password']
        else:
            raise ValueError("No password provided in the configuration file.")
        driver.find_element(By.ID, 'user_password').send_keys(password)
        driver.find_element(By.NAME, 'commit').click()

        # Navigate to another page after login
        driver.get(config['URLs']['WikiURL'])

        # Define the directory and extension
        directory = 'C:/wvw_dps_report/logs_output/'
        extension = '.tid'
        
        # Find all files with the .tid extension 
        files_to_upload = [f for f in os.listdir(directory) if f.endswith(extension)]
        
        for file_name in files_to_upload:
            file_path = os.path.join(directory, file_name)

            # Find the file input element
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )

            # Send the file path to the file input element, simulating a file upload
            file_input.send_keys(file_path)
            print(f"Importing: {file_path}")
            
        time.sleep(2)  # Waiting for upload to finish before clicking import
        
        # Click the "Import" button after all files have been uploaded
        import_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Import']"))
        )
        import_button.click()
        
        time.sleep(2)  # Waiting for import to finish before saving
        
        # Wait for the "Save" SVG button to be clickable
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "g.tc-image-save-button-dynamic-dirty"))
        )
        
        # Click the "Save" button
        save_button.click()

        time.sleep(20)  # Waiting for save

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Cleanup
        driver.quit()

if __name__ == "__main__":
    main()
