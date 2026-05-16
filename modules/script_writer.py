"""
Script writing module using LLMs with fallback support
"""

import json
from dataclasses import dataclass
from typing import List, Optional
from config import config
from utils.logger import get_logger
from utils.rate_limiter import RateLimiter

logger = get_logger(__name__)


@dataclass
class Script:
    """Represents a video script"""
    title: str
    hook: str
    body: str
    cta: str
    full_text: str
    broll_prompts: List[str]
    word_count: int
    estimated_duration: int

    def to_dict(self):
        return {
            "title": self.title,
            "hook": self.hook,
            "body": self.body,
            "cta": self.cta,
            "word_count": self.word_count,
            "estimated_duration": self.estimated_duration,
            "broll_prompts": self.broll_prompts
        }

    def to_text(self) -> str:
        """Convert script to plain text for TTS"""
        return self.full_text


class LLMClient:
    """Base class for LLM clients with fallback"""

    def __init__(self, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self._client = None

    def generate(self, prompt: str, max_tokens: int = None) -> str:
        """Generate text - to be implemented by subclasses"""
        raise NotImplementedError

    def _check_rate_limit(self, service: str) -> bool:
        """Check if we can use this service"""
        if self.rate_limiter:
            return self.rate_limiter.can_use(service)
        return True


class ChatGPTClient(LLMClient):
    """OpenAI ChatGPT client"""

    def __init__(self, api_key: str = None, rate_limiter: RateLimiter = None):
        super().__init__(rate_limiter)
        self.api_key = api_key
        self.model = config.llm.SERVICES["chatgpt"]["model"]

    def generate(self, prompt: str, max_tokens: int = None) -> str:
        """Generate using ChatGPT"""
        if not self._check_rate_limit("chatgpt"):
            raise Exception("ChatGPT rate limit reached")

        if not self.api_key:
            logger.warning("No API key for ChatGPT, using fallback")
            raise Exception("No API key")

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.llm.TEMPERATURE,
                max_tokens=max_tokens or config.llm.MAX_TOKENS
            )

            self.rate_limiter.use("chatgpt")
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"ChatGPT error: {e}")
            raise


class GeminiClient(LLMClient):
    """Google Gemini client"""

    def __init__(self, api_key: str = None, rate_limiter: RateLimiter = None):
        super().__init__(rate_limiter)
        self.api_key = api_key
        self.model = config.llm.SERVICES["gemini"]["model"]

    def generate(self, prompt: str, max_tokens: int = None) -> str:
        """Generate using Gemini"""
        if not self._check_rate_limit("gemini"):
            raise Exception("Gemini rate limit reached")

        if not self.api_key:
            logger.warning("No API key for Gemini, using fallback")
            raise Exception("No API key")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": config.llm.TEMPERATURE,
                    "max_output_tokens": max_tokens or config.llm.MAX_TOKENS
                }
            )

            self.rate_limiter.use("gemini")
            return response.text

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise


class ClaudeClient(LLMClient):
    """Anthropic Claude client"""

    def __init__(self, api_key: str = None, rate_limiter: RateLimiter = None):
        super().__init__(rate_limiter)
        self.api_key = api_key

    def generate(self, prompt: str, max_tokens: int = None) -> str:
        """Generate using Claude"""
        if not self._check_rate_limit("claude"):
            raise Exception("Claude rate limit reached")

        if not self.api_key:
            raise Exception("No API key")

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=max_tokens or config.llm.MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )

            self.rate_limiter.use("claude")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Claude error: {e}")
            raise


