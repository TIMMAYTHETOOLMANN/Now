import os
import sys

import requests


def get_temp_number(api_key, country_code="86"):
    """Request a temporary phone number from the temp-number API."""
    url = "https://api.temp-number.com/v1/number"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {"country_code": country_code}
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if response.status_code == 200:
        data = response.json()
        return data["number"]
    else:
        print(f"Failed to get temporary number: {response.status_code}")
        return None


def receive_verification_code(number, api_key):
    """Retrieve the verification code sent to the temporary number."""
    url = f"https://api.temp-number.com/v1/number/{number}/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        data = response.json()
        messages = data.get("messages", [])
        if not messages:
            print("No messages received yet.")
            return None
        return messages[0]["text"]
    else:
        print(f"Failed to receive verification code: {response.status_code}")
        return None


if __name__ == "__main__":
    api_key = os.environ.get("TEMP_NUMBER_API_KEY")
    if not api_key:
        print(
            "Error: TEMP_NUMBER_API_KEY environment variable is not set.\n"
            "Set it before running the script:\n"
            "  export TEMP_NUMBER_API_KEY='your_api_key_here'"
        )
        sys.exit(1)

    temp_number = get_temp_number(api_key)
    if temp_number:
        print(f"Temporary number obtained: {temp_number}")
        verification_code = receive_verification_code(temp_number, api_key)
        if verification_code:
            print(f"Verification code received: {verification_code}")
        else:
            print("Failed to receive verification code.")
    else:
        print("Failed to obtain a temporary number.")
