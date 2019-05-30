import bpy
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class manageDAW(bpy.types.Node, AnimationNode):
    bl_idname = "an_manageDAW"
    bl_label = "DAW Manager"
    bl_width_default = 250

    yShift  : FloatProperty(name="Cam Y Shift",default=0.2)
    zShift  : FloatProperty(name="Cam Z Shift",default=0.2)
    message : StringProperty()

    def draw(self,layout):
        colM = layout.column()
        colM.scale_y = 1.2
        if self.message is not '':
            layout.label(text=self.message,icon='ERROR')
        row = colM.row()
        row.label(text="DAW Camera Control")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "camCont",data="dn",text = "Up", icon = "EVENT_U")
        col = row.column()
        self.invokeFunction(col, "camCont",data="up",text = "Down", icon = "EVENT_D")
        col = row.column()
        self.invokeFunction(col, "camCont",data="in",text = "In", icon = "EVENT_I")
        col = row.column()
        self.invokeFunction(col, "camCont",data="out",text = "Out", icon = "EVENT_O")
        row = colM.row()
        col = row.column()
        col.prop(self,"yShift")
        col = row.column()
        col.prop(self,"zShift")
        row = colM.row()
        row.label(text="DAW Mode Control")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "viewCont",data="e", text = "Song Editor", icon = "EVENT_S")
        col = row.column()
        self.invokeFunction(col, "viewCont",data="s", text = "Track Editor", icon = "EVENT_T")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "viewCont",data="d", text = "Drum Editor", icon = "EVENT_D")
        col = row.column()
        self.invokeFunction(col, "viewCont",data="a", text = "Automation Editor", icon = "EVENT_A")

    def viewCont(self,data):
        if '.' in self.name:
            self.message = "Duplicate Manage Node"
            self.color = (1,0.3,0.3)
            return
        colList = bpy.data.collections
        if colList.get("Track Editor") is None or colList.get("Song Editor") is None:
            self.message = "Missing Required Collections"
            return
        else:
            if data == "e":
                reqList = ["Song Editor","Common","Notes & Blocks"]
                for c in colList:
                    if c.name in reqList:
                        c.hide_viewport = False
                    else:
                        c.hide_viewport = True
            elif data == "s":
                reqList = ["Track Editor","Common","Notes & Blocks"]
                for c in colList:
                    if c.name in reqList:
                        c.hide_viewport = False
                    else:
                        c.hide_viewport = True
            elif data == "d":
                reqList = ["Drum Editor","Common","Notes & Blocks"]
                for c in colList:
                    if c.name in reqList:
                        c.hide_viewport = False
                    else:
                        c.hide_viewport = True
            elif data == "a":
                reqList = ["Automation Editor","Common","Notes & Blocks"]
                for c in colList:
                    if c.name in reqList:
                        c.hide_viewport = False
                    else:
                        c.hide_viewport = True

    def camCont(self,data):
        if '.' in self.name:
            self.message = "Duplicate Manager Node"
            self.color = (1,0.3,0.3)
            return
        if bpy.data.objects.get("DAW-Cam") == None or bpy.data.cameras.get("DAW-Cam") == None:
            self.message = 'No "DAW-Cam" Object or Camera'
            return
        camObj = bpy.data.objects["DAW-Cam"]
        camCam = bpy.data.cameras["DAW-Cam"]
        if data == "up":
            camObj.location.y = camObj.location.y - self.yShift
        elif data == "dn":
            camObj.location.y = camObj.location.y + self.yShift
        elif data == "in":
            camCam.ortho_scale = camCam.ortho_scale - self.zShift
        elif data == "out":
            camCam.ortho_scale = camCam.ortho_scale + self.zShift

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        if '.' in self.name:
            self.message = "Duplicate Setup Node"
            self.color = (1,0.3,0.3)
        else:
            self.color = (1,0.8,1)
