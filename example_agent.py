"""
Example fleet agent using BaseAgent.

Run with:
    python example_agent.py --vessel oracle1 --domain oracle1_history --plato-url http://localhost:8847
"""

import sys
import time
from fleet_agent import BaseAgent, main_entry_point


class ExampleAgent(BaseAgent):
    """Example domain agent that reads and writes tiles."""

    def run(self) -> None:
        """Main execution loop for this agent."""
        self.logger.info("Starting agent run")

        # Read some tiles from the domain room
        tiles = self.read_tiles(limit=5)
        self.logger.info("Read %d tiles", len(tiles))

        if tiles:
            # Show the most recent tile
            latest = tiles[-1]
            self.logger.info(
                "Latest tile: question='%s' (from %s)",
                latest.get("question", "N/A")[:50],
                latest.get("agent", "unknown")
            )

        # Write a status tile
        status_result = self.write_tile(
            question="Agent status check",
            answer=f"Example agent running successfully at {self.started_at}",
            metadata={"confidence": 1.0, "role": "monitor"}
        )

        if status_result.get("status") in ("success", "accepted"):
            self.logger.info("Status tile written successfully")
        else:
            self.logger.warning("Failed to write status tile: %s", status_result.get("message"))

        # Show identity
        identity = self.get_identity()
        self.logger.info("Agent identity: %s", identity)


if __name__ == "__main__":
    main_entry_point(ExampleAgent)
