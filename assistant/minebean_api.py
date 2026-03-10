"""
Minebean API Module
Fetches REST API data and manages SSE real-time connection.
"""

import requests
import json
import threading
from typing import Callable, Optional
import sseclient

REST_BASE_URL = "https://api.minebean.com"


class MinebeanAPI:
    def __init__(self, sse_callback: Callable = None):
        self.sse_callback = sse_callback
        self._sse_running = False
        self._sse_thread = None

    def get_stats_and_price(self) -> dict:
        """Fetch global stats and BEAN price."""
        try:
            r = requests.get(f"{REST_BASE_URL}/api/stats", timeout=10)
            r.raise_for_status()
            stats = r.json()

            p = requests.get(f"{REST_BASE_URL}/api/price", timeout=10)
            p.raise_for_status()
            price_data = p.json()

            return {"stats": stats, "price": price_data}
        except Exception as e:
            print(f"[MinebeanAPI] Error fetching stats/price: {e}")
            return {}

    def get_current_round(self, user_addr: str = None) -> dict:
        """Fetch the current round state."""
        url = f"{REST_BASE_URL}/api/round/current"
        if user_addr:
            url += f"?user={user_addr}"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"[MinebeanAPI] Error fetching current round: {e}")
            return {}

    def get_user_rewards(self, user_addr: str) -> dict:
        """Fetch pending ETH and BEAN for user."""
        try:
            r = requests.get(f"{REST_BASE_URL}/api/user/{user_addr}/rewards", timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"[MinebeanAPI] Error fetching user rewards: {e}")
            return {}

    def start_sse_stream(self):
        """Start listening to real-time events."""
        if self._sse_running:
            return
        self._sse_running = True
        self._sse_thread = threading.Thread(target=self._sse_worker, daemon=True)
        self._sse_thread.start()

    def stop_sse_stream(self):
        """Stop SSE stream."""
        self._sse_running = False

    def _sse_worker(self):
        url = f"{REST_BASE_URL}/api/events/rounds"
        while self._sse_running:
            try:
                response = requests.get(url, stream=True, timeout=90)
                client = sseclient.SSEClient(response)
                for event in client.events():
                    if not self._sse_running:
                        break
                    if event.data:
                        try:
                            data = json.loads(event.data)
                            if self.sse_callback and data.get("type") in ["deployed", "roundTransition"]:
                                self.sse_callback(data)
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                print(f"[MinebeanAPI] SSE stream error: {e}. Reconnecting in 3s...")
                import time
                time.sleep(3)
