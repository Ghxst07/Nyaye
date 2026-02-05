ScamSentry: Agentic Honey-Pot for Scam Intelligence
Project Overview
This project was developed for a hackathon to address the growing complexity of online fraud. ScamSentry is an AI-powered agentic honey-pot designed to not only detect scam intent but also autonomously engage with scammers. By maintaining a believable human persona, the system handles multi-turn conversations to extract actionable intelligence—such as bank details and phishing links—without revealing that the scammer has been detected.
+4

Technical Architecture
1. Initial Scam Detection
To identify fraudulent intent from the very first message, we implemented a robust machine-learning pipeline:

Dataset: We simulated a comprehensive dataset of 250,000 rows, combining real-world scam data with synthetic examples to ensure high variance and accuracy.

Preprocessing: We utilized a TF-IDF (Term Frequency-Inverse Document Frequency) tokenizer to convert raw text into meaningful numerical features.

Model: The detection engine is powered by an XGBoost model, trained to distinguish between legitimate queries and scam tactics with high precision.

2. Multi-Agentic Engagement
Once the XGBoost model flags a message as a scam, control is handed over to our Multi-Agentic Model:
+1


Autonomous Conversation: The agent engages the scammer in a multi-turn dialogue, adapting its responses dynamically to stay "in character".


Persona Management: It maintains a believable human-like persona to keep the scammer invested in the conversation.

Intelligence Extraction: While conversing, the agent specifically targets and extracts critical data points, including:

Bank Account Numbers 

UPI IDs 

Phishing Links 

Phone Numbers 

3. Intelligence Reporting
After sufficient engagement, the system aggregates all gathered intelligence and sends a final callback to the mandatory evaluation endpoint.

API Specifications
Authentication
All requests must include the following header for security: x-api-key: YOUR_SECRET_API_KEY 
+1

Request Format
The API accepts incoming messages in the following JSON format:

JSON
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
Success Response
If the system is engaging with the scammer, it returns a believable response to keep the conversation going:

JSON
{
  "status": "success",
  "reply": "Wait, why is my account being blocked? I just used it this morning!"
}
Evaluation Criteria
Our solution is designed to be measured against the following:


Scam Detection Accuracy: High-precision identification using XGBoost.


Engagement Depth: Ability to maintain long-form, multi-turn dialogues.


Intelligence Quality: Effectiveness in extracting valid fraudulent credentials.


Ethical Guardrails: Strict adherence to responsible data handling and no harassment rules.