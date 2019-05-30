import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class thresholdSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_thresholdSound"
    bl_label = "SOUND Threshold"
    bl_width_default = 150

    def create(self):
        self.newInput("an_FloatSocket","Threshold","threshold",minValue=0,maxValue=0.5)
        self.newInput("an_FloatSocket","Volume","volume",value=1,minValue=0.001,maxValue=5)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,threshold,volume,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if threshold > 0 and volume > 0:
            if isinstance(snd, aud.Sound):
                self.color = (0.65,1,1)
                self.label = "SOUND Threshold"
                snd = snd.threshold(threshold)
                snd = snd.volume(volume)
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Th BYPASS (No Sound)"
                return None
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Th BYPASS (0 Inputs)"
        return snd
