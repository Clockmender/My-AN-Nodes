import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from mathutils.geometry import intersect_point_line
from mathutils import Vector
import bmesh
import numpy as np
from math import sin, cos, acos, pi, sqrt

mode = [
    ("X-Y", "X-Y", "Use X-Y Plane", "", 0),
    ("X-Z", "X-Z", "Use X-Z Plane", "", 1),
    ("Y-Z", "Y-Z", "Use Y-Z Plane", "", 2)]

class cadFunctions(bpy.types.Node, AnimationNode):
    bl_idname = "an_cadFunctions"
    bl_label = "CAD Functions"
    bl_width_default = 430

    mode: EnumProperty(name = "Working Plane", default = "X-Z",
        items = mode, update = AnimationNode.refresh)

    ang:     FloatProperty(name="Angle",precision=4,min=-180,max=180,update=propertyChanged)
    xValue:  FloatProperty(name="Delta Value",update=propertyChanged)
    yValue:  FloatProperty(name="Y Value",update=propertyChanged)
    zValue:  FloatProperty(name="Z Value",update=propertyChanged)
    cValue:  StringProperty(name="XYZ Coords",update=propertyChanged,default="0,0,0")
    rValue:  StringProperty(name="Command",update=propertyChanged,default="a=0,0,0")
    dValue:  FloatProperty(name="Delta Value",update=propertyChanged)
    pValue:  FloatProperty(name="%",min=0.01,max=99.99,update=propertyChanged)
    count:   IntProperty(name="Selected Vertices",min=0,update=propertyChanged)
    pFlip:   BoolProperty(name="Flip %",default=False,update=propertyChanged)
    intV:    StringProperty(name="I-Loc")
    oldLoc=  {}
    message: StringProperty()

    def draw(self,layout):
        row = layout.row()
        col = row.column()
        col.prop(self,"mode")
        col = row.column()
        col.prop(self,"count")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "findAngle", data = "ANGLE", text="Set Angle 2", icon = "EMPTY_AXIS",
            description = "Set Angle from 2 Vertices")
        col = row.column()
        self.invokeFunction(col, "findAngle", data = "ANGLE3", text="Set Angle 3", icon = "EMPTY_AXIS",
            description = "Set Angle from 3 Vertices (Last = Centre)")
        col = row.column()
        col.prop(self,"ang")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "intersect", data = "JOIN", text="Intersect L", icon = "MOD_OFFSET",
            description = "Intersect 2 Edges")
        col = row.column()
        self.invokeFunction(col, "intersect", data = "POINT", text="Intersect P", icon = "MOD_OFFSET",
            description = "Place Cursor at Intersection of 2 Edges")
        col = row.column()
        col.prop(self,"intV")
        row = layout.row()
        col = row.column()
        col.prop(self,"cValue")
        col = row.column()
        col.prop(self,"dValue")
        row = layout.row()
        row.label(text="Mesh Tools",icon = "NORMALS_VERTEX")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "moveVerts", data = "DELTA", text="Move Delta", icon = "EMPTY_ARROWS",
            description = "Move Selected Vertices by Delta Coordinates")
        col = row.column()
        self.invokeFunction(col, "moveVerts", data = "ABSOLUTE", text="Move Absolute", icon = "EMPTY_ARROWS",
            description = "Move Selected Vertices to Absolute Coordinates")
        col = row.column()
        self.invokeFunction(col, "moveVerts", data = "VECTOR", text="Move Delta@Angle", icon = "EMPTY_ARROWS",
            description = "Move Selected Vertices Delta Distance at Angle")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "extrudeVert", data = "DELTA", text="Extrude Delta", icon = "NORMALS_VERTEX",
            description = "Extrude Selected Vertex by Delta Coordinates")
        col = row.column()
        self.invokeFunction(col, "extrudeVert", data = "ABSOLUTE", text="Extrude Absolute", icon = "NORMALS_VERTEX",
            description = "Extrude Selected Vertex to Absolute Coordinates")
        col = row.column()
        self.invokeFunction(col, "extrudeVert", data = "VECTOR", text="Extrude Delta@Angle", icon = "NORMALS_VERTEX",
            description = "Extrude Selected Vertex Delta Distance at Angle")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "moveVerts", data = "JOIN", text="Join 2 Vertices",
            description = "Join 2 Selected Vertices with an Edge")
        col = row.column()
        col.prop(self,"rValue")
        col = row.column()
        self.invokeFunction(col, "runCommand", icon = "EVENT_R",
            description = "Execute Command")
        row = layout.row()
        row.label(text="Cursor Tools",icon = "ORIENTATION_CURSOR")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "moveCursor", data = "DELTA", text="Delta",
            description = "Move Cursor by Delta Coordinates")
        col = row.column()
        self.invokeFunction(col, "moveCursor", data = "ABSOLUTE", text="Absolute",
            description = "Move Cursor to Absolute Coordinates")
        col = row.column()
        self.invokeFunction(col, "moveCursor", data = "VECTOR", text="Delta@Angle",
            description = "Move Cursor by Delta Value at Angle")
        col = row.column()
        self.invokeFunction(col, "intersect", data = "CURSOR", text="Intersect",
            description = "Move Cursor to Intersect of 2 Edges")
        col = row.column()
        self.invokeFunction(col, "findAngle", data = "HALFWAY", text="Midpoint",
            description = "Move Cursor to Midpoint of 2 Vertices")
        col = row.column()
        self.invokeFunction(col, "findNormal", data = "NORMAL", text="Normal",
            description = "Move Cursor Normal to 3 Vertices")
        col = row.column()
        self.invokeFunction(col, "moveCursor", data = "RESTORE", text="Last",
            description = "Restore Previous Cursor Location")
        row = layout.row()
        row.label(text="Percentage Tools")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "moveCursor", data = "PERCENT", text="C to %",
            description = "Move Cursor to % Between 2 Vertices")
        col = row.column()
        self.invokeFunction(col, "moveCursor", data = "PERCENTMV", text="V to %",
            description = "Move Vertex to % Between 2 other Vertices")
        col = row.column()
        col.prop(self,"pValue")
        col = row.column()
        col.prop(self,"pFlip")

        if (self.message is not ""):
            layout.label(text = self.message, icon = "INFO")

    #def create(self):
    #    self.newOutput("an_GenericSocket","Cursor","cursor")

    def moveCursor(self,data):
        if data != "RESTORE":
            for sc in bpy.data.scenes:
                self.oldLoc[sc.name] = Vector((sc.cursor.location.x,sc.cursor.location.y,sc.cursor.location.z))
        if data == "ABSOLUTE":
            self.message = "Cursor Moved to Absolute"
            if len(self.cValue.split(",")) != 3:
                self.message = "Coords Should be like 1,2,3"
                return
            for sc in bpy.data.scenes:
                sc.cursor.location = Vector((float(self.cValue.split(",")[0]),float(self.cValue.split(",")[1]),float(self.cValue.split(",")[2])))
            return
        elif data == "RESTORE":
            self.message = "No Cursor History"
            for sc in bpy.data.scenes:
                if sc.name in self.oldLoc.keys():
                    sc.cursor.location = self.oldLoc[sc.name]
                    self.message = "Restoring Last Cursor Position"
        elif data == "PERCENT" or data == "PERCENTMV":
            obj = bpy.context.view_layer.objects.active
            if obj is None:
                self.message = "No Active object"
                return
            if obj.mode != 'EDIT':
                self.message = "Object Must be in EDIT Mode"
                return
            oLoc = obj.matrix_world.decompose()[0]
            bm = bmesh.from_edit_mesh(obj.data)
            verts = [v for v in bm.verts if v.select]
            self.count = len(verts)
            if data == "PERCENT":
                if len(verts) != 2:
                    self.message = "Select Only 2 Vertices"
                    return
                self.message = "Cursor to % 2 Vertices"
                p1 = np.array([verts[0].co.x,verts[0].co.y,verts[0].co.z])
                p2 = np.array([verts[1].co.x,verts[1].co.y,verts[1].co.z])
                p4 = np.array([0,0,0])
                p3 = p2-p1
                if self.pFlip:
                    tst = ((p4 + p3) * ((100-self.pValue) / 100)) + p1
                else:
                    tst = ((p4 + p3) * (self.pValue / 100)) + p1
                v3 = Vector((tst[0],tst[1],tst[2])) + oLoc
                for sc in bpy.data.scenes:
                    sc.cursor.location = v3
                return
            else:
                if len(verts) != 3:
                    self.message = "Select Only 3 Vertices"
                    return
                self.message = "Move to % 2 Vertices"
                if len(bm.select_history) < 3:
                    self.message = "Make A Selection in Vertex Mode"
                    for f in bm.faces:
                        f.select_set(False)
                    for e in bm.edges:
                        e.select_set(False)
                    for v in bm.verts:
                        v.select_set(False)
                    bmesh.update_edit_mesh(obj.data)
                    return
                else:
                    v1 = bm.select_history[-3]
                    v2 = bm.select_history[-2]
                    v3 = bm.select_history[-1]
                    p1 = np.array([v1.co.x,v1.co.y,v1.co.z])
                    p2 = np.array([v2.co.x,v2.co.y,v2.co.z])
                    p4 = np.array([0,0,0])
                    p3 = p2-p1
                    if self.pFlip:
                        tst = ((p4 + p3) * ((100-self.pValue) / 100)) + p1
                    else:
                        tst = ((p4 + p3) * (self.pValue / 100)) + p1
                    v4 = Vector((tst[0],tst[1],tst[2]))# + oLoc
                    v3.co = v4
                    bmesh.update_edit_mesh(obj.data)
                    return
        elif data == "DELTA":
            obj = bpy.context.view_layer.objects.active
            if obj is None:
                self.message = "No Active object"
                return
            if len(self.cValue.split(",")) != 3:
                self.message = "Coords Should be like 1,2,3"
                return
            if obj.mode != 'EDIT':
                self.message = "Object Must be in EDIT Mode"
                return
            oLoc = obj.matrix_world.decompose()[0]
            bm = bmesh.from_edit_mesh(obj.data)
            verts = [v for v in bm.verts if v.select]
            self.count = len(verts)
            if len(verts) != 1:
                self.message = "Select Only 1 Vertex"
                return
            self.message = "Cursor Moved by Delta"
            vLoc = verts[0].co
            dLoc = Vector((float(self.cValue.split(",")[0]),float(self.cValue.split(",")[1]),float(self.cValue.split(",")[2])))
            for sc in bpy.data.scenes:
                sc.cursor.location = oLoc + dLoc + vLoc
            return
        elif data == "VECTOR":
            obj = bpy.context.view_layer.objects.active
            if obj is None:
                self.message = "No Active object"
                return
            if obj.mode != 'EDIT':
                self.message = "Object Must be in EDIT Mode"
                return
            oLoc = obj.matrix_world.decompose()[0]
            bm = bmesh.from_edit_mesh(obj.data)
            verts = [v for v in bm.verts if v.select]
            self.count = len(verts)
            if len(verts) != 1:
                self.message = "Select Only 1 Vertex"
                return
            vLoc = Vector((verts[0].co))
            if self.mode == 'X-Y':
                a1 = 0 # H Axis
                a2 = 1 # V Axis
                a3 = 2 # Plane Axis
            elif self.mode == 'X-Z':
                a1 = 0 # H Axis
                a2 = 2 # V Axis
                a3 = 1 # Plane Axis
            else:
                a1 = 1 # H Axis
                a2 = 2 # V Axis
                a3 = 0 # Plane Axis
            self.message = "Cursor Moved Delta@Angle on "+self.mode+" Plane"
            if self.ang == 0:
                vLoc[a1] = vLoc[a1] + self.dValue
            elif self.ang == 90:
                vLoc[a2] = vLoc[a2] + self.dValue
            elif self.ang == 180 or self.ang == -180:
                vLoc[a1] = vLoc[a1] - self.dValue
            elif self.ang == -90:
                vLoc[a2] = vLoc[a2] - self.dValue
            elif self.ang > 0 and self.ang < 90:
                vLoc[a1] = vLoc[a1] + (self.dValue* abs(cos(self.ang*pi/180)))
                vLoc[a2] = vLoc[a2] + (self.dValue * abs(sin(self.ang*pi/180)))
            elif self.ang > 90 and self.ang < 180:
                vLoc[a1] = vLoc[a1] - (self.dValue * abs(cos(self.ang*pi/180)))
                vLoc[a2] = vLoc[a2] + (self.dValue * abs(sin(self.ang*pi/180)))
            elif self.ang < 0 and self.ang > -90:
                vLoc[a1] = vLoc[a1] + (self.dValue * abs(cos(self.ang*pi/180)))
                vLoc[a2] = vLoc[a2] - (self.dValue * abs(sin(self.ang*pi/180)))
            elif self.ang < -90 and self.ang > -180:
                vLoc[a1] = vLoc[a1] - (self.dValue * abs(cos(self.ang*pi/180)))
                vLoc[a2] = vLoc[a2] - (self.dValue * abs(sin(self.ang*pi/180)))
            cLoc = oLoc + vLoc
            for sc in bpy.data.scenes:
                sc.cursor.location = cLoc
            return

    def findNormal(self,data):
        obj = bpy.context.view_layer.objects.active
        if obj is None:
            self.message = "No Active object"
            return
        else:
            if obj.mode != 'EDIT':
                self.message = "Object Must be in EDIT Mode"
                return
            else:
                bm = bmesh.from_edit_mesh(obj.data)
                verts = [v for v in bm.verts if v.select]
                self.count = len(verts)
                if len(verts) != 3:
                    self.message = "Select Only 3 Vertices"
                    return
                elif len(bm.select_history) < 3:
                    self.message = "Make A Selection in Vertex Mode"
                    for f in bm.faces:
                        f.select_set(False)
                    for e in bm.edges:
                        e.select_set(False)
                    for v in bm.verts:
                        v.select_set(False)
                    bmesh.update_edit_mesh(obj.data)
                    return
                else:
                    if data == "NORMAL":
                        for sc in bpy.data.scenes:
                            self.oldLoc[sc.name] = Vector((sc.cursor.location.x,sc.cursor.location.y,sc.cursor.location.z))
                        oVert = bm.select_history[-3]
                        vVert = bm.select_history[-2]
                        pVert = bm.select_history[-1]
                        iVert = intersect_point_line(pVert.co, oVert.co, vVert.co)
                        self.message = "Cursor Moved to Normal Intersect"
                        for sc in bpy.data.scenes:
                            sc.cursor.location = iVert[0] + obj.matrix_world.decompose()[0]
                        return

    def findAngle(self,data):
        obj = bpy.context.view_layer.objects.active
        if obj is None:
            self.message = "No Active object"
            return
        else:
            if obj.mode != 'EDIT':
                self.message = "Object Must be in EDIT Mode"
                return
            else:
                bm = bmesh.from_edit_mesh(obj.data)
                verts = [v for v in bm.verts if v.select]
                if data != "ANGLE3" and len(verts) != 2:
                    self.message = "Select Only 2 Vertices"+data
                    return
                elif data == "ANGLE3":
                    if len(verts) != 3:
                        self.message = "Select Only 3 Vertices"
                        return
                    elif len(bm.select_history) < 3:
                        self.message = "Make A Selection in Vertex Mode"
                        for f in bm.faces:
                            f.select_set(False)
                        for e in bm.edges:
                            e.select_set(False)
                        for v in bm.verts:
                            v.select_set(False)
                        bmesh.update_edit_mesh(obj.data)
                        return
                    else:
                        self.message = "Setting Angle to 3 Vertices"
                        self.count = len(verts)
                        a = np.array([bm.select_history[-3].co.x,bm.select_history[-3].co.y,bm.select_history[-3].co.z])
                        b = np.array([bm.select_history[-1].co.x,bm.select_history[-1].co.y,bm.select_history[-1].co.z])
                        c = np.array([bm.select_history[-2].co.x,bm.select_history[-2].co.y,bm.select_history[-2].co.z])
                        ba = a - b
                        bc = c - b
                        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
                        self.ang = np.degrees(np.arccos(cosine_angle))
                        return
                else:
                    if self.mode == 'X-Y':
                        a1 = 0 # H Axis
                        a2 = 1 # V Axis
                        a3 = 2 # Plane Axis
                        ax = "Z"
                    elif self.mode == 'X-Z':
                        a1 = 0 # H Axis
                        a2 = 2 # V Axis
                        a3 = 1 # Plane Axis
                        ax = "Y"
                    else:
                        a1 = 1 # H Axis
                        a2 = 2 # V Axis
                        a3 = 0 # Plane Axis
                        ax = "X"
                    self.message = "Setting Angle to 2 Vertices"
                    self.count = len(verts)
                    if len(bm.select_history) < 2:
                        self.message = "Make A Selection in Vertex Mode"
                        for f in bm.faces:
                            f.select_set(False)
                        for e in bm.edges:
                            e.select_set(False)
                        for v in bm.verts:
                            v.select_set(False)
                        bmesh.update_edit_mesh(obj.data)
                        return
                    actE = bm.select_history[-2]
                    if isinstance(actE, bmesh.types.BMVert):
                        actV = actE.co
                        othV = bm.select_history[-1].co
                    else:
                        self.message = "Switch to Vertex Select"
                        for f in bm.faces:
                            f.select_set(False)
                        for e in bm.edges:
                            e.select_set(False)
                        for v in bm.verts:
                            v.select_set(False)
                        bmesh.update_edit_mesh(obj.data)
                        return
                    # Check Planar
                    if round(verts[0].co[a3],5) != round(verts[1].co[a3],5):
                        self.message = "Points Not Planar on "+ax+" Axis"
                        return
                    if data == "ANGLE":
                        # get angle of edge
                        p0 = [othV[a1]+1,othV[a2]]
                        p1 = [othV[a1],othV[a2]]
                        p2 = [actV[a1],actV[a2]]
                        v0 = np.array(p0) - np.array(p1)
                        v1 = np.array(p2) - np.array(p1)
                        self.ang = np.rad2deg(np.arctan2(np.linalg.det([v0,v1]),np.dot(v0,v1)))
                        return
                    elif data == "HALFWAY":
                        self.message = "Cursor moved to Midpoint"
                        for sc in bpy.data.scenes:
                            self.oldLoc[sc.name] = Vector((sc.cursor.location.x,sc.cursor.location.y,sc.cursor.location.z))
                        if verts[0].co.x < verts[1].co.x:
                            xLoc = obj.matrix_world.decompose()[0].x + verts[0].co.x + ((verts[1].co.x - verts[0].co.x) / 2)
                        else:
                            xLoc = obj.matrix_world.decompose()[0].x + verts[1].co.x + ((verts[0].co.x - verts[1].co.x) / 2)
                        if verts[0].co.y < verts[1].co.y:
                            yLoc = obj.matrix_world.decompose()[0].y + verts[0].co.y + ((verts[1].co.y - verts[0].co.y) / 2)
                        else:
                            yLoc = obj.matrix_world.decompose()[0].y + verts[1].co.y + ((verts[0].co.y - verts[1].co.y) / 2)
                        if verts[0].co.z < verts[1].co.z:
                            zLoc = obj.matrix_world.decompose()[0].z + verts[0].co.z + ((verts[1].co.z - verts[0].co.z) / 2)
                        else:
                            zLoc = obj.matrix_world.decompose()[0].z + verts[1].co.z + ((verts[0].co.z - verts[1].co.z) / 2)
                        for sc in bpy.data.scenes:
                            sc.cursor.location = Vector((xLoc,yLoc,zLoc))

    def intersect(self,data):
        obj = bpy.context.view_layer.objects.active
        if obj is None:
            self.message = "No Active object"
            return
        else:
            if obj.mode != 'EDIT':
                self.message = "Object Must be in EDIT Mode"
                return
            else:
                bm = bmesh.from_edit_mesh(obj.data)
                edges = [e for e in bm.edges if e.select]
                if len(edges) != 2:
                    self.message = "Select Ony 2 Edges"
                    return
                else:
                    if self.mode == 'X-Y':
                        a1 = 0 # H Axis
                        a2 = 1 # V Axis
                        a3 = 2 # Plane Axis
                        ax = "Z"
                    elif self.mode == 'X-Z':
                        a1 = 0 # H Axis
                        a2 = 2 # V Axis
                        a3 = 1 # Plane Axis
                        ax = "Y"
                    else:
                        a1 = 1 # H Axis
                        a2 = 2 # V Axis
                        a3 = 0 # Plane Axis
                        ax = "X"
                    # Check Planar
                    pvList = [round(v.co[a3],5) for v in bm.verts if v.select]
                    if not all(elem == pvList[0] for elem in pvList):
                        self.message = "Edges Not Planar on "+ax+" Axis"
                        return
                    self.message = "Processed Intersect"
                    self.count = len(edges) * 2
                    # Extend/trim to intersect
                    lv1 = edges[0].verts
                    lv2 = edges[1].verts
                    ap1 = (lv1[0].co[a1],lv1[0].co[a2])
                    ly = lv1[0].co[a3]
                    ap2 = (lv1[1].co[a1],lv1[1].co[a2])
                    bp1 = (lv2[0].co[a1],lv2[0].co[a2])
                    bp2 = (lv2[1].co[a1],lv2[1].co[a2])
                    # Get Intersection
                    s = np.vstack([ap1,ap2,bp1,bp2])
                    h = np.hstack((s, np.ones((4, 1))))
                    l1 = np.cross(h[0], h[1])
                    l2 = np.cross(h[2], h[3])
                    x, y, z = np.cross(l1, l2)
                    if z == 0:
                        # Parallel Lines
                        self.message = "Lines Are Parallel"
                        return
                    nx = x/z
                    nz = y/z
                    self.intV = str(round(nx,5))+','+str(round(ly,5))+','+str(round(nz,5))
                    # Get nearest vertex for each edge
                    if data == "JOIN":
                        d1 = sqrt((nx-ap1[0])**2 + (nx-ap1[1])**2)
                        d2 = sqrt((nx-ap2[0])**2 + (nx-ap2[1])**2)
                        if d1 < d2:
                            lv1[0].co[a1] = nx
                            lv1[0].co[a2] = nz
                        else:
                            lv1[1].co[a1] = nx
                            lv1[1].co[a2] = nz
                        # Second edge
                        d1 = sqrt((nx-bp1[0])**2 + (nx-bp1[1])**2)
                        d2 = sqrt((nx-bp2[0])**2 + (nx-bp2[1])**2)
                        if d1 < d2:
                            lv2[0].co[a1] = nx
                            lv2[0].co[a2] = nz
                        else:
                            lv2[1].co[a1] = nx
                            lv2[1].co[a2] = nz
                    elif data == "POINT":
                        bm.verts.new((nx,ly,nz))
                    elif data == "CURSOR":
                        for sc in bpy.data.scenes:
                            self.oldLoc[sc.name] = Vector((sc.cursor.location.x,sc.cursor.location.y,sc.cursor.location.z))
                        self.message = "Cursor moved to Intersect"
                        for sc in bpy.data.scenes:
                            vLoc = Vector((nx,ly,nz))
                            sc.cursor.location = vLoc + obj.matrix_world.decompose()[0]
                        return
                    bmesh.update_edit_mesh(obj.data)
                    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.001)

    def moveVerts(self,data):
        obj = bpy.context.view_layer.objects.active
        if obj is None:
            self.message = "No Active object"
            return
        else:
            if obj.mode != 'EDIT':
                self.message = "Object Must be in EDIT Mode"
                return
            else:
                bm = bmesh.from_edit_mesh(obj.data)
                verts = [v for v in bm.verts if v.select]
                self.count = len(verts)
                if data == "JOIN":
                    if len(verts) != 2:
                        self.message = "Select Ony 2 Vertices"
                        return
                    else:
                        self.message = "Joining Vertices"
                        edge = bm.edges.new([verts[0],verts[1]])
                        bmesh.update_edit_mesh(obj.data)
                        return
                if len(verts) == 0:
                    self.message = "No Vertices Selected"
                    return
                else:
                    if len(self.cValue.split(",")) != 3:
                        self.message = "Coords Should be like 1,2,3"
                        return
                    xValue = float(self.cValue.split(",")[0])
                    yValue = float(self.cValue.split(",")[1])
                    zValue = float(self.cValue.split(",")[2])
                    if data == "DELTA":
                        self.message = "Moving Vertices by Delta"
                        for v in verts:
                            v.co.x = v.co.x + xValue
                            v.co.y = v.co.y + yValue
                            v.co.z = v.co.z + zValue
                    elif data == "ABSOLUTE":
                        self.message = "Moving Vertices To Absolute"
                        for v in verts:
                            v.co.x = xValue - obj.location.x
                            v.co.y = yValue - obj.location.y
                            v.co.z = zValue - obj.location.z
                    elif data == "VECTOR":
                        if self.mode == 'X-Y':
                            a1 = 0 # H Axis
                            a2 = 1 # V Axis
                            a3 = 2 # Plane Axis
                        elif self.mode == 'X-Z':
                            a1 = 0 # H Axis
                            a2 = 2 # V Axis
                            a3 = 1 # Plane Axis
                        else:
                            a1 = 1 # H Axis
                            a2 = 2 # V Axis
                            a3 = 0 # Plane Axis
                        self.message = "Moving Vertices Delta@Angle on "+self.mode+" Plane"
                        if self.ang == 0:
                            for v in verts:
                                v.co[a1] = v.co[a1] + self.dValue
                        elif self.ang == 90:
                            for v in verts:
                                v.co[a2] = v.co[a2] + dValue
                        elif self.ang == 180 or self.ang == -180:
                            for v in verts:
                                v.co[a1] = v.co[a1] - self.dValue
                        elif self.ang == -90:
                            for v in verts:
                                v.co[a2] = v.co[a2] - self.dValue
                        elif self.ang > 0 and self.ang < 90:
                            for v in verts:
                                v.co[a1] = v.co[a1] + (self.dValue* abs(cos(self.ang*pi/180)))
                                v.co[a2] = v.co[a2] + (self.dValue * abs(sin(self.ang*pi/180)))
                        elif self.ang > 90 and self.ang < 180:
                            for v in verts:
                                v.co[a1] = v.co[a1] - (self.dValue * abs(cos(self.ang*pi/180)))
                                v.co[a2] = v.co[a2] + (self.dValue * abs(sin(self.ang*pi/180)))
                        elif self.ang < 0 and self.ang > -90:
                            for v in verts:
                                v.co[a1] = v.co[a1] + (self.dValue * abs(cos(self.ang*pi/180)))
                                v.co[a2] = v.co[a2] - (self.dValue * abs(sin(self.ang*pi/180)))
                        elif self.ang < -90 and self.ang > -180:
                            for v in verts:
                                v.co[a1] = v.co[a1] - (self.dValue * abs(cos(self.ang*pi/180)))
                                v.co[a2] = v.co[a2] - (self.dValue * abs(sin(self.ang*pi/180)))
                    bmesh.update_edit_mesh(obj.data)
                    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.001)

    def extrudeVert(self,data):
        obj = bpy.context.view_layer.objects.active
        if obj is None:
            self.message = "No Active object"
            return
        else:
            if obj.mode != 'EDIT':
                self.message = "Object Must be in EDIT Mode"
                return
            else:
                bm = bmesh.from_edit_mesh(obj.data)
                verts = [v for v in bm.verts if v.select]
                self.count = len(verts)
                if len(verts) != 1:
                    self.message = "Select Only 1 Vertex"
                    return
                else:
                    self.message = "Extruding Vertex"
                    if len(self.cValue.split(",")) != 3:
                        self.message = "Coords Should be like 1,2,3"
                        return
                    xValue = float(self.cValue.split(",")[0])
                    yValue = float(self.cValue.split(",")[1])
                    zValue = float(self.cValue.split(",")[2])
                    eVert = verts[0]
                    if data == "DELTA":
                        nVert = bm.verts.new((eVert.co.x+xValue,eVert.co.y+yValue,eVert.co.z+zValue))
                    elif data == "ABSOLUTE":
                        nVert = bm.verts.new((xValue - obj.location.x,yValue - obj.location.y,zValue - obj.location.z))
                    elif data == "VECTOR":
                        if self.mode == 'X-Y':
                            a1 = 0 # H Axis
                            a2 = 1 # V Axis
                            a3 = 2 # Plane Axis
                        elif self.mode == 'X-Z':
                            a1 = 0 # H Axis
                            a2 = 2 # V Axis
                            a3 = 1 # Plane Axis
                        else:
                            a1 = 1 # H Axis
                            a2 = 2 # V Axis
                            a3 = 0 # Plane Axis
                        self.message = "Extruding Vertex on "+self.mode+" Plane"
                        if self.ang == 0:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a1] = nVert.co[a1] + self.dValue
                        elif self.ang == 90:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a2] = nVert.co[a2] + self.dValue
                        elif self.ang == 180 or self.ang == -180:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a1] = nVert.co[a1] - self.dValue
                        elif self.ang == -90:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a2] = nVert.co[a2] - self.dValue
                        elif self.ang > 0 and self.ang < 90:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a1] = nVert.co[a1] + (self.dValue * abs(cos(self.ang*pi/180)))
                            nVert.co[a2] = nVert.co[a2] + (self.dValue * abs(sin(self.ang*pi/180)))
                        elif self.ang > 90 and self.ang < 180:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a1] = nVert.co[a1] - (self.dValue * abs(cos(self.ang*pi/180)))
                            nVert.co[a2] = nVert.co[a2] + (self.dValue * abs(sin(self.ang*pi/180)))
                        elif self.ang < 0 and self.ang > -90:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a1] = nVert.co[a1] + (self.dValue * abs(cos(self.ang*pi/180)))
                            nVert.co[a2] = nVert.co[a2] - (self.dValue * abs(sin(self.ang*pi/180)))
                        elif self.ang < -90 and self.ang > -180:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a1] = nVert.co[a1] - (self.dValue * abs(cos(self.ang*pi/180)))
                            nVert.co[a2] = nVert.co[a2] - (self.dValue * abs(sin(self.ang*pi/180)))
                    nEdge = bm.edges.new([eVert,nVert])
                    eVert.select_set(False)
                    nVert.select_set(True)
                    bmesh.update_edit_mesh(obj.data)

    def runCommand(self):
        obj = bpy.context.view_layer.objects.active
        if obj is None:
            self.message = "No Active object"
            return
        else:
            if obj.mode != 'EDIT':
                self.message = "Object Must be in EDIT Mode"
                return
            else:
                bm = bmesh.from_edit_mesh(obj.data)
                verts = [v for v in bm.verts if v.select]
                self.count = len(verts)
                if len(verts) != 1:
                    self.message = "Select Only 1 Vertex"
                    return
                else:
                    self.message = "Extruding Vertex"
                    if len(self.rValue.split("=")) != 2:
                        self.message = "Command not Formatted Correctly (xy=0,0,0) for example"
                        return
                        if self.rValue.split("=")[0] != "di" and len(self.rValue.split("=")[1].split(",")) != 3:
                            self.message = "XY/DX Command not Formatted Correctly (xy=0,0,0) for example"
                            return
                        if self.rValue.split("=")[0] == "di" and len(self.rValue.split("=")[1].split(",")) != 2:
                            self.message = "DI Command not Formatted Correctly (di=0.5,30) for example"
                            return
                    eVert = verts[0]
                    if self.rValue.split("=")[0] == "a":
                        # Absolute XYZ
                        nVert = bm.verts.new((float(self.rValue.split("=")[1].split(",")[0])-obj.location.x,
                            float(self.rValue.split("=")[1].split(",")[1])-obj.location.y,
                            float(self.rValue.split("=")[1].split(",")[2])-obj.location.z))
                    elif self.rValue.split("=")[0] == "d":
                        # Delta XYZ
                        nVert = bm.verts.new((float(self.rValue.split("=")[1].split(",")[0])+eVert.co.x,
                            float(self.rValue.split("=")[1].split(",")[1])+eVert.co.y,
                            float(self.rValue.split("=")[1].split(",")[2])+eVert.co.z))
                    elif self.rValue.split("=")[0] == "i":
                        # Distance @ Angle
                        dis = float(self.rValue.split("=")[1].split(",")[0])
                        ang = float(self.rValue.split("=")[1].split(",")[1])
                        if self.mode == 'X-Y':
                            a1 = 0 # H Axis
                            a2 = 1 # V Axis
                            a3 = 2 # Plane Axis
                        elif self.mode == 'X-Z':
                            a1 = 0 # H Axis
                            a2 = 2 # V Axis
                            a3 = 1 # Plane Axis
                        else:
                            a1 = 1 # H Axis
                            a2 = 2 # V Axis
                            a3 = 0 # Plane Axis
                        self.message = "Extruding Vertex on "+self.mode+" Plane"
                        if ang == 0:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a1] = nVert.co[a1] + dis
                        elif ang == 90:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a2] = nVert.co[a2] + dis
                        elif ang == 180 or ang == -180:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a1] = nVert.co[a1] - dis
                        elif ang == -90:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a2] = nVert.co[a2] - dis
                        elif ang > 0 and ang < 90:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a1] = nVert.co[a1] + (dis * abs(cos(ang*pi/180)))
                            nVert.co[a2] = nVert.co[a2] + (dis * abs(sin(ang*pi/180)))
                        elif ang > 90 and ang < 180:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a1] = nVert.co[a1] - (dis * abs(cos(ang*pi/180)))
                            nVert.co[a2] = nVert.co[a2] + (dis * abs(sin(ang*pi/180)))
                        elif ang < 0 and ang > -90:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a1] = nVert.co[a1] + (dis * abs(cos(ang*pi/180)))
                            nVert.co[a2] = nVert.co[a2] - (dis * abs(sin(ang*pi/180)))
                        elif ang < -90 and ang > -180:
                            nVert = bm.verts.new(eVert.co)
                            nVert.co[a1] = nVert.co[a1] - (dis * abs(cos(ang*pi/180)))
                            nVert.co[a2] = nVert.co[a2] - (dis * abs(sin(ang*pi/180)))
                    else:
                        self.message = "Only xy= dx= & di= Permitted as Commands"
                        return
                    nEdge = bm.edges.new([eVert,nVert])
                    eVert.select_set(False)
                    nVert.select_set(True)
                    bmesh.update_edit_mesh(obj.data)

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.4,0.6,1)
        self.width = 450
        obj = bpy.context.view_layer.objects.active
        if obj is not None:
            self.count = len([v for v in obj.data.vertices if v.select])
        #return self.oldLoc
