import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
from . daw_functions import getIndex, getFreq, findNote
from . utils_setup import getSysData

class calcSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_calcSound"
    bl_label = "UTILS Calculator"
    bl_width_default = 210

    beatM     : IntProperty(name="System Beat Multipler",default=1,min=1,max=64)

    def draw(self,layout):
        layout.prop(self,"beatM")

    def create(self):
        self.newInput("an_TextSocket","Note","noteName")
        self.newInput("an_IntegerSocket","Octave Shift","octS",value=0,minValue=-6,maxValue=2)
        self.newInput("an_FloatSocket","Input Frequency","freqI")
        self.newInput("an_IntegerSocket","Semitone Offset","semiI",value=1,minValue=-12,maxValue=12)
        self.newInput("an_IntegerSocket","Samples","samples",value=44100,minValue=5000)
        self.newOutput("an_TextSocket","note Name","noteO")
        self.newOutput("an_FloatSocket","Factor","factor")
        self.newOutput("an_FloatSocket","Inverse Factor","factorI")
        self.newOutput("an_FloatSocket","Semitone Pitch Shift","offsetP")
        self.newOutput("an_FloatSocket","Frequency","frequency")
        self.newOutput("an_FloatSocket","Note Timing (Uses Setup Node)","timing")
        self.newOutput("an_FloatSocket","Note Samples (Uses Setup Node)","timingS")

    def execute(self,noteName,octS,freqI,semiI,samples):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.73,0.83,1)
        store = getSysData(self)
        if "Time_NL" in store:
            cut = getSysData(self)["Time_NL"] * self.beatM
        else:
            cut = 0
        lenS = int(round(cut * samples,0))

        if noteName is not "":
            indX = getIndex(noteName)
            if indX in range(0,131):
                freqI = getFreq(indX)
            else:
                self.color = (0.75,1,0.75)
                return "", 0, 0, 0, 0, cut, lenS
        elif freqI != 0:
            noteName = findNote(freqI)
        facO = 1
        if semiI > 0 and semiI < 12:
            outF = (1 / (0.5**(semiI/12))) * freqI
            facO = 1 / (0.5**(semiI/12))
        elif semiI < 0 and semiI > -12:
            outF = (1 / (0.5**((12-abs(semiI))/12))) * (freqI / 2)
            facO = (1 / (0.5**((12-abs(semiI))/12))) * 0.5
        elif semiI == 12:
            outF = freqI * 2
            facO = 2
        elif semiI == -12:
            outF = freqI / 2
            facO = 0.5
        else:
            outF = freqI
            facO = 1
        facI = 1 / facO
        if octS < 0:
            for i in range(0,abs(octS)):
                outF = outF / 2
        if octS > 0:
            for i in range(0,abs(octS)):
                outF = outF * 2
        return noteName, facO, facI, facO-1, outF, cut, lenS
