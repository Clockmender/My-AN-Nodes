import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . daw_functions import getNote, getIndex, getFreq, getChord, osc

enum = [('Sine','Sine','Oscillator','',0),
    ('Sawtooth','Sawtooth','Oscillator','',1),
    ('Triangle','Triangle','Oscillator','',2),
    ('Square','Square','Oscillator','',3)
    ]

class PlayScale(bpy.types.Node, AnimationNode):
    bl_idname = "an_PlayScale"
    bl_label = "DAW Play Basic Scales"
    bl_width_default = 180

    store    = {}
    revS     : BoolProperty(name="Reverse",default=False)
    message  : StringProperty()
    nextExec : IntProperty()
    mode     : EnumProperty(name = "Mode", items = enum, update = AnimationNode.refresh)

    def create(self):
        self.newInput("an_TextSocket","Note","noteName",value="c4")
        self.newInput("an_IntegerSocket","Octave Shift","octaveS",value=0,minValue=-4,maxValue=4)
        self.newInput("an_FloatSocket","Duration (s)","duration",value=1,minValue=0.1)
        self.newInput("an_IntegerSocket","Fade %","durP",value=0,minValue=0,maxValue=99)
        self.newInput("an_BooleanSocket","Fade In/Out","fade",value=False)
        self.newInput("an_FloatSocket","Volume","volume",value=1,minValue=0.001,maxValue=1)
        self.newInput("an_IntegerSocket","Samples","samples",value=44100,minValue=5000)
        self.newInput("an_BooleanSocket","Process","process",value=True)
        self.newInput("an_BooleanSocket","Reset Node","clearS",value=False)
        self.newOutput("an_GenericSocket","Stored Information","store")
        self.newOutput("an_IntegerSocket","Samples","samplesO")
        self.newOutput("an_TextSocket","Last Note Played","lastNote")

    def draw(self,layout):
        layout.prop(self, "mode")
        layout.prop(self,"revS")
        if self.message is not '':
            layout.label(text=self.message,icon="NONE")

    def execute(self,noteName,octaveS,duration,durP,fade,volume,samples,process,clearS):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        frameC = bpy.context.scene.frame_current
        fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
        dev = aud.Device()

        if frameC == bpy.context.scene.frame_start or clearS:
            self.store.clear()
            stopF = 1
            dev.stopAll()
            self.color = (0.9,0.7,0.8)
            self.nextExec = 0
            self.inputs[8].value = False
            return self.store, samples,''

        if '.' in self.name:
            name = 'Handle_'+self.name.split('.')[1]
        else:
            name = 'Handle_000'

        if name in self.store:
            stopF = self.store[name+'_stop']
        else:
            stopF = bpy.context.scene.frame_start
            self.nextExec = 0

        # Only process if last note finished
        # Reverses scale if self.revS set to True
        self.message = ''
        freq = 0
        if process and frameC > stopF and self.nextExec <= 7:
            indX = 50
            if self.revS:
                if self.nextExec == 0:
                    indX = getIndex(noteName)
                    if octaveS != 0:
                        indX = indX + (octaveS*12)
                elif self.nextExec == 1 or self.nextExec == 5:
                    indX = self.store[name+'_last']-1
                else:
                    indX = self.store[name+'_last']-2
            else:
                if self.nextExec == 0:
                    indX = getIndex(noteName)
                    if octaveS != 0:
                        indX = indX + (octaveS*12)
                elif self.nextExec == 3 or self.nextExec == 7:
                    indX = self.store[name+'_last']+1
                else:
                    indX = self.store[name+'_last']+2

            if indX in range(0,107):
                freq = getFreq(indX)
            else:
                self.message = 'Note/Octave Shift Invalid'
                return self.store, samples,''

            self.store[name+'_last']=indX
            freq = getFreq(indX)
            snd = osc(self.mode,freq,samples,duration,volume)
            self.nextExec = self.nextExec + 1
            if durP > 0:
                if fade:
                    startW = 0.0
                else:
                    startW = round(duration * ((100-durP)/100),4)
                lengthW = round(duration * (durP/100),4)
                if fade:
                    snd = snd.fadein(startW,lengthW)
                else:
                    snd = snd.fadeout(startW,lengthW)
            handle = dev.play(snd)
            handle.volume = volume
            self.store[name]=handle
            self.store[name+'_start']=int(frameC)
            self.store[name+'_stop']=int(frameC + (duration*fps))

        if name+'_last' in self.store:
            indLast = self.store[name+'_last']
            noteLast = getNote(indLast,0)
        else:
            noteLast = ''

        return self.store, samples, noteLast
