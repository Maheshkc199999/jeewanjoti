from django.core.cache import cache
import random
from datetime import datetime, timedelta

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def store_otp(email, otp, expiration_minutes=5):
    expiration_time = datetime.now() + timedelta(minutes=expiration_minutes)
    cache.set(f"otp:{email}", {"otp": otp, "expires_at": expiration_time}, timeout=expiration_minutes * 60)

def validate_otp(email, email_otp):  
    otp_data = cache.get(f"otp:{email}")
    if not otp_data:
        return False, "OTP expired or not found."

    current_time = datetime.now()
    if current_time > otp_data["expires_at"]:
        cache.delete(f"otp:{email}")
        return False, "OTP expired."

    if otp_data["otp"] == email_otp:
        cache.delete(f"otp:{email}")
        return True, "OTP verified successfully."

    return False, "Invalid OTP."


