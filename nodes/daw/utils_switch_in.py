import bpy
from ... base_types import AnimationNode, DataTypeSelectorSocket

class switchNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_UswitchNodeI"
    bl_label = "UTILS Switch In"
    bl_width_default = 150

    assignedType: DataTypeSelectorSocket.newProperty(default = "Float")

    def create(self):
        self.newInput("an_BooleanSocket", "In 1/In 2", "condition")
        self.newInput(DataTypeSelectorSocket("Input 1", "input1", "assignedType"))
        self.newInput(DataTypeSelectorSocket("Input 2", "input2", "assignedType"))
        self.newOutput(DataTypeSelectorSocket("Out", "output", "assignedType"))

    def execute(self, condition, input1, input2):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.73,0.83,1)
        if condition:
            return input1
        else:
            return input2
