import bpy
from ... base_types import AnimationNode, DataTypeSelectorSocket

variables = {}

class VariableNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_variableATTRStore"
    bl_label = "Variable Store"

    assignedType: DataTypeSelectorSocket.newProperty(default = "Float")

    def create(self):
        self.newInput("an_BooleanSocket", "Condition", "condition")
        self.newInput(DataTypeSelectorSocket("Input", "input", "assignedType"))
        self.newOutput(DataTypeSelectorSocket("Output", "output", "assignedType"))

    def execute(self, condition, input):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.85,0.75,0.5)
        if condition:
            variables[self.identifier] = input

        if self.identifier in variables and type(variables[self.identifier]) == type(input):
            return variables[self.identifier]
        else:
            return self.inputs[1].getDefaultValue()
