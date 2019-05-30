import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class envelopeSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_envelopeSound"
    bl_label = "SOUND Envelope"
    bl_width_default = 150

    def create(self):
        self.newInput("an_FloatSocket","Attack","attack",minValue=0)
        self.newInput("an_FloatSocket","Release","release",minValue=0)
        self.newInput("an_FloatSocket","Threshold","threshold",minValue=0)
        self.newInput("an_FloatSocket","A/R Threshold","arthreshold",minValue=0)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,attack,release,threshold,arthreshold,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if attack > 0:
            self.label = "SOUND Envelope"
            self.color = (0.65,1,1)
            if isinstance(snd, aud.Sound):
                snd = snd.envelope(attack,release,threshold,arthreshold)
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Ev BYPASS (No Sound)"
                return None
        else:
            self.label = "SOUND Ev BYPASS (0 Inputs)"
            self.color = (0.75,1,0.75)
        return snd
