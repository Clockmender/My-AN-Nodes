import bpy
import aud
import numpy as np
import os
from pathlib import Path
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class distortSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_distortSound"
    bl_label = "SOUND Distortion"
    bl_width_default = 150

    message : StringProperty()

    def draw(self,layout):
        if self.message is not '':
            layout.label(text=self.message,icon='NONE')

    def create(self):
        self.newInput("an_IntegerSocket","Distortion","ampM",value=1,minValue=1,maxValue=100)
        self.newInput("an_TextSocket","Name","nameF",value="1")
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,ampM,nameF,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.label = "SOUND Distortion"
        self.color = (0.65,1,1)
        if isinstance(snd, aud.Sound) and ampM > 1 and nameF is not "":
            snd = snd.volume(ampM)
            pathF = bpy.data.filepath[:-6]+"_"+nameF+"dist.flac"
            my_file = Path(pathF)
            if my_file.is_file():
                self.message = "File Exists, Enter New Name/Delete it"
                self.color = (0.75,1,0.75)
                return snd
            sndW = snd.write(pathF,aud.RATE_16000,aud.CHANNELS_STEREO,aud.FORMAT_FLOAT32,aud.CONTAINER_FLAC,aud.CODEC_FLAC)
            sndO = snd.file(pathF)
            self.message = ""
            return sndO
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Di BYPASS (No Sound/No Name)"
            return snd
