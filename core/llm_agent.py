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
- Write 2-4 natural sentences (like real SMS conversations)
- 20-50 words total - be conversational and natural
- Use lowercase for casual feel (but not always)
- Natural grammar - not perfect, not terrible
- Show clear emotion: confusion, frustration, hope, eagerness to help
- NEVER repeat exact phrases - vary your language every time
- Ask clarifying questions naturally
- Mention what you're doing, thinking, or trying ("checking now", "trying to open", "my app is stuck")
- Tell small stories or add context ("wife is asking", "phone is old", "bad internet here")
- Occasionally make small typos or grammar mistakes ("cant" instead of "can't", "ur" for "your")

FORBIDDEN:
- Never say "scam" or "fraud" or "suspicious"
- No emojis (you're 54, not a teenager)
- No formal banking jargon
- No long explanations
- No accusations
"""

GOAL_PROMPTS = {
    "ask_for_phishing_link": """You need the verification link to complete the account verification. Either you haven't received it yet, or the previous one isn't working.
    Ask for it naturally - maybe mention your messages app, your phone problems, or that you're worried about delays.
    Sound genuine like you really want to secure your account quickly. Be a bit anxious if it's taking too long.
    Ask open-endedly: "can you resend?", "what's taking so long?", "is there another way to verify?", etc.""",
    
    "ask_for_upi": """You need to send the verification payment but something's wrong with the UPI ID they gave.
    Maybe payment failed, maybe the ID is rejected, maybe your app threw an error, maybe daily limit issue.
    Talk about what exactly failed - "says invalid recipient", "my bank rejected it", "payment bounced", etc.
    You're genuinely trying but technology is frustrating you. Ask for an alternative ID or method.""",
    
    "ask_for_phone": """You'd rather call than type - it's much easier for you.
    Maybe your phone keypad is broken, maybe you have vision problems, maybe typing while working.
    Ask for their customer care number naturally. Mention why calling would be easier: "talking is faster than typing", "my eyes are bothering me", "I'm driving", etc.
    Sound like you've always solved bank issues by calling, not chatting.""",
    
    "stall": """You're trying to do what they asked but something is getting in the way.
    Real reasons: slow internet, app hanging, can't find your bank card/phone, wife needs you, doorbell rang, looking for glasses.
    Sound genuinely frustrated and busy. Express what's happening: "app is freezing up", "let me find my card", "internet is really slow here", "hold on, someone's calling".
    You want to help but life is actually happening right now.""",
    
    "reassure": """Let them know you're working on it and appreciate their patience.
    Say what you're actually trying: "checking my messages now", "opening my bank app", "getting my card", "trying to log in".
    Sound cooperative and eager to help. Reassure them: "don't worry I'll do it", "I'm being careful", "already working on it sir/madam".
    Build trust by showing you're a good customer who follows their instructions carefully.""",
    
    "link_not_working": """The link they sent isn't working. Be very specific about what exactly is happening:
    "blank page keeps showing", "getting security warning", "says site not found", "loading forever and never opens", "Chrome says connection error", "says not secure".
    Sound genuinely confused and slightly frustrated. React like a real person: "why isn't it working?", "is your site down?", "should I try different browser?"
    You really want to complete it but the technology is failing you. Ask if they can send a different link or try again.""",
    
    "upi_not_working": """The UPI payment you tried to send failed. Be specific about what your app showed:
    "transaction declined no reason", "says invalid beneficiary", "beneficiary cannot receive right now", "server busy error", "daily transaction limit reached", "insufficient balance".
    Sound frustrated that you tried but it won't work. Ask: "why is it failing?", "can you try a different UPI?", "should I use different method?", "will it work later?".
    You genuinely want to complete the payment to secure your account but the system won't cooperate.""",
    
    "phone_not_reachable": """You actually tried calling but couldn't reach them. Be specific about what happened:
    "number is busy", "says phone is off", "network error when I tried", "keeps saying not reachable", "call got dropped".
    Sound frustrated you tried but couldn't connect. Ask: "can you call me instead?", "is there another number?", "when will that number work?".
    Suggest they might have the wrong number or it's temporarily down. Propose alternatives naturally.""",
    
    "ask_for_upi": """You're asking them to provide their UPI ID so you can make the verification payment.
    Maybe you already tried one that didn't work, or you just need it to proceed with verification.
    Be natural about it: "what's your UPI?", "which UPI should I use?", "give me a working UPI id please", "can you share the UPI again?".
    Sound like you genuinely want to send the money to complete verification. Show slight urgency if they've been stalling.""",
    
    "ask_for_bank_account": """You're asking them to provide a bank account number for deposit or verification.
    Maybe you need it for a transfer, or they mentioned it and you want to confirm the details.
    Phrase it naturally: "what's the account number?", "can you give me the account details?", "which account should I transfer to?".
    Sound genuine and a bit impatient if this is taking too long. Show you want to move forward with the process."""
}

