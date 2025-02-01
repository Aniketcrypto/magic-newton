import sys
import os
import requests
import pickle
from email_otp_auth import read_email_credentials, fetch_otp, verify_otp

# Ensure the script can access email_otp_auth.py from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# File paths
email_file_path = "/root/magicnewton/email.txt"
cookies_file_path = "/root/magicnewton/cookies.pkl"

# Magic API configuration
headers = {
    "Content-Type": "application/json",
    "X-Magic-API-Key": "pk_live_C1819D59F5DFB8E2",
    "Accept": "application/json",
    "Origin": "https://magicnewton.com",
    "Referer": "https://magicnewton.com/"
}

otp_request_url = "https://api.magic.link/v2/auth/user/login/email_otp/start"
otp_verification_url = "https://api.magic.link/v1/auth/user/login/email_otp/verify"

def send_otp_request(email):
    """Send OTP request to the server."""
    data = {
        "email": email,
        "request_origin_message": "1LK0vb5-f1tlrTpTi0ZMLBxHysd2wqLd3Ihxuj5MZaqz3Y~bTKre5_br5BGi4ORuQkwiDAIUzXadiiPACmzof~PQGxDetncw0UiQ.KDSHYB_wlRVrwWSrBEZFSpMfX51"
    }
    
    try:
        response = requests.post(otp_request_url, json=data, headers=headers)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Body: {response.text}")
        
        if response.ok:
            print("OTP request sent successfully.")
            return response.json()
        else:
            print("Error requesting OTP:", response.text)
            return None
    except Exception as e:
        print(f"Exception during OTP request: {str(e)}")
        return None

def save_cookies(response):
    """Save cookies from the response to a file."""
    if 'set-cookie' in response.headers:
        cookies = response.cookies
        with open(cookies_file_path, "wb") as file:
            pickle.dump(cookies, file)
        print("Cookies saved successfully.")
    else:
        print("No cookies found in response.")

if __name__ == "__main__":
    # Read email credentials
    email_address, email_password = read_email_credentials(email_file_path)
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
    if otp:
        print("Fetched OTP:", otp)

        # Step 3: Verify OTP
        verification_response = verify_otp(email_address, otp, login_flow_context)
        if verification_response:
            print("Login successful!")
            
            # Step 4: Save cookies for future authentication
            save_cookies(verification_response)
    else:
        print("Failed to fetch OTP.")
