"""
How often visitors can make the platform call its free data providers.

Every fetch on the research page asks CoinGecko and a dozen other public
APIs, and their free tiers allow only so many requests a minute for the whole
server, shared with the background refresh. Without a limit, one person
clicking Fetch in a loop could use up that allowance and leave every other
visitor with "rate limited" errors. A visitor waiting a minute is the
defined off state. Both limits are settings (config.py).
"""
import threading
import time
from collections import deque


class RateLimited(Exception):
    """A limit was reached; the message says what to do."""


class Window:
    """At most `limit` events in any `seconds`-long window. Thread-safe: the
    research app serves every visitor from one process."""

    def __init__(self, limit, seconds):
        self.limit, self.seconds = limit, seconds
        self._times = deque()
        self._lock = threading.Lock()

    def take(self, now=None):
        """Record one event and return True, or return False when full."""
        now = time.monotonic() if now is None else now
        with self._lock:
            while self._times and now - self._times[0] >= self.seconds:
                self._times.popleft()
            if len(self._times) >= self.limit:
                return False
            self._times.append(now)
            return True
