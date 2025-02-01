import requests
import imaplib
import email
import re
import os
import json
import time
from http.cookiejar import LWPCookieJar
from bs4 import BeautifulSoup

# File paths
email_file_path = "/root/magicnewton/email.txt"
cookie_file_path = "/root/magicnewton/cookies.txt"

# Email and OTP handling
IMAP_SERVER = "imap.gmail.com"

# Magic API configuration
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en_US"
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
    """Send OTP request to the Magic API."""
    data = {"email": email}
    try:
        response = requests.post(otp_request_url, json=data, headers=headers)
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
        time.sleep(10)

        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(email_address, email_password)
        mail.select("inbox")
        
        status, messages = mail.search(None, 'FROM "noreply@trymagic.com"')
        email_ids = messages[0].split()
        
        if email_ids:
            email_ids = sorted(email_ids, key=lambda x: int(x), reverse=True)  # Get the latest email first
            
            for num in email_ids:
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
                                    break

                            elif content_type == "text/html" and not otp_code:
                                soup = BeautifulSoup(body, "html.parser")
                                otp_candidates = soup.find_all("span")
                                for candidate in otp_candidates:
                                    text = candidate.get_text(strip=True)
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

def verify_otp(email, otp, login_flow_context):
    """Verify the OTP with the Magic API."""
    data = {
        "email": email,
        "one_time_code": otp,
        "login_flow_context": login_flow_context
    }
    
    try:
        session = requests.Session()
        response = session.post(otp_verification_url, json=data, headers=headers)
        if response.ok:
            print("OTP verification successful!")
            save_cookies(session.cookies)
            return response.json()
        else:
            print("Error verifying OTP:", response.text)
            return None
    except Exception as e:
        print(f"Exception during OTP verification: {str(e)}")
        return None

def save_cookies(cookie_jar):
    """Save cookies to a file for future use."""
    try:
        with open(cookie_file_path, "w") as file:
            json.dump(cookie_jar.get_dict(), file)
        print("Cookies saved successfully.")
    except Exception as e:
        print("Error saving cookies:", e)

if __name__ == "__main__":
    email_address, email_password = read_email_credentials(email_file_path)
    if not email_address or not email_password:
        print("Please provide valid email credentials.")
        exit()
    
    otp_request_response = send_otp_request(email_address)
    if not otp_request_response or "login_flow_context" not in otp_request_response.get("data", {}):
        print("Failed to initiate OTP request.")
        exit()
    
    login_flow_context = otp_request_response["data"]["login_flow_context"]
    print(f"Retrieved login_flow_context: {login_flow_context}")
    
    otp = fetch_otp(email_address, email_password)
    if otp:
        print("Fetched OTP:", otp)
        verification_response = verify_otp(email_address, otp, login_flow_context)
        if verification_response:
            print("Login successful! Cookies saved.")
    else:
        print("Failed to fetch OTP.")
