import bpy
from bpy.props import *
from math import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class frameRangeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_frameRangeNode"
    bl_label = "Frame Range/Switch"
    bl_width_default = 200

    message1 = StringProperty("")
    ins_v = BoolProperty(name = "Inside Frame Range", default = True, update = propertyChanged)

    def create(self):
        self.newInput("Float", "Input Value", "inp_v")
        self.newInput("Integer", "Start Frame", "frm_s")
        self.newInput("Integer", "End Frame", "frm_e")
        self.newOutput("Integer", "Frame (In Range)", "frm_r")
        self.newOutput("Float", "Output Value", "out_v")
        self.newOutput("Boolean", "In/Out of Range", "out_b")
        self.newOutput("Float", "Combined Output", "out_c")

    def draw(self,layout):
        layout.prop(self, "ins_v")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "ERROR")

    def execute(self, inp_v, frm_s, frm_e):
        frm_c = bpy.context.scene.frame_current
        if frm_e < (frm_s + 1):
            self.message1 = "Start Frame > End Frame + 1"
            frm_r = 0
            out_v = 0
            out_b = False
        else:
            self.message1 = ""
            if frm_c < frm_s or frm_c > frm_e:
                frm_r = 0
                out_v = 0
            else:
                frm_r = frm_c - frm_s
                out_v = inp_v
            if self.ins_v:
                out_b = frm_c in range(frm_s,frm_e)
            else:
                out_b = frm_c not in range(frm_s,frm_e)

        out_c = frm_r * out_v * out_b
        return frm_r, out_v, out_b, out_c
