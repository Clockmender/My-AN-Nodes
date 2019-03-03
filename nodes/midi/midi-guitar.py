import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged

class MidiGuitarNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiGuitarNode"
    bl_label = "MIDI Guitar Strings/Frets"
    bl_width_default = 150

    # 6 String Fret List
    fretListS = [
        'NUT','F1','F2','F3','F4',
        'NUT','F1','F2','F3','F4',
        'NUT','F1','F2','F3','F4',
        'NUT','F1','F2','F3',
        'NUT','F1','F2','F3','F4',
        'NUT','F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
        'F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24']
    # Bass Fret List
    fretListB = [
        'NUT','F1','F2','F3','F4',
        'NUT','F1','F2','F3','F4',
        'NUT','F1','F2','F3','F4',
        'NUT','F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
        'F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24']

    mid_c = BoolProperty(name = "Middle C = C4", default = True, update = propertyChanged)
    suffix = StringProperty(name = "Suffix", update = propertyChanged)

    def draw(self,layout):
        layout.prop(self, "mid_c")
        layout.prop(self, "suffix")

    def create(self):
        self.newInput("Integer", "Input Note index", "idx")
        self.newOutput("Text List", "6 String", "sixS")
        self.newOutput("Text List", "Bass", "bass")

    def execute(self,idx):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,1,0.75)
        if not self.mid_c:
            idx = idx + 12
        # 6 string
        if idx >= 52 and idx < 57:
            string = 'El'+self.suffix
        elif idx >= 57 and idx < 62:
            string = 'A'+self.suffix
        elif idx >= 62 and idx < 67:
            string = 'D'+self.suffix
        elif idx >= 67 and idx < 71:
            string = 'G'+self.suffix
        elif idx >= 71 and idx < 76:
            string = 'B'+self.suffix
        elif idx >= 76 and idx < 101:
            string = 'Et'+self.suffix
        else:
            string = 'null'
            fret = 'null'
        # Get Fret
        if string != 'null':
            fret = self.fretListS[idx - 52]
        # Bass
        if idx >= 40 and idx < 45:
            stringb = 'El'+self.suffix
        elif idx >= 45 and idx < 50:
            stringb = 'A'+self.suffix
        elif idx >= 50 and idx < 55:
            stringb = 'D'+self.suffix
        elif idx >= 55 and idx < 80:
            stringb = 'G'+self.suffix
        else:
            stringb = 'null'
            fretb = 'null'
        # Get Fret
        if stringb != 'null':
            fretb = self.fretListB[idx - 40]
        # Set Output List
        sixS = [string,fret]
        bass = [stringb,fretb]

        return sixS, bass
