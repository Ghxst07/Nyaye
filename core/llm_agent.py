import os
from typing import List, Dict

from google import genai
from google.genai import types


client = genai.Client(api_key=os.getenv("LLM_API_KEY"))


MODEL_ID = "gemini-1.5-flash" 



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
"""

GOAL_PROMPTS = {
    "ask_for_phishing_link": "Ask them to resend the payment link because it is not opening.",
    "ask_for_upi": "Say the UPI payment failed and ask them to resend the UPI ID.",
    "ask_for_phone": "Ask for their customer support phone number.",
    "stall": "Say you are trying and ask them to wait.",
    "reassure": "Acknowledge and say you are checking."
}



def fallback_reply(goal: str) -> str:
    return {
        "ask_for_phishing_link": "The link isn’t opening on my phone, can you send it again?",
        "ask_for_upi": "UPI payment failed from my side, please resend the UPI ID.",
        "ask_for_phone": "I can’t reach support, can you share your contact number?",
        "stall": "I’m trying again, please wait a moment.",
        "reassure": "Okay, I’m checking it now."
    }.get(goal, "Please wait, I’m checking.")



def llm_generate(
    goal: str,
    conversation_history: List[Dict[str, str]]
) -> str:
    """
    Executor for the agent using Google GenAI SDK v1.0+
    """

    recent_history = conversation_history[-6:]

    
    user_message = f"""
    Conversation so far:
    {recent_history}

    Current goal:
    {GOAL_PROMPTS[goal]}

    Write the reply now.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_RULES,  
                temperature=0.7,                  
                max_output_tokens=50,             
                stop_sequences=['\n']             
            )
        )


        text = response.text.strip() if response.text else ""

        if len(text.split()) > 25:
            return fallback_reply(goal)

        return text

    except Exception as e:
        return fallback_reply(goal)