import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class an_chorusSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_chorusSound"
    bl_label = "SOUND Chorus"
    bl_width_default = 150

    def create(self):
        self.newInput("an_FloatSocket","Delay (s)","delayT",minValue=0,maxValue=0.03)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,delayT,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if delayT > 0:
            self.label = "SOUND Chorus"
            self.color = (0.65,1,1)
            if isinstance(snd, aud.Sound) and delayT > 0:
                snd1 = snd.delay(delayT)
                snd = snd.mix(snd1)
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Ch BYPASS (No Sound)"
                return None
        else:
            self.label = "SOUND Ch BYPASS (0 Delay)"
            self.color = (0.75,1,0.75)
        return snd
