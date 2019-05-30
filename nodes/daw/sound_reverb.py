import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class an_reverbSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_reverbSound"
    bl_label = "SOUND Reverb"
    bl_width_default = 150

    def create(self):
        self.newInput("an_FloatSocket","Delay (ms)","delayT",minValue=0,maxValue=20)
        self.newInput("an_FloatSocket","Poly Offset (ms)","polyO",minValue=0,maxValue=20)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,delayT,polyO,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if delayT > 0 and polyO > 0:
            delayT = delayT / 1000
            polyO = polyO / 1000
            self.label = "SOUND Reverb"
            self.color = (0.65,1,1)
            if isinstance(snd, aud.Sound) and delayT > 0:
                snd1 = snd.delay(delayT)
                snd = snd.mix(snd1)
                # Add polys
                sndl = snd.limit(polyO,snd.length)
                sndh = snd.limit(-polyO,snd.length)
                snd = snd.mix(sndl)
                snd = snd.mix(sndh)
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Rb BYPASS (No Sound)"
                return None
        else:
            self.label = "SOUND Rb BYPASS (0 Inputs)"
            self.color = (0.75,1,0.75)
        return snd
