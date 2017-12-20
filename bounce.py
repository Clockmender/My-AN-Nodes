import bpy
from bpy.props import *
from math import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class bounceNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_bounceNode"
    bl_label = "Bounce Node v 1.0"
    bl_width_default = 200

    frm_s = FloatProperty(name = "Start Frame", default = 1, precision = 0)
    frm_e = FloatProperty(name = "End Frame", default = 10, precision = 0, min = 10)
    speed = FloatProperty(name = "Cycle Speed", default = 4, min = 4)
    hgt_s = FloatProperty(name = "Start Height", default = 1)
    hgt_b = FloatProperty(name = "Base Height",default = 0)
    message1 = StringProperty("")

    def create(self):
        self.newOutput("Float", "Output Height", "cos_w")

    def draw(self, layout):
        layout.prop(self, "frm_s")
        layout.prop(self, "frm_e")
        layout.prop(self, "speed")
        layout.prop(self, "spd_d")
        layout.prop(self, "hgt_s")
        layout.prop(self, "hgt_b")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "ERROR")

    def execute(self):
        if self.hgt_s <= (self.hgt_b + 0.1):
            self.message1 = "Height Errors!"
        else:
            self.message1 = ""
            frm_c = bpy.context.scene.frame_current
            len_m = self.frm_e - self.frm_s
            if frm_c >= self.frm_s and frm_c <= self.frm_e:
                fac_m = len_m - (frm_c - self.frm_s)
                cos_w = abs(cos((frm_c - self.frm_s) * 2 * pi / (self.speed * 2)))
                cos_w = (cos_w * fac_m * self.hgt_s / (self.frm_e - self.frm_s)) + self.hgt_b
            elif frm_c < self.frm_s:
                cos_w = self.hgt_s + self.hgt_b
            else:
                cos_w = self.hgt_b

            return cos_w
