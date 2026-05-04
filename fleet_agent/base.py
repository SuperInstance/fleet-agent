"""
fleet_agent.base — Minimal shared base class for all domain agents.

Handles:
  - PLATO room connection
  - Tile read/write via HTTP
  - Agent identity
  - Standard CLI with --vessel --domain --plato-url flags

No extra dependencies beyond `requests`.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error


class BaseAgent:
    """Minimal base class for all fleet domain agents.

    Provides:
      - PLATO room connection (HTTP)
      - Tile read/write operations
      - Agent identity management
      - Standard CLI argument parsing
    """

    def __init__(
        self,
        vessel: str,
        domain: str,
        plato_url: str = "http://localhost:8847",
    ):
        """Initialize the base agent.

        Parameters
        ----------
        vessel:
            Vessel/agent name (e.g., "oracle1", "fleet-health-monitor")
        domain:
            Domain/room name for PLATO operations (e.g., "oracle1_history", "fleethealth")
        plato_url:
            Base URL for PLATO server (default: http://localhost:8847)
        """
        self.vessel = vessel
        self.domain = domain
        self.plato_url = plato_url.rstrip("/")

        # Agent identity
        self.agent_id = f"{vessel}@{domain}"
        self.started_at = datetime.now(timezone.utc).isoformat()

        # Logging
        self.logger = logging.getLogger(f"fleet_agent.{vessel}.{domain}")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(name)s %(levelname)s: %(message)s"
            ))
            self.logger.addHandler(handler)

        # Connection state
        self._connected = False

    # ===================================================================
    # Connection
    # ===================================================================

    def connect(self) -> bool:
        """Test connection to PLATO server.

        Returns
        -------
        bool
            True if connection successful, False otherwise.
        """
        try:
            req = urllib.request.Request(
                f"{self.plato_url}/room/{self.domain}",
                method="GET",
                headers={"Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                self._connected = resp.status == 200
                if self._connected:
                    self.logger.info("Connected to PLATO at %s (room: %s)", self.plato_url, self.domain)
                else:
                    self.logger.warning("PLATO returned status %d", resp.status)
                return self._connected
        except urllib.error.URLError as e:
            self.logger.error("Failed to connect to PLATO: %s", e)
            self._connected = False
            return False
        except Exception as e:
            self.logger.error("Unexpected error connecting to PLATO: %s", e)
            self._connected = False
            return False

    def is_connected(self) -> bool:
        """Check if agent is connected to PLATO.

        Returns
        -------
        bool
            True if connected, False otherwise.
        """
        return self._connected

    # ===================================================================
    # Tile Operations
    # ===================================================================

    def read_tiles(
        self,
        room: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Read tiles from a PLATO room.

        Parameters
        ----------
        room:
            Room name (defaults to agent's domain if not specified)
        limit:
            Maximum number of tiles to return
        offset:
            Number of tiles to skip (for pagination)

        Returns
        -------
        list[dict]
            List of tile dictionaries, or empty list on error.
        """
        target_room = room or self.domain

        try:
            url = f"{self.plato_url}/room/{target_room}?limit={limit}&offset={offset}"
            req = urllib.request.Request(
                url,
                method="GET",
                headers={"Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    self.logger.debug("Read %d tiles from room %s", len(data.get("tiles", [])), target_room)
                    return data.get("tiles", [])
                else:
                    self.logger.warning("PLATO returned status %d reading room %s", resp.status, target_room)
                    return []
        except urllib.error.URLError as e:
            self.logger.error("Failed to read tiles from %s: %s", target_room, e)
            return []
        except json.JSONDecodeError as e:
            self.logger.error("Failed to decode JSON from %s: %s", target_room, e)
            return []
        except Exception as e:
            self.logger.error("Unexpected error reading tiles: %s", e)
            return []

    def write_tile(
        self,
        question: str,
        answer: str,
        room: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Write a tile to a PLATO room.

        Parameters
        ----------
        question:
            The question or topic for this tile
        answer:
            The answer or content for this tile
        room:
            Room name (defaults to agent's domain if not specified)
        metadata:
            Optional additional metadata (e.g., confidence, model, role)

        Returns
        -------
        dict
            Response from PLATO server, or error dict on failure.
        """
        target_room = room or self.domain

        tile = {
            "domain": target_room,
            "question": question,
            "answer": answer,
            "agent": self.vessel,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if metadata:
            tile.update(metadata)

        try:
            data = json.dumps(tile).encode("utf-8")
            req = urllib.request.Request(
                f"{self.plato_url}/submit",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    result = json.loads(resp.read().decode())
                    self.logger.info(
                        "Wrote tile to %s (status: %s, tile_count: %s)",
                        target_room,
                        result.get("status", "unknown"),
                        result.get("room_tile_count", "?")
                    )
                    return result
                else:
                    error_msg = resp.read().decode() if resp.readable else str(resp.status)
                    self.logger.error("PLATO returned status %d: %s", resp.status, error_msg)
                    return {"status": "error", "code": resp.status, "message": error_msg}
        except urllib.error.URLError as e:
            self.logger.error("Failed to write tile to %s: %s", target_room, e)
            return {"status": "error", "code": "url_error", "message": str(e)}
        except Exception as e:
            self.logger.error("Unexpected error writing tile: %s", e)
            return {"status": "error", "code": "unexpected", "message": str(e)}

    # ===================================================================
    # Identity
    # ===================================================================

    def get_identity(self) -> Dict[str, Any]:
        """Get agent identity information.

        Returns
        -------
        dict
            Agent identity including vessel, domain, agent_id, etc.
        """
        return {
            "vessel": self.vessel,
            "domain": self.domain,
            "agent_id": self.agent_id,
            "started_at": self.started_at,
            "plato_url": self.plato_url,
            "connected": self._connected,
        }

    # ===================================================================
    # CLI Interface
    # ===================================================================

    @classmethod
    def parse_args(cls) -> argparse.Namespace:
        """Parse standard CLI arguments.

        Returns
        -------
        argparse.Namespace
            Parsed arguments with vessel, domain, and plato_url.
        """
        parser = argparse.ArgumentParser(
            description=f"Run {cls.__name__} agent",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument(
            "--vessel",
            type=str,
            required=True,
            help="Vessel/agent name (e.g., oracle1, fleet-health-monitor)",
        )
        parser.add_argument(
            "--domain",
            type=str,
            required=True,
            help="Domain/room name for PLATO operations (e.g., oracle1_history, fleethealth)",
        )
        parser.add_argument(
            "--plato-url",
            type=str,
            default=os.environ.get("PLATO_URL", "http://localhost:8847"),
            help="Base URL for PLATO server",
        )
        return parser.parse_args()

    @classmethod
    def from_args(cls) -> "BaseAgent":
        """Create agent instance from CLI arguments.

        Returns
        -------
        BaseAgent
            Initialized agent instance.
        """
        args = cls.parse_args()
        return cls(vessel=args.vessel, domain=args.domain, plato_url=args.plato_url)

    # ===================================================================
    # Abstract Methods (to be implemented by subclasses)
    # ===================================================================

    def run(self) -> None:
        """Main agent execution loop.

        Subclasses must implement this method with their specific logic.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.run() must be implemented")


# ===================================================================
# Utility functions
# ===================================================================

def setup_logging(level: str = "INFO") -> None:
    """Setup root logging for the agent.

    Parameters
    ----------
    level:
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        stream=sys.stderr,
    )


def main_entry_point(agent_class: type) -> None:
    """Standard main entry point for CLI-based agents.

    Usage in your agent's __main__ block:
        if __name__ == "__main__":
            main_entry_point(MyAgent)

    Parameters
    ----------
    agent_class:
        The agent class to instantiate and run (must be a subclass of BaseAgent)
    """
    setup_logging()
    agent = agent_class.from_args()

    if not agent.connect():
        agent.logger.error("Failed to connect to PLATO. Exiting.")
        sys.exit(1)

    try:
        agent.run()
    except KeyboardInterrupt:
        agent.logger.info("Agent interrupted by user")
        sys.exit(0)
    except Exception as e:
        agent.logger.exception("Agent run failed with exception: %s", e)
        sys.exit(1)
