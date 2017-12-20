import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class BonesScaleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BonesScaleNode"
    bl_label = "Bones Transform Scale"
    bl_width_default = 180

    def create(self):
        self.newInput("Bone List", "Bones List", "bones")
        self.newOutput("Bone List", "Bones List", "bones")
        self.newInput("Float", "X Scale", "loc_x")
        self.newInput("Float", "Y Scale", "loc_y")
        self.newInput("Float", "Z Scale", "loc_z")

    def execute(self, bones, loc_x, loc_y, loc_z):
        if bones:
            for b in bones:
                b.scale.x = loc_x
                b.scale.y = loc_y
                b.scale.z = loc_z
        return bones
