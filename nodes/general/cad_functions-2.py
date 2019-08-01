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

class cadFunctions2(bpy.types.Node, AnimationNode):
    bl_idname = "an_cadFunctions2"
    bl_label = "CAD Functions Mk2"
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
        self.invokeFunction(col, "twoVert", data = "ANGLE2", text="Set Angle 2", icon = "EMPTY_AXIS",
            description = "Set Angle from 2 Vertices (Last = Centre)")
        col = row.column()
        self.invokeFunction(col, "threeVert", data = "ANGLE3", text="Set Angle 3", icon = "EMPTY_AXIS",
            description = "Set Angle from 3 Vertices (Last = Centre)")
        col = row.column()
        col.prop(self,"ang")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "fourVert", data = "V-INTERSECT", text="Intersect L", icon = "MOD_OFFSET",
            description = "Intersect 4 Vertices")
        col = row.column()
        self.invokeFunction(col, "fourVert", data = "P-INTERSECT", text="Intersect P", icon = "MOD_OFFSET",
            description = "Place Vertex at Intersection of 4 vertices")
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
        self.invokeFunction(col, "multiVert", data = "V-DELTA", text="Move Delta", icon = "EMPTY_ARROWS",
            description = "Move Selected Vertices by Delta Coordinates")
        col = row.column()
        self.invokeFunction(col, "multiVert", data = "V-ABSOLUTE", text="Move Absolute", icon = "EMPTY_ARROWS",
            description = "Move Selected Vertices to Absolute Coordinates")
        col = row.column()
        self.invokeFunction(col, "multiVert", data = "V-VECTOR", text="Move Delta@Angle", icon = "EMPTY_ARROWS",
            description = "Move Selected Vertices Delta Distance at Angle")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "oneVert", data = "E-DELTA", text="Extrude Delta", icon = "NORMALS_VERTEX",
            description = "Extrude Selected Vertex by Delta Coordinates")
        col = row.column()
        self.invokeFunction(col, "oneVert", data = "E-ABSOLUTE", text="Extrude Absolute", icon = "NORMALS_VERTEX",
            description = "Extrude Selected Vertex to Absolute Coordinates")
        col = row.column()
        self.invokeFunction(col, "oneVert", data = "E-VECTOR", text="Extrude Delta@Angle", icon = "NORMALS_VERTEX",
            description = "Extrude Selected Vertex Delta Distance at Angle")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "twoVert", data = "JOIN", text="Join 2 Vertices",
            description = "Join 2 Selected Vertices to Form an Edge")
        col = row.column()
        col.prop(self,"rValue")
        col = row.column()
        self.invokeFunction(col, "oneVert", data = "E-COMMAND", icon = "EVENT_R",
            description = "Execute Command")
        row = layout.row()
        row.label(text="Cursor Tools",icon = "ORIENTATION_CURSOR")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "oneVert", data = "C-DELTA", text="Delta",
            description = "Move Cursor by Delta Coordinates")
        col = row.column()
        self.invokeFunction(col, "zeroVert", data = "C-ABSOLUTE", text="Absolute",
            description = "Move Cursor to Absolute Coordinates")
        col = row.column()
        self.invokeFunction(col, "oneVert", data = "C-VECTOR", text="Delta@Angle",
            description = "Move Cursor by Delta Value at Angle")
        col = row.column()
        self.invokeFunction(col, "fourVert", data = "C-INTERSECT", text="Intersect",
            description = "Move Cursor to Intersect of 4 Vertices")
        col = row.column()
        self.invokeFunction(col, "twoVert", data = "C-HALFWAY", text="Midpoint",
            description = "Move Cursor to Midpoint of 2 Vertices")
        col = row.column()
        self.invokeFunction(col, "threeVert", data = "C-NORMAL", text="Normal",
            description = "Move Cursor Normal to 3 Vertices (Last is Norma)")
        col = row.column()
        self.invokeFunction(col, "zeroVert", data = "C-RESTORE", text="Last",
            description = "Restore Previous Cursor Location")
        row = layout.row()
        row.label(text="Percentage Tools (Enter 1/3rd as 100/3, etc.)")
        row = layout.row()
        col = row.column()
        self.invokeFunction(col, "twoVert", data = "C-PERCENT", text="C to %",
            description = "Move Cursor to % Between 2 Vertices (From Active)")
        col = row.column()
        self.invokeFunction(col, "threeVert", data = "V-PERCENT", text="V to %",
            description = "Move Active Vertex to % Between 2 other Vertices")
        col = row.column()
        col.prop(self,"pValue")
        col = row.column()
        col.prop(self,"pFlip")

        if (self.message is not ""):
            layout.label(text = self.message, icon = "INFO")

    def checkObj(self):
        # Store Current Cursor location
        for sc in bpy.data.scenes:
            self.oldLoc[sc.name] = Vector((sc.cursor.location.x,sc.cursor.location.y,sc.cursor.location.z))
        obj = bpy.context.view_layer.objects.active
        if obj is None:
            self.message = "No Active object"
            return None,None,None,None
        if obj.mode != 'EDIT':
            self.message = "Object Must be in EDIT Mode"
            return None,None,None,None
        bm = bmesh.from_edit_mesh(obj.data)
        verts = [v for v in bm.verts if v.select]
        if len(verts) < 1:
            return None,None,None,None
        oLoc = obj.matrix_world.decompose()[0]
        self.message = "Checks Complete"
        return obj,bm,oLoc,verts

    def checkCoords(self):
        if len(self.cValue.split(",")) != 3:
            self.message = "Coords Should be Formatted as 1,2,3"
            return True
        else:
            return False

    def checkPlanar(self,bm,a3,ax):
        pvList = [round(v.co[a3],5) for v in bm.verts if v.select]
        if not all(elem == pvList[0] for elem in pvList):
            self.message = "Edges Not Planar on "+ax+" Axis"
            return True
        else:
            return False

    def checkSelection(self,num,bm):
        if len(bm.select_history) < num:
            self.message = "Make A Selection in Vertex Mode; "+str(num)+" Vertices"
            for f in bm.faces:
                f.select_set(False)
            for e in bm.edges:
                e.select_set(False)
            for v in bm.verts:
                v.select_set(False)
            bmesh.update_edit_mesh(obj.data)
            return None,None,None,None
        actE = bm.select_history[-1]
        if isinstance(actE, bmesh.types.BMVert):
            actV = actE.co
            othV = bm.select_history[-2].co
            if num == 3:
                lstV = bm.select_history[-3].co
                return actV,othV,lstV,None
            elif num == 4:
                lstV = bm.select_history[-3].co
                fstV = bm.select_history[-4].co
                return actV,othV,lstV,fstV
            else:
                return actV,othV,None,None
        else:
            self.message = "Switch to Vertex Mode"
            for f in bm.faces:
                f.select_set(False)
            for e in bm.edges:
                e.select_set(False)
            for v in bm.verts:
                v.select_set(False)
            bmesh.update_edit_mesh(obj.data)
            return None,None,None,None

    def getIntersect(self,ap1,ap2,bp1,bp2):
        s = np.vstack([ap1,ap2,bp1,bp2])
        h = np.hstack((s, np.ones((4, 1))))
        l1 = np.cross(h[0], h[1])
        l2 = np.cross(h[2], h[3])
        x, y, z = np.cross(l1, l2)
        if z == 0:
            # Parallel Lines
            self.message = "Lines Are Parallel"
            return None,None
        nx = x/z
        nz = y/z
        return nx,nz

    def getPercent(self,actV,othV):
        p1 = np.array([actV.x,actV.y,actV.z])
        p2 = np.array([othV.x,othV.y,othV.z])
        p4 = np.array([0,0,0])
        p3 = p2-p1
        if self.pFlip:
            tst = ((p4 + p3) * (self.pValue / 100)) + p1
        else:
            tst = ((p4 + p3) * ((100-self.pValue) / 100)) + p1
        return Vector((tst[0],tst[1],tst[2]))

    def modeSet(self):
        if self.mode == 'X-Y':
            a1 = 0 # H Axis
            a2 = 1 # V Axis
            a3 = 2 # Plane Axis
            ax = "Z"
            return a1,a2,a3,ax
        elif self.mode == 'X-Z':
            a1 = 0 # H Axis
            a2 = 2 # V Axis
            a3 = 1 # Plane Axis
            ax = "Y"
            return a1,a2,a3,ax
        else:
            a1 = 1 # H Axis
            a2 = 2 # V Axis
            a3 = 0 # Plane Axis
            ax = "X"
            return a1,a2,a3,ax

    def zeroVert(self,data):
        if data == "C-ABSOLUTE":
            # Set Cursor to Absolute Coords
            for sc in bpy.data.scenes:
                self.oldLoc[sc.name] = Vector((sc.cursor.location.x,sc.cursor.location.y,sc.cursor.location.z))
            if self.checkCoords():
                return
            else:
                self.message = "Placing Cursor to XYZ"
                for sc in bpy.data.scenes:
                    sc.cursor.location = Vector((float(self.cValue.split(",")[0]),float(self.cValue.split(",")[1]),float(self.cValue.split(",")[2])))
                return
        elif data == "C-RESTORE":
            # Restore Cursor Location
            self.message = "No Cursor History"
            for sc in bpy.data.scenes:
                if sc.name in self.oldLoc.keys():
                    sc.cursor.location = self.oldLoc[sc.name]
                    self.message = "Restoring Last Cursor Position"
            return
        else:
            # None Option
            return

    def oneVert(self,data):
        obj,bm,oLoc,verts = self.checkObj()
        if obj is None or bm is None or oLoc is None or verts is None:
            self.message = "No Object Selected, or not in EDIT Mode, or no Selected Vertices"
            return
        if len(verts) != 1:
            self.message = "Select Only 1 Vertex"
            return
        self.count = len(verts)
        if self.checkCoords():
            return
        else:
            dVal = self.cValue.split(",")
            dValue = self.dValue
            ang = self.ang
        if data == "C-DELTA":
            self.message = "Moving Cursor Delta from Selected Vertex"
            vLoc = verts[0].co
            dLoc = Vector((float(dVal[0]),float(dVal[1]),float(dVal[2])))
            for sc in bpy.data.scenes:
                sc.cursor.location = oLoc + dLoc + vLoc
            return
        elif data == "C-VECTOR":
            self.message = "Moving Cursor Distance@Angle"
            if self.dValue == 0:
                self.message = "Set Delta Value First"
                return
            else:
                a1,a2,a3,ax = self.modeSet()
                vLoc = Vector((verts[0].co))
                vLoc[a1] = vLoc[a1] + (self.dValue * cos(self.ang*pi/180))
                vLoc[a2] = vLoc[a2] + (self.dValue * sin(self.ang*pi/180))
                cLoc = oLoc + vLoc
                for sc in bpy.data.scenes:
                    sc.cursor.location = cLoc
                return
        elif "E-" in data:
            if data == "E-COMMAND":
                if len(self.rValue.split("=")) != 2:
                    self.message = "Command not Formatted Correctly (e.g. a=0,1,0)"
                    return
                    if self.rValue.split("=")[0] in "ad" and len(self.rValue.split("=")[1].split(",")) != 3:
                        self.message = "a/d Command not Formatted Correctly (e.g. a=0,0,0)"
                        return
                    if self.rValue.split("=")[0] == "i" and len(self.rValue.split("=")[1].split(",")) != 2:
                        self.message = "i Command not Formatted Correctly (e.g. i=0.5,30)"
                        return
                else:
                    dVal = self.rValue.split("=")[1].split(",")
                    for i in range(0,len(dVal)):
                        if dVal[i] == "":
                            dVal[i] = "0"
                    dValue = float(dVal[0])
                    ang = float(dVal[1])
            self.message = "Executing Extrude Command"
            eVert = verts[0]
            if data == "E-DELTA" or (data == "E-COMMAND" and self.rValue.split("=")[0] == "d"):
                nVert = bm.verts.new((eVert.co.x+float(dVal[0]),eVert.co.y+float(dVal[1]),eVert.co.z+float(dVal[2])))
            elif data == "E-ABSOLUTE" or (data == "E-COMMAND" and self.rValue.split("=")[0] == "a"):
                nVert = bm.verts.new((float(dVal[0]) - oLoc.x,float(dVal[1]) - oLoc.y,float(dVal[2]) - oLoc.z))
            elif data == "E-VECTOR" or (data == "E-COMMAND" and self.rValue.split("=")[0] == "i"):
                if dValue == 0:
                    self.message = "Set Delta Value First"
                    return
                else:
                    a1,a2,a3,ax = self.modeSet()
                    nVert = bm.verts.new(eVert.co)
                    nVert.co[a1] = nVert.co[a1] + (dValue * cos(ang*pi/180))
                    nVert.co[a2] = nVert.co[a2] + (dValue * sin(ang*pi/180))
            nEdge = bm.edges.new([eVert,nVert])
            eVert.select_set(False)
            nVert.select_set(True)
            bmesh.update_edit_mesh(obj.data)
            return
        else:
            # None Option
            return

    def twoVert(self,data):
        obj,bm,oLoc,verts = self.checkObj()
        if obj is None or bm is None or oLoc is None or verts is None:
            self.message = "No Object Selected, or not in EDIT Mode, or no Selected Vertices"
            return
        if len(verts) != 2:
            self.message = "Select Only 2 Vertices"
            return
        self.count = len(verts)
        actV,othV,lstV,fstV = self.checkSelection(2,bm)
        if data == "ANGLE2":
            self.message = "Setting Angle by 2 Vertices"
            if actV is None or othV is None:
                return
            else:
                a1,a2,a3,ax = self.modeSet()
                if self.checkPlanar(bm,a3,ax):
                    return
                else:
                    v0 = np.array([actV[a1]+1,actV[a2]]) - np.array([actV[a1],actV[a2]])
                    v1 = np.array([othV[a1],othV[a2]]) - np.array([actV[a1],actV[a2]])
                    self.ang = np.rad2deg(np.arctan2(np.linalg.det([v0,v1]),np.dot(v0,v1)))
                    return
        elif data == "C-HALFWAY":
            self.message = "Cursor moved to Midpoint"
            if actV is None or othV is None:
                return
            else:
                xLoc = oLoc.x + actV.x + ((othV.x - actV.x) / 2) if actV.x < othV.x else oLoc.x + othV.x + ((actV.x - othV.x) / 2)
                yLoc = oLoc.y + actV.y + ((othV.y - actV.y) / 2) if actV.y < othV.y else oLoc.y + othV.y + ((actV.y - othV.y) / 2)
                zLoc = oLoc.z + actV.z + ((othV.z - actV.z) / 2) if actV.z < othV.z else oLoc.z + othV.z + ((actV.z - othV.z) / 2)
                for sc in bpy.data.scenes:
                    sc.cursor.location = Vector((xLoc,yLoc,zLoc))
        elif data == "JOIN":
            self.message = "Joining Vertices"
            edge = bm.edges.new([verts[0],verts[1]])
            bmesh.update_edit_mesh(obj.data)
            return
        elif data == "C-PERCENT":
            self.message = "Cursor to % 2 Vertices"
            cLoc = self.getPercent(actV,othV)
            for sc in bpy.data.scenes:
                sc.cursor.location = cLoc + oLoc
            return
        else:
            # None Option
            return

    def threeVert(self,data):
        obj,bm,oLoc,verts = self.checkObj()
        if obj is None or bm is None or oLoc is None or verts is None:
            self.message = "No Object Selected, or not in EDIT Mode, or no Selected Vertices"
            return
        if len(verts) != 3:
            self.message = "Select Only 3 Vertices"
            return
        self.count = len(verts)
        actV,othV,lstV,fstV = self.checkSelection(3,bm)
        if actV is None or othV is None or lstV is None:
            return
        if data == "ANGLE3":
            self.message = "Setting Angle by 3 Vertices"
            ba = np.array([othV.x,othV.y,othV.z]) - np.array([actV.x,actV.y,actV.z])
            bc = np.array([lstV.x,lstV.y,lstV.z]) - np.array([actV.x,actV.y,actV.z])
            cosA = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            self.ang = np.degrees(np.arccos(cosA))
            return
        elif data == "C-NORMAL":
            self.message = "Setting Cursor to Normal Intersection"
            iVert = intersect_point_line(actV, othV, lstV)
            for sc in bpy.data.scenes:
                sc.cursor.location = iVert[0] + oLoc
            return
        elif data == "V-PERCENT":
            self.message = "Moved Active to % Other Two Vertices"
            cLoc = self.getPercent(othV,lstV)
            bm.select_history[-1].co = cLoc
            bmesh.update_edit_mesh(obj.data)
            return
        else:
            # None Option
            return

    def fourVert(self,data):
        obj,bm,oLoc,verts = self.checkObj()
        if obj is None or bm is None or oLoc is None or verts is None:
            self.message = "No Object Selected, or not in EDIT Mode, or no Selected Vertices"
            return
        if len(verts) != 4:
            self.message = "Select Only 4 Vertices"
            return
        self.count = len(verts)
        actV,othV,lstV,fstV = self.checkSelection(4,bm)
        if "INTERSECT" in data:
            a1,a2,a3,ax = self.modeSet()
            if self.checkPlanar(bm,a3,ax):
                return
            else:
                ap1 = (fstV[a1],fstV[a2])
                ap2 = (lstV[a1],lstV[a2])
                bp1 = (othV[a1],othV[a2])
                bp2 = (actV[a1],actV[a2])
                nx,nz = self.getIntersect(ap1,ap2,bp1,bp2)
                ly = actV.y
                self.intV = str(round(nx,5))+','+str(round(ly,5))+','+str(round(nz,5))
                if data == "C-INTERSECT":
                    self.message = "Cursor moved to Intersect"
                    for sc in bpy.data.scenes:
                        vLoc = Vector((nx,ly,nz))
                        sc.cursor.location = vLoc + obj.matrix_world.decompose()[0]
                    return
                elif data == "P-INTERSECT":
                    bm.verts.new((nx,ly,nz))
                    bmesh.update_edit_mesh(obj.data)
                elif data == "V-INTERSECT":
                    self.message = "Intersecting Edges/Vertices"
                    d1 = sqrt((nx-ap1[0])**2 + (nx-ap1[1])**2)
                    d2 = sqrt((nx-ap2[0])**2 + (nx-ap2[1])**2)
                    if d1 < d2:
                        fstV[a1] = nx
                        fstV[a2] = nz
                    else:
                        lstV[a1] = nx
                        lstV[a2] = nz
                    # Second edge
                    d1 = sqrt((nx-bp1[0])**2 + (nx-bp1[1])**2)
                    d2 = sqrt((nx-bp2[0])**2 + (nx-bp2[1])**2)
                    if d1 < d2:
                        othV[a1] = nx
                        othV[a2] = nz
                    else:
                        actV[a1] = nx
                        actV[a2] = nz
                    bmesh.update_edit_mesh(obj.data)
                    bmesh.ops.remove_doubles(bm, verts=verts, dist=0.001)
        else:
            # None Option
            return

    def multiVert(self,data):
        obj,bm,oLoc,verts = self.checkObj()
        if obj is None or bm is None or oLoc is None or verts is None:
            self.message = "No Object Selected, or not in EDIT Mode, or no Selected Vertices"
            return
        if len(verts) < 1:
            self.message = "Select 1 or More Vertices"
            return
        self.count = len(verts)
        if self.checkCoords():
            return
        else:
            dVal = self.cValue.split(",")
        if data == "V-DELTA":
            self.message = "Moving Vertices by Delta"
            for v in verts:
                v.co.x = v.co.x + float(dVal[0])
                v.co.y = v.co.y + float(dVal[1])
                v.co.z = v.co.z + float(dVal[2])
            bmesh.update_edit_mesh(obj.data)
            return
        elif data == "V-ABSOLUTE":
            self.message = "Moving Vertices To Absolute"
            for v in verts:
                v.co.x = float(dVal[0]) - oLoc.x
                v.co.y = float(dVal[1]) - oLoc.y
                v.co.z = float(dVal[2]) - oLoc.z
            bmesh.update_edit_mesh(obj.data)
            bmesh.ops.remove_doubles(bm, verts=verts, dist=0.001)
            return
        elif data == "V-VECTOR":
            self.message = "Moving Vertices by Distance@Angle"
            if self.dValue == 0:
                self.message = "Set Delta Value First"
                return
            else:
                a1,a2,a3,ax = self.modeSet()
                for v in verts:
                    v.co[a1] = v.co[a1] + (self.dValue * cos(self.ang*pi/180))
                    v.co[a2] = v.co[a2] + (self.dValue * sin(self.ang*pi/180))
                bmesh.update_edit_mesh(obj.data)
                bmesh.ops.remove_doubles(bm, verts=verts, dist=0.001)
                return
        else:
            # None Option
            return

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.4,0.6,1)
        self.width = 470
        obj = bpy.context.view_layer.objects.active
        if obj is not None:
            self.count = len([v for v in obj.data.vertices if v.select])
