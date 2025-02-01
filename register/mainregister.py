import requests
import imaplib
import email
import re
import os
import time
from bs4 import BeautifulSoup

# File paths
email_file_path = "/root/magicnewton/email.txt"

# Email and OTP handling
IMAP_SERVER = "imap.gmail.com"

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

def read_email_credentials(file_path):
    """Reads email:password from the specified file."""
    if not os.path.exists(file_path):
        print("Email file not found.")
        return None, None
    
    with open(file_path, "r") as file:
        line = file.readline().strip()
        if line:
            email, password = line.split(":")
            return email, password
    print("No valid email credentials found.")
    return None, None

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

def fetch_otp(email_address, email_password):
    """Fetch OTP from the email inbox."""
    try:
        print("Waiting for OTP email...")
        time.sleep(10)  # Wait for 10 seconds before fetching OTP

        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(email_address, email_password)
        mail.select("inbox")
        
        status, messages = mail.search(None, 'FROM "noreply@trymagic.com"')
        if messages[0]:
            for num in messages[0].split():
                status, msg_data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])

                otp_code = None
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode(errors="ignore")

                            if content_type == "text/plain":
                                otp_match = re.search(r"\b\d{6}\b", body)
                                if otp_match:
                                    otp_code = otp_match.group()
                                    break  # Stop once OTP is found

                            elif content_type == "text/html" and not otp_code:
                                soup = BeautifulSoup(body, "html.parser")
                                text = soup.get_text()
                                otp_match = re.search(r"\b\d{6}\b", text)
                                if otp_match:
                                    otp_code = otp_match.group()
                                    break
                
                if otp_code:
                    return otp_code

        print("No OTP found.")
    except Exception as e:
        print("Error fetching OTP:", e)
    return None

def verify_otp(email, otp):
    """Verify the OTP with the server."""
    data = {
        "email": email,
        "otp": otp,
        "request_origin_message": "1LK0vb5-f1tlrTpTi0ZMLBxHysd2wqLd3Ihxuj5MZaqz3Y~bTKre5_br5BGi4ORuQkwiDAIUzXadiiPACmzof~PQGxDetncw0UiQ.KDSHYB_wlRVrwWSrBEZFSpMfX51"
    }
    
    try:
        response = requests.post(otp_verification_url, json=data, headers=headers)
        if response.ok:
            print("OTP verification successful!")
            return response.json()
        else:
            print("Error verifying OTP:", response.text)
            return None
    except Exception as e:
        print(f"Exception during OTP verification: {str(e)}")
        return None

if __name__ == "__main__":
    # Read email credentials
    email_address, email_password = read_email_credentials(email_file_path)
    if not email_address or not email_password:
        print("Please provide valid email credentials.")
        exit()
    
    # Step 1: Send OTP request
    otp_request_response = send_otp_request(email_address)
    if not otp_request_response:
        print("Failed to initiate OTP request.")
        exit()
    
    # Step 2: Fetch OTP from the email
    otp = fetch_otp(email_address, email_password)
    if otp:
        print("Fetched OTP:", otp)
        # Step 3: Verify OTP
        verification_response = verify_otp(email_address, otp)
        if verification_response:
            print("Authentication successful!")
    else:
        print("Failed to fetch OTP.")
