import requests
import os
import json
from email_otp_auth import read_email_credentials, send_otp_request, fetch_otp, verify_otp

# Define paths
BASE_DIR = "/root/magicnewton"
COOKIE_FILE_PATH = os.path.join(BASE_DIR, "cookies.json")
EMAIL_FILE_PATH = os.path.join(BASE_DIR, "email.txt")

# Headers for authentication
headers = {
    "Content-Type": "application/json",
    "X-Magic-API-Key": "pk_live_C1819D59F5DFB8E2",
    "Accept": "application/json",
    "Origin": "https://magicnewton.com",
    "Referer": "https://magicnewton.com/"
}

def save_cookies(session):
    """Save session cookies to a file."""
    cookies_dict = session.cookies.get_dict()
    with open(COOKIE_FILE_PATH, "w") as file:
        json.dump(cookies_dict, file)
    print(f"Cookies saved to {COOKIE_FILE_PATH}")

if __name__ == "__main__":
    # Read email credentials
    email_address, email_password = read_email_credentials(EMAIL_FILE_PATH)
    if not email_address or not email_password:
        print("Please provide valid email credentials.")
        exit()
    
    # Step 1: Send OTP request
    otp_request_response = send_otp_request(email_address)
    if not otp_request_response or "login_flow_context" not in otp_request_response.get("data", {}):
        print("Failed to initiate OTP request.")
        exit()
    
    login_flow_context = otp_request_response["data"]["login_flow_context"]
    print(f"Retrieved login_flow_context: {login_flow_context}")
    
    # Step 2: Fetch OTP from the email
    otp = fetch_otp(email_address, email_password)
    if not otp:
        print("Failed to fetch OTP.")
        exit()
    
    print("Fetched OTP:", otp)
    
    # Step 3: Verify OTP
    verification_response = verify_otp(email_address, otp, login_flow_context)
    if not verification_response:
        print("OTP verification failed.")
        exit()
    
    print("Authentication successful!")
    
    # Step 4: Start a session and save cookies
    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(requests.utils.cookiejar_from_dict(verification_response.get("data", {})))
    
    save_cookies(session)
    print("Login and cookie retrieval complete!")
