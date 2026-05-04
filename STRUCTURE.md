# Fleet Agent Base Class — Structure Summary

## Created Files

### Core Module
- **`fleet_agent/base.py`** (364 lines)
  - Minimal shared base class for all domain agents
  - PLATO room connection via HTTP
  - Tile read/write operations
  - Agent identity management
  - Standard CLI with --vessel, --domain, --plato-url flags
  - Only uses Python standard library (no external deps)

### Package Files
- **`fleet_agent/__init__.py`**
  - Package exports: BaseAgent, main_entry_point, setup_logging
  - Version: 0.1.0

### Documentation
- **`README.md`** — Comprehensive documentation with:
  - Quick start guide
  - Full API reference
  - Usage examples
  - CLI arguments reference
  - PLATO integration details

### Examples
- **`example_agent.py`** — Working example agent demonstrating:
  - Connection to PLATO
  - Reading tiles
  - Writing tiles with metadata
  - Identity management

## Key Features

### 1. PLATO Integration
- **Connection**: Simple `connect()` method with timeout and error handling
- **Read tiles**: `read_tiles(room, limit, offset)` with pagination support
- **Write tiles**: `write_tile(question, answer, room, metadata)` with rich metadata support

### 2. Agent Identity
- **vessel**: Agent name (e.g., "oracle1", "fleet-health-monitor")
- **domain**: PLATO room name (e.g., "oracle1_history", "fleethealth")
- **agent_id**: Combined identifier (vessel@domain)
- **started_at**: Timestamp of agent initialization

### 3. CLI Interface
Standard arguments for all fleet agents:
- `--vessel` (required): Vessel/agent name
- `--domain` (required): Domain/room name
- `--plato-url` (optional): PLATO server URL (default: http://localhost:8847)

Environment variable support:
- `PLATO_URL`: Default PLATO server URL

### 4. Logging
- Structured logging with agent context
- Configurable log levels
- Proper error messages with context

### 5. Error Handling
- Graceful connection failures
- HTTP error handling with status codes
- JSON decode error handling
- URL/network error handling

## Usage Pattern

```python
from fleet_agent import BaseAgent, main_entry_point

class MyDomainAgent(BaseAgent):
    def run(self):
        # Your domain-specific logic here
        tiles = self.read_tiles(limit=10)
        # Process tiles...
        self.write_tile("status", "done", metadata={"role": "processor"})

if __name__ == "__main__":
    main_entry_point(MyDomainAgent)
```

## Testing

All core functionality tested and working:
- ✓ Agent instantiation
- ✓ Identity management
- ✓ PLATO connection
- ✓ Tile reading
- ✓ Tile writing
- ✓ CLI argument parsing
- ✓ Logging setup
- ✓ Error handling

## Design Principles

1. **Minimal**: Only essential functionality, no bloat
2. **Functional**: Works out of the box with sensible defaults
3. **Explicit**: Clear method names and parameters
4. **Extensible**: Simple abstract `run()` method for domain logic
5. **Standardized**: Consistent interface across all fleet agents
6. **Zero dependencies**: Only Python standard library

## Next Steps for Domain Agents

1. Import BaseAgent from fleet_agent
2. Create subclass with domain-specific name
3. Implement `run()` method with domain logic
4. Use `read_tiles()` and `write_tile()` for PLATO operations
5. Use `main_entry_point()` for standard CLI entry point

Example domain agent locations:
- `/home/ubuntu/.openclaw/workspace/repos/*/agent.py`
- Domain-specific subdirectories
- Fleet service scripts

## PLATO API Endpoints Used

- **Read tiles**: `GET /room/{room_name}?limit={limit}&offset={offset}`
- **Write tiles**: `POST /submit` with JSON body

Tile structure:
```json
{
  "domain": "room_name",
  "question": "What is...?",
  "answer": "The answer...",
  "agent": "agent_name",
  "timestamp": "2026-05-04T03:58:30.928311+00:00",
  "confidence": 0.9,
  "model": "llama-3.3-70b",
  "role": "researcher"
}
```

## Version

- **Current**: 0.1.0
- **Status**: Functional and tested
- **Dependencies**: None (Python standard library only)
