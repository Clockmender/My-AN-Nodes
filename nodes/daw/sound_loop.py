import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class loopSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_loopSound"
    bl_label = "SOUND Loop"
    bl_width_default = 150

    def create(self):
        self.newInput("an_IntegerSocket","Loops","loop",value=1,minValue=1,maxValue=10)
        self.newInput("an_FloatSocket","Duration","durT",value=1)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_FloatSocket","Duration","duration")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,loop,duration,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.65,1,1)
        if loop > 1:
            self.label = "SOUND Loop"
            self.color = (0.65,1,1)
            if isinstance(snd, aud.Sound):
                snd = snd.loop(loop-1)
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Lo BYPASS (No Sound)"
                return duration, None
        else:
            self.label = "SOUND Lo BYPASS (0 Count)"
            self.color = (0.75,1,0.75)
            return duration, snd
        return duration*(loop+1), snd
