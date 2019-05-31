import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class pitchSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_pitchSound"
    bl_label = "SOUND Pitch Bender"
    bl_width_default = 150

    def create(self):
        self.newInput("an_IntegerSocket","Pitch Factor","pitch",value=1,minValue=0.25,maxValue=4)
        self.newInput("an_FloatSocket","Samples","samples")
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,pitch,samples,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if pitch != 1:
            self.color = (0.65,1,1)
            self.label = "SOUND Pitch Bender"
            if isinstance(snd, aud.Sound) and pitch != 1.0:
                snd = snd.pitch(pitch)
                snd = snd.resample(samples,False)
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Pb BYPASS (No Sound)"
                return None
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Pb BYPASS (1 Pitch)"
        return snd
