import bpy
import aud
import os
from pathlib import Path
from ... utils.sequence_editor import getOrCreateSequencer, getEmptyChannel
from ... utils.path import getAbsolutePathOfSound
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class FileSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_FileSound"
    bl_label = "SOUND Play File"
    bl_width_default = 150

    message   : StringProperty()
    soundFile : StringProperty()
    soundName : StringProperty()

    def draw(self,layout):
        col = layout.column()
        col.scale_y = 1.2
        self.invokeSelector(col, "PATH", "loadFile",
            text = "Load Sound File", icon = "FILE_NEW")
        self.invokeFunction(col, "clearFile",
            text = "Clear Sound File", icon = "EVENT_X")
        self.invokeFunction(col, "addSound", text="Add Sound File to VSE", icon="SPEAKER")
        if self.message is not '':
            layout.label(text=self.message,icon="NONE")

    def create(self):
        self.newInput("an_FloatSocket","Volume","volume",value=1,minValue=0.001,maxValue=5)
        self.newInput("an_FloatSocket","Start Offset (s)","startoff",value=0,minValue=0)
        self.newInput("an_FloatSocket","Duration (s)","duration",value=1,minValue=0)
        self.newInput("an_IntegerSocket","Samples","samples",value=44100,minValue=5000)
        self.newInput("an_BooleanSocket","Reverse","revB",value = False)
        self.newOutput("an_IntegerSocket","Samples","samplesO")
        self.newOutput("an_SoundSocket","Sound","sound")


    def clearFile(self):
        self.soundFile = ""
        self.soundName = ""
        self.message = ""
        self.color = (0.75,1,0.75)

    def addSound(self):
        if self.soundFile is not "":
            frameC = bpy.context.scene.frame_current
            path = self.soundFile
            editor = getOrCreateSequencer(self.nodeTree.scene)
            channel = getEmptyChannel(editor)
            sequence = editor.sequences.new_sound(
                name = os.path.basename(path),
                filepath = path,
                channel = channel,
                frame_start = frameC)
            sequence.show_waveform = True
            self.message = "File Added to VSE"
        else:
            self.message1 = "No File to Add"

    def loadFile(self,path):
        self.soundFile = str(path)
        self.soundName = str(os.path.basename(path))
        self.message = 'File Loaded: '+self.soundName

    def execute(self,volume,startoff,duration,samples,revB):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.95,0.6)
        len = 0
        if duration > 0:
            if self.soundFile is not '':
                my_file = Path(self.soundFile)
                if not my_file.is_file():
                    return samples, None
                snd = aud.Sound.file(self.soundFile)
                snd = snd.volume(volume)
                if int(snd.specs[0]) != samples:
                    snd = snd.resample(samples,False)

                if revB:
                    snd = snd.reverse()
            else:
                return len, None
            duration = duration + startoff
            snd = snd.limit(startoff,duration).fadein(0,duration*0.03).fadeout((duration*0.97),(duration*0.03))
            snd = snd.rechannel(2)
            self.label = "SOUND Play File"
        else:
            self.color = (0.75,1,0.75)
            snd = None

        return samples, snd
