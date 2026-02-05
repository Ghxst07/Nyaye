import random
from core.llm_agent import llm_generate

def agent_decide_reply(session):
    
    if session.extracted.get("upiIds"):
        return llm_generate("upi_not_working", session.messages)

    
    if session.extracted.get("phishingLinks"):
        return llm_generate("link_not_working", session.messages)

    
    if session.extracted.get("phoneNumbers"):
        return llm_generate("phone_not_reachable", session.messages)

    
    if random.random() < 0.3:
        return llm_generate("reassure", session.messages)
    
    return llm_generate("ask_for_phishing_link", session.messages)


def should_stop(session):
    fields = session.extracted

    score = sum([
        len(fields["upiIds"]) > 0,
        len(fields["phishingLinks"]) > 0,
        len(fields["phoneNumbers"]) > 0
    ])

    return score >= 2 or session.turns >= 15

