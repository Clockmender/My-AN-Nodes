import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
from . daw_functions import getNote, getIndex, getFreq, getChord
import random

enum = [('1','1','Number of Channels','',0),
    ('4','4','Number of Channels','',1),
    ('8','8','Number of Channels','',2),
    ('10','10','Number of Channels','',3),
    ('12','12','Number of Channels','',4),
    ]

class PlayedFiles(bpy.types.Node, AnimationNode):
    bl_idname = "an_PlayedFiles"
    bl_label = "DAW File Track Control"
    bl_width_default = 200

    mess   : StringProperty()
    reQuan : BoolProperty(name="Quantise Perfect",default=False)
    reSize : BoolProperty(name="Random De-Quantise",default=False)
    qLow   : FloatProperty(name="Q Low",min=0.96,max=0.999)
    qHigh  : FloatProperty(name="Q High",min=1.001,max=1.04)
    chanN  : EnumProperty(name="Channels", items = enum, update = AnimationNode.refresh)

    def draw(self,layout):
        layout.prop(self,"chanN")
        layout.prop(self,"reQuan")
        layout.prop(self,"reSize")
        layout.prop(self,"qLow")
        layout.prop(self,"qHigh")
        if self.mess is not '':
            layout.label(text=self.mess, icon='INFO')

    def create(self):
        self.newInput("an_ObjectListSocket","Note Objects","objs")
        self.newInput("an_FloatSocket","Duration Factor","durF")
        self.newInput("an_FloatSocket","Pointer Location","pLoc")
        self.newInput("an_IntegerSocket","Samples","samples")
        self.newOutput("an_FloatSocket","Duration 1","dur1")
        if int(self.chanN) > 1:
            self.newOutput("an_FloatSocket","Duration 2","dur2")
            self.newOutput("an_FloatSocket","Duration 3","dur3")
            self.newOutput("an_FloatSocket","Duration 4","dur4")
            if int(self.chanN) > 4:
                self.newOutput("an_FloatSocket","Duration 5","dur5")
                self.newOutput("an_FloatSocket","Duration 6","dur6")
                self.newOutput("an_FloatSocket","Duration 7","dur7")
                self.newOutput("an_FloatSocket","Duration 8","dur8")
                if int(self.chanN) > 8:
                    self.newOutput("an_FloatSocket","Duration 9","dur9")
                    self.newOutput("an_FloatSocket","Duration 10","dur10")
                    if int(self.chanN) > 10:
                        self.newOutput("an_FloatSocket","Duration 11","dur11")
                        self.newOutput("an_FloatSocket","Duration 12","dur12")
        self.newOutput("an_IntegerSocket","Samples","samplesO")

    def execute(self,objs,durF,pLoc,samples):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        self.label = "DAW File Track Control"
        retList = []
        while len(retList) < int(self.chanN):
            retList.append(0)
        if len(objs) > 0 and durF > 0:
            objsNote = [o for o in objs if o.location.x > pLoc-0.05 and o.location.x < pLoc+0.05]
            for i in range(0,len(objsNote)):
                yLoc = int(round(objsNote[i].location.y * 10,0)) + 15
                duration = objsNote[i].dimensions.x / durF
                if yLoc <= len(retList)-1:
                    retList[yLoc] = duration
            retList.append(samples)

            if self.reSize:
                for o in objs:
                    n = random.uniform(self.qLow,self.qHigh)
                    o.scale.x = n
                    o.location.x = o.location.x + (-1+n)
                self.reSize = False

            if self.reQuan:
                for o in objs:
                    o.scale.x = 1
                    o.location.x = round(o.location.x,1)
                self.reQuan = False

        return retList
