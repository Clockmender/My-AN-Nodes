import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class manCPfromObj(bpy.types.Node, AnimationNode):
    bl_idname = "manCPfromObj"
    bl_label = "Manage Variables"
    bl_width = 200

    def create(self):
        self.newOutput("Text List", "Variables", "cusProp")

    def draw(self,layout):
        col = layout.column()
        self.invokeFunction(col, "resetNode", icon = "X",
            text = "Reset Variables", confirm=True)

    def resetNode(self):
        cpObj = bpy.data.objects.get('VAR_Store')
        if cpObj is not None:
            bpy.data.objects.remove(cpObj, True)
            for sc in bpy.data.scenes:
                sc.update()

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        cpObj = bpy.data.objects.get('VAR_Store')
        if cpObj is not None:
            cps = cpObj.keys()
            cps.sort()
            return cps
        else:
            return None
