import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . daw_functions import getIndex, getFreq, osc

enum = [('Sine','Sine','Oscillator','',0),
    ('Sawtooth','Sawtooth','Oscillator','',1),
    ('Triangle','Triangle','Oscillator','',2)
    ]

class modulateSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_modulateSound"
    bl_label = "SOUND Modulator"
    bl_width_default = 180

    message   : StringProperty()
    mode      : EnumProperty(name = "OSC", items = enum, update = AnimationNode.refresh)

    def draw(self,layout):
        layout.prop(self, "mode")
        if self.message is not "":
            layout.label(text=self.message,icon="NONE")

    def create(self):
        self.newInput("an_TextSocket","Mod Note","noteName")
        self.newInput("an_FloatSocket","Mod Frequency","freqMod",minValue=0)
        self.newInput("an_FloatSocket","Volume","volM",value=1,minValue=0.001,maxValue=5)
        self.newInput("an_FloatSocket","Duration","durT",value=1)
        self.newInput("an_IntegerSocket","Samples","samples",value=44100,minValue=5000)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_IntegerSocket","Samples","samplesO")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,noteName,freqMod,volM,durT,samples,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.message = ""

        if freqMod > 0 or noteName is not "":
            self.label = "SOUND Modulator"
            self.color = (0.65,1,1)

            if noteName is not '':
                indX = getIndex(noteName)
                if indX in range(0,131):
                    freqMod = getFreq(indX)
                else:
                    self.message = 'Note Invalid'
                    return samples, snd

            if isinstance(snd, aud.Sound):
                sndI = osc(self.mode,freqMod,samples,durT*2,volM)
                try:
                    sndO = snd.modulate(sndI)
                except:
                    self.label = "SOUND Mo BYPASS (Incompatible Sounds)"
                    self.color = (0.75,1,0.75)
                    return samples, None
                return samples, sndO
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Mo BYPASS (No Sound)"
                return samples, None
        else:
            self.label = "SOUND Mo BYPASS (Too Low Frequency)"
            self.color = (0.75,1,0.75)
            return samples, snd.limit(0,durT)
