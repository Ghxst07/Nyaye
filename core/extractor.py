import re

def extract_upi(text):
    pattern = r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}"
    return re.findall(pattern, text)

def extract_phone(text):
    pattern = r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)"
    return re.findall(pattern, text)

def extract_links(text):
    pattern =r"(https?://[^\s]+|www\.[^\s]+|\b[a-zA-Z0-9-]+\.(com|in|net|org|co\.in)\b)"

    return re.findall(pattern, text)

def extract_bank(text):
    pattern = r"\b\d{9,18}\b"
    return re.findall(pattern, text)

SCAM_KEYWORDS = ["urgent", "verify", "blocked", "suspended", "click", "otp"]
def extract_keywords(text):
    found = []
    for k in SCAM_KEYWORDS:
        if k in text.lower():
            found.append(k)
    return found

def extract_all(text):
        return {
        "upiIds": extract_upi(text),
        "phoneNumbers": extract_phone(text),
        "phishingLinks": extract_links(text),
        "bankAccounts": extract_bank(text),
        "suspiciousKeywords": extract_keywords(text)
    }

