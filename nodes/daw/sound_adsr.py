import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class adsrSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_adsrSound"
    bl_label = "SOUND ADSR"
    bl_width_default = 150

    def create(self):
        self.newInput("an_FloatSocket","Attack","attack",minValue=0)
        self.newInput("an_FloatSocket","Decay","decay",minValue=0)
        self.newInput("an_FloatSocket","Sustain","sustain",minValue=0,maxValue=0.99)
        self.newInput("an_FloatSocket","Release","release",minValue=0,maxValue=0.99)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,attack,decay,sustain,release,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if attack > 0 and decay > 0 and sustain > 0 and release > 0:
            self.label = "SOUND ADSR"
            self.color = (0.65,1,1)
            if isinstance(snd, aud.Sound):
                sndO = snd.ADSR(attack,decay,sustain,release)
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND ADSR BYPASS (No Sound)"
                return None
        else:
            self.label = "SOUND ADSR BYPASS (0 Inputs)"
            self.color = (0.75,1,0.75)
            return snd
        return sndO
