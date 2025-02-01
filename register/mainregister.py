import requests
import imaplib
import email
import re
import os

# File paths
email_file_path = "/root/magicnewton/email.txt"

# Email and OTP handling
IMAP_SERVER = "imap.gmail.com"

# Verified domain for Magic authentication
DOMAIN = "magicnewton.com"

# Updated headers with production domain
headers = {
    "Content-Type": "application/json",
    "X-Magic-API-Key": "pk_live_C1819D59F5DFB8E2",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en_US",
    "Origin": "https://magicnewton.com",
    "Referer": "https://magicnewton.com/",
    "X-Magic-Sdk": "magic-sdk-js",
    "X-Magic-Sdk-Version": "21.0.0",
    "Host": "api.magic.link",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

otp_request_url = "https://api.magic.link/v2/auth/user/login/email_otp/start"
otp_verification_url = "https://api.magic.link/v2/auth/user/login/email_otp/verify"

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
        "showUI": False,
        "cryptoWalletType": "METAMASK",
        "network": "mainnet",
        "configuration": {
            "redirectURI": "https://magicnewton.com/callback",
            "walletConnectorConfiguration": {
                "networkConfiguration": {
                    "chainId": "0x1",
                }
            }
        },
        "deviceInfo": {
            "sdk": "magic-sdk-js",
            "sdkVersion": "21.0.0",
            "platform": "web",
            "platformVersion": "web",
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "method": "magic_downloadable",
            "language": "en-US"
        }
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
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(email_address, email_password)
        mail.select("inbox")
        
        # Wait a bit for the email to arrive and then search
        status, messages = mail.search(None, '(UNSEEN FROM "noreply@trymagic.com")')
        if messages[0]:
            for num in messages[0].split():
                status, msg_data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            otp_match = re.search(r"\b\d{6}\b", body)
                            if otp_match:
                                return otp_match.group()
        print("No OTP found.")
    except Exception as e:
        print("Error fetching OTP:", e)
    return None

def verify_otp(email, otp):
    """Verify the OTP with the server."""
    data = {
        "email": email,
        "otp": otp,
        "configuration": {
            "redirectURI": "https://magicnewton.com/callback",
            "walletConnectorConfiguration": {
                "networkConfiguration": {
                    "chainId": "0x1",
                }
            }
        },
        "deviceInfo": {
            "sdk": "magic-sdk-js",
            "sdkVersion": "21.0.0",
            "platform": "web",
            "platformVersion": "web",
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "method": "magic_downloadable",
            "language": "en-US"
        }
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
