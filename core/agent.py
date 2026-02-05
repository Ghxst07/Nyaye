import random
import re
from core.llm_agent import llm_generate
from core.extractor import extract_all


def analyze_scammer_intent(last_message: str) -> dict:
    msg_lower = last_message.lower()
    
    intent = {
        "asking_to_click_link": False,
        "asking_for_info": False,
        "providing_link": False,
        "providing_upi": False,
        "providing_phone": False,
        "asking_confirmation": False,
        "threatening": False,
        "requesting_action": False
    }
    
    extracted = extract_all(last_message)
    intent["providing_link"] = len(extracted["phishingLinks"]) > 0
    intent["providing_upi"] = len(extracted["upiIds"]) > 0
    intent["providing_phone"] = len(extracted["phoneNumbers"]) > 0
    
    link_keywords = ["click", "open", "visit", "go to", "check link", "follow link", "tap"]
    intent["asking_to_click_link"] = any(kw in msg_lower for kw in link_keywords)
    
    info_keywords = ["your account", "your number", "your otp", "send otp", "enter", "provide", "share"]
    intent["asking_for_info"] = any(kw in msg_lower for kw in info_keywords)
    
    confirm_keywords = ["did you", "have you", "confirm", "verify", "done", "completed", "received"]
    intent["asking_confirmation"] = any(kw in msg_lower for kw in confirm_keywords)
    
    threat_keywords = ["urgent", "immediately", "blocked", "suspended", "close", "deactivate", "within", "hours"]
    intent["threatening"] = any(kw in msg_lower for kw in threat_keywords)
    
    action_keywords = ["please", "kindly", "request", "need to", "must", "required", "should"]
    intent["requesting_action"] = any(kw in msg_lower for kw in action_keywords)
    
    return intent


def agent_decide_reply(session):
    last_scammer_msg = ""
    if len(session.messages) > 0:
        for msg in reversed(session.messages):
            if msg["role"] == "assistant":
                last_scammer_msg = msg["content"]
                break
    
    scammer_intent = analyze_scammer_intent(last_scammer_msg)
    extracted = session.extracted
    
    has_upi = len(extracted.get("upiIds", [])) > 0
    has_link = len(extracted.get("phishingLinks", [])) > 0
    has_phone = len(extracted.get("phoneNumbers", [])) > 0
    has_bank = len(extracted.get("bankAccounts", [])) > 0
    
    if scammer_intent["providing_upi"] and has_upi:
        if session.turns % 3 == 0:
            return llm_generate("ask_for_phone", session.messages)
        return llm_generate("upi_not_working", session.messages)
    
    if scammer_intent["providing_link"] and has_link:
        if session.turns > 5 and random.random() < 0.5:
            return llm_generate("ask_for_phone", session.messages)
        return llm_generate("link_not_working", session.messages)
    
    if scammer_intent["providing_phone"] and has_phone:
        if session.turns > 3 and random.random() < 0.4:
            return llm_generate("ask_for_phishing_link", session.messages)
        return llm_generate("phone_not_reachable", session.messages)
    
    if scammer_intent["asking_to_click_link"] and has_link:
        return llm_generate("link_not_working", session.messages)
    
    if scammer_intent["asking_confirmation"]:
        if random.random() < 0.7:
            return llm_generate("stall", session.messages)
        return llm_generate("reassure", session.messages)
    
    if scammer_intent["threatening"]:
        return llm_generate("reassure", session.messages)
    
    if scammer_intent["asking_for_info"]:
        if random.random() < 0.6:
            return llm_generate("ask_for_phone", session.messages)
        return llm_generate("stall", session.messages)
    
    if scammer_intent["requesting_action"] and not has_link:
        return llm_generate("ask_for_phishing_link", session.messages)
    
    needed_info = []
    if not has_link:
        needed_info.append("link")
    if not has_upi:
        needed_info.append("upi")
    if not has_phone:
        needed_info.append("phone")
    if not has_bank:
        needed_info.append("bank")
    
    if len(needed_info) > 0:
        if session.turns % 2 == 1:
            if "link" in needed_info and random.random() < 0.7:
                return llm_generate("ask_for_phishing_link", session.messages)
            elif "upi" in needed_info and random.random() < 0.7:
                return llm_generate("ask_for_upi", session.messages)
            elif "phone" in needed_info and random.random() < 0.6:
                return llm_generate("ask_for_phone", session.messages)
    
    if session.turns > 0 and session.turns % 4 == 0:
        return llm_generate("reassure", session.messages)
    
    if random.random() < 0.5:
        if not has_link:
            return llm_generate("ask_for_phishing_link", session.messages)
        elif not has_upi:
            return llm_generate("ask_for_upi", session.messages)
        else:
            return llm_generate("stall", session.messages)
    
    return llm_generate("stall", session.messages)


def should_stop(session):
    fields = session.extracted

    score = sum([
        len(fields["upiIds"]) > 0,
        len(fields["phishingLinks"]) > 0,
        len(fields["phoneNumbers"]) > 0,
        len(fields["bankAccounts"]) > 0
    ])

    has_enough_info = score >= 2
    too_many_turns = session.turns >= 20
    
    if len(session.messages) >= 6:
        recent_scammer_msgs = [
            msg["content"] for msg in session.messages[-6:] 
            if msg["role"] == "assistant"
        ]
        if len(recent_scammer_msgs) >= 3:
            avg_length = sum(len(msg.split()) for msg in recent_scammer_msgs) / len(recent_scammer_msgs)
            scammer_giving_up = avg_length < 3
            if scammer_giving_up and score > 0:
                return True
    
    return has_enough_info or too_many_turns

