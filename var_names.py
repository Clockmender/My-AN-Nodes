import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class getCPfromObj(bpy.types.Node, AnimationNode):
    bl_idname = "getCPfromObj"
    bl_label = "Get Variable Names"
    bl_width = 200

    indX = IntProperty(name = 'Index', min = 0, default = 0)

    def create(self):
        self.newOutput("Text", "Index Variable", "indxCP")

    def draw(self,layout):
        layout.prop(self, "indX")

    def execute(self):
        cpObj = bpy.data.objects.get('VAR_Store')
        if cpObj is not None:
            if self.indX >= len(cpObj.keys()):
                self.indX = len(cpObj.keys()) - 1
            cps = cpObj.keys()
            cps.sort()
            self.label = 'Active Var: '+cps[self.indX]
            return cps[self.indX]
        else:
            return None
