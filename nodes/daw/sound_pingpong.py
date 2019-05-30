import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class pingpongSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_pingpongSound"
    bl_label = "SOUND PingPong Player"
    bl_width_default = 170

    message : StringProperty()
    revA    : BoolProperty(name="Reverse Alt",default=False)

    def draw(self,layout):
        layout.label(text="Don't use mp3 files!",icon="OUTLINER_OB_SPEAKER")
        layout.prop(self,"revA")

    def create(self):
        self.newInput("an_FloatSocket","Volume","volM",value=1,minValue=0,maxValue=5)
        self.newInput("an_IntegerSocket","Loops","loop",value=1,minValue=1,maxValue=10)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,volM,loop,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if volM == 0:
            self.color = (0.75,1,0.75)
        else:
            self.color = (0.65,1,1)
        self.label = "SOUND PingPong Player"
        if isinstance(snd, aud.Sound):
            if self.revA:
                sndR = snd.reverse()
                sndR = sndR.pingpong()
            snd = snd.pingpong()
            snd = snd.volume(volM)
            rev = False
            if loop > 1:
                for i in range(0,loop):
                    if i == 0:
                        sndO = snd
                    else:
                        sndO = sndO.join(sndR) if rev and self.revA else sndO.join(snd)
                    rev = False if rev else True
                return sndO
            else:
                return snd
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Pg BYPASS (No Sound)"
            return None
