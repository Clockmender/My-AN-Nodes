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
    bl_width_default = 400

    mode: EnumProperty(name = "Working Plane", default = "X-Z",
        items = mode, update = AnimationNode.refresh)

    ang:     FloatProperty(name="Angle",precision=4,min=-180,max=180,update=propertyChanged)
    xValue:  FloatProperty(name="Delta Value",update=propertyChanged)
    yValue:  FloatProperty(name="Y Value",update=propertyChanged)
    zValue:  FloatProperty(name="Z Value",update=propertyChanged)
    cValue:  StringProperty(name="XYZ Coords",update=propertyChanged,default="1,1,1")
    dValue:  FloatProperty(name="Delta Value",update=propertyChanged)
    count:   IntProperty(name="Selected Vertices",min=0,update=propertyChanged)
    intV:    StringProperty(name="I-Loc")
    message: StringProperty()

    def draw(self,layout):
        row = layout.row()
        col = row.column()
        col.prop(self,"mode")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "findAngle", data = "ANGLE", text="Set Angle", icon = "EMPTY_AXIS")
        col = row.column()
        col.prop(self,"ang")
        col = row.column()
        col.prop(self,"count")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "intersect", data = "JOIN", text="Intersect L", icon = "MOD_OFFSET")
        col = row.column()
        self.invokeFunction(col, "intersect", data = "POINT", text="Intersect P", icon = "MOD_OFFSET")
        col = row.column()
        col.prop(self,"intV")
        row = layout.row()
        col = row.column()
        col.prop(self,"cValue")
        col = row.column()
        col.prop(self,"dValue")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "moveVerts", data = "DELTA", text="Move Delta", icon = "EMPTY_ARROWS")
        col = row.column()
        self.invokeFunction(col, "moveVerts", data = "ABSOLUTE", text="Move Absolute", icon = "EMPTY_ARROWS")
        col = row.column()
        self.invokeFunction(col, "moveVerts", data = "VECTOR", text="Move Delta@Angle", icon = "EMPTY_ARROWS")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "extrudeVert", data = "DELTA", text="Extrude Delta", icon = "NORMALS_VERTEX")
        col = row.column()
        self.invokeFunction(col, "extrudeVert", data = "ABSOLUTE", text="Extrude Absolute", icon = "NORMALS_VERTEX")
        col = row.column()
        self.invokeFunction(col, "extrudeVert", data = "VECTOR", text="Extrude Delta@Angle", icon = "NORMALS_VERTEX")
        row = layout.row()
        row.label(text="Cursor Tools",icon = "ORIENTATION_CURSOR")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "moveCursor", data = "DELTA", text="Delta")
        col = row.column()
        self.invokeFunction(col, "moveCursor", data = "ABSOLUTE", text="Absolute")
        col = row.column()
        self.invokeFunction(col, "moveCursor", data = "VECTOR", text="Delta@Angle")
        col = row.column()
        self.invokeFunction(col, "intersect", data = "CURSOR", text="Intersect")
        col = row.column()
        self.invokeFunction(col, "findAngle", data = "HALFWAY", text="Midpoint")
        col = row.column()
        self.invokeFunction(col, "findNormal", data = "NORMAL", text="Normal")
        if (self.message is not ""):
            layout.label(text = self.message, icon = "INFO")

    def moveCursor(self,data):
        if data == "ABSOLUTE":
            self.message = "Cursor Moved to Absolute"
            if len(self.cValue.split(",")) != 3:
                self.message = "Coords Should be like 1,2,3"
                return
            for sc in bpy.data.scenes:
                sc.cursor.location = Vector((float(self.cValue.split(",")[0]),float(self.cValue.split(",")[1]),float(self.cValue.split(",")[2])))
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
                lv1 = [v for v in bm.verts if v.select]
                if len(lv1) != 2:
                    self.message = "Select Ony 2 Vertices"
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
                    self.message = "Processed Angle"
                    self.count = len(lv1)
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
                    if round(lv1[0].co[a3],5) != round(lv1[1].co[a3],5):
                        self.message = "Points Not Planar on "+ax+" Axis"
                        return
                    # get angle of edge
                    xin = abs(lv1[0].co[a1] - lv1[1].co[a1])
                    zin = abs(lv1[0].co[a2] - lv1[1].co[a2])
                    if data == "ANGLE":
                        hyp = sqrt(xin**2 + zin**2)
                        self.ang = acos(xin/hyp) * 180 / pi
                        if othV[a1] < actV[a1] and othV[a2] > actV[a2]:
                            self.ang = 180 - self.ang
                        elif othV[a1] < actV[a1] and othV[a2] < actV[a2]:
                            self.ang = -180 + self.ang
                        elif othV[a1] > actV[a1] and othV[a2] < actV[a2]:
                            self.ang = -self.ang
                        elif othV[a1] == actV[a1] and othV[a2] > actV[a2]:
                            self.ang = 90
                        elif othV[a1] == actV[a1] and othV[a2] < actV[a2]:
                            self.ang = -90
                    elif data == "HALFWAY":
                        self.message = "Cursor moved to Midpoint"
                        if lv1[0].co.x < lv1[1].co.x:
                            xLoc = obj.matrix_world.decompose()[0].x + lv1[0].co.x + ((lv1[1].co.x - lv1[0].co.x) / 2)
                        else:
                            xLoc = obj.matrix_world.decompose()[0].x + lv1[1].co.x + ((lv1[0].co.x - lv1[1].co.x) / 2)
                        if lv1[0].co.y < lv1[1].co.y:
                            yLoc = obj.matrix_world.decompose()[0].y + lv1[0].co.y + ((lv1[1].co.y - lv1[0].co.y) / 2)
                        else:
                            yLoc = obj.matrix_world.decompose()[0].y + lv1[1].co.y + ((lv1[0].co.y - lv1[1].co.y) / 2)
                        if lv1[0].co.z < lv1[1].co.z:
                            zLoc = obj.matrix_world.decompose()[0].z + lv1[0].co.z + ((lv1[1].co.z - lv1[0].co.z) / 2)
                        else:
                            zLoc = obj.matrix_world.decompose()[0].z + lv1[1].co.z + ((lv1[0].co.z - lv1[1].co.z) / 2)
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
                        self.message = "Cursor moved to Intersect"
                        for sc in bpy.data.scenes:
                            vLoc = Vector((nx,ly,nz))
                            sc.cursor.location = vLoc + obj.matrix_world.decompose()[0]
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
                        self.message = "Extruding Vertices on "+self.mode+" Plane"
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

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.4,0.6,1)
        self.width = 400
        obj = bpy.context.view_layer.objects.active
        if obj is not None:
            self.count = len([v for v in obj.data.vertices if v.select])
