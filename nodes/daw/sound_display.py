import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from matplotlib import pyplot as plt

class displaySound(bpy.types.Node, AnimationNode):
    bl_idname = "an_displaySound"
    bl_label = "SOUND Display"
    bl_width_default = 150

    def create(self):
        self.newInput("an_TextSocket","File Name","fileName",value="/Users/mac/Documents/Blender/2.8-files/fig.png")
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,fileName,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        if fileName is not "":
            self.label = "SOUND Display"
            self.color = (0.65,1,1)
            if isinstance(snd, aud.Sound):
                fig1 = plt.figure(figsize=(20,2))
                fig, ax = plt.plot(snd.data(),scalex=True,scaley=True,color='#008080')
                ax = plt.gca()
                ax.set_facecolor('#80F0F0')
                fig.set_figure(fig1)
                plt.tight_layout()
                plt.savefig(fileName)
                plt.close('all')
            else:
                self.color = (0.75,1,0.75)
                self.label = "SOUND Di BYPASS (No Sound)"
                return None
        else:
            self.label = "SOUND Di BYPASS (No Filename)"
            self.color = (0.75,1,0.75)
        return snd
