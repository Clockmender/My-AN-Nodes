import bpy
import aud
import numpy as np
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . daw_functions import getIndex, getFreq, getChord, osc

enum = [('Sine','Sine','Oscillator','',0),
    ('Sawtooth','Sawtooth','Oscillator','',1),
    ('Triangle','Triangle','Oscillator','',2),
    ('Square','Square','Oscillator','',3),
    ('Silence','Silence','Oscillator','',4),
    ('White','White Noise','Oscillator','',5)
    ]

class GenerateSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_GenerateSound"
    bl_label = "SOUND Generator"
    bl_width_default = 150

    message   : StringProperty()
    mode      : EnumProperty(name = "OSC", items = enum, update = AnimationNode.refresh)

    def draw(self,layout):
        layout.prop(self, "mode")
        if self.message is not '':
            layout.label(text=self.message,icon="NONE")

    def create(self):
        if self.mode == "White":
            self.newInput("an_FloatSocket","Min Frequency","minFreq",value=20)
            self.newInput("an_FloatSocket","Max Frequency","maxFreq",value=20000)
        else:
            self.newInput("an_FloatListSocket","Sound Data","listI")
            self.newInput("an_TextSocket","Note","noteName")
            self.newInput("an_IntegerSocket","Octave Shift","octaveS",value=0,minValue=-4,maxValue=4)
            self.newInput("an_FloatSocket","Frequency","frequency",value=440,minValue=0)
        self.newInput("an_FloatSocket","Volume","volume",value=1,minValue=0.001,maxValue=5)
        self.newInput("an_FloatSocket","Duration (s)","duration",value=1,minValue=0)
        self.newInput("an_IntegerSocket","Samples","samples",value=44100,minValue=5000)
        if self.mode != "White":
            self.newOutput("an_FloatSocket","Frequency","freqO")
        self.newOutput("an_FloatSocket","Duration","duration")
        self.newOutput("an_IntegerSocket","Samples","samplesO")
        self.newOutput("an_SoundSocket","Sound","sound")

    def getExecutionFunctionName(self):
        if self.mode == "White":
            return "executeW"
        else:
            return "executeO"

    def executeW(self,minFreq,maxFreq,volume,duration,samples):
        # White Noise
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.95,0.6)
        self.message = ""
        if duration > 0 and minFreq > 0 and maxFreq > minFreq:
            def band_limited_noise(min_freq, max_freq, samples, samplerate=1):
                freqs = np.abs(np.fft.fftfreq(samples, 1/samplerate))
                f = np.zeros(samples)
                idx = np.where(np.logical_and(freqs>=min_freq, freqs<=max_freq))[0]
                f[idx] = 1
                return fftnoise(f)

            def fftnoise(f):
                f = np.array(f, dtype='complex')
                Np = (len(f) - 1) // 2
                phases = np.random.rand(Np) * 2 * np.pi
                phases = np.cos(phases) + 1j * np.sin(phases)
                f[1:Np+1] *= phases
                f[-1:-1-Np:-1] = np.conj(f[1:Np+1])
                return np.fft.ifft(f).real

            array = band_limited_noise(minFreq,maxFreq,samples,samples)
            array = np.float32(array)
            sndO = aud.Sound.buffer(array,samples)
            loop = int(duration)
            if loop > 0:
                sndO = sndO.loop(loop)
            sndO = sndO.limit(0,duration).rechannel(2).volume(10*volume)
            return duration, samples, sndO
        else:
            self.color = (0.75,1,0.75)
            return duration, samples, None

    def executeO(self,listI,noteName,octaveS,frequency,volume,duration,samples):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.95,0.6)
        self.message = ""
        freq = 0
        limit = 0
        if len(listI) > 0:
            self.inputs[5].value = 0
            # Process input list from Array format [note,start,vol,duration] repeated in blocks of 4
            rangeN = int(len(listI) / 4)
            dev = aud.Device()
            for i in range(0,rangeN):
                n = i * 4
                noteIdx = int(listI[n])
                freq    = getFreq(noteIdx)
                startT  = listI[n+1]
                volM    = listI[n+2]
                durT    = listI[n+3]
                if i == 0:
                    sndM = osc(self.mode,freq,samples,durT,volM).fadein(0,durT*0.05).fadeout(durT*0.95,durT*0.05)
                else:
                    sndM = sndM.mix(osc(self.mode,freq,samples,durT,volM).fadein(0,durT*0.05).fadeout(durT*0.95,durT*0.05))
            duration = sndM.length / sndM.specs[0]
            return 0, duration, samples, sndM

        elif duration > 0:
            if noteName is not '':
                indX = getIndex(noteName)
                if octaveS != 0:
                    indX = indX + (octaveS*12)
                if indX in range(0,131):
                    freq = getFreq(indX)
                else:
                    self.message = 'Note/Octave Shift Invalid'
                    return freq,samples,duration,None
                snd = osc(self.mode,freq,samples,duration,volume)
            elif frequency >= 16.35160:
                freq = frequency
                snd = osc(self.mode,freq,samples,duration,volume)
            else:
                return freq, duration, samples, None
            snd = snd.fadeout((duration*0.98),(duration*0.02))
            return freq, duration, samples, snd
        else:
            self.color = (0.75,1,0.75)
            return freq, duration, samples, None
