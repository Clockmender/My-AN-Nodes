import bpy
import bmesh
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class createCurvesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_createCurvesNode"
    bl_label = "Plot Graph in 3D View"
    bl_width_default = 180

    message1 = StringProperty("")
    message2 = StringProperty("")
    exe_b = BoolProperty(name = "Execute", default = False, update = propertyChanged)

    def create(self):
        self.newInput("Text", "Graph Name", "nam_c")
        self.newInput("Float", "Input", "val_i")
        self.newInput("Integer", "Start Frame", "frm_s")
        self.newInput("Integer", "End Frame", "frm_e")
        self.newInput("Float", "X Scale", "fac_x")
        self.newInput("Float", "Y Offset", "fac_y")
        self.newInput("Float", "Z Scale", "fac_z")

    def draw(self,layout):
        layout.prop(self, "exe_b")
        if (self.message2 != ""):
            layout.label(self.message2, icon = "INFO")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")

    def execute(self, nam_c, val_i, frm_s, frm_e, fac_x, fac_y, fac_z):
        if self.exe_b:
            self.message2 = "Processing"
            frm_p = bpy.context.scene.frame_start
            if frm_e <= frm_s or frm_s <= frm_p + 1 or fac_x == 0 or fac_z == 0 or nam_c == "":
                self.message1 = "Set Frames/Scales, etc."
            else:
                frm_c = bpy.context.scene.frame_current
                if frm_c == frm_s - 1:
                    self.message1 = "Initial Processing"
                    # Deselect All objects
                    for obj in bpy.data.objects:
                        obj.select = False
                    # Make initial object
                    mesh = bpy.data.meshes.new("mesh")  # add a new mesh
                    obj = bpy.data.objects.new(nam_c, mesh)  # add a new object using the mesh
                    scene = bpy.context.scene
                    scene.objects.link(obj)  # put the object into the scene (link)
                    scene.objects.active = obj  # set as the active object in the scene
                    obj.select = True  # select object
                    mesh = bpy.context.object.data
                    bm = bmesh.new()
                    # make the bmesh the object's mesh
                    bm.to_mesh(mesh)
                    bm.free()  # always do this when finished
                elif frm_c >= frm_s and frm_c <= frm_e:
                    self.message1 = "Building Curves"
                    # Add curve points
                    vert = ((frm_c * fac_x), fac_y, (val_i * fac_z)) # next vert made with XYZ coords
                    mesh = bpy.context.object.data
                    bm = bmesh.new()
                    # convert the current mesh to a bmesh (must be in edit mode)
                    bpy.ops.object.mode_set(mode='EDIT')
                    bm.from_mesh(mesh)
                    bpy.ops.object.mode_set(mode='OBJECT')  # return to object mode
                    bm.verts.new(vert)  # add a new vert
                    bm.verts.ensure_lookup_table() # reset table lookup
                    if len(mesh.vertices) > 1:
                        bm.edges.new((bm.verts[-1], bm.verts[-2])) # Add edge using last two verts
                    # make the bmesh the object's mesh
                    bm.to_mesh(mesh)
                    bm.free()  # always do this when finished
                elif frm_c > frm_e:
                    self.message1 = "Processing Complete"
                    self.exe_b = False # Stop node running again until user changes this
                else:
                    self.message1 = "Waiting for start frame"
        else:
            self.message2 = "Not Processing"
            self.message1 = ""
