import random
from core.llm_agent import llm_generate

def agent_decide_reply(session):
    """
    Decides the next move based on what data has been extracted so far.
    Prioritizes: Link > UPI > Phone > Stall/Reassure Mix
    """

    if not session.extracted.get("phishingLinks"):
        return llm_generate("ask_for_phishing_link", session.messages)

    if not session.extracted.get("upiIds"):
        return llm_generate("ask_for_upi", session.messages)

    if not session.extracted.get("phoneNumbers"):
        return llm_generate("ask_for_phone", session.messages)

    if random.random() < 0.3:
        return llm_generate("reassure", session.messages)
    
    return llm_generate("stall", session.messages)


def should_stop(session):
    fields = session.extracted

    score = sum([
        len(fields["upiIds"]) > 0,
        len(fields["phishingLinks"]) > 0,
        len(fields["phoneNumbers"]) > 0
    ])

    return score >= 2 or session.turns >= 15

