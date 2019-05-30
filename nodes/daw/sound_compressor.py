import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class compressorFilter(bpy.types.Node, AnimationNode):
    bl_idname = "an_compressorFilter"
    bl_label = "SOUND Compressor"
    bl_width_default = 200

    low1   : FloatProperty(name="Low Frequency",min=15,max=20000)
    qlfac1 : FloatProperty(name="L-QFactor",min=0,max=1)

    low2   : FloatProperty(name="Low Frequency",min=15,max=20000)
    qlfac2 : FloatProperty(name="L-QFactor",min=0,max=1)
    high1  : FloatProperty(name="High Frequency",min=15,max=20000)
    qhfac1 : FloatProperty(name="H-QFactor",min=0,max=1)

    low3   : FloatProperty(name="Low Frequency",min=15,max=20000)
    qlfac3 : FloatProperty(name="L-QFactor",min=0,max=1)
    high2  : FloatProperty(name="High Frequency",min=15,max=20000)
    qhfac2 : FloatProperty(name="H-QFactor",min=0,max=1)

    high3  : FloatProperty(name="High Frequency",min=15,max=20000)
    qhfac3 : FloatProperty(name="H-QFactor",min=0,max=1)

    def draw(self,layout):
        layout.label(text="First LowPass",icon="NONE")
        layout.prop(self,"low1")
        layout.prop(self,"qlfac1")
        layout.label(text="First BandPass",icon="NONE")
        layout.prop(self,"low2")
        layout.prop(self,"qlfac2")
        layout.prop(self,"high1")
        layout.prop(self,"qhfac1")
        layout.label(text="Second BandPass",icon="NONE")
        layout.prop(self,"low3")
        layout.prop(self,"qlfac3")
        layout.prop(self,"high2")
        layout.prop(self,"qhfac2")
        layout.label(text="Final HighPass",icon="NONE")
        layout.prop(self,"high3")
        layout.prop(self,"qhfac3")

    def create(self):
        self.newInput("an_FloatSocket","Master Volume","volM",value=1,minValue=0,maxValue=5)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,volM,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if any([self.qlfac1==0,self.qlfac2==0,self.qlfac3==0,self.qhfac1==0,self.qhfac2==0,self.qhfac2==0]):
            self.label = "SOUND C BYPASS (QFs = 0)"
            self.color = (0.75,1,0.75)
            self.label = "SOUND D BYPASS (0 Inputs)"
            return None
        else:
            self.label = "SOUND Compressor"
            self.color = (0.65,1,1)
            if isinstance(snd, aud.Sound):
                # first LowPass
                snd = snd.lowpass(self.low1,self.qlfac1)
                # first BandPass
                snd = snd.lowpass(self.low2,self.qlfac2)
                snd = snd.highpass(self.high1,self.qhfac1)
                # second BandPass
                snd = snd.lowpass(self.low3,self.qlfac3)
                snd = snd.highpass(self.high2,self.qhfac2)
                # final HighPass
                snd = snd.highpass(self.high3,self.qhfac3)
                if volM != 0:
                    snd = snd.volume(volM)
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Co BYPASS (No Sound)"
                return None
        return snd