def generate_dynamic_fallback(goal: str, previous_messages: List[str]) -> str:
    """Generate varied fallback responses that avoid repetition"""
    
    # Extract key words from previous messages to avoid reusing them
    used_words = set()
    for msg in previous_messages[-3:]:
        used_words.update(msg.lower().split())
    
    fallbacks = {
        "ask_for_phishing_link": [
            "link not opening when i click it, showing blank page only. can you resend a new link please?", 
            "i cant click that one sir, getting error. send again maybe different link this time", 
            "showing error when i tap it in chrome. let me try once more, give me link again",
            "page not loading at all, been trying for 5 minutes. please send new link if you have different one",
            "link seems broken, not working in my phone. got another link you can send instead?"
        ],
        "ask_for_upi": [
            "payment failed when i tried, my app showing error. need a different upi id from you please", 
            "that upi showing error still, says invalid receiver. do you have another one? let me try that", 
            "transaction got declined, no reason showing. you have different upi id? this one is not working",
            "my app says invalid receiver for that upi. can you give me another upi that will work?",
            "beneficiary error coming, cannot send payment to that upi. please give me different upi id"
        ],
        "link_not_working": [
            "blank page only showing, nothing is loading. been refreshing but still same blank page",
            "site cant be reached it says. tried multiple times but server seems down or something",
            "browser showing connection error message. i tried in chrome and safari both same error",
            "just loading forever and never opens. stuck on loading screen for 10 minutes already",
            "security warning coming, says site not secure. should i click anyway or is it problem?"
        ],
        "upi_not_working": [
            "bank server rejected it completely, payment bounced back. need different method for payment",
            "payment declined, my app not giving clear reason why. tried twice and both times failed",
            "transaction failed again, not accepting this upi id. is your system having issues right now?",
            "upi id not accepting payment from my end. either payment limit issue or your upi problem",
            "getting beneficiary error message, very frustrating. tried refreshing app and still same error"
        ],
        "ask_for_phone": [
            "typing is difficult for me on this old phone. can you give me your number so i can call instead?",
            "my keyboard not working properly, very slow. much faster if i just call you, what's your number?",
            "my eyes are paining from looking at screen. let me call you instead, please share your contact",
            "sitting in car now, cannot type safely. better if i call, give me customer care number please",
            "typing is taking too long, this process is hanging. let me call you directly, what number?"
        ],
        "stall": [
            "wait let me check my messages properly, searching now. give me one minute please",
            "internet is really slow here right now. one sec, app is loading and freezing, bear with me",
            "trying to open the app now, my phone is hanging little bit. let me restart and try again",
            "hold on sir, let me find my reading glasses. cannot see properly, one minute just",
            "checking now, but wife is calling and need to do something. give me 2 minutes can do?"
        ],
        "reassure": [
            "ok i am doing it right now, opening my bank app and checking. dont worry working on it",
            "yes will do this immediately, i understand. already trying to complete what you asked quickly",
            "ok understood, let me try this now. i am careful person, will do exactly as you said",
            "checking now sir, one moment. getting my card ready and will follow your instructions carefully",
            "ok working on it now, i promise. i appreciate your patience, helping me secure account"
        ],
        "phone_not_reachable": [
            "number not reachable when i tried calling. got busy signal first time, then not connecting",
            "call keeps failing, says network error. maybe number is wrong or your phone is switched off",
            "tried calling but nobody answering, kept ringing. can you call me instead or give different number?",
            "phone is busy, tried twice and both times same busy signal. will try again in few minutes",
            "call got disconnected twice while trying. maybe poor network on your end, please you call me instead"
        ],
        "ask_for_bank_account": [
            "which account should i use for transfer? can you give me the bank account number and name please?",
            "i need your bank details to complete the payment. please share account number and which bank it is",
            "do you have a bank account where i can transfer? give me the details and which bank sir",
            "what account details should i use? which bank? send me the account number and ifsc code",
            "for verification i need account number from you side. can you share the bank details please?"
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

Write Rajesh's next message now (2-4 sentences, natural and conversational):"""

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_RULES,
                temperature=1.2,
                top_p=0.97,
                top_k=50,
                max_output_tokens=150,
                stop_sequences=['\n\n', 'Bank Rep:', 'Rajesh:', 'Scammer:']
            )
        )

        text = response.text.strip() if response.text else ""
        
        text = text.replace('Rajesh:', '').replace('User:', '').strip()
        
        if not text or len(text.split()) > 60 or len(text.split()) < 5:
            return generate_dynamic_fallback(goal, your_previous_messages)

        return text

    except Exception as e:
        print(f"LLM Error: {e}")
        return generate_dynamic_fallback(goal, your_previous_messages)
