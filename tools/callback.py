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

    for attempt in range(3):  
        try:
            response = requests.post(
                GUVI_CALLBACK_URL,
                json=payload,
                timeout=5
            )

            print("GUVI CALLBACK STATUS:", response.status_code)
            print("GUVI RESPONSE:", response.text)

            if response.status_code == 200:
                session.callback_sent = True
                return 

        except Exception as e:
            print("GUVI CALLBACK ERROR:", str(e))

        time.sleep(2)  

    print("GUVI CALLBACK FAILED AFTER RETRIES")
