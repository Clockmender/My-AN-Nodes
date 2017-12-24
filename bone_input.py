import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from math import pi

class BoneInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BoneInputNode"
    bl_label = "Bone Transforms Input"
    bl_width_default = 180

    use_d = BoolProperty(name = "Degrees (Euler Bones Only)", default = False, update = propertyChanged)

    def create(self):
        self.newInput("Bone", "Bone", "bone")
        self.newOutput("Bone", "Bone", "bone")
        self.newOutput("Float List", "Locations List", "locations")
        self.newOutput("Float List", "Rotations List", "rotations")
        self.newOutput("Float List", "Scales List", "scales")

    def draw(self, layout):
        layout.prop(self, "use_d")

    def execute(self, bone):
        if bone:
            if bone.rotation_mode == 'QUATERNION':
                locations = [bone.location.x, bone.location.y, bone.location.z]
                w = bone.rotation_quaternion.w
                x = bone.rotation_quaternion.x
                y = bone.rotation_quaternion.y
                z = bone.rotation_quaternion.z
                rotations = [w, x, y, z]
                scales = [bone.scale.x, bone.scale.y, bone.scale.z]
            else:
                locations = [bone.location.x, bone.location.y, bone.location.z]
                x = bone.rotation_euler.x
                y = bone.rotation_euler.y
                z = bone.rotation_euler.z
                if self.use_d:
                    x = round((x * 180 / pi), 5)
                    y = round((y * 180 / pi), 5)
                    z = round((z * 180 / pi), 5)
                rotations = [x, y, z]
                scales = [bone.scale.x, bone.scale.y, bone.scale.z]
        else:
            locations = [0,0,0]
            rotations = [0,0,0]
            scales = [1,1,1]

        return bone, locations, rotations, scales
