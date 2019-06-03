import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . daw_functions import getNote, getIndex, getChord, osc

enum = [('Sine','Sine','Oscillator','',0),
    ('Sawtooth','Sawtooth','Oscillator','',1),
    ('Triangle','Triangle','Oscillator','',2),
    ('Square','Square','Oscillator','',3)
    ]

class FMSynthDAW(bpy.types.Node, AnimationNode):
    bl_idname = "an_FMSynthDAW"
    bl_label = "SOUND FM Synthesiser"
    bl_width_default = 450

    message   : StringProperty()
    osc1      : EnumProperty(name = "OSC 1", items = enum, update = AnimationNode.refresh)
    osc2      : EnumProperty(name = "OSC 2", items = enum, update = AnimationNode.refresh)
    osc3      : EnumProperty(name = "OSC 3", items = enum, update = AnimationNode.refresh)
    osc4      : EnumProperty(name = "OSC 4", items = enum, update = AnimationNode.refresh)
    dir2      : BoolProperty(name="Up 2",default=True)
    dir3      : BoolProperty(name="Up 3",default=True)
    dir4      : BoolProperty(name="Up 4",default=True)
    vol1      : FloatProperty(name="Vol 1",default=1,min=0,max=2)
    vol2      : FloatProperty(name="Vol 2",default=1,min=0,max=2)
    vol3      : FloatProperty(name="Vol 3",default=1,min=0,max=2)
    vol4      : FloatProperty(name="Vol 4",default=1,min=0,max=2)
    sto1      : FloatProperty(name="Off 1",default=0,min=0,max=1)
    sto2      : FloatProperty(name="Off 2",default=0,min=0,max=1)
    sto3      : FloatProperty(name="Off 3",default=0,min=0,max=1)
    sto4      : FloatProperty(name="Off 4",default=0,min=0,max=1)

    def draw(self,layout):
        row = layout.row()
        col1 = row.column()
        col1.prop(self, "osc1")
        col1.prop(self, "vol1")
        col1.prop(self,"sto1")

        col2 = row.column()
        col2.prop(self, "osc2")
        col2.prop(self, "vol2")
        col2.prop(self,"sto2")
        col2.prop(self, "dir2")

        col3 = row.column()
        col3.prop(self, "osc3")
        col3.prop(self, "vol3")
        col3.prop(self,"sto3")
        col3.prop(self, "dir3")

        col4 = row.column()
        col4.prop(self, "osc4")
        col4.prop(self, "vol4")
        col4.prop(self,"sto4")
        col4.prop(self, "dir4")

        if self.message is not '':
            layout.label(text=self.message,icon="NONE")

    def create(self):
        self.newInput("an_FloatListSocket","Sound Data","listI")
        self.newInput("an_TextSocket","Note","noteName")
        self.newInput("an_IntegerSocket","Octave Shift","octaveS",value=0,minValue=-4,maxValue=4)
        self.newInput("an_FloatSocket","Duration (s)","durT",value=1,minValue=0)
        self.newInput("an_IntegerSocket","Samples","samples",value=44100,minValue=5000)
        self.newInput("an_FloatSocket","Master Volume","volM",value=1,minValue=0,maxValue=5)
        self.newOutput("an_IntegerSocket","Samples","samplesO")
        self.newOutput("an_SoundSocket","Sound O","sndO")

    def execute(self,listI,noteName,octaveS,durT,samples,volM):
        self.use_custom_color = True
        self.useNetworkColor = False
        if durT == 0:
            self.color = (0.75,1,0.75)
            return samples, None
        self.color = (1,0.95,0.6)
        vol1 = self.vol1 * volM
        vol2 = self.vol2 * volM
        vol3 = self.vol3 * volM
        vol4 = self.vol4 * volM
        self.message = ""
        sndM = None
        if len(listI) == 0:
            self.label = "SOUND FM Synthesiser"
            indX = getIndex(noteName)
            if indX in range(0,119):
                if octaveS != 0:
                    indX = indX + (octaveS*12)
                freqList = getChord(noteName,-4)
            else:
                self.label = "SOUND FM Synth BYPASS - No Input"
                self.color = (0.75,1,0.75)
                return samples, None
            playedNotes = [indX,0,volM,durT]
            rangeN = 1
        else:
            playedNotes = listI
            rangeN = int(len(listI) / 4)

        limit = 0
        for i in range(0,rangeN):
            n = i * 4
            indX   = int(playedNotes[n])
            if octaveS != 0:
                indX = indX + (octaveS*12)
            startT = playedNotes[n+1]
            soundV = playedNotes[n+2]
            durT   = playedNotes[n+3]
            noteName = getNote(indX,0)
            freqList = getChord(noteName,-4)

            # Carrier Sound
            snd1 = osc(self.osc1,freqList[3],samples,durT,vol1)
            snd1 = snd1.delay(self.sto1)

            r = 4 if self.dir2 else 2
            snd2 = osc(self.osc2,freqList[r],samples,durT,vol2)
            snd2 = snd2.delay(self.sto2)
            snd2 = snd1.modulate(snd2)

            r = 5 if self.dir3 else 1
            snd3 = osc(self.osc3,freqList[r],samples,durT,vol3)
            snd3 = snd3.delay(self.sto3)
            snd3 = snd1.modulate(snd3)

            r = 6 if self.dir4 else 0
            snd4 = osc(self.osc4,freqList[r],samples,durT,vol4)
            snd4 = snd4.delay(self.sto4)
            snd4 = snd1.modulate(snd4)

            sndO = snd1.mix(snd2).mix(snd3).mix(snd4).volume(soundV)
            if startT > 0:
                sndO = sndO.delay(startT)
            if sndO.specs[1] != 2:
                sndO = sndO.rechannel(2)
            if i == 0:
                sndM = sndO
            else:
                sndM = sndM.mix(sndO)
            if startT + durT > limit:
                limit = startT + durT

        sndM = sndM.limit(0,limit)
        if sndM.specs[1] != 2:
            sndM = sndM.rechannel(2)
        return samples, sndM
