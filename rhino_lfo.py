import flvfx as vfx
import math
import random

shapeNames = [
    "Sine",
    "Square",
    "Triangle",
    "Ramp Up",
    "Ramp Down",
    "Sample & Hold",
    "Rnd",
]
phases = [0] * 8
LFOs = [0.5] * 8
lastramps = [0] * 8
randAmps = [1.0] * 8
randOffsets = [0.0] * 8
randPhases = [0.0] * 8


def onTick():
    global phases, LFOs, lastramps, randAmps, randOffsets, randPhases

    numLFOs = int(vfx.context.form.getInputValue("LFOs: Number of LFOs"))

    for i in range(numLFOs):
        if vfx.context.form.getInputValue("Speed: Range") == 0:
            denom = 1
        else:
            denom = 8

        if vfx.context.form.getInputValue("Speed: Sync"):
            phases[i] = (
                vfx.context.ticks
                * 2
                * math.pi
                * vfx.context.form.getInputValue("Speed: Speed")
                / (vfx.context.PPQ / denom)
            )
        else:
            phases[i] += (
                2
                * math.pi
                * vfx.context.form.getInputValue("Speed: Speed")
                / (vfx.context.PPQ / denom)
            )

        numShape = vfx.context.form.getInputValue("Shape: Shape")
        shape = shapeNames[numShape]

        ramp = (phases[i] / (2 * math.pi)) % 1

        if shape == "Sine":
            LFOs[i] = 0.5 * math.sin(phases[i]) + 0.5
        elif shape == "Rnd":
            if ramp < lastramps[i]:
                # GUIで設定されたランダム振幅の最小・最大値を取得
                randAmpMin = vfx.context.form.getInputValue("Rand: Rand Amp Min")
                randAmpMax = vfx.context.form.getInputValue("Rand: Rand Amp Max")

                randAmps[i] = random.uniform(randAmpMin, randAmpMax)
                randOffsets[i] = random.uniform(-0.5, 0.5)
                randPhases[i] = random.uniform(0, 2 * math.pi)

            LFOs[i] = (
                0.5 * (math.sin(phases[i] + randPhases[i]) * randAmps[i] + 1.0)
                + randOffsets[i]
            )
            LFOs[i] = max(0, min(1, LFOs[i]))
        elif shape == "Ramp Up":
            LFOs[i] = ramp
        elif shape == "Ramp Down":
            LFOs[i] = 1.0 - ramp
        elif shape == "Square":
            LFOs[i] = ramp > 0.5
        elif shape == "Triangle":
            LFOs[i] = 1 - 2 * abs(ramp - 0.5)
        elif shape == "Sample & Hold":
            if ramp < lastramps[i]:
                LFOs[i] = random.random()

        lastramps[i] = ramp

        # Amplitude & Offset adjustments
        LFOscl = (
            vfx.context.form.getInputValue("Amplitude: Amplitude") * (LFOs[i] - 0.5)
            + 0.5
        )
        LFOscl += (
            vfx.context.form.getInputValue("Amplitude: Offset")
            * 0.5
            * (1.0 - vfx.context.form.getInputValue("Amplitude: Amplitude"))
        )
        LFOscl = min(max(0, LFOscl), 1)

        vfx.setOutputController(f"LFO {i+1}", LFOscl)


scriptText = """Classic LFO. Offers a variety of waveform shapes (sine, square, triangle, ramp up, ramp down, sample & hold, random) and two different speed ranges (slower, faster). See Script for details."""


def createDialog():
    form = vfx.ScriptDialog("", scriptText)
    form.addGroup("LFOs")
    form.addInputKnob("Number of LFOs", 1, 1, 8, hint="Number of LFO outputs")
    form.endGroup()
    form.addGroup("Speed")
    form.addInputKnob("Speed", 0.5, 0, 1, hint="LFO speed: cycles / quarter note")
    form.addInputCombo(
        "Range",
        ["Slower", "Faster"],
        0,
        hint="LFO speed range: slower (x1), faster (x8)",
    )
    form.AddInputCheckbox("Sync", 0, hint="Sync to project clock")
    form.endGroup()
    form.addGroup("Amplitude")
    form.addInputKnob("Amplitude", 1, 0, 1, hint="LFO amplitude")
    form.addInputKnob("Offset", 0, -1, 1, hint="LFO offset")
    form.endGroup()
    form.addGroup("Shape")
    form.addInputCombo("Shape", shapeNames, 2, hint="LFO shape")
    form.endGroup()
    form.addGroup("Rand")
    form.addInputKnob("Rand Amp Min", 0.4, 0, 1, hint="Minimum random amplitude")
    form.addInputKnob("Rand Amp Max", 1.0, 0, 1, hint="Maximum random amplitude")
    form.endGroup()

    for i in range(8):
        vfx.addOutputController(f"LFO {i+1}", 0)

    return form
