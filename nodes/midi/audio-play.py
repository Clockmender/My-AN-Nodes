import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
import pygame.mixer as pgm
pgm.init()

class AudioPlayNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_AudioPlayNode"
    bl_label = "AUDIO Play Music File"
    bl_width_default = 200

    message: StringProperty()
    loaded:  BoolProperty()
    loaded = False

    def draw(self,layout):
        col = layout.column()
        col.scale_y = 1.5
        self.invokeSelector(col ,"PATH", "loadFile", icon = "FILE_NEW",
            text = "Select Sound File")
        layout.label(text=self.message,icon="NONE")
        self.invokeFunction(col, "playFile", icon = "PLAY",
            text = "Play File")
        self.invokeFunction(col, "pauseFile", icon = "PAUSE",
            text = "Pause Playback")
        self.invokeFunction(col, "resumeFile", icon = "TRIA_RIGHT_BAR",
            text = "Resume Playback")
        self.invokeFunction(col, "stopFile", icon = "CANCEL",
            text = "Stop Playback")

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.65,0.65,0.95)

    def loadFile(self,path):
        self.loaded = True
        pgm.music.load(path)
        self.message = str(path)

    def playFile(self):
        if self.loaded:
            pgm.music.play()

    def pauseFile(self):
        if self.loaded:
            pgm.music.pause()

    def resumeFile(self):
        if self.loaded:
            pgm.music.unpause()

    def stopFile(self):
        if self.loaded:
            pgm.music.stop()
