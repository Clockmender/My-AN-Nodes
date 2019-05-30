import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

enum = [('2','2','Number of Channels','',0),
    ('6','6','Number of Channels','',1),
    ('8','8','Number of Channels','',2),
    ('12','12','Number of Channels','',3)
    ]

class mixSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_mixSound"
    bl_label = "SOUND Multi-Channel Mixer"
    bl_width_default = 180

    mode    : EnumProperty(name = "Channels", items = enum, update = AnimationNode.refresh)

    def draw(self,layout):
        layout.prop(self,"mode")

    def create(self):
        self.newInput("an_SoundSocket","Sound 1","snd1")
        self.newInput("an_FloatSocket","Vol 1","vol1",value=1,minValue=0,maxValue=5)
        self.newInput("an_SoundSocket","Sound 2","snd2")
        self.newInput("an_FloatSocket","Vol 2","vol2",value=1,minValue=0,maxValue=5)
        if int(self.mode) > 2:
            self.newInput("an_SoundSocket","Sound 3","snd3")
            self.newInput("an_FloatSocket","Vol 3","vol3",value=1,minValue=0,maxValue=5)
            self.newInput("an_SoundSocket","Sound 4","snd4")
            self.newInput("an_FloatSocket","Vol 4","vol4",value=1,minValue=0,maxValue=5)
            self.newInput("an_SoundSocket","Sound 5","snd5")
            self.newInput("an_FloatSocket","Vol 5","vol5",value=1,minValue=0,maxValue=5)
            self.newInput("an_SoundSocket","Sound 6","snd6")
            self.newInput("an_FloatSocket","Vol 6","vol6",value=1,minValue=0,maxValue=5)
            if int(self.mode) > 6:
                self.newInput("an_SoundSocket","Sound 7","snd7")
                self.newInput("an_FloatSocket","Vol 7","vol7",value=1,minValue=0,maxValue=5)
                self.newInput("an_SoundSocket","Sound 8","snd8")
                self.newInput("an_FloatSocket","Vol 8","vol8",value=1,minValue=0,maxValue=5)
                if int(self.mode) > 8:
                    self.newInput("an_SoundSocket","Sound 9","snd9")
                    self.newInput("an_FloatSocket","Vol 9","vol9",value=1,minValue=0,maxValue=5)
                    self.newInput("an_SoundSocket","Sound 10","snd10")
                    self.newInput("an_FloatSocket","Vol 10","vol10",value=1,minValue=0,maxValue=5)
                    self.newInput("an_SoundSocket","Sound 11","snd11")
                    self.newInput("an_FloatSocket","Vol 11","vol11",value=1,minValue=0,maxValue=5)
                    self.newInput("an_SoundSocket","Sound 12","snd12")
                    self.newInput("an_FloatSocket","Vol 12","vol12",value=1,minValue=0,maxValue=5)
        self.newInput("an_FloatSocket","Master Volume","volM",value=1,minValue=0,maxValue=5)
        self.newOutput("an_SoundSocket","Sound O","sound")

    def getExecutionFunctionName(self):
        if self.mode == "2":
            return "execute2"
        elif self.mode == "6":
            return "execute6"
        elif self.mode == "8":
            return "execute8"
        elif self.mode == "12":
            return "execute12"

    def execute2(self,snd1,vol1,snd2,vol2,volM):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.95,0.6)
        self.label = "SOUND "+str(self.mode)+" Channel Mixer"
        snd = None
        if isinstance(snd1, aud.Sound):
            snd = snd1.volume(vol1)
        if isinstance(snd2, aud.Sound):
            snd2 = snd2.volume(vol2)
            if snd == None:
                snd = snd2
            else:
                snd = snd.mix(snd2)
        if snd is not None:
            snd = snd.volume(volM)
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Mi BYPASS (No Sound)"
            return None
        return snd

    def execute6(self,snd1,vol1,snd2,vol2,snd3,vol3,snd4,vol4,snd5,vol5,snd6,vol6,volM):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.95,0.6)
        self.label = "SOUND "+str(self.mode)+" Channel Mixer"
        snd = None
        if isinstance(snd1, aud.Sound):
            snd = snd1.volume(vol1)
        if isinstance(snd2, aud.Sound):
            snd2 = snd2.volume(vol2)
            if snd == None:
                snd = snd2
            else:
                snd = snd.mix(snd2)
        if isinstance(snd3, aud.Sound):
            snd3 = snd3.volume(vol3)
            if snd == None:
                snd = snd3
            else:
                snd = snd.mix(snd3)
        if isinstance(snd4, aud.Sound):
            snd4 = snd4.volume(vol4)
            if snd == None:
                snd = snd4
            else:
                snd = snd.mix(snd4)
        if isinstance(snd5, aud.Sound):
            snd5 = snd5.volume(vol5)
            if snd == None:
                snd = snd5
            else:
                snd = snd.mix(snd5)
        if isinstance(snd6, aud.Sound):
            snd6 = snd6.volume(vol6)
            if snd == None:
                snd = snd6
            else:
                snd = snd.mix(snd6)
        if snd is not None:
            snd = snd.volume(volM)
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Mi BYPASS (No Sound)"
            return None
        return snd

    def execute8(self,snd1,vol1,snd2,vol2,snd3,vol3,snd4,vol4,snd5,vol5,snd6,vol6,snd7,vol7,snd8,vol8,volM):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.95,0.6)
        self.label = "SOUND "+str(self.mode)+" Channel Mixer"
        snd = None
        if isinstance(snd1, aud.Sound):
            snd = snd1.volume(vol1)
        if isinstance(snd2, aud.Sound):
            snd2 = snd2.volume(vol2)
            if snd == None:
                snd = snd2
            else:
                snd = snd.mix(snd2)
        if isinstance(snd3, aud.Sound):
            snd3 = snd3.volume(vol3)
            if snd == None:
                snd = snd3
            else:
                snd = snd.mix(snd3)
        if isinstance(snd4, aud.Sound):
            snd4 = snd4.volume(vol4)
            if snd == None:
                snd = snd4
            else:
                snd = snd.mix(snd4)
        if isinstance(snd5, aud.Sound):
            snd5 = snd5.volume(vol5)
            if snd == None:
                snd = snd5
            else:
                snd = snd.mix(snd5)
        if isinstance(snd6, aud.Sound):
            snd6 = snd6.volume(vol6)
            if snd == None:
                snd = snd6
            else:
                snd = snd.mix(snd6)
        if isinstance(snd7, aud.Sound):
            snd7 = snd7.volume(vol7)
            if snd == None:
                snd = snd7
            else:
                snd = snd.mix(snd7)
        if isinstance(snd8, aud.Sound):
            snd8 = snd8.volume(vol8)
            if snd == None:
                snd = snd8
            else:
                snd = snd.mix(snd8)
        if snd is not None:
            snd = snd.volume(volM)
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Mi BYPASS (No Sound)"
            return None
        return snd

    def execute12(self,snd1,vol1,snd2,vol2,snd3,vol3,snd4,vol4,snd5,vol5,snd6,vol6,snd7,vol7,snd8,vol8,snd9,vol9,snd10,vol10,snd11,vol11,snd12,vol12,volM):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.95,0.6)
        self.label = "SOUND "+str(self.mode)+" Channel Mixer"
        snd = None
        if isinstance(snd1, aud.Sound):
            snd = snd1.volume(vol1)
        if isinstance(snd2, aud.Sound):
            snd2 = snd2.volume(vol2)
            if snd == None:
                snd = snd2
            else:
                snd = snd.mix(snd2)
        if isinstance(snd3, aud.Sound):
            snd3 = snd3.volume(vol3)
            if snd == None:
                snd = snd3
            else:
                snd = snd.mix(snd3)
        if isinstance(snd4, aud.Sound):
            snd4 = snd4.volume(vol4)
            if snd == None:
                snd = snd4
            else:
                snd = snd.mix(snd4)
        if isinstance(snd5, aud.Sound):
            snd5 = snd5.volume(vol5)
            if snd == None:
                snd = snd5
            else:
                snd = snd.mix(snd5)
        if isinstance(snd6, aud.Sound):
            snd6 = snd6.volume(vol6)
            if snd == None:
                snd = snd6
            else:
                snd = snd.mix(snd6)
        if isinstance(snd7, aud.Sound):
            snd7 = snd7.volume(vol7)
            if snd == None:
                snd = snd7
            else:
                snd = snd.mix(snd7)
        if isinstance(snd8, aud.Sound):
            snd8 = snd8.volume(vol8)
            if snd == None:
                snd = snd8
            else:
                snd = snd.mix(snd8)
        if isinstance(snd9, aud.Sound):
            snd9 = snd9.volume(vol9)
            if snd == None:
                snd = snd9
            else:
                snd = snd.mix(snd9)
        if isinstance(snd10, aud.Sound):
            snd10 = snd10.volume(vol10)
            if snd == None:
                snd = snd10
            else:
                snd = snd.mix(snd10)
        if isinstance(snd11, aud.Sound):
            snd11= snd11.volume(vol11)
            if snd == None:
                snd = snd11
            else:
                snd = snd.mix(snd11)
        if isinstance(snd12, aud.Sound):
            snd12= snd12.volume(vol12)
            if snd == None:
                snd = snd12
            else:
                snd = snd.mix(snd12)
        if snd is not None:
            snd = snd.volume(volM)
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Mi BYPASS (No Sound)"
            return None
        return snd
