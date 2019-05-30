import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . daw_functions import getNote, getChord
from ... utils.sequence_editor import getOrCreateSequencer, getEmptyChannel
from ... utils.path import getAbsolutePathOfSound

class loadSoundDAW(bpy.types.Node, AnimationNode):
    bl_idname = "an_loadSoundDAW"
    bl_label = "DAW Load Sound to VSE"
    bl_width_default = 180

    channel   : IntProperty(name="VSE Channel",min=0)
    offSet    : IntProperty(name="Insert Frame",min=0)
    volM      : FloatProperty(name="Initial Volume",min=0,max=5)
    message   : StringProperty()

    def draw(self,layout):
        layout.label(text="Uses Current Frame if 0")
        layout.prop(self,"offSet")
        layout.label(text="Uses New Channel if 0")
        layout.prop(self,"channel")
        layout.label(text="")
        col = layout.column()
        col.scale_y = 1.2
        self.invokeSelector(col, "PATH", "loadSound",
            text = "Load Sound File to VSE", icon = "SOUND")
        if self.message is not "":
            layout.label(text=self.message,icon="INFO")

    def create(self):
        self.newOutput("an_TextSocket","Last File Loaded","lastF")

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        return None

    def loadSound(self, path):
        editor = getOrCreateSequencer(self.nodeTree.scene)
        channel = getEmptyChannel(editor) if self.channel == 0 else self.channel
        offSet = bpy.context.scene.frame_current if self.offSet == 0 else self.offSet
        sequence = editor.sequences.new_sound(
            name = os.path.basename(path),
            filepath = path,
            channel = channel,
            frame_start = offSet)
        sequence.show_waveform = True
        self.message = "Sound Loaded."
