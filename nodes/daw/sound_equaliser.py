import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

enum = [('split','Split Output','Opperation Mode','',0),
    ('one','Only Combined','Operation Mode','',1)
    ]

class equalSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_equalSound"
    bl_label = "SOUND Equaliser"
    bl_width_default = 300

    vol1 : FloatProperty(default=0.5,min=0,max=1)
    vol2 : FloatProperty(default=0.5,min=0,max=1)
    vol3 : FloatProperty(default=0.5,min=0,max=1)
    vol4 : FloatProperty(default=0.5,min=0,max=1)
    vol5 : FloatProperty(default=0.5,min=0,max=1)
    vol6 : FloatProperty(default=0.5,min=0,max=1)
    vol7 : FloatProperty(default=0.5,min=0,max=1)
    vol8 : FloatProperty(default=0.5,min=0,max=1)

    spl1 : IntProperty()
    spl2 : IntProperty()
    spl3 : IntProperty()
    spl4 : IntProperty()
    spl5 : IntProperty()
    spl6 : IntProperty()
    spl7 : IntProperty()
    spl8 : IntProperty()

    mode:    EnumProperty(name = "Mode", items = enum, update = AnimationNode.refresh)

    def draw(self,layout):
        layout.prop(self, "mode")
        colm = layout.column()
        box = colm.box()
        row = box.row()
        row.label(text="Volume Controls",icon="FILE_SOUND")
        row = box.row()
        for i in range(1,9):
            col = row.column()
            col.label(text="V"+str(i),icon="NONE")
            col = row.column()
            self.invokeFunction(col, "volUp",data="vol"+str(i), icon = "TRIA_UP")
        col = row.column()

        row = box.row()
        for i in range(1,9):
            col = row.column()
            col.label(text="V"+str(i),icon="NONE")
            col = row.column()
            self.invokeFunction(col, "volDn",data="vol"+str(i), icon = "TRIA_DOWN")
        col = row.column()

        row = colm.row()
        row.label(text="Volumes",icon="OUTLINER_OB_SPEAKER")
        row = colm.row()
        for i in range(1,9):
            col = row.column()
            col.prop(self,"vol"+str(i))

        row = colm.row()
        row = colm.row()
        row.label(text="Frequency Splits (Think Quadratic Scales)",icon="PARTICLE_POINT")
        row = colm.row()
        for i in range(1,9):
            col = row.column()
            col.prop(self,"spl"+str(i))


    def volUp(self,data):
        setattr(self, data, getattr(self, data) + 0.05)

    def volDn(self,data):
        setattr(self, data, getattr(self, data) - 0.05)

    def create(self):
        self.newInput("an_FloatSocket","Q Factor","qfactor",value=0.5,minValue=0,maxValue=1)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Mixed Sound O","sound")
        if self.mode == "split":
            self.newOutput("an_SoundSocket","Band 1","sound1")
            self.newOutput("an_SoundSocket","Band 2","sound2")
            self.newOutput("an_SoundSocket","Band 3","sound3")
            self.newOutput("an_SoundSocket","Band 4","sound4")
            self.newOutput("an_SoundSocket","Band 5","sound5")
            self.newOutput("an_SoundSocket","Band 6","sound6")
            self.newOutput("an_SoundSocket","Band 7","sound7")
            self.newOutput("an_SoundSocket","Band 8","sound8")

    def execute(self,qfactor,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.65,1,1)
        self.width=500
        self.label = "SOUND Equaliser"
        if isinstance(snd, aud.Sound):
            # Filter the sounds
            snd1 = snd.lowpass(self.spl1,qfactor)
            snd1 = snd1.volume(self.vol1)

            snd2 = snd.lowpass(self.spl2,qfactor)
            snd2 = snd2.highpass(self.spl1+1,qfactor)
            snd2 = snd2.volume(self.vol2)

            snd3 = snd.lowpass(self.spl3,qfactor)
            snd3 = snd3.highpass(self.spl2+1,qfactor)
            snd3 = snd3.volume(self.vol3)

            snd4 = snd.lowpass(self.spl4,qfactor)
            snd4 = snd4.highpass(self.spl3+1,qfactor)
            snd4 = snd4.volume(self.vol4)

            snd5 = snd.lowpass(self.spl5,qfactor)
            snd5 = snd5.highpass(self.spl4+1,qfactor)
            snd5 = snd5.volume(self.vol5)

            snd6 = snd.lowpass(self.spl6,qfactor)
            snd6 = snd6.highpass(self.spl5+1,qfactor)
            snd6 = snd6.volume(self.vol6)

            snd7 = snd.lowpass(self.spl7,qfactor)
            snd7 = snd7.highpass(self.spl6+1,qfactor)
            snd7 = snd7.volume(self.vol7)

            snd8 = snd.lowpass(self.spl8,qfactor)
            snd8 = snd8.highpass(self.spl7+1,qfactor)
            snd8 = snd8.volume(self.vol8)
            # mix the sounds together
            snd = snd1.mix(snd2)
            snd = snd.mix(snd3)
            snd = snd.mix(snd4)
            snd = snd.mix(snd5)
            snd = snd.mix(snd6)
            snd = snd.mix(snd7)
            snd = snd.mix(snd8)
            if self.mode == "split":
                return snd, snd1, snd2, snd3, snd4, snd5, snd6, snd7, snd8
            else:
                return snd
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Eq BYPASS (No Sound)"
            if self.mode == "split":
                return snd, None, None, None, None, None, None, None, None
            else:
                return snd
