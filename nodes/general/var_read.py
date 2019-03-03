import bpy
from bpy.props import *
from ... base_types import AnimationNode, AutoSelectDataType
from ... sockets.info import toIdName

class objCPConvertNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_objCPConvertNode"
    bl_label = "Read Variables"
    bl_width = 100

    dataType = StringProperty(default = "Generic", update = AnimationNode.refresh)
    lastCorrectionType = IntProperty()

    fixedOutputDataType = BoolProperty(name = "Fixed Data Type", default = False,
        description = "When activated the output type does not automatically change",
        update = AnimationNode.refresh)

    def create(self):
        self.newInput("Object", "Object", "inpObj")
        self.newInput("Text", "Variable Name", "cpName")
        self.newOutput(self.dataType, "Output", "new")

        if not self.fixedOutputDataType:
            self.newSocketEffect(AutoSelectDataType(
                "dataType", [self.outputs[0]], ignore = {"Generic"}))

    def draw(self, layout):
        row = layout.row(align = True)
        self.invokeSelector(row, "DATA_TYPE", "assignOutputType", text = "to " + self.dataType)
        icon = "LOCKED" if self.fixedOutputDataType else "UNLOCKED"
        row.prop(self, "fixedOutputDataType", icon = icon, text = "")

        if self.lastCorrectionType == 2:
            layout.label("Conversion Failed", icon = "ERROR")

    def assignOutputType(self, dataType):
        self.fixedOutputDataType = True
        if self.dataType != dataType:
            self.dataType = dataType

    def execute(self, inpObj, cpName):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        cpObj = bpy.data.objects.get('VAR_Store')
        if cpObj is not None and inpObj is None:
            cps = cpObj.keys()
            if cpName in cps:
                new, self.lastCorrectionType = self.outputs[0].correctValue(cpObj[cpName])
                return new
            else:
                return None
        elif inpObj is not None and cpName is not None:
            cps = inpObj.keys()
            if cpName in cps:
                new, self.lastCorrectionType = self.outputs[0].correctValue(inpObj[cpName])
                return new
            else:
                return None
        else:
            return None
