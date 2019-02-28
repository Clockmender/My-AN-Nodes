import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged

class MidiNameNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiNameNode"
    bl_label = "MIDI Name Object(s)"
    bl_width_default = 180

    # Setup variables
    mid_c = BoolProperty(name = "Middle C = C4", default = True, update = propertyChanged)
    proc = BoolProperty(name = "Process", default = False, update = propertyChanged)

    def create(self):
        self.newInput("Integer"     , "Start Note Index", "start_i")
        self.newInput("Text"        , "Suffix"          , "suff")
        self.newInput("Object List" , "Selected Objects", "objs")

    def draw(self,layout):
        layout.prop(self,"proc")
        layout.prop(self,"mid_c")
        layout.label("Check Process to Start/Stop", icon = "INFO")

    def execute(self, start_i, suff, objs):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,1,0.75)
        if self.proc and len(objs) > 0 and start_i != 0:
            idx = start_i
            note_list = [
                'c0','cs0','d0','ds0','e0','f0','fs0','g0','gs0','a0','as0','b0',
                'c1','cs1','d1','ds1','e1','f1','fs1','g1','gs1','a1','as1','b1',
                'c2','cs2','d2','ds2','e2','f2','fs2','g2','gs2','a2','as2','b2',
                'c3','cs3','d3','ds3','e3','f3','fs3','g3','gs3','a3','as3','b3',
                'c4','cs4','d4','ds4','e4','f4','fs4','g4','gs4','a4','as4','b4',
                'c5','cs5','d5','ds5','e5','f5','fs5','g5','gs5','a5','as5','b5',
                'c6','cs6','d6','ds6','e6','f6','fs6','g6','gs6','a6','as6','b6',
                'c7','cs7','d7','ds7','e7','f7','fs7','g7','gs7','a7','as7','b7',
                'c8','cs8','d8','ds8','e8','f8','fs8','g8','gs8','a8','as8','b8',
                'c9','cs9','d9','ds9','e9','f9','fs9','g9']
            for i in objs:
                if self.mid_c:
                    note_name = note_list[idx - 12]
                else:
                    note_name = note_list[idx]
                if suff != '':
                    note_name = note_name + suff
                i.name = note_name
                idx = idx + 1

            self.proc = False
