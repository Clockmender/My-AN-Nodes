import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class BonesScaleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BonesScaleNode"
    bl_label = "Bone(s) Transform Scale"
    bl_width_default = 180

    use_s = BoolProperty(name = "Single Bone", default = True, update = AnimationNode.refresh)

    def create(self):
        if self.use_s:
            self.newInput("Bone", "Single Bone", "bone")
            self.newOutput("Bone", "Single Bone", "bone")
        else:
            self.newInput("Bone List", "Bones List", "bones")
            self.newOutput("Bone List", "Bones List", "bones")
        self.newInput("Float", "X Scale", "loc_x")
        self.newInput("Float", "Y Scale", "loc_y")
        self.newInput("Float", "Z Scale", "loc_z")

    def draw(self, layout):
        layout.prop(self, "use_s")

    def getExecutionFunctionName(self):
        if self.use_s:
            return "execute_bone"
        else:
            return "execute_bones"

    def execute_bone(self, bone, loc_x, loc_y, loc_z):
        if bone:
            bone.scale.x = loc_x
            bone.scale.y = loc_y
            bone.scale.z = loc_z

        return bone

    def execute_bones(self, bones, loc_x, loc_y, loc_z):
        if bones:
            for b in bones:
                b.scale.x = loc_x
                b.scale.y = loc_y
                b.scale.z = loc_z

        return bones
