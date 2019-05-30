import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class DelaySound(bpy.types.Node, AnimationNode):
    bl_idname = "an_DelaySound"
    bl_label = "SOUND Single Delay"
    bl_width_default = 150

    def create(self):
        self.newInput("an_FloatSocket","Delay (s)","delayT",minValue=0)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,delayT,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if delayT > 0:
            self.label = "SOUND Delay"
            self.color = (0.65,1,1)
            if isinstance(snd, aud.Sound) and delayT > 0:
                snd = snd.delay(delayT)
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND De BYPASS (No Sound)"
                return None
        else:
            self.label = "SOUND De BYPASS (0 Delay)"
            self.color = (0.75,1,0.75)
        return snd
