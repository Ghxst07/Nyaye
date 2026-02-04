
"""Ye wala abhi rule based hai yaha par ai agent abhi tak dala nhi hai"""

def agent_decide_reply(session, last_message):

    if not session.extracted["phishingLinks"]:
        return "The page is not opening. Please share the payment link again."

    if not session.extracted["upiIds"]:
        return "UPI payment failed. Can you send the UPI ID again?"

    if not session.extracted["phoneNumbers"]:
        return "Support is not responding. Please share your contact number."

    return "Okay, I am checking now. Please wait."


def should_stop(session):
    fields = session.extracted

    score = sum([
        len(fields["upiIds"]) > 0,
        len(fields["phishingLinks"]) > 0,
        len(fields["phoneNumbers"]) > 0
    ])

    return score >= 2 or session.turns >= 15

