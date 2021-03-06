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
        self.newInput("an_FloatSocket","Pitch Factor","pitch",minValue=0.1,maxValue=4)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,pitch,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,0.5)
        if snd is not None:
            snd = snd.pitch(pitch)
        return snd
