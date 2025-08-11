import flvfx as vfx


def createDialog():
    """Defines script UI. Must return a vfx.ScriptDialog instance."""
    pass


def onTick():
    """Called every tick for continuous processing and updates."""
    pass


def onTriggerVoice(voice: vfx.Voice):
    """Called whenever an incoming voice (i.e. note) is triggered. incomingVoice is a vfx.Voice object."""
    pass


def onReleaseVoice(voice: vfx.Voice):
    """Called whenever an incoming voice is released. incomingVoice is the original vfx.Voice that triggered."""
    pass
