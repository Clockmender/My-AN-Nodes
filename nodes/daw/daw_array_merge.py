import bpy
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
import numpy as np
from pypianoroll import Track, Multitrack
from matplotlib import pyplot as plt
from . daw_functions import getIndex, getFreq

class arrayMergeDAW(bpy.types.Node, AnimationNode):
    bl_idname = "an_arrayMergeDAW"
    bl_label = "ARRAY Merge"
    bl_width_default = 200

    saveM  : BoolProperty(name="Save Multi-Track",default=False)
    saveI  : BoolProperty(name="Save Image",default=False)

    def draw(self,layout):
        layout.prop(self,"saveM")
        layout.prop(self,"saveI")

    def create(self):
        self.newInput("an_FloatSocket","BPM","bpm")
        self.newInput("an_IntegerSocket","Bars #","barsN")
        self.newInput("an_IntegerSocket","Note Denominator","noteL")
        self.newInput("an_IntegerSocket","Trigger Frame","tFrame",value=0,min=0)
        self.newInput("an_GenericSocket","Track 1","track1")
        self.newInput("an_GenericSocket","Track 2","track2")
        self.newInput("an_TextSocket","File Name (no Ext)","fileName")
        self.newOutput("an_GenericSocket","Output","output")

    def execute(self,bpm,barsN,noteL,tFrame,track1,track2,fileName):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        self.width = 200
        frameC = bpy.context.scene.frame_current
        output = None
        if frameC == tFrame and track1 is not None and track2 is not None and noteL > 0 and barsN > 0:
            dBeats = []
            trackS = []
            trackS.append(track1)
            trackS.append(track2)
            for i in range(0, barsN):
                dBeats.append(i*noteL)
            multitrack = Multitrack(tracks=trackS, tempo=bpm,downbeat=dBeats, beat_resolution=16)
            fig, ax = multitrack.plot()
            fig.set_size_inches(64,(len(trackS)*6))
            if self.saveI:
                plt.savefig(fileName+".png")
            if self.saveM:
                multitrack.save(fileName+".npz")
            return dBeats
        else:
            return None
