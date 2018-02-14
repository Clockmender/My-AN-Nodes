import bpy
from bpy.props import *
from ... base_types import AnimationNode

class sequenceNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_sequenceNode"
    bl_label = "5 Channel Sequencer"
    bl_width_default = 180

    message1 = StringProperty("")

    def create(self):
        self.newInput("Integer", "Start Frame", "start")
        self.newInput("Integer", "End Frame", "endf")
        self.newInput("Float", "Step Value", "step")
        self.newOutput("Integer", "Out 1", "out_1")
        self.newOutput("Integer", "Out 2", "out_2")
        self.newOutput("Integer", "Out 3", "out_3")
        self.newOutput("Integer", "Out 4", "out_4")
        self.newOutput("Integer", "Out 5", "out_5")

    def draw(self,layout):
        if (self.message1 != ""):
            layout.label(self.message1, icon = "ERROR")

    def execute(self, start, endf, step):
        frame = bpy.context.scene.frame_current
        out_1 = 0
        out_2 = 0
        out_3 = 0
        out_4 = 0
        out_5 = 0

        if step >= 1 and start >= 0 and frame <= endf:
            end = start + (5 * step)
            self.message1 = ""

            if frame <= (start + (step * 5)):
                frm = frame - start
            else:
                count = int((frame - start) / (step * 5))
                frm = frame - (start + (step * 5 * count))

            if frm >= 0 and frm < step:
                out_1 = 1
            elif frm >= step and frm < (step * 2):
                out_2 = 1
            elif frm >= (step * 2) and frm < (step * 3):
                out_3 = 1
            elif frm >= (step * 3) and frm < (step * 4):
                out_4 = 1
            elif frm >= (step * 4) and frm < (step * 5):
                out_5 = 1
        else:
            if endf < (start + (step * 5)) or step < 1:
                self.message1 = "Check Start/End/Step Values"
            else:
                self.message1 = ""

        return out_1, out_2, out_3, out_4, out_5
