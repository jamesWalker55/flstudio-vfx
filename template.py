# Script written by jisai
# https://x.com/jisai_w

import flvfx as vfx


def createDialog() -> vfx.ScriptDialog:
    """Defines script UI. Must return a vfx.ScriptDialog instance."""

    form = vfx.ScriptDialog(
        "Your script name",
        "Description of your script here",
    )

    return form


def onTriggerVoice(voice: vfx.Voice):
    """Called whenever an incoming voice (i.e. note) is triggered. incomingVoice is a vfx.Voice object."""
    pass


def onReleaseVoice(voice: vfx.Voice):
    """Called whenever an incoming voice is released. incomingVoice is the original vfx.Voice that triggered."""
    pass


def onTick():
    """Called every tick for continuous processing and updates."""
    pass
