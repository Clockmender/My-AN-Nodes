import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class readSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_readSound"
    bl_label = "DAW Manage Slices"
    bl_width_default = 180

    sndIn    : StringProperty(name="Sound In",default="")
    lengthS  : FloatProperty(name="Length",default=1,min=0.01)
    offset   : FloatProperty(name="Offset",default=0,precision=1)
    message  : StringProperty()

    def draw(self,layout):
        layout.prop(self,"sndIn")
        layout.prop(self,"lengthS")
        layout.prop(self,"offset")
        if self.message is not '':
            layout.label(text=self.message,icon="INFO")

    def create(self):
        self.newInput("an_GenericSocket","Store","store")
        self.newInput("an_FloatSocket","Pitch Factor","pitch",value=1,minValue=0.25,maxValue=4)
        self.newInput("an_BooleanSocket","Process","process")
        self.newInput("an_ObjectListSocket","Objects","objs")
        self.newInput("an_FloatSocket","Pointer Location","pLoc")
        self.newOutput("an_SoundSocket","Sound O","soundO")

    def execute(self,store,pitch,process,objs,pLoc):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.mesage = ""
        if len(objs) == 0:
            if store is not None and process:
                if self.sndIn is not "":
                    self.color = (1,0.8,1)
                    if self.sndIn in store:
                        storeL = store["TimeS"]
                        pitchL = self.lengthS * pitch
                        if pitchL > storeL:
                            pitchL = storeL
                        sndO = store[self.sndIn]
                        sndO = sndO.pitch(pitch)
                        sndO = sndO.limit(0,pitchL)
                        self.message = ""
                        return sndO
                    else:
                        self.color = (0.75,1,0.75)
                        self.message = "Sound Not Found"
                        return None
                else:
                    self.color = (0.75,1,0.75)
                    return None
            else:
                self.color = (0.75,1,0.75)
                return None
        else:
            self.mesage = ""
            self.color = (1,0.8,1)
            if store is not None:
                objsNote = [o for o in objs if o.location.x > pLoc-0.05 and o.location.x < pLoc+0.05]
                if len(objsNote) > 0:
                    ob = objsNote[0]
                    indX = int((ob.location.y+self.offset) * 10)
                    if indX in range(2,14):
                        sndO = store["snd"+str(indX)]
                    elif indX == 1:
                        sndO = store["SoundCut"]
                    elif indX == 0:
                        sndO = store["sndO"]
                    else:
                        self.color = (0.75,1,0.75)
                        return None
                    return sndO
                else:
                    self.color = (0.75,1,0.75)
                    return None
            else:
                self.color = (0.75,1,0.75)
                return None
