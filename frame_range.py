import bpy
from bpy.props import *
from math import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class frameRangeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_frameRangeNode"
    bl_label = "Frame Range/Switch v 1.0"
    bl_width_default = 200

    message1 = StringProperty("")

    def create(self):
        self.newInput("Float", "Input Value", "inp_v")
        self.newInput("Integer", "Start Frame", "frm_s")
        self.newInput("Integer", "End Frame", "frm_e")
        self.newOutput("Integer", "Frame", "frm_r")
        self.newOutput("Float", "Output Value", "out_v")

    def draw(self,layout):
        if (self.message1 != ""):
            layout.label(self.message1, icon = "ERROR")
            frm_r = 0
            out_v = 0

    def execute(self, inp_v, frm_s, frm_e):
        if frm_e < (frm_s + 1):
            self.message1 = "Start Frame > End Frame + 1"
            frm_r = 0
            out_v = 0
        else:
            self.message1 = ""
            frm_c = bpy.context.scene.frame_current
            if frm_c < frm_s or frm_c > frm_e:
                frm_r = 0
                out_v = 0
            else:
                frm_r = frm_c - frm_s
                out_v = inp_v

        return frm_r, out_v
