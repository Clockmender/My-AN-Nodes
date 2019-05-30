import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class fadeSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_fadeSound"
    bl_label = "SOUND Fader"
    bl_width_default = 180

    def create(self):
        self.newInput("an_FloatSocket","Start","start",minValue=0)
        self.newInput("an_FloatSocket","Length","length",value=1,minValue=0)
        self.newInput("an_FloatSocket","Input Duration","durI")
        self.newInput("an_IntegerSocket","Fade %","durP",value=0,minValue=0,maxValue=99)
        self.newInput("an_BooleanSocket","Fade In/out","fade",value=False)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,start,length,durI,durP,fade,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if durP > 0:
            if fade:
                startW = 0.0
            else:
                startW = round(durI * ((100-durP)/100),4)
            lengthW = round(durI * (durP/100),4)
        else:
            startW = start
            lengthW = length

        if length > 0 or durP > 0:
            self.label = "SOUND Fader"
            self.color = (0.65,1,1)
            if isinstance(snd, aud.Sound):
                if fade:
                    snd = snd.fadein(startW,lengthW)
                else:
                    snd = snd.fadeout(startW,lengthW)
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Fa BYPASS (No Sound)"
                return None
        else:
            self.label = "SOUND Fa BYPASS (0 Inputs)"
            self.color = (0.75,1,0.75)
        return snd
