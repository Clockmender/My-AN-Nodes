import bpy
import os
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
import numpy as np
from pypianoroll import Track, Multitrack
from matplotlib import pyplot as plt
from . daw_functions import getIndex, getFreq, getChordInd

store = {}

class arrayDAW(bpy.types.Node, AnimationNode):
    bl_idname = "an_arrayDAW"
    bl_label = "ARRAY Manager"
    bl_width_default = 300

    noteName : StringProperty(name="Note Name",default="c4")
    startPos : IntProperty(name="Start Offset (ND)",min=0)
    duration : IntProperty(name="Duration (ND)",min=1)
    noteVel  : IntProperty(name="Velocity",min=0,max=127,default=100)
    chordNum : IntProperty(name="Chord #",default=3,min=3,max=5)
    message  : StringProperty()
    fileName : StringProperty()

    def draw(self,layout):
        colM = layout.column()
        row = colM.row()
        col = row.column()
        col.prop(self,"noteName")
        col = row.column()
        col.prop(self,"startPos")
        col = row.column()
        col.prop(self,"duration")
        col = row.column()
        col.prop(self,"noteVel")
        col = row.column()
        col.prop(self,"chordNum")
        row = colM.row()
        col = row.column()
        col.scale_y = 1.2
        self.invokeFunction(col, "addNote", text="Add Note", icon = "INFO")
        col = row.column()
        col.scale_y = 1.2
        self.invokeFunction(col, "addChord", text="Add Chord", icon = "INFO")
        col = row.column()
        col.scale_y = 1.2
        self.invokeFunction(col, "clearAll", text="Reset Node", icon = "INFO")
        row = colM.row()
        col = row.column()
        col.scale_y = 1.2
        self.invokeSelector(col, "PATH", "saveArray", text="Save Array", icon = "INFO")
        col = row.column()
        col.scale_y = 1.2
        self.invokeSelector(col, "PATH", "loadArray", text="Load Array", icon = "INFO")
        if self.message is not '':
            layout.label(text="ARRAY Manager: "+self.message,icon='NONE')

    def clearAll(self):
        store = {}
        self.fileName = ""
        self.label = "ARRAY Manager Empty"

    def addNote(self):
        indX = getIndex(self.noteName) + 12
        if '.' in self.name:
            name = 'Pianoroll_'+self.name.split('.')[1]
        else:
            name = 'Pianoroll_000'
        if name in store:
            self.message = "Added "+str(indX)+","+str(self.startPos)+","+str(self.duration)+","+str(self.noteVel)
            store[name][self.startPos:(self.startPos+self.duration), indX] = self.noteVel
            np.save(self.fileName,store[name])
        else:
            self.message = "No Pianoroll Yet"

    def addChord(self):
        freqList = getChordInd(self.noteName,self.chordNum)
        if '.' in self.name:
            name = 'Pianoroll_'+self.name.split('.')[1]
        else:
            name = 'Pianoroll_000'
        if name in store:
            self.message = "Added 5 Note Chord for "+self.noteName
            if len(freqList) > 0:
                for indX in freqList:
                    store[name][self.startPos:(self.startPos+self.duration), indX] = self.noteVel
                    self.message = self.message+","+str(indX)
                np.save(self.fileName,store[name])
            else:
                self.message = "No Frequencies Returned"
        else:
            self.message = "No Pianoroll Yet"

    def saveArray(self,path):
        if '.' in self.name:
            name = 'Pianoroll_'+self.name.split('.')[1]
        else:
            name = 'Pianoroll_000'
        if name in store:
            self.message = "Array Stored"
            np.save(str(path),store[name])
            self.fileName = str(path)
        else:
            self.message = "No Pianoroll Yet"

    def loadArray(self,path):
        self.message = "Array Loaded"
        if '.' in self.name:
            name = 'Pianoroll_'+self.name.split('.')[1]
        else:
            name = 'Pianoroll_000'
        store[name] = np.load(str(path))
        self.fileName = str(path)

    def create(self):
        self.newInput("an_FloatSocket","BPM","bpm")
        self.newInput("an_IntegerSocket","Bars #","barsN")
        self.newInput("an_IntegerSocket","Note Denominator","noteL")
        self.newInput("an_FloatSocket","FPS","fps")
        self.newInput("an_TextSocket","Time Signature","tSig")
        self.newInput("an_TextSocket","File Directory","fileName")
        self.newInput("an_IntegerSocket","Trigger Frame","tFrame",value=0,min=0)
        self.newInput("an_TextSocket","track Name","tName")
        self.newOutput("an_GenericSocket","Output Track","track")
        self.newOutput("an_FloatListSocket","Sound Data","noteSO")

    def execute(self,bpm,barsN,noteL,fps,tSig,fileName,tFrame,tName):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        self.width = 450
        self.message = ""
        frameC = bpy.context.scene.frame_current
        if frameC != tFrame:
            return None,[]
        else:
            dev = aud.Device()
            stop = dev.stopAll()
        if '.' in self.name:
            name = 'Pianoroll_'+self.name.split('.')[1]
        else:
            name = 'Pianoroll_000'
        if self.fileName is not "":
            store[name] = np.load(self.fileName)
            self.label = "ARRAY Manager "+os.path.basename(self.fileName)
        if tSig == "" or noteL == 0 or fps == 0 or barsN == 0:
            return None, []
        if ":" in tSig:
                sigFac = int(tSig.split(":")[0]) / int(tSig.split(":")[1])
        else:
            sigFac = 1
        beatRes = noteL / sigFac
        lenA    = int(barsN * noteL * sigFac)
        time    = (60 / bpm) / noteL
        if name not in store:
            pianoRoll = np.zeros((lenA, 128))
            store[name] = pianoRoll
        else:
            pianoRoll = store[name]
        indX = getIndex(self.noteName) + 12
        noteS = []
        notesList = []
        track = None
        if name in store:
            noteS = []
            for i in range(0,127):
                pianorolls = store[name][:, i]
                cn = 0
                for r in pianorolls:
                    if r > 0 and i not in noteS:
                        noteS.append(i)
                        break
                    cn = cn + r

            for n in noteS:
                pianorolls = store[name][:, n]
                r=0
                vol = 0
                rec = True
                for i in pianorolls:
                    if i > 0 and rec:
                        s = r
                        notesList.append(n)
                        notesList.append(r*time)
                        vol = round(i/128,4)
                        notesList.append(vol)
                        rec = False
                    if not rec and i == 0:
                        notesList.append((r-s)*time)
                        rec = True
                    r = r+1
            if tName == "":
                tName = "Track-1"
            track = Track(pianoroll=store[name], program=0, is_drum=False, name=tName)
            if frameC == tFrame:
                fig,ax = track.plot(xtick='beat',beat_resolution=16,ytick='octave')
                fig.set_size_inches(32,3.5)
                plt.tight_layout()
                plt.savefig(fileName+tName+".png")
        else:
            self.message = "No Pianoroll Yet"
            return None, []
        return track, notesList
