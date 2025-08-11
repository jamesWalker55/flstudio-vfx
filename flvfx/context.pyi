from . import ScriptDialog, Voice

voice: list[Voice]
"""Active vfx.Voice objects triggered by this script."""

ticks: int
"""Current host clock time in PPQ ticks (read-only)."""

PPQ: int
"""Project's Pulses Per Quarter note (read-only)."""

isPlaying: bool
"""True if FL Studio transport is playing (read-only)."""

form: ScriptDialog