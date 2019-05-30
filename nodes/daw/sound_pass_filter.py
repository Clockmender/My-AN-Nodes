import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class passFilter(bpy.types.Node, AnimationNode):
    bl_idname = "an_passFilter"
    bl_label = "SOUND High/LowPass Filter"
    bl_width_default = 180

    highB : BoolProperty(name="HighPass",default=True)
    lowB  : BoolProperty(name="LowPass",default=True)

    def draw(self,layout):
        layout.prop(self,"highB")
        layout.prop(self,"lowB")

    def create(self):
        self.newInput("an_FloatSocket","High Frequency","frequencyH",minValue=15,maxValue=20000)
        self.newInput("an_FloatSocket","High Q Factor","qfactorH",value=0.5,minValue=0,maxValue=1)
        self.newInput("an_FloatSocket","Low Frequency","frequencyL",minValue=15,maxValue=20000)
        self.newInput("an_FloatSocket","Low Q Factor","qfactorL",value=0.5,minValue=0,maxValue=1)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,frequencyH,qfactorH,frequencyL,qfactorL,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if frequencyL <= frequencyH and self.highB and self.lowB:
            self.label = "SOUND Notch"
            self.color = (0.65,1,1)
        elif frequencyL > frequencyH and self.highB and self.lowB:
            self.label = "SOUND BandPass"
            self.color = (0.65,1,1)
        elif (self.highB and not self.lowB) or (self.lowB and not self.highB):
            self.label = "SOUND High/LowPass Filter"
            self.color = (0.65,1,1)
        elif not self.highB and not self.lowB:
            self.label = "SOUND HLF BYPASS (No Types)"
            self.color = (0.75,1,0.75)

        if qfactorH == 0 and qfactorL == 0:
            self.label = "SOUND HLF BYPASS (0 QFactors)"
            self.color = (0.75,1,0.75)
            return None
        elif qfactorH == 0 and self.highB:
            self.label = "SOUND HLF BYPASS (0 QFactor H)"
            self.color = (0.75,1,0.75)
            return None
        elif qfactorL == 0 and self.lowB:
            self.label = "SOUND HLF BYPASS (0 QFactor L)"
            self.color = (0.75,1,0.75)
            return None

        if isinstance(snd, aud.Sound):
            if self.highB:
                snd = snd.highpass(frequencyH,qfactorH)
            if self.lowB:
                snd = snd.lowpass(frequencyL,qfactorL)
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Hl BYPASS (No Sound)"
            return None
        return snd

#Alko TCS Duotec 2500
