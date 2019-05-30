import bpy
import aud
import numpy as np
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from math import pi, sin

class flangerSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_flangerSound"
    bl_label = "SOUND Flanger"
    bl_width_default = 180

    def create(self):
        self.newInput("an_FloatSocket","Max Offset (ms)","maxOff",value=1,minValue=0.1,maxValue=20)
        self.newInput("an_IntegerSocket","Resolution","resN",value=30,minValue=10,maxValue=100)
        self.newInput("an_FloatSocket","Phase Length (s)","phaseL",value=1,minValue=0.1,maxValue=50)
        self.newInput("an_IntegerSocket","Samples","samples",value=44100,minValue=5000)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,maxOff,resN,phaseL,samples,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.65,1,1)
        if isinstance(snd, aud.Sound):
            self.label = "SOUND Flanger"
            seq = aud.Sequence()
            maxOff = maxOff / 1000
            # Incomming sound length in seconds:
            sliceT = snd.length / samples
            refT   = sliceT / resN

            for i in range(0,resN):
                slice = snd.limit(refT*i,(refT*i)+refT)
                shift = sin(((i * pi) /  phaseL)) * maxOff
                entry = seq.add(slice,(refT*i)+shift,(refT*i)+refT+shift,0)
            seq = seq.resample(samples,False)
            sndO = snd.mix(seq).limit(0,snd.length/samples)
            return sndO
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Fl BYPASS (No Sound)"
            return None
