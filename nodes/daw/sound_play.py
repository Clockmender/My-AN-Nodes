import bpy
import aud
import os
from pathlib import Path
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from ... utils.sequence_editor import getOrCreateSequencer, getEmptyChannel
from ... utils.path import getAbsolutePathOfSound

class PlaySound(bpy.types.Node, AnimationNode):
    bl_idname = "an_PlaySound"
    bl_label = "SOUND Output Player"
    bl_width_default = 170

    fileOut   : StringProperty(name="Name",default="")
    addF      : BoolProperty(name="Add Saved File to VSE",default=False,update=propertyChanged)
    channel   : IntProperty(name="VSE Channel",min=0)
    offSet    : IntProperty(name="Insert Frame",min=0)
    message : StringProperty()

    def draw(self,layout):
        layout.prop(self,"addF")
        if self.addF:
            layout.prop(self,"channel")
            layout.prop(self,"offSet")
        layout.prop(self,"fileOut")
        if self.message is not '':
            layout.label(text=self.message,icon="INFO")

    def create(self):
        self.newInput("an_FloatSocket","Volume","volM",value=1,minValue=0,maxValue=10)
        self.newInput("an_BooleanSocket","Write Sound to FLAC File","writeF",value=False)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,volM,writeF,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if volM == 0:
            self.color = (0.75,1,0.75)
        else:
            self.color = (1,0.95,0.6)
        dev = aud.Device()
        frameC = bpy.context.scene.frame_current
        if frameC == bpy.context.scene.frame_end or frameC == bpy.context.scene.frame_start:
            stop = dev.stopAll()
            return None
        else:
            self.message = ""
            if isinstance(snd, aud.Sound):
                if self.fileOut is not "" and writeF:
                    pathF = bpy.data.filepath[:-6]+"_"+self.fileOut+"_"+str(frameC)+".flac"
                    my_file = Path(pathF)
                    if my_file.is_file():
                        self.message = "File Exists, Enter New Name/Delete it"
                        self.addF = False
                        self.inputs[1].value = False
                    else:
                        sndW = snd.write(pathF,aud.RATE_16000,aud.CHANNELS_STEREO,aud.FORMAT_FLOAT32,aud.CONTAINER_FLAC,aud.CODEC_FLAC)
                        self.message = "Written "+str(pathF)
                        if self.addF:
                            editor = getOrCreateSequencer(self.nodeTree.scene)
                            channel = getEmptyChannel(editor) if self.channel == 0 else self.offSet
                            offSet = bpy.context.scene.frame_current if self.offSet == 0 else self.offSet
                            sequence = editor.sequences.new_sound(
                                name = os.path.basename(my_file),
                                filepath = fileName,
                                channel = self.channel,
                                frame_start = self.offSet)
                            sequence.show_waveform = True
                try:
                    snd = snd.volume(volM)
                    play = dev.play(snd)
                    return snd
                except:
                    self.color = (0.75,1,0.75)
                    return None
            else:
                self.color = (0.75,1,0.75)
                return None
