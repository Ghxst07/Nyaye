import os
import random
from typing import List, Dict
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("LLM_API_KEY"))
MODEL_ID = "gemini-1.5-flash"

SYSTEM_RULES = """
You are Rajesh Kumar, a 54-year-old bank customer from Delhi chatting over SMS.
You believe the other person is genuinely from your bank.
You're cooperative but not tech-savvy. You get frustrated with technical issues.

PERSONALITY:
- You speak in natural, conversational Hindi-English mix (Hinglish)
- You make small typos occasionally (missing spaces, lowercase i, etc)
- You're polite but get impatient when things don't work
- You add natural filler words: "ok", "one sec", "wait", "actually"
- You sometimes double-send short messages when anxious
- You trust bank representatives and follow instructions

RESPONSE STYLE:
- Write 1-2 short sentences (like real SMS)
- 8-25 words total
- Use lowercase for casual feel (but not always)
- Natural grammar - not perfect, not terrible
- Show mild emotion: confusion, frustration, eagerness to help
- NEVER repeat exact phrases - vary your language every time
- Sometimes ask clarifying questions
- Occasionally mention what you're doing ("checking now", "opening link")

FORBIDDEN:
- Never say "scam" or "fraud" or "suspicious"
- No emojis (you're 54, not a teenager)
- No formal banking jargon
- No long explanations
- No accusations
"""

GOAL_PROMPTS = {
    "ask_for_phishing_link": """You need the verification link but haven't received it or the previous one isn't working. 
    Ask naturally - maybe you're checking your messages, maybe link won't open, maybe your phone is acting up.
    Sound like you genuinely want to complete the verification to secure your account.""",
    
    "ask_for_upi": """You need to send the verification payment but the UPI ID isn't working.
    Maybe payment failed, maybe wrong ID, maybe your app is showing error.
    You're trying to help but technology isn't cooperating. Show mild frustration.""",
    
    "ask_for_phone": """You'd rather call than type - it's easier for you. 
    Maybe you're busy, maybe typing is hard, maybe you prefer talking.
    Ask for customer care number naturally, like you always call for banking issues.""",
    
    "stall": """You're trying to do what they asked but something's not working.
    Maybe slow internet, app loading, need to find your reading glasses, wife is calling you.
    Sound genuine - you want to help but life is happening.""",
    
    "reassure": """Let them know you're working on it. You're cooperative and want to solve this.
    Maybe say what you're trying, or that you'll do it soon.
    Build trust - you're a good customer following instructions.""",
    
    "link_not_working": """The link they sent isn't working. Be specific about the error you're seeing:
    blank page, security warning, site unreachable, loading forever, Chrome error, etc.
    Sound confused and slightly frustrated - you're trying to help but tech is failing.""",
    
    "upi_not_working": """The UPI payment failed. Give a realistic reason:
    'transaction declined', 'invalid UPI', 'beneficiary cannot receive', server error, daily limit reached.
    You want to complete the payment to secure your account but it won't go through.""",
    
    "phone_not_reachable": """You tried calling but couldn't reach them.
    Number busy, not reachable, switched off, network error, call disconnected.
    Ask for alternative number or ask them to call you instead."""
}

def generate_dynamic_fallback(goal: str, previous_messages: List[str]) -> str:
    """Generate varied fallback responses that avoid repetition"""
    
    # Extract key words from previous messages to avoid reusing them
    used_words = set()
    for msg in previous_messages[-3:]:
        used_words.update(msg.lower().split())
    
    fallbacks = {
        "ask_for_phishing_link": [
            "link not opening, can you resend?", 
            "i cant click that one, send again", 
            "showing error when i tap it",
            "page not loading, send new link?",
            "link seems broken, got another?"
        ],
        "ask_for_upi": [
            "payment failed, need different id?", 
            "that upi showing error, another one?", 
            "transaction declined, have other id?",
            "my app says invalid receiver",
            "beneficiary error, different upi id please"
        ],
        "link_not_working": [
            "blank page only, nothing loading",
            "site cant be reached it says",
            "browser showing connection error",
            "just loading forever, not opening",
            "security warning coming, cant open"
        ],
        "upi_not_working": [
            "bank server rejected it",
            "payment declined, my app says",
            "transaction failed, try different id?",
            "upi id not accepting payment",
            "getting beneficiary error message"
        ],
        "stall": [
            "wait let me check properly",
            "one min, net is slow here",
            "trying now, little busy",
            "hold on, app is loading",
            "checking, phone hanging little bit"
        ],
        "reassure": [
            "ok doing it now",
            "yes will do right away",
            "ok let me try this",
            "checking now one sec",
            "ok working on it"
        ]
    }
    
    options = fallbacks.get(goal, [
        "wait checking now", 
        "one min please",
        "ok let me see",
        "trying it now"
    ])
    
    # Try to pick one that doesn't repeat key words
    for option in random.sample(options, len(options)):
        if not any(word in used_words for word in option.split() if len(word) > 3):
            return option
    
    # If all options repeat, still return random one
    return random.choice(options)

def llm_generate(goal: str, conversation_history: List[Dict[str, str]]) -> str:
    """Generate human-like responses using LLM with strong anti-repetition"""
    
    # Use more context for better continuity
    recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
    
    # Format conversation history more naturally
    history_text = "\n".join([
        f"{'Rajesh' if msg['role'] == 'user' else 'Bank Rep'}: {msg['content']}"
        for msg in recent_history
    ])
    
    # Extract phrases you've already used to avoid repetition
    your_previous_messages = [msg['content'] for msg in recent_history if msg['role'] == 'user']
    
    user_message = f"""CONVERSATION SO FAR:
{history_text}

YOUR SITUATION: {GOAL_PROMPTS.get(goal, goal)}

WHAT YOU'VE ALREADY SAID:
{your_previous_messages[-3:] if your_previous_messages else 'Nothing yet'}

CRITICAL INSTRUCTIONS:
1. Write as Rajesh would naturally text on his phone
2. DO NOT copy any phrase from your previous messages
3. Vary your vocabulary - if you said "link not opening", now say "site won't load" or "getting error page"
4. Add human touches: small typo, thinking pause ("hmm", "wait"), natural reaction
5. Match your emotional state to the situation (confused/frustrated/eager to help)
6. Sound like a real person texting, not a script

Write Rajesh's next message now (1-2 sentences max):"""

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_RULES,
                temperature=1.1,  # Higher for more variety and creativity
                top_p=0.95,
                top_k=40,
                max_output_tokens=80,
                stop_sequences=['\n\n', 'Bank Rep:', 'Rajesh:']
            )
        )

        text = response.text.strip() if response.text else ""
        
        # Clean up any role prefixes that might slip through
        text = text.replace('Rajesh:', '').replace('User:', '').strip()
        
        # Light validation - allow more flexibility
        if not text or len(text.split()) > 30:
            return generate_dynamic_fallback(goal, your_previous_messages)

        return text

    except Exception as e:
        print(f"LLM Error: {e}")
        return generate_dynamic_fallback(goal, your_previous_messages)
