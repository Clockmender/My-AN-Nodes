import bpy
from ... base_types import AnimationNode, DataTypeSelectorSocket
from bpy.props import *
from ... events import propertyChanged

class switchInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_switchInputNode"
    bl_label = "Input Switch"

    assignedType: DataTypeSelectorSocket.newProperty(default = "Float")
    frameS: IntProperty(name = "Switch Frame", default = 1, min = 1)

    def draw(self,layout):
        layout.prop(self,"frameS")

    def create(self):
        self.newInput("an_BooleanSocket", "Switch", "sw")
        self.newInput(DataTypeSelectorSocket("Input-1", "a", "assignedType"))
        self.newInput(DataTypeSelectorSocket("Input-2", "b", "assignedType"))
        self.newOutput(DataTypeSelectorSocket("Output", "output", "assignedType"))

    def execute(self, sw, a, b):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.4,0.6,1)
        frameC = bpy.context.scene.frame_current
        return b if sw or frameC >= self.frameS else a
