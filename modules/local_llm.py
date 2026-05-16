"""
Local LLM Integration - Ollama (free, runs locally)
https://ollama.ai
"""

import requests
from typing import Optional
from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class LocalLLM:
    """Use Ollama for local LLM inference - completely free"""

    DEFAULT_MODEL = "llama3.2:1b"
    FALLBACK_MODELS = ["mistral", "phi3", "gemma:2b"]

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = self.DEFAULT_MODEL

    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using local LLM"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": max_tokens}
                },
                timeout=120
            )

            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                raise Exception(f"Ollama returned {response.status_code}")

        except Exception as e:
            logger.error(f"Local LLM generation failed: {e}")
            raise

    def list_models(self):
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                return response.json().get("models", [])
        except:
            return []


class ScriptWriter:
    """Script generation using local LLM"""

    def __init__(self, api_keys: dict = None, rate_limiter=None):
        self.api_keys = api_keys or {}
        self.local_llm = LocalLLM()

        from modules.script_writer import FallbackLLMClient
        self.fallback = FallbackLLMClient()

    def generate_script(self, stories, video_title=None):
        """Generate script - tries local LLM first, then fallback"""
        # First try local LLM
        if self.local_llm.is_available():
            try:
                logger.info("Using local LLM (Ollama) for script generation")

                story_text = "\n\n".join([
                    f"Story: {s.title}\n{s.summary[:300]}"
                    for s in stories[:3]
                ])

                prompt = f"""Write a 2-minute YouTube tech news narration script.

Title: {video_title or "Tech News Update"}

Stories:
{story_text}

IMPORTANT: Write ONLY the narration text that will be spoken aloud. Do NOT include:
- Camera directions like "gesture here" or "point to screen"
- Timestamps or time markers
- Stage directions
- B-ROLL instructions or any text in brackets

Format (just the spoken words):
- Opening (10 sec): Catchy hook like "Hey guys, here's what's happening in tech..."
- Main content (100 sec): Cover each story in plain conversational English
- Closing (20 sec): Quick call to action like "Thanks for watching, subscribe for more!"

Write as if speaking directly to the camera. No formatting markers.
"""

                response = self.local_llm.generate(prompt, max_tokens=800)

                # Parse into Script object
                return self._parse_to_script(response, video_title, stories)

            except Exception as e:
                logger.warning(f"Local LLM failed: {e}, using fallback")

        # Fallback to template
        logger.info("Using template-based script generation")
        prompt = f"Write a script about {len(stories)} tech news stories"
        response = self.fallback.generate(prompt)
        return self._parse_to_script(response, video_title, stories)

    def _parse_to_script(self, text: str, title: str, stories) -> object:
        """Parse LLM response to Script object"""
        import re

        clean_text = text
        broll_prompts = []

        # Remove all bracket content like [B-ROLL: ...] or [gesture] etc
        clean_text = re.sub(r'\[.*?\]', '', clean_text)
        # Remove any remaining special markers
        clean_text = re.sub(r'\([A-Za-z\s]+\)', '', clean_text)
        # Clean up extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        class Script:
            def __init__(self):
                self.title = title or "Tech News Update"
                self.hook = clean_text[:200] if clean_text else "Welcome to tech news!"
                self.body = clean_text[200:] if clean_text else "Today we're covering the latest tech stories..."
                self.cta = "Thanks for watching! Subscribe for more."
                self.full_text = clean_text or "Welcome to tech news! Today we're covering the latest in technology."
                self.broll_prompts = broll_prompts
                self.word_count = len(self.full_text.split())
                self.estimated_duration = self.word_count // 2

        return Script()


# Make it work with the main orchestrator
def get_script_writer(api_keys=None, rate_limiter=None):
    return ScriptWriter(api_keys, rate_limiter)