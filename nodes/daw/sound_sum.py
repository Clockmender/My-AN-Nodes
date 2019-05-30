import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class sumSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_sumSound"
    bl_label = "SOUND Sum"
    bl_width_default = 150

    def create(self):
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.label = "SOUND Sum"
        self.color = (0.65,1,1)
        if isinstance(snd, aud.Sound):
            snd = snd.sum()
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Su BYPASS (No Sound)"
            return None
        return snd
