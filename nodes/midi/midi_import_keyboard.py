import bpy
import os
from ... base_types import AnimationNode
from bpy.props import *
from mathutils import Matrix
from ... events import propertyChanged

class MidiImpKBNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiImpKBNode"
    bl_label = "MIDI Load Keyboards, etc."
    bl_width_default = 200

    message: StringProperty()
    bridgeLen: FloatProperty(name = "Bridge Length", min = 0.5, update = propertyChanged)
    scale_f: FloatProperty(name = "Scale Factor", min = 0.5, max = 1, update = propertyChanged)

    def draw(self,layout):
        col = layout.column()
        col.scale_y = 1.5
        self.invokeFunction(col, "impKeyb88", icon = "FILE_NEW",
            text = "Load Sys 88-Note Keyboard")
        self.invokeFunction(col, "impKeyb61", icon = "FILE_NEW",
            text = "Load Sys 61-Note Keyboard")
        self.invokeSelector(col, "PATH", "impUdae", icon = "FILE_NEW",
            text = "Load User Selected .DAE file")
        self.invokeSelector(col, "PATH", "impUobj", icon = "FILE_NEW",
            text = "Load User Selected .OBJ file")
        self.invokeFunction(col, "impFrets", icon = "FILE_NEW",
            text = "Build Fretboard")
        layout.prop(self, "bridgeLen")
        layout.prop(self, "scale_f")
        layout.label(text="Imports to Acive Collection", icon = "INFO")
        if self.message != '':
            layout.label(text = self.message, icon = "ERROR")

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.85,0.75,0.5)

    def impKeyb88(self):
        for ob in bpy.data.objects:
            ob.select_set(state=False)
        path = str(bpy.utils.user_resource('SCRIPTS', "addons")) + '/zeecee_midi/88keys.dae'
        bpy.ops.wm.collada_import(filepath=path)
        self.message = ''

    def impKeyb61(self):
        for ob in bpy.data.objects:
            ob.select_set(state=False)
        path = str(bpy.utils.user_resource('SCRIPTS', "addons")) + '/zeecee_midi/61keys.dae'
        bpy.ops.wm.collada_import(filepath=path)
        self.message = ''

    def impFrets(self):
        path = str(bpy.utils.user_resource('SCRIPTS', "addons")) + '/zeecee_midi/frets.dae'
        bpy.ops.wm.collada_import(filepath=path)
        self.message = ''
        src_obj = bpy.context.view_layer.objects.get('Base-Mesh')
        src_obj.name = 'Bridge'
        src_obj.select_set(state=True)
        src_obj.scale = (self.bridgeLen,self.bridgeLen,self.bridgeLen)
        bpy.context.view_layer.objects.active = src_obj
        bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)
        src_obj.select_set(state=False)
        scl = self.scale_f
        xLoc = src_obj.location.x
        fret = self.bridgeLen

        fretN = ['NUT','F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
            'F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24']

        for i in range (0,25):
            bpy.ops.wm.collada_import(filepath=path)
            new_obj = bpy.context.view_layer.objects.get('Base-Mesh')
            new_obj.name = fretN[i]
            new_obj.location.x = fret
            new_obj.scale.y = scl
            new_obj.select_set(state=True)
            bpy.context.view_layer.objects.active = new_obj
            bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)
            new_obj.select_set(state=False)
            fret = fret * (0.5**(1/12))
            scl = self.scale_f + (((self.bridgeLen - fret) / self.bridgeLen) * (1 - self.scale_f))

    def impUdae(self, path):
        if str(path).split(".")[1] == 'dae':
            bpy.ops.wm.collada_import(filepath=str(path))
            self.message = ''
        else:
            self.message = 'NOT DAE! ' + str(path)

    def impUobj(self, path):
        if str(path).split(".")[1] == 'obj':
            bpy.ops.import_scene.obj(filepath=path)
            self.message = ''
        else:
            self.message = 'NOT OBJ! ' + str(path)
