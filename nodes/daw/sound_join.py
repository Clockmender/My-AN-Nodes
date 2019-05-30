import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

enum = [('2','2','Number of Channels','',0),
    ('3','3','Number of Channels','',1),
    ('4','4','Number of Channels','',2),
    ('5','5','Number of Channels','',3)
    ]

class joinSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_joinSound"
    bl_label = "SOUND Join"
    bl_width_default = 150

    mode    : EnumProperty(name = "Channels", items = enum, update = AnimationNode.refresh)

    def draw(self,layout):
        layout.prop(self,"mode")

    def create(self):
        self.newInput("an_SoundSocket","Sound 1","snd1")
        self.newInput("an_SoundSocket","Sound 2","snd2")
        if int(self.mode) > 2:
            self.newInput("an_SoundSocket","Sound 3","snd3")
            if int(self.mode) > 3:
                self.newInput("an_SoundSocket","Sound 4","snd4")
                if int(self.mode) > 4:
                    self.newInput("an_SoundSocket","Sound 5","snd5")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def getExecutionFunctionName(self):
        if self.mode == "2":
            return "execute2"
        elif self.mode == "3":
            return "execute3"
        elif self.mode == "4":
            return "execute4"
        elif self.mode == "5":
            return "execute5"

    def execute2(self,snd1,snd2):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.65,1,1)
        if isinstance(snd1, aud.Sound) and 'aud.Sound' in str(snd2):
            snd = snd1.join(snd2)
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Jo BYPASS (No Sound(s))"
            return None
        return snd

    def execute3(self,snd1,snd2,snd3):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.65,1,1)
        snd = None
        if isinstance(snd1, aud.Sound):
            snd = snd1
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Jo BYPASS (No Sound(s))"
            return None
        if isinstance(snd2, aud.Sound) and snd is not None:
            snd = snd.join(snd2)
        if isinstance(snd3, aud.Sound) and snd is not None:
            snd = snd.join(snd3)
        return snd

    def execute4(self,snd1,snd2,snd3,snd4):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.65,1,1)
        snd = None
        if isinstance(snd1, aud.Sound):
            snd = snd1
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Jo BYPASS (No Sound(s))"
            return None
        if isinstance(snd2, aud.Sound) and snd is not None:
            snd = snd.join(snd2)
        if isinstance(snd3, aud.Sound) and snd is not None:
            snd = snd.join(snd3)
        if isinstance(snd4, aud.Sound) and snd is not None:
            snd = snd.join(snd4)
        return snd

    def execute5(self,snd1,snd2,snd3,snd4,snd5):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.65,1,1)
        snd = None
        if isinstance(snd1, aud.Sound):
            snd = snd1
        else:
            self.color = (0.75,1,0.75)
            self.label = "SOUND Jo BYPASS (No Sound(s))"
            return None
        if isinstance(snd2, aud.Sound) and snd is not None:
            snd = snd.join(snd2)
        if isinstance(snd3, aud.Sound) and snd is not None:
            snd = snd.join(snd3)
        if isinstance(snd4, aud.Sound) and snd is not None:
            snd = snd.join(snd4)
        if isinstance(snd5, aud.Sound) and snd is not None:
            snd = snd.join(snd5)
        return snd
