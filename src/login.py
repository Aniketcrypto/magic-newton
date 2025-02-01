import requests
import os
import time
from email_otp_auth import read_email_credentials, fetch_otp, verify_otp

# File paths
email_file_path = "/root/magicnewton/email.txt"
cookie_file_path = "/root/magicnewton/cookies.txt"

# API Endpoints
otp_request_url = "https://api.magic.link/v2/auth/user/login/email_otp/start"
otp_verification_url = "https://api.magic.link/v1/auth/user/login/email_otp/verify"

# Headers
headers = {
    "Content-Type": "application/json",
    "X-Magic-API-Key": "pk_live_C1819D59F5DFB8E2",
    "Accept": "application/json",
    "Origin": "https://magicnewton.com",
    "Referer": "https://magicnewton.com/"
}

def send_otp_request(email):
    """Send OTP request and retrieve request_origin_message."""
    data = {"email": email}
    
    try:
        response = requests.post(otp_request_url, json=data, headers=headers)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        if response.ok:
            response_json = response.json()
            request_origin_message = response_json.get("data", {}).get("request_origin_message", None)
            login_flow_context = response_json.get("data", {}).get("login_flow_context", None)
            
            if not request_origin_message or not login_flow_context:
                print("Missing request_origin_message or login_flow_context in response.")
                return None, None
            
            print("OTP request sent successfully.")
            return request_origin_message, login_flow_context
        else:
            print("Error requesting OTP:", response.text)
            return None, None
    except Exception as e:
        print(f"Exception during OTP request: {str(e)}")
        return None, None

if __name__ == "__main__":
    # Read email credentials
    email_address, email_password = read_email_credentials(email_file_path)
    if not email_address or not email_password:
        print("Please provide valid email credentials.")
        exit()

    # Step 1: Send OTP request
    request_origin_message, login_flow_context = send_otp_request(email_address)
    if not request_origin_message or not login_flow_context:
        print("Failed to initiate OTP request.")
        exit()

    # Step 2: Fetch OTP from the email
    otp = fetch_otp(email_address, email_password)
    if otp:
        print("Fetched OTP:", otp)
        
        # Step 3: Verify OTP
        verification_response = verify_otp(email_address, otp, login_flow_context)
        if verification_response:
            print("Authentication successful!")
            
            # Save cookies for future requests
            cookies = requests.utils.dict_from_cookiejar(verification_response.cookies)
            with open(cookie_file_path, "w") as f:
                f.write(str(cookies))
            print("Cookies saved successfully.")

    else:
        print("Failed to fetch OTP.")
