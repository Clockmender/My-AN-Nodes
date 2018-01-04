import bpy
from bpy.props import *
from ... base_types import AnimationNode

class objectTransformNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_objectTransformNode"
    bl_label = "Object World Transforms v 1.0"
    bl_width_default = 180

    def create(self):
        self.newInput("Object", "Object", "obj")
        self.newOutput("Vector", "W-Location", "loc")
        self.newOutput("Quaternion", "W-Rotation", "rot")
        self.newOutput("Vector", "W-Scale", "scale")

    def execute(self, obj):
        loc, rot, scale = obj.matrix_world.decompose()
        return loc, rot, scale
