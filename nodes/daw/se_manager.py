import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . utils_setup import getSysData

class managerSE(bpy.types.Node, AnimationNode):
    bl_idname = "an_managerSE"
    bl_label = "SE & Track Manager"
    bl_width_default = 300

    noteL    : IntProperty(name="Offset Factor.",min=1,default=16,max=64)
    veloV    : IntProperty(name="Velocity",min=10,default=100,max=127)
    veloS    : BoolProperty(name="All Selected",default=False)
    message  : StringProperty()

    def draw(self,layout):
        colM = layout.column()
        row = colM.row()
        row.label(text="Move Selected SE Block",icon="NONE")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "obMove", data = -1, text = "Left", icon = "TRIA_LEFT")
        col = row.column()
        self.invokeFunction(col, "obMove", data = 1, text = "Right", icon = "TRIA_RIGHT")
        col = row.column()
        self.invokeFunction(col, "obMove", data = 2, text = "Up", icon = "TRIA_UP")
        col = row.column()
        self.invokeFunction(col, "obMove", data = 3, text = "Down", icon = "TRIA_DOWN")
        row = colM.row()
        row.label(text="Edit Selected Block",icon="NONE")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "obMove", data = -2, text = "Duplicate Right", icon = "TRIA_RIGHT")
        col = row.column()
        self.invokeFunction(col, "obMove", data = -3, text = "Delete", confirm = True, icon = "GPBRUSH_ERASE_STROKE")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "obMove", data = 4, text = "Expand", icon = "TRIA_RIGHT")
        col = row.column()
        self.invokeFunction(col, "obMove", data = 5, text = "Contract", icon = "TRIA_LEFT")
        row = colM.row()
        row.label(text="")
        row = colM.row()
        row.prop(self,"noteL")
        row = colM.row()
        row.label(text="")
        row = colM.row()
        row.label(text="Move Selected Note",icon="NONE")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "ntMove", data = -1, text = "Left", icon = "TRIA_LEFT")
        col = row.column()
        self.invokeFunction(col, "ntMove", data = 1, text = "Right", icon = "TRIA_RIGHT")
        col = row.column()
        self.invokeFunction(col, "ntMove", data = 2, text = "Up", icon = "TRIA_UP")
        col = row.column()
        self.invokeFunction(col, "ntMove", data = 3, text = "Down", icon = "TRIA_DOWN")
        row = colM.row()
        row.label(text="Edit Selected Note",icon="NONE")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "ntMove", data = -2, text = "Duplicate Right", icon = "TRIA_RIGHT")
        col = row.column()
        self.invokeFunction(col, "ntMove", data = -3, text = "Delete", confirm = True, icon = "GPBRUSH_ERASE_STROKE")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "ntMove", data = 4, text = "Expand", icon = "TRIA_RIGHT")
        col = row.column()
        self.invokeFunction(col, "ntMove", data = 5, text = "Contract", icon = "TRIA_LEFT")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "velSet", text = "Set Velocity", icon = "RNDCURVE")
        col = row.column()
        col.prop(self,"veloS")
        col = row.column()
        col.prop(self,"veloV")
        if self.message is not '':
            layout.label(text=self.message,icon='ERROR')

    def velSet(self):
        if self.veloS:
            obs = [o for o in bpy.data.objects if o.select_get() and "Velocity" in o]
            for o in obs:
                o["Velocity"] = self.veloV
                o.dimensions.y = 0.1 * (self.veloS / 127)
        else:
            object = bpy.context.view_layer.objects.active
            object["Velocity"] = self.veloV
            object.dimensions.y = 0.1 * (self.veloS / 127)
        # Set all Notes
        for o in bpy.data.objects:
            if "Velocity" in o:
                o.dimensions.y = 0.1 * (o["Velocity"] / 127)

    def ntMove(self,data):
        if '.' in self.name:
            self.message = "Duplicate SE/Track Node"
            self.color = (1,0.3,0.3)
            return
        if self.noteL > 64:
            self.message = "Offset must be >= 64"
            return
        object = bpy.context.view_layer.objects.active
        if "Drum_" in object.name or "Note_" in object.name and "Roll" not in object.name:
            self.message = ""
            if int(data) == 2:
                object.location.y = object.location.y + (0.1 * self.noteL)
            elif int(data) == 3:
                object.location.y = object.location.y - (0.1 * self.noteL)
            elif int(data) == -3:
                bpy.data.objects.remove(object, do_unlink=True)
            elif int(data) == -2:
                colName = object.users_collection[0]
                lenN = object.dimensions.x
                objectDup = object.copy()
                objectDup.data = object.data.copy()
                colName.objects.link(objectDup)
                objectDup.location.x = object.location.x + (lenN * self.noteL)
                objectDup.select_set(state=False)
            elif int(data) == 4:
                object.dimensions.x = object.dimensions.x + (0.1 * self.noteL)
            elif int(data) == 5:
                if object.dimensions.x > (0.1 * self.noteL):
                    object.dimensions.x = object.dimensions.x - (0.1 * self.noteL)
            else:
                object.location.x = object.location.x + (int(data) * 0.1 * self.noteL)
        else:
            self.message = "Object is not Note or Drum Object"
            return

    def obMove(self,data):
        if '.' in self.name:
            self.message = "Duplicate SE/Track Node"
            self.color = (1,0.3,0.3)
            return
        object = bpy.context.view_layer.objects.active
        if "SEB_" in object.name:
            colName = object.name.split('_')[1]
            if "." in colName:
                colName = colName.split(".")[0]
        else:
            self.message = "Object is not SE Object"
            return
        if self.noteL not in [1,2,4,8,16,32,64]:
            self.message = "Offset must be 1,2,4,8,16,32 or 64"
            return
        if bpy.data.collections.get("Song Editor") is None:
            self.message = "Song Editor Collection Missing"
            return

        self.message = ""
        if int(data) == 2:
            object.location.y = object.location.y + 0.4
        elif int(data) == 3:
            object.location.y = object.location.y - 0.4
        elif int(data) == 4:
            object.dimensions.x = object.dimensions.x + (0.1 * self.noteL)
        elif int(data) == 5:
            if object.dimensions.x > (0.1 * self.noteL):
                object.dimensions.x = object.dimensions.x - (0.1 * self.noteL)
        elif int(data) < 2:
            rangO = object.dimensions.x + object.location.x
            if bpy.data.collections.get(colName) is None:
                self.message = "Matching Colection "+colName+" Not Found"
                return
            else:
                objects = [ob for ob in bpy.data.collections[colName].objects if ob.location.x > object.location.x -0.01 and ob.location.x < rangO]
            sysNoteL = getSysData(self)['NoteL']
            if int(data) > -2:
                offset = (0.1 * float(data)) * self.noteL
                object.location.x = object.location.x + offset
                for ob in objects:
                    ob.location.x = ob.location.x + offset
            elif int(data) == -2:
                # Duplicate
                offset = object.dimensions.x + (0.1*sysNoteL) + 0.05
                objectDup = object.copy()
                objectDup.data = object.data.copy()
                bpy.data.collections['Song Editor'].objects.link(objectDup)
                objectDup.location.x = object.location.x + offset
                for ob in objects:
                    obDup = ob.copy()
                    obDup.data = ob.data.copy()
                    bpy.data.collections[colName].objects.link(obDup)
                    ob.location.x = ob.location.x + offset
            elif int(data) == -3:
                bpy.data.objects.remove(object, do_unlink=True)
                for ob in objects:
                    bpy.data.objects.remove(ob, do_unlink=True)

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.message = ""
        self.color = (1,0.8,1)
        if '.' in self.name:
            self.message = "Duplicate SE/Track Node"
            self.color = (1,0.3,0.3)
        else:
            try: sysNoteL = getSysData(self)['NoteL']
            except: sysNoteL = 0
            self.label = "SE & Track Manager, Sys NoteL = 1/"+str(sysNoteL)+"th"
