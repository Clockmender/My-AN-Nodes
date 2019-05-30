import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
import random

enum = [('Files','Files','Sound Type','',0),
    ('Sounds','Sounds','Sound Type','',1)
    ]

class indexFiles(bpy.types.Node, AnimationNode):
    bl_idname = "an_indexFiles"
    bl_label = "DAW Track Control"
    bl_width_default = 200

    message : StringProperty()
    offSet  : IntProperty(name="Track Offset",default=0)
    reQuan  : BoolProperty(name="Quantise Perfect",default=False)
    reSize  : BoolProperty(name="Random De-Quantise",default=False)
    qHigh   : FloatProperty(name="Q Max",min=1.001,max=1.08)
    qLow    : FloatProperty(name="Q Max",min=0.92,max=0.999)
    mode    : EnumProperty(name = "Mode", items = enum, update = AnimationNode.refresh)

    def draw(self,layout):
        layout.prop(self,"mode")
        layout.prop(self,"reQuan")
        layout.prop(self,"reSize")
        layout.prop(self,"qHigh")
        layout.prop(self,"qLow")
        if self.message is not '':
            layout.label(text=self.message, icon='INFO')

    def create(self):
        self.newInput("an_ObjectListSocket","Note Objects","objs")
        if self.mode == "Sounds":
            self.newInput("an_FloatSocket","Short Note Time","noteL")
        self.newInput("an_FloatSocket","Pointer Location","pLoc")
        if self.mode == "Sounds":
            self.newInput("an_IntegerSocket","Samples","samples")
        self.newOutput("an_IntegerListSocket","Sound Data","sndList")
        if self.mode == "Sounds":
            self.newOutput("an_IntegerSocket","Samples","samplesO")

    def getExecutionFunctionName(self):
        if self.mode == "Files":
            return "executeF"
        else:
            return "executeS"

    def executeF(self,objs,pLoc):
        # Passes list of lists [[index,delay,volume,duration]] duration omitted for files
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        self.label = "DAW Track Control"
        retList = []
        if len(objs) > 0:
            selObs = [o for o in objs if o.select_get()]
            if len(selObs) == 1:
                if "Velocity" not in selObs[0]:
                    selObs[0]["Velocity"] = 127
                vel = round(selObs[0]["Velocity"] / 127,4)
                yLoc = int(round(selObs[0].location.y * 10,0))
                xOff = round(selObs[0].location.x - round(selObs[0].location.x,1),3)
                retList.append([yLoc,xOff,vel])
                self.message = str(round(selObs[0].location.x - round(selObs[0].location.x,1),3))+","+str(xOff)+" Playing Selected Note Only"
                return retList
            self.message = ""
            objsNote = [o for o in objs if o.location.x > pLoc-0.01 and o.location.x < pLoc+0.09]
            for i in range(0,len(objsNote)):
                if "Velocity" not in objsNote[i]:
                    objsNote[i]["Velocity"] = 127
                vel = round(objsNote[i]["Velocity"] / 127,4)
                yLoc = int(round(objsNote[i].location.y * 10,0))
                xOff = round(objsNote[i].location.x - round(objsNote[i].location.x,1),3)
                if yLoc in range(0,89):
                    retList.append([yLoc,xOff,vel])

            if self.reSize:
                for o in objs:
                    nL = random.uniform(1,self.qHigh)
                    nD = random.uniform(self.qLow,self.qHigh)
                    o.location.x = o.location.x + (-1+nD)
                    o.dimensions.x = o.dimensions.x * nD
                self.reSize = False

            if self.reQuan:
                for o in objs:
                    o.location.x = round(o.location.x,1)
                    o.dimensions.x = round(o.dimensions.x,1)
                self.reQuan = False
        return retList

    def executeS(self,objs,noteL,pLoc,samples):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        self.label = "DAW Track Control"
        retList = []
        if len(objs) > 0:
            selObs = [o for o in objs if o.select_get()]
            if len(selObs) == 1:
                if "Velocity" not in selObs[0]:
                    selObs[0]["Velocity"] = 127
                vel = round(selObs[0]["Velocity"] / 127,4)
                yLoc = int(round(selObs[0].location.y * 10,0))
                xOff = abs(round(selObs[0].location.x - round(selObs[0].location.x,1),3))
                durT = round(selObs[0].dimensions.x * 10 * noteL,4)
                if yLoc in range(0,89):
                    for i in [yLoc-3,xOff,vel,durT]:
                        retList.append(i)
                self.message = str(round(selObs[0].location.x - round(selObs[0].location.x,1),3))+","+str(xOff)+" Playing Selected Note Only"
                return retList, samples
            self.message = ""
            objsNote = [o for o in objs if o.location.x > pLoc-0.01 and o.location.x < pLoc+0.09]
            for i in range(0,len(objsNote)):
                if "Velocity" not in objsNote[i]:
                    objsNote[i]["Velocity"] = 127
                vel = round(objsNote[i]["Velocity"] / 127,4)
                yLoc = int(round(objsNote[i].location.y * 10,0))
                durT = round(objsNote[i].dimensions.x * 10 * noteL,4)
                xOff = abs(round(objsNote[i].location.x - round(objsNote[i].location.x,1),3))
                if yLoc in range(0,89):
                    for i in [yLoc-3,xOff,vel,durT]:
                        retList.append(i)

            if self.reSize:
                for o in objs:
                    nL = random.uniform(1,self.qHigh)
                    nD = random.uniform(self.qLow,self.qHigh)
                    o.location.x = o.location.x + (-1+nD)
                    o.dimensions.x = o.dimensions.x * nD
                self.reSize = False

            if self.reQuan:
                for o in objs:
                    o.location.x = round(o.location.x,1)
                    o.dimensions.x = round(o.dimensions.x,1)
                self.reQuan = False
        return retList, samples
