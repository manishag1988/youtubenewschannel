"""
News gathering module with RSS feed aggregation and fallback
"""

import feedparser
import requests
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from config import config
from utils.logger import get_logger
from utils.rate_limiter import RateLimiter
import time

logger = get_logger(__name__)


@dataclass
class NewsStory:
    """Represents a news story"""
    title: str
    summary: str
    url: str
    source: str
    published: datetime
    score: float = 0.0

    def to_dict(self):
        return {
            "title": self.title,
            "summary": self.summary[:200] + "..." if len(self.summary) > 200 else self.summary,
            "url": self.url,
            "source": self.source,
            "published": self.published.isoformat(),
            "score": self.score
        }


class NewsGatherer:
    """
    Aggregates news from multiple RSS feeds with fallback sources
    """

    def __init__(self, rate_limiter: RateLimiter = None):
        self.feeds = config.news.RSS_FEEDS
        self.max_stories = config.news.MAX_STORIES_PER_CHECK
        self.min_score = config.news.MIN_SCORE_THRESHOLD
        self.rate_limiter = rate_limiter or RateLimiter()

        self._fallback_feeds = [
            "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen",
            "https://feeds.feedburner.com/TechCrunch/",
        ]

    def fetch_all_news(self) -> List[NewsStory]:
        """
        Fetch news from all configured RSS feeds

        Returns:
            List of NewsStory objects sorted by relevance
        """
        all_stories = []

        for feed_url in self.feeds:
            try:
                stories = self._fetch_feed(feed_url)
                all_stories.extend(stories)
                logger.info(f"Fetched {len(stories)} stories from {self._extract_source_name(feed_url)}")
            except Exception as e:
                logger.warning(f"Failed to fetch from {feed_url}: {e}")
                continue

        if not all_stories:
            logger.warning("Primary feeds failed, trying fallbacks...")
            all_stories = self._fetch_fallbacks()

        scored_stories = self._score_and_filter(all_stories)
        return scored_stories[:self.max_stories]

    def _fetch_feed(self, feed_url: str) -> List[NewsStory]:
        """Fetch and parse a single RSS feed"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(feed_url, headers=headers, timeout=15)
        response.raise_for_status()

        feed = feedparser.parse(response.content)

        stories = []
        for entry in feed.entries[:10]:
            try:
                published = self._parse_date(entry.get('published', ''))
                story = NewsStory(
                    title=entry.get('title', '').strip(),
                    summary=self._clean_summary(entry.get('summary', '')),
                    url=entry.get('link', ''),
                    source=feed.feed.get('title', 'Unknown'),
                    published=published
                )
                stories.append(story)
            except Exception as e:
                logger.debug(f"Failed to parse entry: {e}")
                continue

        return stories

    def _fetch_fallbacks(self) -> List[NewsStory]:
        """Fetch from fallback sources"""
        all_stories = []

        for feed_url in self._fallback_feeds:
            try:
                stories = self._fetch_feed(feed_url)
                all_stories.extend(stories)
            except Exception as e:
                logger.warning(f"Fallback feed failed: {feed_url} - {e}")

        return all_stories

    def _score_and_filter(self, stories: List[NewsStory]) -> List[NewsStory]:
        """Score stories by relevance and filter"""
        for story in stories:
            score = 0.0

            title_lower = story.title.lower()
            summary_lower = story.summary.lower()

            tech_keywords = ['ai', 'google', 'microsoft', 'apple', 'meta', 'openai',
                            'tech', 'startup', 'launch', 'release', 'device', 'software']

            for keyword in tech_keywords:
                if keyword in title_lower:
                    score += 2.0
                if keyword in summary_lower:
                    score += 0.5

            if 'announce' in title_lower or 'launch' in title_lower:
                score += 1.5

            story.score = score

        filtered = [s for s in stories if s.score >= self.min_score]
        return sorted(filtered, key=lambda x: x.score, reverse=True)

    def _clean_summary(self, summary: str) -> str:
        """Clean HTML from summary"""
        import re
        clean = re.sub(r'<[^>]+>', '', summary)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()

    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats"""
        from email.utils import parsedate_to_datetime

        if not date_str:
            return datetime.now()

        try:
            return parsedate_to_datetime(date_str)
        except:
            pass

        formats = [
            '%a, %d %b %Y %H:%M:%S %z',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue

        return datetime.now()

    def _extract_source_name(self, url: str) -> str:
        """Extract source name from URL"""
        domain = url.split('/')[2] if '://' in url else url.split('/')[0]
        return domain.split('.')[-2] if '.' in domain else domain


class AINewsGatherer(NewsGatherer):
    """Enhanced news gatherer with AI-powered filtering"""

    def __init__(self, llm_client=None, rate_limiter: RateLimiter = None):
        super().__init__(rate_limiter)
        self.llm_client = llm_client

    def fetch_and_curate(self) -> List[NewsStory]:
        """Fetch news and use AI to curate best stories"""
        stories = self.fetch_all_news()

        if not self.llm_client or not stories:
            return stories

        try:
            curated = self._ai_curate(stories)
            return curated
        except Exception as e:
            logger.warning(f"AI curation failed: {e}, returning scored stories")
            return stories

    def _ai_curate(self, stories: List[NewsStory]) -> List[NewsStory]:
        """Use LLM to curate best stories"""
        story_list = "\n\n".join([
            f"{i+1}. {s.title} - {s.source}"
            for i, s in enumerate(stories[:5])
        ])

        prompt = f"""From these tech news stories, select the top 3 most interesting/important for a YouTube tech news channel. Return ONLY the numbers (e.g., "1, 3, 5"):

{story_list}

Consider: relevance, uniqueness, viewer interest, and news value.
"""

        response = self.llm_client.generate(prompt, max_tokens=50)

        selected_indices = []
        for char in response:
            if char.isdigit():
                selected_indices.append(int(char) - 1)

        selected = [stories[i] for i in selected_indices if i < len(stories)]
        return selected if selected else stories[:3]