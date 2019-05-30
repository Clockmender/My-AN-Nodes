import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class accumulateSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_accumulateSound"
    bl_label = "SOUND Accumulator"
    bl_width_default = 150

    def create(self):
        self.newInput("an_BooleanSocket","Additive","addB",value=False)
        self.newInput("an_FloatSocket","Limit (s)","limit")
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,addB,limit,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.label = "SOUND Accumulator"
        self.color = (0.65,1,1)
        if isinstance(snd, aud.Sound):
            snd = snd.accumulate(addB)
            snd = snd.limit(0,limit)
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Ac BYPASS (No Sound)"
            return None
        return snd
