import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class pitchSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_resampleSound"
    bl_label = "SOUND Resampler"
    bl_width_default = 150

    def create(self):
        self.newInput("an_IntegerSocket","Samples","samples",value=44100,min=6000)
        self.newInput("an_BooleanSocket","High Quality","qSpec")
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,samples,qSpec,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.65,1,1)
        self.label = "SOUND Resampler"
        if isinstance(snd, aud.Sound):
            if snd.specs[0] != samples:
                snd = snd.resample(samples,qSpec)
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Rs BYPASS (No Sound)"
            return None
        return snd
