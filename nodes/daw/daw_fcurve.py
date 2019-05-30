import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from ... data_structures import FloatList, DoubleList

class objectFCurve(bpy.types.Node, AnimationNode):
    bl_idname = "an_FCurve"
    bl_label = "DAW FCurve Value"
    bl_width_default = 200

    message : StringProperty()
    trigger : IntProperty(name="Trigger Frame",default=1,min=0)
    notesP = []

    def draw(self,layout):
        layout.prop(self,"trigger")
        if self.message is not "":
            layout.label(text=self.message,icon='INFO')

    def create(self):
        self.newInput("an_ObjectSocket","Object","object")
        self.newInput("an_FloatSocket","Value Multiplier","valM",value=1,minvalue=0)
        self.newInput("an_FloatSocket","Value offset","valS",value=0)
        self.newInput("an_IntegerSocket","FCurve Index","curveI",value=0,minValue=0)
        self.newOutput("an_FloatSocket", "FCurve Value", "value")
        #self.newOutput("an_FloatListSocket", "KeyFrames", "keyframesFrames")
        #self.newOutput("an_FloatListSocket", "KeyValues", "keyframesValues")
        self.newOutput("an_GenericSocket","Notes Played","notesP")
        self.newOutput("an_TextSocket","Note","note")
        self.newOutput("an_FloatSocket","Duration","durT")

    def execute(self,object,valM,valS,curveI):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        frameC = bpy.context.scene.frame_current

        try: fCurves = list(object.animation_data.action.fcurves)
        except: fCurves = []
        if len(fCurves) >= (curveI + 1):
            self.message = ""
            fCurve = fCurves[curveI]
            valO = (fCurve.evaluate(frameC) + valS) * valM
            self.label = "DAW FCurve Value "+str(round(valO,2))
            # Get Keyframes and Values
            allValues = FloatList(len(fCurve.keyframe_points) * 2)
            fCurve.keyframe_points.foreach_get("co", allValues.asMemoryView())
            kFrames = DoubleList.fromValues(allValues[0::2])
            kValues = DoubleList.fromValues(allValues[1::2])
            durT = 0
            if frameC == self.trigger:
                self.notesP.clear()
                for i in range(0,len(kValues)):
                    if kValues[i] > 0 and kValues[i+1] > 0:
                        fRange = round(kFrames[i+1] - kFrames[i],3)
                        self.notesP.append([round(kFrames[i],3),fRange,round(kValues[i],3)])
            else:
                for r in self.notesP:
                    if r[0] >= frameC and r[0] < frameC+1:
                        durT = round(r[1] / bpy.context.scene.render.fps,3)

            #return valO, kFrames, kValues, self.notesP
            return valO, self.notesP, object.name.split("_")[0], durT
        else:
            self.message = "No Animation Data"
            self.label = "DAW FCurve Value"
            #return 0.0, DoubleList(), DoubleList(), self.notesP
            return 0.0, self.notesP, 0, 0
