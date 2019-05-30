import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . daw_functions import getNote, getChord, osc

enum = [('Sine','Sine','Oscillator','',0),
    ('Sawtooth','Sawtooth','Oscillator','',1),
    ('Triangle','Triangle','Oscillator','',2),
    ('Square','Square','Oscillator','',3)
    ]

class arpeggioSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_arpeggioSound"
    bl_label = "DAW Arpeggio"
    bl_width_default = 160

    message   : StringProperty()
    mode      : EnumProperty(name = "Mode", items = enum, update = AnimationNode.refresh)

    def draw(self,layout):
        layout.prop(self, "mode")
        if self.message is not '':
            layout.label(text=self.message,icon="NONE")

    def create(self):
        self.newInput("an_ObjectListSocket","Note Objects","objs")
        self.newInput("an_IntegerSocket","Octave Shift","oShift")
        self.newInput("an_IntegerSocket","Count","sizeB",minValue=3,maxValue=9)
        self.newInput("an_BooleanSocket","Climbing","revB")
        self.newInput("an_FloatSocket","Duration Factor","durF")
        self.newInput("an_FloatSocket","Pointer Location","pLoc")
        self.newInput("an_FloatSocket","Volume","volM",value=1,minValue=0.001,maxValue=5)
        self.newInput("an_FloatSocket","Start Offset (s)","startT",value=0,minValue=0)
        self.newInput("an_IntegerSocket","Samples","samples",value=44100,minValue=5000)
        self.newOutput("an_IntegerSocket","Samples","samplesO")
        self.newOutput("an_SoundSocket","Sound","sound")

    def execute(self,objs,oShift,sizeB,revB,durF,pLoc,volM,startT,samples):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        self.message = ""
        snd = None
        objsNote = [o for o in objs if o.location.x > pLoc-0.05 and o.location.x < pLoc+0.05]
        if len(objsNote) == 0 or durF == 0:
            return samples, None
        else:
            obj = objsNote[0]
        if obj:
            yLoc = int(round(obj.location.y * 10,0))
            noteName = getNote(yLoc,oShift*12)
            duration = round(obj.dimensions.x / durF,4)
            freqList = getChord(noteName,sizeB)
            if len(freqList) < sizeB:
                return samples, None
            if not revB:
                freqList = freqList[::-1]
            snd = None
            for i in range(0,sizeB):
                duration = duration + startT
                freq = freqList[i]
                sndI = osc(self.mode,freq,samples,duration,volM).fadeout(duration*0.95,duration*0.05)
                if i > 0:
                    snd = snd.join(sndI)
                else:
                    snd = sndI

        return samples, snd
