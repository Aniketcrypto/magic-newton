import requests
import imaplib
import email
import re
import os

# File paths
email_file_path = "magicnewton/email.txt"

# Email and OTP handling
IMAP_SERVER = "imap.gmail.com"

headers = {
    "Content-Type": "application/json",
}

otp_request_url = "https://auth.magic.link/send/rpc/auth/magic_auth_login_with_email_otp"
otp_verification_url = "https://auth.magic.link/send/rpc/auth/magic_auth_login_with_email_otp/verify_otp_code"

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
    data = {"email": email, "showUI": False}
    response = requests.post(otp_request_url, json=data, headers=headers)
    if response.ok:
        print("OTP request sent successfully.")
    else:
        print("Error requesting OTP:", response.text)


def fetch_otp(email_address, email_password):
    """Fetch OTP from the email inbox."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(email_address, email_password)
        mail.select("inbox")
        
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
    data = {"email": email, "otp": otp}
    response = requests.post(otp_verification_url, json=data, headers=headers)
    if response.ok:
        print("OTP verification successful!")
    else:
        print("Error verifying OTP:", response.text)


if __name__ == "__main__":
    # Read email credentials
    email_address, email_password = read_email_credentials(email_file_path)

    if not email_address or not email_password:
        print("Please provide valid email credentials.")
        exit()

    # Step 1: Send OTP request
    send_otp_request(email_address)

    # Step 2: Fetch OTP from the email
    otp = fetch_otp(email_address, email_password)

    if otp:
        print("Fetched OTP:", otp)
        # Step 3: Verify OTP
        verify_otp(email_address, otp)
    else:
        print("Failed to fetch OTP.")
