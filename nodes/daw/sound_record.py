import bpy
import aud
import os
from pathlib import Path
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from ... utils.sequence_editor import getOrCreateSequencer, getEmptyChannel
from ... utils.path import getAbsolutePathOfSound

class recordSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_recordSound"
    bl_label = "SOUND Recorder"
    bl_width_default = 200

    sndO = {}
    message  : StringProperty()
    fileName : StringProperty(name="Sound Name")
    startF   : IntProperty(name="Start Frame",min=2,default=2)
    stopF    : IntProperty(name="End Frame",min=3,default=3)
    channel  : IntProperty(name="VSE Channel",min=0)

    def draw(self,layout):
        layout.prop(self,"fileName")
        layout.prop(self,"startF")
        layout.prop(self,"stopF")
        layout.prop(self,"channel")
        if self.message is not '':
            layout.label(text=self.message, icon='INFO')

    def create(self):
        self.newInput("an_BooleanSocket","Write Sound to FLAC File","writeF",value=False)
        self.newInput("an_BooleanSocket","Overwrite Existing","writeO",value=False)
        self.newInput("an_FloatSocket","Short Note Time","noteT")
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_GenericSocket","Recorded Sound Store","sound")

    def execute(self,writeF,writeO,noteT,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if self.stopF <= self.startF:
            self.color = (0.75,1,0.75)
            self.message = "Start/Stop Frames Invalid"
            return None
        if noteT ==0:
            self.message = "0 Short Note Time"
            self.color = (0.75,1,0.75)
            return None
        elif writeF:
            if self.fileName == "" or "/" in self.fileName:
                self.color = (0.75,1,0.75)
                self.message = "Enter Sound Name (AphaNum Only)"
                return None
            self.color = (1,0.5,0.5)
            self.message = "Recording from Frame "+str(self.startF)+" to Frame"+str(self.stopF)
            frameC = bpy.context.scene.frame_current
            if frameC == bpy.context.scene.frame_end or frameC == self.stopF:
                pathF = bpy.data.filepath[:-6]+"_"+self.fileName+str(self.startF)+"_"+str(self.stopF)+".flac"
                my_file = Path(pathF)
                if my_file.is_file():
                    if writeO:
                        os.remove(pathF)
                    else:
                        self.message = "Output File Exists, No Overwrite"
                        self.inputs[0].value = False
                        self.color = (0.75,1,0.75)
                        return None
                if self.fileName in self.sndO:
                    if len(self.sndO[self.fileName]) > 0:
                        sndM = self.sndO[self.fileName][0]
                        for s in self.sndO[self.fileName]:
                            sndM = sndM.mix(s)
                if self.fileName in self.sndO:
                    self.sndO[self.fileName].clear()
                sndW = sndM.write(pathF,aud.RATE_16000,aud.CHANNELS_STEREO,aud.FORMAT_FLOAT32,aud.CONTAINER_FLAC,aud.CODEC_FLAC)
                self.message = pathF
                self.inputs[0].value = False
                self.color = (0.75,1,0.75)
                self.message = "Written File "+pathF
                # Load to VSE
                editor = getOrCreateSequencer(self.nodeTree.scene)
                channel = getEmptyChannel(editor) if self.channel == 0 else self.channel
                offSet = self.startF
                sequence = editor.sequences.new_sound(
                    name = self.fileName+str(self.startF)+"_"+str(self.stopF),
                    filepath = pathF,
                    channel = channel,
                    frame_start = offSet)
                sequence.show_waveform = True
                return self.sndO
            elif frameC < self.startF:
                if self.fileName in self.sndO:
                    if writeO:
                        self.sndO[self.fileName] = []
                    else:
                        self.message = "Sound Name "+self.fileName+" in Use"
                        self.color = (0.75,1,0.75)
                        return self.sndO
            else:
                if isinstance(snd,aud.Sound):
                    if self.fileName not in self.sndO:
                        self.sndO[self.fileName] = []
                    sndD = snd.delay((frameC-self.startF)*noteT)
                    self.message = "Adding Sound "+str(frameC)+"-D "+str((frameC-self.startF)*noteT)
                    self.sndO[self.fileName].append(sndD)
                return self.sndO
        else:
            self.color = (0.75,1,0.75)
            self.message = "Not Recording"
            return None
