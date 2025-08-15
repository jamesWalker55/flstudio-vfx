from . import context

def addOutputController(name: str, default: int | float) -> None:
    """Defines an output controller (automation) pin. e.g., ('LFO', 0.0)."""
    ...

def setOutputController(name: str, value: int | float) -> None: ...

class Voice:
    def __init__(self, existingVoice: Voice | None = None) -> None:
        """
        Creates a new, empty voice.

        If existingVoice is given, copies properties from existingVoice.
        """
    note: float
    """MIDI note number (e.g., 60.0 = C4). Fractional for microtuning."""

    finePitch: float
    """Fine pitch offset in fractional note numbers."""

    velocity: float
    """Note velocity (0.0 to 1.0)."""

    pan: float
    """Stereo panning (-1.0 Left, 0.0 Center, 1.0 Right)."""

    length: int
    """Duration in ticks. If set, auto-releases after this time."""

    output: int
    """Voice output for the event (0-based). Default 0."""

    fcut: float
    """Mod X parameter (-1.0 to 1.0)."""

    fres: float
    """Mod Y parameter (-1.0 to 1.0)."""

    def trigger(self) -> None:
        """Sends Note On for this voice."""

    def release(self) -> None:
        """Sends Note Off for this voice."""

    def copyFrom(self, otherVoice: Voice) -> None:
        """Copies all properties from otherVoice. Used for slide note handling."""

class ScriptDialog:
    def __init__(self, title: str, description: str) -> None:
        """Creates the UI dialog."""

    def addInputKnob(
        self,
        name: str,
        default: int | float,
        min: int | float,
        max: int | float,
        hint: str = ...,
    ):
        """Adds a float knob."""

    def addInputKnobInt(
        self,
        name: str,
        default: int | float,
        min: int | float,
        max: int | float,
        hint: str = ...,
    ):
        """Adds an integer knob."""

    def addInputCheckbox(self, name: str, default: int | float, hint: str = ...):
        """Adds a checkbox."""

    def addInputCombo(
        self, name: str, opts: list[str], default_idx: int, hint: str = ...
    ):
        """Adds a dropdown menu. "opts" is a list of strings."""

    def addInputText(self, name: str, default_text: str, hint: str = ...):
        """Adds a text input field."""

    def addInputSurface(self):
        """Uses the embedded Control Surface as a UI."""

    def addGroup(self, name: str):
        """Starts a named UI group."""

    def endGroup(self):
        """Ends the current UI group."""

    def getInputValue(self, name: str):
        """
        Gets value from UI control. Use 'GroupName: ControlName' for grouped controls.
        """

    def setNormalizedValue(self, name: str, value: int | float):
        """
        Sets value (normalized to 0-1) of a UI control.
        """
