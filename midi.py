# Script written by jisai
# https://x.com/jisai_w

from dataclasses import dataclass
from typing import NamedTuple
import flvfx as vfx
import random
import math
from enum import Enum


class Interp(Enum):
    LINEAR = 1
    COSINE = 2
    CUBIC = 3


class PerlinNoise:
    """
    Modified 1D Perlin Noise, derived from:
    https://github.com/alexandr-gnrk/perlin-1d

    Modified to lock frequency and amplitude to 1.0

    Output range is approximately -1.0 -- 1.0 when octaves = 1.
    If octaves > 1, output range will be larger than -1.0 -- 1.0.
    """

    def __init__(
        self,
        seed,
        octaves: int = 1,
        interp=Interp.COSINE,
        use_fade=False,
    ):
        self.seed = random.Random(seed).random()
        self.octaves = octaves
        self.interp = interp
        self.use_fade = use_fade

        self.mem_x = dict()

    def __noise(self, x):
        # made for improve performance
        if x not in self.mem_x:
            self.mem_x[x] = random.Random(self.seed + x).uniform(-1, 1)
        return self.mem_x[x]

    def __interpolated_noise(self, x):
        prev_x = int(x)  # previous integer
        next_x = prev_x + 1  # next integer
        frac_x = x - prev_x  # fractional of x

        if self.use_fade:
            frac_x = self.__fade(frac_x)

        # intepolate x
        if self.interp is Interp.LINEAR:
            res = self.__linear_interp(
                self.__noise(prev_x), self.__noise(next_x), frac_x
            )
        elif self.interp is Interp.COSINE:
            res = self.__cosine_interp(
                self.__noise(prev_x), self.__noise(next_x), frac_x
            )
        else:
            res = self.__cubic_interp(
                self.__noise(prev_x - 1),
                self.__noise(prev_x),
                self.__noise(next_x),
                self.__noise(next_x + 1),
                frac_x,
            )

        return res

    def get(self, x):
        """
        Output range is approximately -1.0 -- 1.0 when octaves = 1.
        If octaves > 1, output range will be larger than -1.0 -- 1.0.
        """
        frequency = 1.0
        amplitude = 1.0
        result = 0
        for _ in range(self.octaves):
            result += self.__interpolated_noise(x * frequency) * amplitude
            frequency *= 2
            amplitude /= 2

        return result

    def __linear_interp(self, a, b, x):
        return a + x * (b - a)

    def __cosine_interp(self, a, b, x):
        x2 = (1 - math.cos(x * math.pi)) / 2
        return a * (1 - x2) + b * x2

    def __cubic_interp(self, v0, v1, v2, v3, x):
        p = (v3 - v2) - (v0 - v1)
        q = (v0 - v1) - p
        r = v2 - v0
        s = v1
        return p * x**3 + q * x**2 + r * x + s

    def __fade(self, x):
        # useful only for linear interpolation
        return (6 * x**5) - (15 * x**4) + (10 * x**3)


class FormValue(NamedTuple):
    note_length_min: int
    note_length_max: int
    transition_rate: float

    @staticmethod
    def setup(form: vfx.ScriptDialog):
        form.addInputKnobInt("Note Length Min", 100, 1, 1000, "Duration in PPQ")
        form.addInputKnobInt("Note Length Max", 100, 1, 1000, "Duration in PPQ")
        form.addInputKnob(
            "Random Rate",
            0.01,
            0.0001,
            1.0,
            "How quickly the slicing speed changes over time",
        )

    @classmethod
    def get(cls):
        note_length_min: int = vfx.context.form.getInputValue("Note Length Min")
        note_length_max: int = vfx.context.form.getInputValue("Note Length Max")
        transition_rate: float = vfx.context.form.getInputValue("Random Rate")

        return cls(
            note_length_min,
            max(note_length_max, note_length_min),
            transition_rate,
        )


@dataclass
class VoiceSlicer:
    parent_voice: vfx.Voice
    """The original voice that triggered this slicer"""
    current_voice: vfx.Voice
    """The voice that is being managed by this slicer"""
    current_voice_age: int
    """The time (PPQ) elapsed for the current voice"""
    noise: PerlinNoise
    """The noise instance, each note should have a different seed"""
    noise_pos: float
    """The current position in the perlin noise instance"""

    def __init__(self, parent_voice: vfx.Voice, seed: int | float):
        self.parent_voice = parent_voice
        self.current_voice = vfx.Voice(parent_voice)  # copy properties from parent
        # negative 1, so on the first tick, it increments to 0
        self.current_voice_age = -1
        self.noise = PerlinNoise(seed)
        self.noise_pos = 0.0

    def on_trigger(self, val: FormValue):
        self.current_voice.trigger()

    def on_tick(self, val: FormValue):
        self.noise_pos += val.transition_rate
        noise = self.noise.get(self.noise_pos)

        note_length = (noise + 1.0) / 2.0 * (
            val.note_length_max - val.note_length_min
        ) + val.note_length_min
        note_length = max(round(note_length), 1)

        self.current_voice_age += 1
        if self.current_voice_age >= note_length:
            self.current_voice.release()
            self.current_voice = vfx.Voice(self.parent_voice)
            self.current_voice.trigger()
            self.current_voice_age = 0
        else:
            self.current_voice.copyFrom(self.parent_voice)

    def on_release(self, val: FormValue):
        self.current_voice.release()


# Map from `voice.output` index to Voice and its cycles
active_voices: dict[vfx.Voice, VoiceSlicer] = {}


def createDialog() -> vfx.ScriptDialog:
    """Defines script UI. Must return a vfx.ScriptDialog instance."""

    form = vfx.ScriptDialog(
        "MIDI Random Slicer",
        "Slices incoming MIDI notes randomly, smoothly transitioning between different slicing densities",
    )
    FormValue.setup(form)

    return form


def onTriggerVoice(voice: vfx.Voice):
    """Called whenever an incoming voice (i.e. note) is triggered. incomingVoice is a vfx.Voice object."""

    if voice in active_voices:
        print(active_voices)
        print(voice)
        raise RuntimeError("duplicate voice found in active voices")

    val = FormValue.get()

    slicer = VoiceSlicer(voice, random.random())
    slicer.on_trigger(val)
    active_voices[voice] = slicer


def onReleaseVoice(voice: vfx.Voice):
    """Called whenever an incoming voice is released. incomingVoice is the original vfx.Voice that triggered."""

    if voice not in active_voices:
        print(active_voices)
        print(voice)
        raise RuntimeError("incoming voice not found in active voices")

    val = FormValue.get()

    active_voices.pop(voice).on_release(val)


def onTick():
    """Called every tick for continuous processing and updates."""

    val = FormValue.get()

    for slicer in active_voices.values():
        slicer.on_tick(val)
