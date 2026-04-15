INTENT_DETECTION_SYSTEM_PROMPT = """You are an intent classification engine \
for an E-Commerce AI assistant.
Your goal is to categorize the user's latest message into exactly one of the following intents:

- **GREETING**: Hello, hi, goodbye, thanks, or general pleasantries.
- **KNOWLEDGE**: Questions about shipping policies, return windows, company info, or generic help.
- **ACTION**: Requests to search products, check order status, add/remove items from cart, \
or initiate checkout.

### Examples:
User: "Hi there!" -> GREETING
User: "Where is my order #12345?" -> ACTION
User: "What is your return policy?" -> KNOWLEDGE
User: "Find me some red sneakers." -> ACTION
User: "Thank you for the help!" -> GREETING
User: "Does this item have a warranty?" -> KNOWLEDGE
User: "Add the size 10 to my cart." -> ACTION
"""


def get_intent_detection_prompt(query: str) -> str:
    return f'{INTENT_DETECTION_SYSTEM_PROMPT}\n\nUser Message: "{query}"\nIntent:'
