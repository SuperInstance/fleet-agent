"""
FleetAgent base class — all domain agents inherit from this.
Handles PLATO room connection, tile read/write, agent identity, and standard CLI.
"""

import argparse
import json
import urllib.request
from datetime import datetime, timezone
from typing import Any, Optional


class FleetAgent:
    """Base class for all fleet domain agents."""

    PLATO_URL = "http://localhost:8847"

    def __init__(
        self,
        vessel: str = "unknown",
        domain: str = None,
        plato_url: str = None,
        verbose: bool = True,
    ):
        self.vessel = vessel
        self.domain = domain or self.__class__.__name__.lower().replace("_agent", "")
        self.plato_url = plato_url or self.PLATO_URL
        self.verbose = verbose

        if self.verbose:
            print(f"[{self.__class__.__name__}] vessel={self.vessel} domain={self.domain}")

    # ─── PLATO Tile Operations ──────────────────────────────────────

    def tile_read(self, room: str, limit: int = 50) -> list[dict]:
        """Read tiles from a PLATO room."""
        try:
            url = f"{self.plato_url}/rooms/{room}/tiles?limit={limit}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                return data.get("tiles", data) if isinstance(data, dict) else data
        except Exception as e:
            if self.verbose:
                print(f"[{self.domain}] tile_read error: {e}")
            return []

    def tile_write(self, room: str, content: str, agent: str = None) -> bool:
        """Write a tile to a PLATO room."""
        try:
            url = f"{self.plato_url}/rooms/{room}/tiles"
            body = json.dumps({
                "content": content,
                "agent": agent or self.vessel,
            }).encode()
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception as e:
            if self.verbose:
                print(f"[{self.domain}] tile_write error: {e}")
            return False

    # ─── Domain Hooks ────────────────────────────────────────────────

    def run_cycle(self):
        """Override in subclass — called each agent loop iteration."""
        raise NotImplementedError

    # ─── Standard CLI ────────────────────────────────────────────────

    @classmethod
    def cli(cls):
        parser = argparse.ArgumentParser(description=f"{cls.__name__} — fleet domain agent")
        parser.add_argument("--vessel", default="oracle1", help="Vessel name")
        parser.add_argument("--domain", default=None, help="Domain override")
        parser.add_argument("--plato-url", default=None, help="PLATO server URL")
        parser.add_argument("--once", action="store_true", help="Run single cycle and exit")
        args = parser.parse_args()

        agent = cls(
            vessel=args.vessel,
            domain=args.domain,
            plato_url=args.plato_url,
        )

        if args.once:
            agent.run_cycle()
        else:
            print(f"[{cls.__name__}] Running on {args.plato_url or cls.PLATO_URL} — Ctrl+C to stop")
            try:
                while True:
                    agent.run_cycle()
            except KeyboardInterrupt:
                print(f"\n[{cls.__name__}] Stopped")
