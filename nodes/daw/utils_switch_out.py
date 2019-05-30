import bpy
from ... base_types import AnimationNode, DataTypeSelectorSocket

class switchNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_UswitchNode"
    bl_label = "UTILS Switch Out"
    bl_width_default = 150

    assignedType: DataTypeSelectorSocket.newProperty(default = "Float")

    def create(self):
        self.newInput("an_BooleanSocket", "Out 1/Out 2", "condition")
        self.newInput(DataTypeSelectorSocket("Input", "input", "assignedType"))
        self.newOutput(DataTypeSelectorSocket("Out 1", "output1", "assignedType"))
        self.newOutput(DataTypeSelectorSocket("Out 2", "output2", "assignedType"))

    def execute(self, condition, input):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.73,0.83,1)
        if condition:
            return input, self.inputs[1].getDefaultValue()
        else:
            return self.inputs[1].getDefaultValue(), input
