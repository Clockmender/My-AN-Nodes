import bpy
from ... base_types import AnimationNode
from bpy.props import *
from mathutils import Vector, Euler, Quaternion
from ... events import propertyChanged

class variableCPStore(bpy.types.Node, AnimationNode):
    bl_idname = "an_variableCPStore"
    bl_label = "Variable Store"
    bl_width_default = 200

    strV = StringProperty()
    booV = BoolProperty(default = True)
    mess = StringProperty()
    intV = IntProperty(default = 0)
    floV = FloatProperty(default = 0)
    vecV = FloatVectorProperty(subtype = 'XYZ')
    eulV = FloatVectorProperty(subtype = 'EULER')
    quaV = FloatVectorProperty(subtype = 'QUATERNION')
    enum = [("STRING","String","String Variable","",0),
        ("FLOAT","Float","Float Variable","",1),
        ("INTEGER","Integer","Integer Variable","",2),
        ("VECTOR","Vector","Vector Variable","",3),
        ("EULER","Euler","Euler Rotation Variable","",4),
        ("QUATERNION","Quaternion","Quaternion Rotation Variable","",5),
        ("BOOLEAN","Boolean","Boolean Rotation Variable","",6)]

    mode = EnumProperty(name = "Type", items = enum, update = AnimationNode.refresh)

    def draw(self,layout):
        layout.prop(self, "mode")
        layout.prop(self, "booC")
        if self.mess != '':
            layout.label(self.mess,icon = "ERROR")

    def create(self):
        if self.mode == "STRING":
            self.newInput("Text", "Input", "varInput")
            self.newOutput("Text", "Output", "varOutput")
        elif self.mode == "INTEGER":
            self.newInput("Integer", "Input", "varInput")
            self.newOutput("Integer", "Output", "varOutput")
        elif self.mode == "FLOAT":
            self.newInput("Float", "Input", "varInput")
            self.newOutput("Float", "Output", "varOutput")
        elif self.mode == "VECTOR":
            self.newInput("Vector", "Input", "varInput")
            self.newOutput("Vector", "Output", "varOutput")
        elif self.mode == "EULER":
            self.newInput("Euler", "Input", "varInput")
            self.newOutput("Euler", "Output", "varOutput")
        elif self.mode == "QUATERNION":
            self.newInput("Quaternion", "Input", "varInput")
            self.newOutput("Quaternion", "Output", "varOutput")
        elif self.mode == "BOOLEAN":
            self.newInput("Boolean", "Input", "varInput")
            self.newOutput("Boolean", "Output", "varOutput")
        self.newInput("Boolean", "Process", "boolInput")
        self.newInput("Text", "Variable Name", "cpName")

    def execute(self,varInput,boolInput,cpName):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if cpName == '':
            self.mess = 'Enter Variable Name'
            return None
        else:
            self.mess = ''
        if self.mode == "STRING":
            if boolInput:
                self.strV = varInput
                varOutput = varInput
            else:
                varOutput = self.strV
        elif self.mode == "INTEGER":
            if boolInput:
                self.intV = varInput
                varOutput = varInput
            else:
                varOutput = self.intV
        elif self.mode == "FLOAT":
            if boolInput:
                self.floV = varInput
                varOutput = varInput
            else:
                varOutput = self.floV
        elif self.mode == "BOOLEAN":
            if boolInput:
                self.booV = varInput
                varOutput = varInput
            else:
                varOutput = self.booV
        elif self.mode == "VECTOR":
            if boolInput:
                self.vecV = varInput
                varOutput = varInput
            else:
                varOutput = self.vecV
        elif self.mode == "EULER":
            if boolInput:
                self.eulV = varInput
                varOutput = varInput
            else:
                varOutput = self.eulV
        elif self.mode == "QUATERNION":
            if boolInput:
                self.quaV = varInput
                varOutput = varInput
            else:
                varOutput = self.quaV

        cpObj = bpy.data.objects.get('VAR_Store')
        if cpObj is None:
            bpy.data.objects.new('VAR_Store', None)
            cpObj = bpy.data.objects.get('VAR_Store')

        cpObj[cpName] = varOutput

        return varOutput
