"""
Response generation with personality
"""
from typing import Dict, Optional
import random


class ResponseGenerator:
    """
    Generate responses with different personality modes
    In production, this would integrate with OpenAI/Anthropic for more natural responses
    """

    # Pre-written responses by intent and personality
    RESPONSES = {
        "spending_query": {
            "supportive": [
                "Let me check that for you! {}",
                "I've got your spending info right here: {}",
                "Here's what I found: {}"
            ],
            "funny": [
                "Oof, let's see the damage... 💸 {}",
                "Time to face the music! 🎵 {}",
                "Ready for this? (Don't shoot the messenger!) {}"
            ],
            "strict": [
                "Here's your spending breakdown: {}",
                "The numbers don't lie: {}",
                "This is what you spent: {}"
            ],
            "roast": [
                "Yikes, brace yourself... 😬 {}",
                "You REALLY wanna know? Fine. {}",
                "Oh honey, let me break it to you gently... JK! {}"
            ]
        },
        "balance_query": {
            "supportive": [
                "Your current balance is {}. You're doing great!",
                "You have {} available. Keep it up!",
                "Looking good! Your balance is {}"
            ],
            "funny": [
                "You've got {} in the bank! Time to treat yourself? (Kidding... mostly 😄)",
                "Balance check! You're sitting at {}",
                "Ka-ching! 💰 Your balance: {}"
            ],
            "strict": [
                "Current balance: {}",
                "Available funds: {}",
                "Balance: {}"
            ],
            "roast": [
                "You have {} left. Try not to blow it all at Starbucks this time 🤦",
                "{} in the bank. Living dangerously, I see!",
                "Balance: {}. But for how long? 👀"
            ]
        },
        "budget_query": {
            "supportive": [
                "Great question! {}",
                "Let me show you how you're doing: {}",
                "You're on the right track! {}"
            ],
            "funny": [
                "Budget check time! 📊 {}",
                "Let's see if you've been good... {}",
                "Budget status: {}"
            ],
            "strict": [
                "Budget status: {}",
                "Current budget utilization: {}",
                "{}"
            ],
            "roast": [
                "Let's see how badly you've ignored your budget... {}",
                "Budget? What budget? 😏 {}",
                "Oh you actually care about your budget? {}",
            ]
        },
        "greeting": {
            "supportive": [
                "Hi there! 👋 How can I help you today?",
                "Hello! I'm here to help with your finances!",
                "Hey! What can I do for you?"
            ],
            "funny": [
                "Yo! What's up? Need to talk money? 💰",
                "Hey hey! Ready to adulting today? 😄",
                "Hiya! Let's make your wallet happy!"
            ],
            "strict": [
                "Hello. How can I assist you?",
                "Greetings. State your query.",
                "Hello. What do you need?"
            ],
            "roast": [
                "Oh look who's back. Miss me? 😏",
                "Hey there, big spender! What now?",
                "Back so soon? Spent all your money already? 🤭"
            ]
        },
        "thanks": {
            "supportive": [
                "You're so welcome! Happy to help anytime! 😊",
                "My pleasure! That's what I'm here for!",
                "Anytime! Glad I could help!"
            ],
            "funny": [
                "No prob, Bob! 😄",
                "You got it, dude! 👍",
                "That's what friends are for! (We're friends, right?)"
            ],
            "strict": [
                "You're welcome.",
                "Acknowledged.",
                "No problem."
            ],
            "roast": [
                "Yeah yeah, just don't spend it all in one place 🙄",
                "Sure thing. Try to stay out of trouble now!",
                "Aww, you're welcome! Now go be responsible! 😜"
            ]
        },
        "general_question": {
            "supportive": [
                "That's a great question! {}",
                "Let me help you with that! {}",
                "I'd be happy to explain! {}"
            ],
            "funny": [
                "Ooh good question! 🤔 {}",
                "Let me drop some knowledge! 📚 {}",
                "Glad you asked! {}"
            ],
            "strict": [
                "Here's the answer: {}",
                "{}",
                "The answer is: {}"
            ],
            "roast": [
                "Did you even Google this first? Fine, I'll tell you... {}",
                "Seriously? Okay, here goes... {}",
                "*Sighs* Alright, listen up... {}"
            ]
        }
    }

    # Fallback responses
    FALLBACK_RESPONSES = {
        "supportive": "I'm not quite sure about that, but I'm here to help! Can you rephrase that?",
        "funny": "Hmm, you stumped me! 🤔 Can you say that differently?",
        "strict": "I don't understand that query. Please rephrase.",
        "roast": "Um, what? That didn't make any sense. Try again! 🤷"
    }

    @classmethod
    def generate(
        cls,
        intent: str,
        personality: str,
        data: Optional[str] = None
    ) -> str:
        """
        Generate response based on intent and personality
        """
        personality = personality or "supportive"

        # Get responses for this intent and personality
        intent_responses = cls.RESPONSES.get(intent, {})
        personality_responses = intent_responses.get(personality, [])

        if personality_responses:
            # Pick a random response template
            template = random.choice(personality_responses)

            # Fill in data if provided
            if "{}" in template and data:
                return template.format(data)
            elif "{}" not in template:
                return template
            else:
                return template.format("I couldn't find that information right now")

        # Fallback
        return cls.FALLBACK_RESPONSES.get(personality, "I'm not sure how to help with that")

    @classmethod
    def generate_suggestions(cls, intent: str) -> list:
        """
        Generate follow-up suggestions based on intent
        """
        suggestions_map = {
            "spending_query": [
                "Show me my budget status",
                "What are my top expenses?",
                "How does this compare to last month?"
            ],
            "balance_query": [
                "Show me recent transactions",
                "What bills are coming up?",
                "How much can I safely spend?"
            ],
            "budget_query": [
                "Show me spending by category",
                "Am I on track this month?",
                "Give me saving tips"
            ],
            "greeting": [
                "What's my balance?",
                "How much did I spend this month?",
                "Show me my budget status"
            ]
        }

        return suggestions_map.get(intent, [
            "What's my balance?",
            "Show my spending",
            "Check my budget"
        ])
