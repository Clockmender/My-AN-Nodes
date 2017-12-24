import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class BonesLocateNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BonesLocateNode"
    bl_label = "Bone(s) Transform Locate"
    bl_width_default = 180

    use_s = BoolProperty(name = "Single Bone", default = True, update = AnimationNode.refresh)

    def create(self):
        if self.use_s:
            self.newInput("Bone", "Single Bone", "bone")
            self.newOutput("Bone", "Single Bone", "bone")
        else:
            self.newInput("Bone List", "Bones List", "bones")
            self.newOutput("Bone List", "Bones List", "bones")
        self.newInput("Float", "X Loc", "loc_x")
        self.newInput("Float", "Y Loc", "loc_y")
        self.newInput("Float", "Z Loc", "loc_z")

    def draw(self, layout):
        layout.prop(self, "use_s")

    def getExecutionFunctionName(self):
        if self.use_s:
            return "execute_bone"
        else:
            return "execute_bones"

    def execute_bone(self, bone, loc_x, loc_y, loc_z):
        if bone:
            bone.location.x = loc_x
            bone.location.y = loc_y
            bone.location.z = loc_z

    def execute_bones(self, bones, loc_x, loc_y, loc_z):
        if bones:
            for b in bones:
                b.location.x = loc_x
                b.location.y = loc_y
                b.location.z = loc_z

        return bones
