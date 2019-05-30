import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class volumeSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_volumeSound"
    bl_label = "SOUND Volume"
    bl_width_default = 150

    def create(self):
        self.newInput("an_FloatSocket","Volume","volume",value=1,minValue=0,maxValue=5)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,volume,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if volume > 0:
            self.label = "SOUND Volume"
            self.color = (0.65,1,1)
            if isinstance(snd, aud.Sound):
                snd = snd.volume(volume)
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Vo BYPASS (No Sound)"
                return None
        else:
            self.label = "SOUND Vo BYPASS (0 Volume)"
            self.color = (0.75,1,0.75)

        return snd
