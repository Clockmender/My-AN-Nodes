import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . daw_functions import getNote, getIndex, getFreq

enum = [('Animated','Animated','Mode','',0),
    ('Selected','Selected','Mode','',1)
    ]

class objectAnSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_objectAnSound"
    bl_label = "DAW Sound From Animated Objects"
    bl_width_default = 180

    message  : StringProperty()
    mode     : EnumProperty(name = "Mode", items = enum, update = AnimationNode.refresh)

    def draw(self,layout):
        layout.prop(self, "mode")
        if self.message is not '':
            layout.label(text=self.message,icon="NONE")

    def create(self):
        self.newInput("an_ObjectListSocket","Input Objects","objs")
        if self.mode == "Animated":
            self.newInput("an_TextSocket","Anim Variable","var",value="rotation_euler.x")
        self.newInput("an_FloatSocket","Duration","durT")
        self.newInput("an_IntegerSocket","Beat Multiplier","beatM",minValue=1,maxValue=32)
        self.newOutput("an_FloatListSocket","Sound Data","noteSO")

    def getExecutionFunctionName(self):
        if self.mode == "Animated":
            return "executeA"
        else:
            return "executeS"

    def executeA(self,objs,var,durT,beatM):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        # Process input list from Array format [note,start,vol,duration] repeated in blocks of 4
        self.message = ""
        noteSO = []
        for o in objs:
            if eval("o."+var+" != 0"):
                noteName = o.name.split("_")[0]
                indX = getIndex(noteName)
                noteSO.append(indX)
                noteSO.append(0)
                noteSO.append(1)
                noteSO.append(durT*beatM)
        return noteSO

    def executeS(self,objs,durT,beatM):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        # Process input list from Array format [note,start,vol,duration] repeated in blocks of 4
        self.message = ""
        noteSO = []
        for o in objs:
            if o.select_get() == True:
                noteName = o.name.split("_")[0]
                indX = getIndex(noteName)
                noteSO.append(indX)
                noteSO.append(0)
                noteSO.append(1)
                noteSO.append(durT*beatM)
        return noteSO
