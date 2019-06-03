import bpy
import aud
import numpy as np
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from math import pi, sin

class pitchVarSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_pitchVarSound"
    bl_label = "SOUND Variable Pitch"
    bl_width_default = 180

    def create(self):
        self.newInput("an_FloatSocket","Max Pitch Shift","maxOff",value=1,minValue=-1,maxValue=1)
        self.newInput("an_BooleanSocket","Up/Down","typeB",value=False)
        self.newInput("an_BooleanSocket","Full Cycle","fullB",value=False)
        self.newInput("an_IntegerSocket","Resolution","resN",value=30,minValue=10,maxValue=100)
        self.newInput("an_IntegerSocket","Samples","samples",value=44100,minValue=5000)
        self.newInput("an_BooleanSocket","Mix Original","mixO")
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,maxOff,typeB,fullB,resN,samples,mixO,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.65,1,1)
        if isinstance(snd, aud.Sound):
            if maxOff != 0:
                self.label = "SOUND Variable Pitch"
                # Incomming sound length in seconds:
                sliceT = snd.length / samples
                refT   = sliceT / resN
                for i in range(0,resN):
                    strT = refT*i
                    endT = (refT*i)+refT
                    slice = snd.limit(strT,endT)
                    cycN = resN if fullB else resN * 2
                    pVal = 1+(sin(i*(pi/cycN)) * maxOff) if typeB else 1-(sin(i*(pi/cycN)) * maxOff)
                    sndS = slice.pitch(pVal).resample(samples,False)
                    if i == 0:
                        sndO = sndS
                    else:
                        sndO = sndO.join(sndS)
                if sndO.specs[1] != 2:
                    sndO = sndO.rechannel(2)
                if not typeB and not fullB:
                    sndO = sndO.fadeout((sliceT*0.93),(sliceT*0.07))
                if mixO:
                    sndO = sndO.mix(snd)
                if sndO.length > 0:
                    return sndO
                else:
                    self.color = (0.75,1,0.75)
                    self.label = "SOUND Vp BYPASS (Failed)"
                    return snd
                return sndO
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Vp BYPASS (0 Pitch Shift)"
                return snd
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Vp BYPASS (No Sound)"
            return None
