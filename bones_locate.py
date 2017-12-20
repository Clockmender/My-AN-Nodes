import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class BonesLocateNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BonesLocateNode"
    bl_label = "Bones Transform Locate"
    bl_width_default = 180

    def create(self):
        self.newInput("Bone List", "Bones List", "bones")
        self.newOutput("Bone List", "Bones List", "bones")
        self.newInput("Float", "X Loc", "loc_x")
        self.newInput("Float", "Y Loc", "loc_y")
        self.newInput("Float", "Z Loc", "loc_z")

    def execute(self, bones, loc_x, loc_y, loc_z):
        if bones:
            for b in bones:
                b.location.x = loc_x
                b.location.y = loc_y
                b.location.z = loc_z
        return bones
