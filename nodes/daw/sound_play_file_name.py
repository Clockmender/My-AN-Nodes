import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class playFileSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_playFileSound"
    bl_label = "SOUND Play File by Note Name"
    bl_width_default = 200

    message   : StringProperty()
    soundFile : StringProperty()
    soundName : StringProperty()

    def draw(self,layout):
        col = layout.column()
        col.scale_y = 1.2
        if self.message is not '':
            layout.label(text=self.message,icon="NONE")

    def create(self):
        self.newInput("an_TextSocket","Note","noteName")
        self.newInput("an_TextSocket","File Directory","direct",value="/Users/mac/Music/Piano Sounds/")
        self.newInput("an_FloatSocket","Volume","volume",value=1,minValue=0.001,maxValue=30)
        self.newInput("an_FloatSocket","Start Offset (s)","startoff",value=0,minValue=0)
        self.newInput("an_FloatSocket","Duration (s)","duration",value=1,minValue=0)
        self.newInput("an_BooleanSocket","Reverse","revB",value = False)
        self.newOutput("an_SoundSocket","Sound","sound")

    def execute(self,noteName,direct,volume,startoff,duration,revB):
        # Plays a specific set of clips that use flat instead of sharp
        # File format is Piano.pp.Db4.aiff
        duration = duration + startoff
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.95,0.6)
        if duration > 0:
            if noteName is not '':
                noteNameR = noteName.capitalize()
                if noteName[1] == "s":
                    letters = ["C","D","E","F","G","A","B"]
                    indX = letters.index(noteNameR[0]) + 1
                    letter = letters[indX]
                    noteNameR = letter+"b"+noteNameR[-1]
                self.label = "SOUND Play File by Note Name: "+noteNameR

                self.soundFile = direct+"Piano.pp."+noteNameR+".aiff"
                snd = aud.Sound.file(self.soundFile)
                snd = snd.volume(volume)
                duration = duration + startoff
                snd = snd.limit(startoff,duration).fadein(0,duration*0.03).fadeout((duration*0.97),(duration*0.03))
                if snd.specs[1] != 2:
                    snd = snd.rechannel(2)
                if revB:
                    snd = snd.reverse()
            else:
                return None
        else:
            snd = None

        self.Soundfile = ""
        return snd