class DeepSeekClient(LLMClient):
    """DeepSeek client"""

    def __init__(self, api_key: str = None, rate_limiter: RateLimiter = None):
        super().__init__(rate_limiter)
        self.api_key = api_key

    def generate(self, prompt: str, max_tokens: int = None) -> str:
        """Generate using DeepSeek"""
        if not self._check_rate_limit("deepseek"):
            raise Exception("DeepSeek rate limit reached")

        if not self.api_key:
            raise Exception("No API key")

        try:
            import requests

            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": config.llm.TEMPERATURE,
                    "max_tokens": max_tokens or config.llm.MAX_TOKENS
                },
                timeout=30
            )

            self.rate_limiter.use("deepseek")
            return response.json()["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"DeepSeek error: {e}")
            raise


class FallbackLLMClient(LLMClient):
    """Simple rule-based fallback when no API keys available"""

    def generate(self, prompt: str, max_tokens: int = None) -> str:
        """Generate simple response using templates"""
        logger.info("Using fallback LLM (template-based)")

        prompt_lower = prompt.lower()

        if "write a script" in prompt_lower or "youtube" in prompt_lower:
            return self._generate_script_from_template(prompt)
        elif "summarize" in prompt_lower:
            return self._generate_summary_from_template(prompt)
        else:
            return self._generate_default_response(prompt)

    def _generate_script_from_template(self, prompt: str) -> str:
        """Generate a basic script from template"""
        return """Hey everyone! Welcome back to the channel!

Today we're diving into some major tech news that's been making waves across the industry.

[STORY CONTENT HERE - Add your news content]

This is a significant development because it shows how the tech landscape is evolving. What do you think about this? Drop your thoughts in the comments below!

If you enjoyed this video, don't forget to like and subscribe for more tech news updates. I'll see you in the next one!"""

    def _generate_summary_from_template(self, prompt: str) -> str:
        """Generate a summary"""
        return "This is a summary of the key points from the provided content."

    def _generate_default_response(self, prompt: str) -> str:
        """Generate default response"""
        return "Here's some content based on your request."


class ScriptWriter:
    """
    Generates video scripts from news stories using LLMs with fallback
    """

    def __init__(self, api_keys: dict = None, rate_limiter: RateLimiter = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.api_keys = api_keys or {}

        self.clients = self._init_clients()

    def _init_clients(self) -> List[LLMClient]:
        """Initialize LLM clients in priority order"""
        clients = []

        if self.api_keys.get("openai"):
            clients.append(ChatGPTClient(self.api_keys["openai"], self.rate_limiter))

        if self.api_keys.get("gemini"):
            clients.append(GeminiClient(self.api_keys["gemini"], self.rate_limiter))

        if self.api_keys.get("claude"):
            clients.append(ClaudeClient(self.api_keys["claude"], self.rate_limiter))

        if self.api_keys.get("deepseek"):
            clients.append(DeepSeekClient(self.api_keys["deepseek"], self.rate_limiter))

        clients.append(FallbackLLMClient(self.rate_limiter))

        return clients

    def generate_script(self, stories: List, video_title: str = None) -> Script:
        """
        Generate a video script from news stories

        Args:
            stories: List of NewsStory objects
            video_title: Optional custom title

        Returns:
            Script object
        """
        if not stories:
            raise ValueError("No stories provided")

        if video_title is None:
            video_title = self._generate_title(stories)

        prompt = self._build_script_prompt(stories, video_title)

        for client in self.clients:
            try:
                logger.info(f"Generating script with {client.__class__.__name__}")
                response = client.generate(prompt, max_tokens=config.llm.MAX_TOKENS)
                script = self._parse_response(response, stories, video_title)
                logger.info(f"Script generated successfully ({script.word_count} words)")
                return script
            except Exception as e:
                logger.warning(f"Script generation failed with {client.__class__.__name__}: {e}")
                continue

        raise Exception("All LLM clients failed")

    def _generate_title(self, stories: List) -> str:
        """Generate video title from stories"""
        main_topic = stories[0].title.split()[0:4]
        return "Tech News: " + " ".join(main_topic)

    def _build_script_prompt(self, stories: List, title: str) -> str:
        """Build prompt for script generation"""
        story_text = "\n\n".join([
            f"Story {i+1}: {s.title}\n{s.summary}"
            for i, s in enumerate(stories[:3])
        ])

        template = f"""Write a 2-3 minute YouTube narration script for a tech news video.

Title: {title}

Stories to cover:
{story_text}

Requirements:
- Hook (10 sec): Catchy opening that grabs attention
- Context (30 sec): Brief background on why this matters
- Main story (100 sec): Detailed coverage of each story
- Takeaway (20 sec): What viewers should know/think about

Tone: Conversational, enthusiastic, tech-nerd energy
Format: Write naturally, as if speaking to camera
Include B-roll suggestions in brackets, e.g. [B-ROLL: AI robot working]
Include emoji where appropriate for engagement
"""

        return template

    def _parse_response(self, response: str, stories: List, title: str) -> Script:
        """Parse LLM response into Script object"""
        parts = {
            "hook": "",
            "body": "",
            "cta": ""
        }

        lines = response.split('\n')
        current_section = "body"

        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()
            if 'hook' in line_lower or 'intro' in line_lower:
                current_section = "hook"
                continue
            elif 'conclusion' in line_lower or 'takeaway' in line_lower or 'cta' in line_lower:
                current_section = "cta"
                continue

            parts[current_section] += line + " "

        hook = parts["hook"].strip() or response[:200]
        body = parts["body"].strip() or response[200:]
        cta = parts["cta"].strip() or "Thanks for watching! Like and subscribe for more tech news."

        full_text = f"{hook} {body} {cta}"

        broll_prompts = self._extract_broll_prompts(response)

        word_count = len(full_text.split())
        estimated_duration = int(word_count / 2.5)

        return Script(
            title=title,
            hook=hook,
            body=body,
            cta=cta,
            full_text=full_text,
            broll_prompts=broll_prompts,
            word_count=word_count,
            estimated_duration=estimated_duration
        )

    def _extract_broll_prompts(self, text: str) -> List[str]:
        """Extract B-roll prompts from script"""
        import re
        pattern = r'\[B-ROLL:([^\]]+)\]'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [m.strip() for m in matches]