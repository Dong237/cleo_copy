"""
Intent classification for user messages
"""
from typing import Dict, Tuple
import re


class IntentClassifier:
    """
    Simple rule-based intent classifier
    In production, this would use a trained ML model (BERT-based or similar)
    """

    # Define intents and their patterns
    INTENT_PATTERNS = {
        "spending_query": [
            r"how much.*spent",
            r"what.*spent",
            r"spending.*on",
            r"total.*spent"
        ],
        "balance_query": [
            r"what.*balance",
            r"how much.*have",
            r"account balance",
            r"available.*money"
        ],
        "budget_query": [
            r"budget.*status",
            r"how.*budget",
            r"budget.*doing",
            r"budget.*left"
        ],
        "savings_query": [
            r"savings.*goal",
            r"how much.*saved",
            r"savings.*progress"
        ],
        "transaction_search": [
            r"find.*transaction",
            r"where.*spend",
            r"transaction.*at",
            r"charge.*from"
        ],
        "bill_query": [
            r"when.*bill.*due",
            r"upcoming.*bills",
            r"bill.*reminder"
        ],
        "advice_request": [
            r"help.*save",
            r"advice.*money",
            r"what.*should.*do",
            r"recommend.*budget"
        ],
        "greeting": [
            r"^(hi|hello|hey|sup|yo)\b",
            r"good\s+(morning|afternoon|evening)"
        ],
        "thanks": [
            r"thank",
            r"thanks",
            r"appreciate"
        ],
        "general_question": [
            r"what.*is",
            r"how.*does",
            r"explain",
            r"tell.*about"
        ]
    }

    @classmethod
    def classify(cls, message: str) -> Tuple[str, float]:
        """
        Classify intent of message
        Returns: (intent, confidence)
        """
        message_lower = message.lower().strip()

        # Check patterns for each intent
        for intent, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    # Calculate confidence based on pattern specificity
                    confidence = 0.9 if len(pattern) > 20 else 0.8
                    return intent, confidence

        # Default to general_question with lower confidence
        return "general_question", 0.5

    @classmethod
    def extract_entities(cls, message: str, intent: str) -> Dict:
        """
        Extract entities from message based on intent
        In production, this would use NER (Named Entity Recognition)
        """
        entities = {}

        message_lower = message.lower()

        # Extract time periods
        if "month" in message_lower:
            if "last month" in message_lower:
                entities["period"] = "last_month"
            elif "this month" in message_lower:
                entities["period"] = "this_month"

        # Extract categories
        categories = ["food", "dining", "restaurant", "grocery", "shopping", "uber", "transport"]
        for category in categories:
            if category in message_lower:
                entities["category"] = category
                break

        # Extract amounts
        amount_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', message)
        if amount_match:
            entities["amount"] = float(amount_match.group(1).replace(',', ''))

        return entities
