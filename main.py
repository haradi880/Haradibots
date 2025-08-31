import json
import random
import logging
import re
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Haradi:
    """
    A chatbot that directly maps patterns to responses (no classification).
    """

    def __init__(self, intents_file: str = './data/intents.json') -> None:
        self.intents = self._load_intents(intents_file)
        self.pattern_response_map = self._build_pattern_response_map()

    def _load_intents(self, filename: str) -> Dict[str, Any]:
        """Load intents JSON safely."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if not isinstance(data, dict) or 'intents' not in data:
                    raise ValueError("Invalid intents file structure")
                return data
        except FileNotFoundError:
            logger.error(f"Intents file not found: {filename}")
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in intents file")
        except Exception as e:
            logger.error(f"Error loading intents: {e}")
        return {"intents": []}

    def _build_pattern_response_map(self) -> List[Dict[str, Any]]:
        """
        Convert intents data into a list of {pattern, responses} dicts.
        """
        mapping = []
        for intent in self.intents.get("intents", []):
            patterns = intent.get("patterns", [])
            responses = intent.get("responses", [])
            for pattern in patterns:
                if isinstance(pattern, str) and responses:
                    mapping.append({"pattern": pattern.lower(), "responses": responses})
        return mapping

    def get_response(self, user_input: str) -> str:
        """
        Return the exact mapped response if pattern matches.
        """
        if not user_input.strip():
            return "Please type something so I can help you."

        user_input_lower = user_input.lower().strip()

        # First try exact match
        for entry in self.pattern_response_map:
            if user_input_lower == entry["pattern"]:
                return random.choice(entry["responses"])

        # Then try partial/fuzzy match
        for entry in self.pattern_response_map:
            if re.search(rf"\b{re.escape(entry['pattern'])}\b", user_input_lower):
                return random.choice(entry["responses"])

        return "I don't have a response for that yet."

    def __call__(self, user_input: str) -> str:
        return self.get_response(user_input)


if __name__ == "__main__":
    chatbot = Haradi()
    print("Haradi: Hello! Talk to me (type 'quit' to exit).")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            print("Haradi: Goodbye!")
            break
        print("Haradi:", chatbot(user_input))
