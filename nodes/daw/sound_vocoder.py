import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . daw_functions import getIndex, getFreq, getChord, osc

enum = [('Sine','Sine','Oscillator','',0),
    ('Sawtooth','Sawtooth','Oscillator','',1),
    ('Triangle','Triangle','Oscillator','',2),
    ('Square','Square','Oscillator','',3)
    ]

class vocoderSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_vocoderSound"
    bl_label = "SOUND VoCoder"
    bl_width_default = 200

    mode      : EnumProperty(name = "OSC 1", items = enum, update = AnimationNode.refresh)
    message   : StringProperty()
    soundFile : StringProperty()
    soundName : StringProperty()

    def draw(self,layout):
        layout.prop(self, "mode")
        col = layout.column()
        col.scale_y = 1.2
        self.invokeSelector(col, "PATH", "loadFile",
            text = "Load Sound File", icon = "FILE_NEW")
        self.invokeFunction(col, "clearFile",
            text = "Clear Sound File", icon = "EVENT_X")
        if self.message is not '':
            layout.label(text=self.message,icon="NONE")

    def create(self):
        self.newInput("an_TextSocket","Note","noteName")
        self.newInput("an_FloatSocket","Frequency","frequency",value=440,minValue=0.1)
        self.newInput("an_FloatSocket","Volume","volume",value=0.2,minValue=0.001,maxValue=5)
        self.newInput("an_FloatSocket","Start Offset (s)","startT",value=0,minValue=0)
        self.newInput("an_FloatSocket","Duration (s)","duration",value=1,minValue=0)
        self.newInput("an_IntegerSocket","Samples","samples",value=44100,minValue=5000)
        self.newInput("an_BooleanSocket","Reverse","revB",value=False)
        self.newOutput("an_IntegerSocket","Samples","samplesO")
        self.newOutput("an_SoundSocket","Sound","sound")

    def clearFile(self):
        self.soundFile = ""
        self.soundName = ""
        self.message = ""

    def loadFile(self,path):
        self.soundFile = str(path)
        self.soundName = str(os.path.basename(path))
        self.message = 'File Loaded: '+self.soundName

    def execute(self,noteName,frequency,volume,startT,duration,samples,revB):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.65,1,1)
        self.message = ""
        self.label = "SOUND VoCoder"
        if duration > 0:
            indX = getIndex(noteName)
            if indX in range(0,131):
                freq = getFreq(indX)
            elif frequency >= 0.1:
                freq = frequency
            else:
                self.message = 'Note Invalid'
                self.color = (0.75,1,0.75)
                return samples, None
            if self.soundFile is not '':
                sndV = aud.Sound.file(self.soundFile)
                sndV = sndV.volume(volume)
                if revB:
                    sndV = sndV.reverse()
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Vc BYPASS (No Sound File)"
                return samples, None

            durationF = duration + startT
            sndV = sndV.limit(startT,durationF).volume(volume)
            if sndV.specs[1] != 2:
                sndV = sndV.rechannel(2)
            sndI = osc(self.mode,freq,samples,duration,volume)
            try:
                sndO = sndV.modulate(sndI)
            except:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Vc BYPASS (Incompatible Sounds)"
                return samples, None
            return samples, sndO
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Vc BYPASS (0 Duration)"
            return samples, None
