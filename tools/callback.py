import requests
import time


GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"


def send_guvi_callback(session):

    payload = {
        "sessionId": session.session_id,
        "scamDetected": True,
        "totalMessagesExchanged": session.turns,
        "extractedIntelligence": session.extracted,
        "agentNotes": "Scammer used urgency and redirection tactics"
    }

    try:
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload,
            timeout=5
        )

        print("GUVI CALLBACK STATUS:", response.status_code)
        print("GUVI RESPONSE:", response.text)

    except Exception as e:
        print("GUVI CALLBACK ERROR:", str(e))
