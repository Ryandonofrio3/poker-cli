"""
OpenRouter LLM client for poker decision making
Uses structured outputs to ensure reliable action parsing
"""

import os
import requests
import json
from typing import Dict, List, Optional, Tuple
from texasholdem import TexasHoldEm, ActionType
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OpenRouterClient:
    """Client for OpenRouter API with structured outputs"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY in .env file"
            )

        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/pokerbench",  # Optional for rankings
            "X-Title": "PokerBench LLM Battle",  # Optional for rankings
        }

        # Define the poker action schema for structured outputs - fixed format
        self.poker_action_schema = {
            "name": "poker_action",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["FOLD", "CHECK", "CALL", "RAISE"],
                        "description": "The poker action to take",
                    },
                    "amount": {
                        "type": "integer",
                        "description": "Amount to raise (only for RAISE action, 0 for other actions)",
                        "minimum": 0,
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of the decision (1-2 sentences)",
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Confidence in this decision (0.0 to 1.0)",
                    },
                },
                "required": ["action", "amount", "reasoning", "confidence"],
                "additionalProperties": False,
            },
        }

    def make_poker_decision_structured(
        self, model: str, prompt: str, max_tokens: int = 200
    ) -> Dict:
        """
        Make a poker decision using structured outputs (for supported models)
        """
        # Enhanced system prompt for structured outputs
        system_prompt = """You are an expert poker player. Analyze the situation and make the best decision. 

IMPORTANT: You must respond with valid JSON in this exact format:
{
  "action": "FOLD" | "CHECK" | "CALL" | "RAISE",
  "amount": integer (raise amount if RAISE, otherwise 0),
  "reasoning": "brief explanation",
  "confidence": number between 0.0 and 1.0
}"""

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": self.poker_action_schema,
            },
            "max_tokens": max_tokens,
            "temperature": 0.1,
        }

        try:
            response = requests.post(
                self.base_url, headers=self.headers, json=payload, timeout=30
            )
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Parse the structured JSON response
            decision = json.loads(content)

            # Convert amount=0 to None for non-RAISE actions
            if decision["action"] != "RAISE" and decision["amount"] == 0:
                decision["amount"] = None

            return decision

        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter API request failed: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {e}")
        except KeyError as e:
            raise Exception(f"Unexpected response format: {e}")

    def make_poker_decision_text(
        self, model: str, prompt: str, max_tokens: int = 200
    ) -> Dict:
        """
        Make a poker decision using text response and parse it
        """
        enhanced_prompt = f"""{prompt}

Respond with your decision in this exact format:
ACTION: [FOLD/CHECK/CALL/RAISE]
AMOUNT: [number if raising, otherwise null]
REASONING: [brief explanation]
CONFIDENCE: [0.0 to 1.0]"""

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert poker player. Always respond in the exact format requested.",
                },
                {"role": "user", "content": enhanced_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        try:
            response = requests.post(
                self.base_url, headers=self.headers, json=payload, timeout=30
            )
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Parse the text response
            return self._parse_text_response(content)

        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter API request failed: {e}")
        except Exception as e:
            raise Exception(f"Failed to parse text response: {e}")

    def _parse_text_response(self, content: str) -> Dict:
        """Parse text response into structured format"""
        lines = content.strip().split("\n")
        result = {
            "action": "CALL",
            "amount": None,
            "reasoning": "Default action",
            "confidence": 0.5,
        }

        for line in lines:
            line = line.strip()
            if line.startswith("ACTION:"):
                action = line.split(":", 1)[1].strip().upper()
                if action in ["FOLD", "CHECK", "CALL", "RAISE"]:
                    result["action"] = action
            elif line.startswith("AMOUNT:"):
                amount_str = line.split(":", 1)[1].strip()
                if amount_str.lower() not in ["null", "none", ""]:
                    try:
                        result["amount"] = int(amount_str)
                    except ValueError:
                        result["amount"] = None
            elif line.startswith("REASONING:"):
                result["reasoning"] = line.split(":", 1)[1].strip()
            elif line.startswith("CONFIDENCE:"):
                conf_str = line.split(":", 1)[1].strip()
                try:
                    result["confidence"] = float(conf_str)
                except ValueError:
                    result["confidence"] = 0.5

        return result

    def make_poker_decision(
        self, model: str, prompt: str, max_tokens: int = 200
    ) -> Dict:
        """
        Make a poker decision, trying structured outputs first, then falling back to text parsing
        """
        try:
            # Try structured outputs first
            return self.make_poker_decision_structured(model, prompt, max_tokens)
        except Exception as e:
            print(f"Structured output failed ({e}), trying text parsing...")
            # Fallback to text parsing
            return self.make_poker_decision_text(model, prompt, max_tokens)

    def test_connection(self, model: str = "openai/gpt-4.1-mini") -> bool:
        """Test the connection to OpenRouter with a model that definitely supports structured outputs"""
        try:
            test_prompt = "You have pocket aces (A♠ A♥) in early position preflop. The blinds are 10/20. What should you do?"
            decision = self.make_poker_decision(model, test_prompt)
            print(f"Test decision: {decision}")
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def test_structured_output_specifically(self, model: str) -> bool:
        """Test structured output specifically"""
        try:
            test_prompt = "You have pocket aces (A♠ A♥) in early position preflop. The blinds are 10/20. What should you do?"
            decision = self.make_poker_decision_structured(model, test_prompt)
            print(f"✅ Structured output SUCCESS for {model}: {decision}")
            return True
        except Exception as e:
            print(f"❌ Structured output FAILED for {model}: {e}")
            return False


# Available models - updated with models that definitely support structured outputs
AVAILABLE_MODELS = {
    "gpt-4.1": "openai/gpt-4.1-mini",  # Definitely supports structured outputs
    "gpt4": "openai/gpt-4.1",  # Definitely supports structured outputs
    "llama": "meta-llama/llama-3.1-8b-instruct",  # Should support structured outputs
    "gemma": "google/gemma-3-27b-it:free",  # Should support structured outputs
}


def get_model_name(model_key: str) -> str:
    """Get full model name from key"""
    return AVAILABLE_MODELS.get(model_key, model_key)


def create_llm_client() -> OpenRouterClient:
    """Create and return an OpenRouter client"""
    return OpenRouterClient()
