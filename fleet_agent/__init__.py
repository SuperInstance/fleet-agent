"""fleet_agent — Minimal shared base class for fleet domain agents."""

from .base import BaseAgent, main_entry_point, setup_logging
from .fleet_math import (
    EmergenceDetector,
    HolonomyConsensus,
    encode_pythagorean48,
    decode_pythagorean48,
    compute_h1_cohomology,
    check_rigidity,
    optimal_neighbor_count,
    MAX_RIGID_NEIGHBORS,
    BITS_PER_VECTOR,
    CONVERGENCE_CONSTANT,
)

__all__ = [
    "BaseAgent",
    "main_entry_point",
    "setup_logging",
    "EmergenceDetector",
    "HolonomyConsensus",
    "encode_pythagorean48",
    "decode_pythagorean48",
    "compute_h1_cohomology",
    "check_rigidity",
    "optimal_neighbor_count",
    "MAX_RIGID_NEIGHBORS",
    "BITS_PER_VECTOR",
    "CONVERGENCE_CONSTANT",
]
__version__ = "0.2.0"