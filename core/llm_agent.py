import os
import random
from typing import List, Dict
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("LLM_API_KEY"))
MODEL_ID = "gemini-1.5-flash"

# Improved System Rules to encourage natural variation
SYSTEM_RULES = """
You are a normal Indian bank customer chatting over SMS.
You believe the other person is a bank representative.
You are cooperative but slightly confused.

Rules you MUST follow:
- Write ONLY one sentence
- Max 20 words
- No stories, no metaphors
- No explanations
- No emojis
- Never accuse or mention scam
- Sound natural and human
- IMPORTANT: diverse phrasing. If you see you have already asked something similar in the history, ASK IT DIFFERENTLY.
"""

# Updated Goal Prompts with specific instructions for variation
GOAL_PROMPTS = {
    "ask_for_phishing_link": "Ask for the link. If you already asked, say the previous one is broken or you can't click it.",
    "ask_for_upi": "Ask for UPI ID. If you have one, say it failed payment and ask for a different one.",
    "ask_for_phone": "Ask for a phone number to call. Say typing is difficult.",
    "stall": "Say you are trying to do what they asked but internet is slow or you are confused.",
    "reassure": "Acknowledge their instruction and say you are working on it.",
    # New goals for your updated logic
    "link_not_working": "Complain that the link they sent is not loading or showing an error.",
    "upi_not_working": "Complain that the payment to their UPI ID failed/bounced.",
    "phone_not_reachable": "Complain that the number they gave is busy or not connecting."
}

def fallback_reply(goal: str) -> str:
    # Random selection from a list to avoid exact repetition even in fallback
    fallbacks = {
        "ask_for_phishing_link": [
            "The link isn’t opening, send again?", 
            "I can't click that, can you resend?", 
            "It gives an error, send a new link."
        ],
        "ask_for_upi": [
            "Payment failed, give me another ID.", 
            "UPI server error, do you have another ID?", 
            "That ID is invalid, send fresh one."
        ],
        "link_not_working": [
            "This link is just showing a blank page.",
            "It says site can't be reached.",
            "Still not opening, is the server down?"
        ],
        "upi_not_working": [
            "Bank server rejected this UPI.",
            "It says payment declined for this ID.",
            "My app shows 'Invalid Receiver' for that UPI."
        ]
    }
    # specific fallback or generic catch-all
    options = fallbacks.get(goal, ["Please wait, I’m checking.", "One minute, internet is slow."])
    return random.choice(options)

def llm_generate(goal: str, conversation_history: List[Dict[str, str]]) -> str:
    
    # Get last few messages to check for repetition
    recent_history = conversation_history[-6:]
    
    # We explicitly point out to the LLM that it should check history
    user_message = f"""
    conversation_history_so_far:
    {recent_history}

    YOUR CURRENT GOAL: "{GOAL_PROMPTS.get(goal, goal)}"

    INSTRUCTION: Look at the last message from 'user' (which is you). 
    Do NOT repeat the exact same phrase. 
    If you just said "The link isn't working", now say "It's giving a 404 error" or "It won't load".
    
    Write the reply now:
    """

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_RULES,
                temperature=0.85, # Increased temperature for more variety
                max_output_tokens=60,
                stop_sequences=['\n']
            )
        )

        text = response.text.strip() if response.text else ""

        if not text or len(text.split()) > 25:
            return fallback_reply(goal)

        return text

    except Exception as e:
        print(f"LLM Error: {e}")
        return fallback_reply(goal)