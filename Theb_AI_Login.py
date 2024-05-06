# Theb-API-Generator
# ====================
# Author: Devs Do Code (Sree)
# Description: A Python script to generate API keys and organization IDs for Theb AI platform.
# Features: Automatic email creation, registration, verification, and API token generation.
# License: MIT License
# Contributing: Fork and submit a pull request to contribute.

import re
import requests
import asyncio
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webscout import tempid
import json
import threading
import os

def update_file(api_key, organization_id):
    data = []  # Initialize an empty list

    # Check if the JSON file exists and is not empty
    if os.path.exists("Theb_API.json") and os.path.getsize("Theb_API.json") > 0:
        # Read the existing JSON data as a list of dictionaries
        with open("Theb_API.json", "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                pass  # Ignore and continue with an empty list if the file is not valid JSON

    # Update the API key and organization ID
    data.append({"API_KEY": api_key, "ORGANIZATION_ID": organization_id})

    # Write the updated data back to the JSON file
    with open("Theb_API.json", "w") as file:
        json.dump(data, file, indent=4)

async def generate_email():
    """Generates a temporary email using webscout."""
    client = tempid.Client()
    domains = await client.get_domains()
    email = await client.create_email(domain=domains[0].name)
    print(f"\033[96mTemporary email created: {email.email}\033[0m")
    return email

async def register_user(email, fullname="DevsDoCode", password="DevsDoCode@07"):
    """Registers on the website using the temporary email."""
    print("\033[91m--- REGISTRATION ---\033[0m")
    url = "https://beta.theb.ai/api/register"
    payload = {
        "fullname": fullname,
        "email": email.email,
        "password": password,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "X-Cf-Turnstile-Token": "",
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Response Status Code (Registration):", response.status_code)
    print("Response Content (Registration):", response.json())
    return fullname, password

async def verify_email(email, client, headless=True):
    """Extracts the verification link from the temporary email and verifies it."""
    print("\033[91m--- VERIFICATION ---\033[0m")
    async def get_verification_link() -> str:
        while True:
            print("Waiting for the verification email...", flush=True, end="\r")
            messages = await client.get_messages(email.email)
            if messages:
                break
        for message in messages:
            match = re.search(r'https://beta\.theb\.ai/verify-email\?t=[^ ]+', message.body_text)
            if match:
                return match.group(0)
        return None

    verification_link = await get_verification_link()
    if verification_link:
        print("Verification link found in the email:", verification_link)
        options = Options()
        if headless: options.add_argument("--headless")
        options.add_argument("--disable-gpu")

        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome(options=options)

        # Open the verification link
        driver.get(verification_link)
        time.sleep(5)
        driver.quit()
        print("Email verified successfully!")
    else:
        print("Verification link not found in the email.")
        return 

async def get_api_token(email, fullname="DevsDoCode", password="DevsDoCode@07"):
    """Gets the API token for the user."""
    print("\033[91m--- API TOKEN ---\033[0m")
    url = "https://beta.theb.ai/api/token"
    payload = {
        "username": email.email,
        "password": password
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "X-Client-Language": "en"
    }
    response = requests.post(url, data=payload, headers=headers)
    print("Response Status Code (Token):", response.status_code)
    print("Response Content (Token):", response.json())

    if response.status_code == 200:
        access_token = response.json()['access_token']
        print("Access Token:", access_token)
        return access_token
    else:
        print("Failed to retrieve API token. Error:", response.json().get('data', {}).get('detail', 'Unknown error'))
        return # Exit the function if the token request fails

async def get_organization_id(access_token):
    print("\033[91m--- ORGANIZATION ID ---\033[0m")
    url = "https://beta.theb.ai/api/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "X-Client-Language": "en"
    }

    response = requests.get(url, headers=headers)

    print("Response Status Code:", response.status_code)
    print("Response Content:", response.json())
    if response.status_code == 200:
        print("User logged in successfully!")
        organization_id = response.json()['data']['organizations'][0]['id']
        print("Organization ID:", organization_id)
        return organization_id
    else:
        print("Failed to Login. Error:", response.json())

async def main():
    email = await generate_email()
    await register_user(email)
    client = tempid.Client() 
    await verify_email(email, client, headless=True)
    api_token  = await get_api_token(email)
    organization_id =await get_organization_id(api_token)
    if api_token is not None and organization_id is not None:
        print(f"Successfully Initialized.....\nAPI KEY : \033[92m{api_token}\033[0m\nORGANIZATION ID : \033[92m{organization_id}\033[0m")
        update_file(api_key=api_token, organization_id=organization_id)
    else: print("\033[91mFailed to initialize. Please try again.\033[0m")

def start_async_tasks(at_once: int = 5):
    """Starts multiple instances of an asynchronous main task."""
    threads = []

    # Launch multiple threads to run the async task concurrently
    for _ in range(at_once):
        thread = threading.Thread(target=lambda:asyncio.run(main()))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish execution
    for thread in threads:
        thread.join()

    # Signal that all threads have completed their tasks
    print("\033[92mAll async tasks have been completed.\033[0m")


"""For Multiple Thread Execution i.e. Concurrent Execution"""
if __name__ == '__main__':
    start_async_tasks()

"""For Single Thread Execution i.e . One By One"""
# if __name__ == '__main__':
#     while True:
#         asyncio.run(main())


