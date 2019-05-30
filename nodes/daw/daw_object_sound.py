import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from ... data_structures import FloatList, DoubleList, IntegerList

class objectSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_objectSound"
    bl_label = "DAW Play Sound From Object"
    bl_width_default = 200

    message : StringProperty()

    def draw(self,layout):
        if self.message is not "":
            layout.label(text=self.message,icon='INFO')

    def create(self):
        self.newInput("an_FloatSocket","Volume Factor","volF",minValue=0.01)
        self.newInput("an_ObjectSocket","Object","object")
        self.newInput("an_FloatSocket","Value Multiplier","valM",value=1,minvalue=0)
        self.newOutput("an_TextSocket","Note Name","noteName")
        self.newOutput("an_FloatSocket","Volume","volume")
        self.newOutput("an_FloatSocket","Duration","duration")
        self.newOutput("an_FloatSocket", "FCurve Value", "value")


    def execute(self,volF,object,valM):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        frameC = bpy.context.scene.frame_current
        fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
        duration = 0
        volume = 0

        #Get 1st of FCurves
        try: fCurves = list(object.animation_data.action.fcurves)
        except: fCurves = []
        if len(fCurves) == 0:
            return "",0.0,0.0,0.0
        fCurve = fCurves[0]
        value = fCurve.evaluate(frameC) + valM
        allValues = FloatList(len(fCurve.keyframe_points) * 2)
        fCurve.keyframe_points.foreach_get("co", allValues.asMemoryView())
        keyframesD = FloatList.fromValues(allValues[0::2])
        values = FloatList.fromValues(allValues[1::2])
        keyframes = [round(i,0) for i in keyframesD]

        if "_" in object.name:
            noteName = object.name.split("_")[0]
            self.message = ""
        else:
            self.message = "Not a Valid Note Object"
            return "",0.0,0.0,0.0

        # Works for integer keyframes
        if frameC in keyframes:
            indX = keyframes.index(frameC)
            if values[indX] > 0:
                nextV = keyframes[indX+1]
                if values[indX+1] > 0:
                    duration = (nextV-frameC) / fps
                    volume = values[indX] * volF
                    volume = volume if volume <= 1 else 1
        return noteName,volume,duration,value
