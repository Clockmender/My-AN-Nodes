import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class an_iirFirFilter(bpy.types.Node, AnimationNode):
    bl_idname = "an_iirFirFilter"
    bl_label = "SOUND IIR/FIR Filter"
    bl_width_default = 220

    typeB : BoolProperty(name="IIR/FIR",default=True)
    a : FloatProperty(name='B1')
    b : FloatProperty(name='B2')
    c : FloatProperty(name='B3')
    d : FloatProperty(name='B4')
    e : FloatProperty(name='B5')
    f : FloatProperty(name='B6')

    g : FloatProperty(name='A1')
    h : FloatProperty(name='A2')
    i : FloatProperty(name='A3')
    j : FloatProperty(name='A4')
    k : FloatProperty(name='A5')
    l : FloatProperty(name='A6')

    def draw(self,layout):
        colm = layout.column()
        layout.prop(self,"typeB")
        row = colm.row()
        col = row.column()
        col.prop(self,"a")
        col = row.column()
        col.prop(self,"b")
        row = colm.row()
        col = row.column()
        col.prop(self,"c")
        col = row.column()
        col.prop(self,"d")
        row = colm.row()
        col = row.column()
        col.prop(self,"e")
        col = row.column()
        col.prop(self,"f")
        row = colm.row()
        row.label(text="FIR Sequence")
        row = colm.row()
        col = row.column()
        col.prop(self,"g")
        col = row.column()
        col.prop(self,"h")
        row = colm.row()
        col = row.column()
        col.prop(self,"i")
        col = row.column()
        col.prop(self,"j")
        row = colm.row()
        col = row.column()
        col.prop(self,"k")
        col = row.column()
        col.prop(self,"l")
        row = colm.row()
        row.label(text="IIR Sequence")


    def create(self):
        self.newInput("an_IntegerSocket","Number of Filter Values","filterN",minValue=1,maxValue=6)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,filterN,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if any([self.a!=0,self.b!=0,self.c!=0,self.d!=0,self.e!=0,self.f!=0]):
            self.color = (0.65,1,1)
            self.label = "SOUND IIR/FIR Filter"
            if isinstance(snd, aud.Sound):
                filterSi = [self.a,self.b,self.c,self.d,self.e,self.f]
                filterSf = [self.g,self.h,self.i,self.j,self.k,self.l]
                while len(filterSi) > filterN:
                    filterSi.pop(-1)
                while len(filterSf) > filterN:
                    filterSf.pop(-1)
                tupleSi = tuple(filterSi)
                tupleSf = tuple(filterSf)
                if self.typeB:
                    snd = snd.filter(tupleSi,tupleSf)
                else:
                    snd = snd.filter(tupleSi)
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND IIR BYPASS (No Sound)"
                return None
        else:
            self.label = "SOUND IIR BYPASS (0 Inputs)"
            self.color = (0.75,1,0.75)
        return snd
