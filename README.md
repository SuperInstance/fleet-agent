# fleet-agent

Shared base class for all SuperInstance domain agents (deckboss, fishinglog, etc.).

## Usage

```python
from fleet_agent import FleetAgent

class MyAgent(FleetAgent):
    def run_cycle(self):
        tiles = self.tile_read(f"{self.domain}-ai")
        for tile in tiles:
            print(tile["content"])

if __name__ == "__main__":
    MyAgent.cli()
```

## Structure

- `FleetAgent` — base class with PLATO integration and standard CLI
- Domain agents inherit from it and override `run_cycle()`
