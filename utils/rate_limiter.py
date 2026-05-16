"""
Rate limiter for managing API calls and credits
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass, field
from utils.logger import get_logger

logger = get_logger()


@dataclass
class ServiceLimit:
    """Tracks usage limits for a service"""
    name: str
    limit: int
    used: int = 0
    reset_time: datetime = field(default_factory=datetime.now)
    unlimited: bool = False

    def can_use(self) -> bool:
        """Check if service can be used"""
        if self.unlimited:
            return True

        if datetime.now() >= self.reset_time:
            self.reset()

        return self.used < self.limit

    def use(self, count: int = 1):
        """Record usage"""
        if not self.unlimited:
            self.used += count
            logger.debug(f"{self.name}: used {self.used}/{self.limit}")

    def reset(self):
        """Reset usage counters"""
        self.used = 0
        self.reset_time = datetime.now() + timedelta(days=1)
        logger.debug(f"{self.name}: reset usage counters")


class RateLimiter:
    """Manages rate limits and credits across multiple services"""

    def __init__(self):
        self.services: Dict[str, ServiceLimit] = {}
        self._init_default_limits()

    def _init_default_limits(self):
        """Initialize default service limits"""
        self.services = {
            "kling": ServiceLimit(name="Kling AI", limit=66),
            "pika": ServiceLimit(name="Pika Labs", limit=80),
            "luma": ServiceLimit(name="Luma", limit=8),
            "freeai": ServiceLimit(name="Free.ai", limit=100),
            "leonardo": ServiceLimit(name="Leonardo AI", limit=150),
            "chatgpt": ServiceLimit(name="ChatGPT", limit=50),
            "gemini": ServiceLimit(name="Gemini", limit=60),
            "claude": ServiceLimit(name="Claude", limit=100),
            "deepseek": ServiceLimit(name="DeepSeek", limit=200),
        }

    def can_use(self, service: str) -> bool:
        """Check if service is available"""
        if service not in self.services:
            return True

        return self.services[service].can_use()

    def use(self, service: str, count: int = 1):
        """Record service usage"""
        if service in self.services:
            self.services[service].use(count)

    def wait_if_needed(self, service: str, wait_seconds: int = 60):
        """Wait if service limit reached"""
        if service in self.services and not self.can_use(service):
            logger.warning(f"{service} limit reached, waiting {wait_seconds}s...")
            time.sleep(wait_seconds)

    def set_limit(self, service: str, limit: int, unlimited: bool = False):
        """Set custom limit for a service"""
        self.services[service] = ServiceLimit(
            name=service,
            limit=limit,
            unlimited=unlimited
        )

    def get_status(self) -> Dict:
        """Get status of all services"""
        status = {}
        for name, service in self.services.items():
            status[name] = {
                "used": service.used,
                "limit": "unlimited" if service.unlimited else service.limit,
                "available": service.can_use(),
                "reset_at": service.reset_time.isoformat()
            }
        return status

    def reset_service(self, service: str):
        """Manually reset a service"""
        if service in self.services:
            self.services[service].reset()
            logger.info(f"Reset {service} limits")