import bpy
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

sysNoteL = {}

def getSysData(self):
    return sysNoteL

class setupDAW(bpy.types.Node, AnimationNode):
    bl_idname = "an_setupDAW"
    bl_label = "UTILS Setup"
    bl_width_default = 180

    bpm     : FloatProperty(name="BPM",min=12,default=120,max=300)
    tsNum   : IntProperty(name="Time Sig Numerator",default=4,min=1,max=16)
    tsDen   : IntProperty(name="Time Sig Denominator",default=4,min=1,max=16)
    fps     : FloatProperty()
    noteL   : IntProperty(name="Note Denom.",min=1,default=16,max=64)
    barsN   : IntProperty(name="Bars #",min=9,default=10)
    message : StringProperty()
    samples : IntProperty(name="Samples",default=44100,min=6000)

    def draw(self,layout):
        layout.prop(self,"bpm")
        layout.prop(self,"noteL")
        layout.prop(self,"tsNum")
        layout.prop(self,"tsDen")
        layout.prop(self,"barsN")
        layout.prop(self,"samples")
        col = layout.column()
        col.scale_y = 1.2
        if self.message is not '':
            layout.label(text=self.message,icon='ERROR')
        self.invokeFunction(col, "setup", text="Setup", icon = "INFO")

    def setup(self):
        if '.' in self.name:
            return
        if self.bpm >= 12 and self.noteL in [1,2,4,8,16,32,64]:
            self.fps = round((self.bpm/60 * self.noteL)*100,2)
            bpy.context.scene.render.fps = self.fps
            bpy.context.scene.render.fps_base = 100
            self.message = str(round(self.fps,2))
        else:
            self.message = "Note Denom. must be 1,2,4,8,16,32 or 64"

    def create(self):
        self.newInput("an_ObjectSocket","Pointer","barM")
        self.newInput("an_ObjectSocket","Bar Marker","pointer")
        self.newOutput("an_FloatSocket","BPM","bpmO")
        self.newOutput("an_IntegerSocket","Bars #","barsN")
        self.newOutput("an_IntegerSocket","Note Denominator","noteLO")
        self.newOutput("an_FloatSocket","FPS","fpsO")
        self.newOutput("an_FloatSocket","Duration Factor","dFac")
        self.newOutput("an_FloatSocket","Short Note Time","noteT")
        self.newOutput("an_FloatSocket","Pointer Loc","pLoc")
        self.newOutput("an_TextSocket","Time Signature:","tSig")
        self.newOutput("an_IntegerSocket","Samples","samplesO")

    def execute(self,pointer,barM):
        self.use_custom_color = True
        self.useNetworkColor = False
        if '.' in self.name:
            self.message = "Duplicate Setup Node"
            self.color = (1,0.3,0.3)
            return None,None,None,None,None,None,None,None
        else:
            self.color = (0.73,0.83,1)
        sysNoteL['NoteL'] = self.noteL
        sysNoteL['BPM'] = self.bpm
        sysNoteL['TS_Num'] = self.tsNum
        sysNoteL['TS_Den'] = self.tsDen
        sysNoteL['Bars'] = self.barsN
        sysNoteL['Time_NL'] = round((1 / (self.bpm / 60)) / self.noteL,5)
        sysNoteL['Channels'] = 2
        self.message = ""
        bpy.context.scene.frame_end = self.noteL * (self.barsN+1)
        frameC = bpy.context.scene.frame_current
        if pointer is not None:
            pointer.location.x = (frameC-1)* 0.1
            pLoc = pointer.location.x
        else:
            pLoc = 0
        if self.tsNum == 0 or self.tsDen == 0:
            self.message = "Set Time Signature"
            self.color = (0.75,1,0.75)
            return self.bpm,self.barsN,self.noteL,0,0,0,0,self.samples

        if barM is not None:
            spcB = (self.tsNum / self.tsDen) * (self.noteL / 10)
            if bpy.data.objects.get("Piano-Roll") is not None:
                bpy.data.objects['Piano-Roll'].scale.x = (self.barsN / 10 * (self.tsNum/self.tsDen))
            if bpy.data.objects.get("Drum-Roll") is not None:
                bpy.data.objects['Drum-Roll'].scale.x = (self.barsN / 10 * (self.tsNum/self.tsDen))
            if bpy.data.objects.get("Automation-Roll") is not None:
                bpy.data.objects['Automation-Roll'].scale.x = (self.barsN / 10 * (self.tsNum/self.tsDen))
            if bpy.data.objects.get("SE-Roll") is not None:
                bpy.data.objects['SE-Roll'].scale.x = (self.barsN / 10 * (self.tsNum/self.tsDen))
            if bpy.data.objects.get("Counter-1") is not None:
                bpy.data.objects['Counter-1'].data.body = 'Bar '+str(int((frameC-1)/self.noteL)+1)
            if barM.modifiers["Array"].constant_offset_displace[0] != spcB:
                barM.modifiers["Array"].constant_offset_displace[0] = spcB
            if barM.modifiers["Array"].count != self.barsN+1:
                barM.modifiers["Array"].count = self.barsN+1

        fpsO = round(bpy.context.scene.render.fps/100,2)
        dFac = self.noteL * self.bpm /600
        noteT = round((60 / self.bpm) / self.noteL,4)
        tSig = str(self.tsNum)+":"+str(self.tsDen)
        return self.bpm, self.barsN,self.noteL, fpsO,dFac,noteT,pLoc,tSig,self.samples
