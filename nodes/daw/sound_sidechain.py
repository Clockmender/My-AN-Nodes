import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class sidechainSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_sidechainSound"
    bl_label = "SOUND Side-Chain"
    bl_width_default = 150

    message : StringProperty()

    def draw(self,layout):
        if self.message is not '':
            layout.label(text=self.message,icon='NONE')

    def create(self):
        self.newInput("an_IntegerSocket","Samples","samples",value=12000,minValue=6000)
        self.newInput("an_SoundSocket","Sound C","sndC")
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,samples,sndC,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.label = "SOUND Side-Chain"
        self.color = (0.65,1,1)
        if isinstance(snd, aud.Sound) and isinstance(sndC, aud.Sound):
            sndArrayI = snd.data()
            sndArrayA = sndC.data()

            for i in range(0,len(sndArrayI)):
                if i < len(sndArrayA):
                    if sndArrayI[i][0] > 0:
                        sndArrayI[i][0] = sndArrayI[i][0] - abs(sndArrayA[i][0])
                    else:
                         sndArrayI[i][0] = sndArrayI[i][0] + abs(sndArrayA[i][0])

                    if sndArrayI[i][1] > 0:
                        sndArrayI[i][1] = sndArrayI[i][1] - abs(sndArrayA[i][1])
                    else:
                         sndArrayI[i][1] = sndArrayI[i][1] + abs(sndArrayA[i][1])

            sndO = aud.Sound.buffer(sndArrayI,samples)
            if sndO.specs[1] != 2:
                sndO = sndO.rechannel(2)
            return sndO
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Sc BYPASS (No Sound)"
            return None
        return snd
