import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
from . midi_functions import getNote

class MidiNameNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiNameNode"
    bl_label = "MIDI Name Object(s)"
    bl_width_default = 180

    # Setup variables
    mid_c: BoolProperty(name = "Middle C = C4", default = True, update = propertyChanged)
    procI: BoolProperty(name = "Process by Index", default = False, update = propertyChanged)
    procL: BoolProperty(name = "Process by List", default = False, update = propertyChanged)

    def create(self):
        self.newInput("Integer"     , "Start Note Index", "start_i")
        self.newInput("Text"        , "Suffix"          , "suffix")
        self.newInput("Text List", "Notes Played", "noteL")
        self.newInput("Object List" , "Selected Objects", "objs")

    def draw(self,layout):
        layout.prop(self,"procI")
        layout.prop(self,"procL")
        layout.prop(self,"mid_c")
        layout.label(text="Check Process to Start/Stop", icon = "INFO")

    def execute(self, start_i, suffix, noteL, objs):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.85,0.75,0.5)
        if self.procI and len(objs) > 0 and start_i > 0:
            indX = (start_i - 12) if self.mid_c else start_i
            for ob in objs:
                noteName = getNote(indX, 0)
                if suffix is not '':
                    noteName = noteName +'_'+ suffix
                ob.name = noteName
                indX = indX + 1
            self.procI = False
        elif self.procL and len(objs) == len(noteL):
            self.message = ''
            indX = 0
            for ob in objs:
                ob.name = noteL[indX]
                indX = indX + 1
            self.procL = False
