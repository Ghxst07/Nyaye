import re

def extract_upi(text):
    pattern = r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}"
    return re.findall(pattern, text)

def extract_phone(text):
    pattern = r"(?:\+91)?[6-9]\d{9}"
    return re.findall(pattern, text)

def extract_links(text):
    pattern = r"https?://[^\s]+"
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

