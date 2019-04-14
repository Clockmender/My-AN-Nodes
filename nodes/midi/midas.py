import bpy
from bpy.props import *
from ... base_types import AnimationNode, DataTypeSelectorSocket
from ... events import propertyChanged
from math import pi
from mathutils import Vector, Euler, Quaternion
from . midi_functions import getNote, getIndex

enum = [('Full','Full-Fat Cream','Opperation Mode','',0),
    ('Skinny','Skinny Latte','Operation Mode','',1)
    ]

class midasNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_midasNode"
    bl_label = "Clockworx MIDAS - MIDI Animation Assistant"
    bl_width_default = 400

    assignedType: DataTypeSelectorSocket.newProperty(default = "Object List")
    locVec:  FloatVectorProperty(name="Location",subtype="XYZ",update=propertyChanged)
    rotVec:  FloatVectorProperty(name="Rotation Euler",subtype="EULER",update=propertyChanged)
    quaVec:  FloatVectorProperty(name="Rotation Quaternion",size=4,subtype="QUATERNION",default=(1.0,0.0,0.0,0.0),update=propertyChanged)
    sclVec:  FloatVectorProperty(name="Scale",subtype="XYZ",default=(1.0,1.0,1.0))
    message: StringProperty()
    label1:  StringProperty()
    label2:  StringProperty()
    label3:  StringProperty()
    label4:  StringProperty()
    noteNam: StringProperty()
    startI:  IntProperty(name="S-OCT",default=2,min=1,max=6,update=propertyChanged)
    frameC:  IntProperty(name="W-FRM",default=1,update=propertyChanged)
    fps:     FloatProperty(name="FPS",default=24,update=propertyChanged)
    factV:   FloatProperty(name="OFF",default=1,precision=3,update=propertyChanged)
    param:   FloatProperty(name="Parameter",default=1,precision=3,update=propertyChanged)
    mid_c:   BoolProperty(name = "Mid-C = C4", default = True, update = propertyChanged)
    acuVal:  BoolProperty(name = "Accumulate", default = False, update = propertyChanged)
    keyLoc:  BoolProperty(name = "Key Loc", default = True, update = propertyChanged)
    keyRot:  BoolProperty(name = "Key Rot", default = True, update = propertyChanged)
    keyScl:  BoolProperty(name = "Key Scl", default = True, update = propertyChanged)
    usePar:  BoolProperty(name = "Use Param", default = True, update = propertyChanged)
    moveT:   BoolProperty(name = "Move TL", default = True, update = propertyChanged)
    mode:    EnumProperty(name = "Mode", items = enum, update = AnimationNode.refresh)

    def draw(self, layout):
        if self.mode == 'Full':
            rowT = layout.row()
            boxT = rowT.box()
            rowE = boxT.row()
            rowE.label(text=self.label2,icon="NONE")
            rowF = boxT.row()
            rowF.label(text=self.label3,icon="NONE")

            row2 = layout.row()

            colm2 = row2.column()
            box2 = colm2.box()
            rowC = box2.row()
            rowC.label(text=self.label1,icon="NONE")
            rowD = box2.row(align=True)
            col = rowD.column()
            col.prop(self,"startI")
            col = rowD.column()
            col.prop(self,"frameC")
            col = rowD.column()
            self.invokeFunction(col, "advanceFrame", icon = "TRIA_UP")
            col = rowD.column()
            self.invokeFunction(col, "retardFrame", icon = "TRIA_DOWN")
            col = rowD.column()
            col.prop(self,"fps")
            col = rowD.column()
            col.prop(self,"factV")
            col = rowD.column()
            self.invokeFunction(col, "advanceFact", icon = "TRIA_UP")
            col = rowD.column()
            self.invokeFunction(col, "retardFact", icon = "TRIA_DOWN")
            rowK = box2.row()
            rowK.prop(self,"mid_c")
            rowK.prop(self,"acuVal")
            rowK.prop(self,"usePar")
            rowK.prop(self,"param")
            rowL = box2.row()
            rowL.prop(self,"moveT")
            rowL.prop(self,"keyLoc")
            rowL.prop(self,"keyRot")
            rowL.prop(self,"keyScl")
            rowM = box2.row()
            rowM.label(text=self.label4,icon='NONE')
            rowM.prop(self, "mode")

            colm1 = row2.column()
            box = colm1.box()
            rowA = box.row()
            rowB = box.row()
            col = rowB.column()
            col.prop(self,"locVec")
            col = rowB.column()
            col.prop(self,"rotVec")
            col = rowB.column()
            col.prop(self,"quaVec")
            col = rowB.column()
            col.prop(self,"sclVec")
            rowH = box.row()
            rowH.scale_y = 1.2
            self.invokeFunction(rowH, "resetLoc", text="Reset Location", icon="FRAME_PREV")
            self.invokeFunction(rowH, "resetRot", text="Reset Rotation", icon="FRAME_PREV")
            self.invokeFunction(rowH, "resetQua", text="Reset Quaternion", icon="FRAME_PREV")
            self.invokeFunction(rowH, "resetScl", text="Reset Scale", icon="FRAME_PREV")
        else:
            colm2 = layout.column()
            box2 = colm2.box()
            rowC = box2.row()
            rowC.label(text=self.label1,icon="NONE")
            rowD = box2.row(align=True)
            col = rowD.column()
            col.prop(self,"startI")
            col = rowD.column()
            col.prop(self,"frameC")
            col = rowD.column()
            self.invokeFunction(col, "advanceFrame", icon = "TRIA_UP")
            col = rowD.column()
            self.invokeFunction(col, "retardFrame", icon = "TRIA_DOWN")
            col = rowD.column()
            col.prop(self,"fps")
            col = rowD.column()
            col.prop(self,"factV")
            col = rowD.column()
            self.invokeFunction(col, "advanceFact", icon = "TRIA_UP")
            col = rowD.column()
            self.invokeFunction(col, "retardFact", icon = "TRIA_DOWN")
            rowK = box2.row()
            rowK.prop(self,"mid_c")
            rowK.prop(self,"acuVal")
            rowK.prop(self,"usePar")
            rowK.prop(self,"param")
            rowL = box2.row()
            rowL.prop(self,"moveT")
            rowL.prop(self,"keyLoc")
            rowL.prop(self,"keyRot")
            rowL.prop(self,"keyScl")
            rowM = box2.row()
            rowM.label(text=self.label4,icon='NONE')
            rowM.prop(self, "mode")

    def advanceFrame(self):
        offset = int(self.param) if self.usePar else 1
        self.frameC = self.frameC + offset
        if self.frameC > bpy.context.scene.frame_end:
            self.frameC = bpy.context.scene.frame_end

    def retardFrame(self):
        offset = int(self.param) if self.usePar else 1
        self.frameC = self.frameC - offset
        if self.frameC < bpy.context.scene.frame_start:
            self.frameC = bpy.context.scene.frame_start

    def advanceFact(self):
        if self.factV > 0:
            self.factV = self.factV * 2
        if self.factV > -0.002 and self.factV < 0:
            self.factV = 0.002
        elif self.factV < -0.002:
            self.factV = self.factV / 2

    def retardFact(self):
        if self.factV > 0:
            self.factV = self.factV / 2
        if self.factV < 0.001 and self.factV > 0:
            self.factV = -0.002
        elif self.factV < -0.002:
            self.factV = self.factV * 2

    def resetLoc(self):
        self.locVec = Vector((0.0,0.0,0.0))

    def resetRot(self):
        self.rotVec = Euler((0.0,0.0,0.0))

    def resetQua(self):
        self.quaVec = Quaternion((0.0,0.0,0.0,0.0))

    def resetScl(self):
        self.sclVec = Vector((0.0,0.0,0.0))

    def create(self):
        self.newInput(DataTypeSelectorSocket("Input", "input", "assignedType"))
        self.newInput("Integer","Note In","noteIn")
        self.newInput("Float","Parameter","param")

    def execute(self,input,noteIn,param):
        # Setup Node
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.65,0.85,0.65)
        if self.mode == 'Full':
            self.width = 900
        else:
            self.width = 500
        self.param = param
        offset = param if self.usePar else self.factV
        startI = self.startI * 12
        if noteIn in range(startI,startI+34):
            self.noteNam = getNote(noteIn,-12) if self.mid_c else getNote(noteIn,0)
        else:
            self.noteNam = 'Out Of Active Range'
        if self.moveT:
            bpy.context.scene.frame_current = self.frameC
        self.fps = bpy.context.scene.render.fps
        self.frameC = bpy.context.scene.frame_current

        indexName = getNote(startI,-12) if self.mid_c else getNote(startI,0)
        self.label1 = 'MIDI Note Setup, Index Note: '+indexName
        self.label4 = "Note: "+self.noteNam
        rotName = getNote(startI+12,-12) if self.mid_c else getNote(startI+12,0)
        sclName = getNote(startI+24,-12) if self.mid_c else getNote(startI+24,0)
        self.label2 = "Loc Keys= "+indexName+" + next 5 Natural | "
        self.label2 = self.label2 + "Rot Keys= "+rotName+" + next 5 Natural, w; Third Sharp | "
        self.label2 = self.label2 + "Scale Keys= "+sclName+" + next 5 Natural"
        advFac = getNote(startI+3,-12) if self.mid_c else getNote(startI+1,0)
        retFac = getNote(startI+1,-12) if self.mid_c else getNote(startI+3,0)
        addFrm = getNote(startI+10,-12) if self.mid_c else getNote(startI+6,0)
        retFrm = getNote(startI+6,-12) if self.mid_c else getNote(startI+10,0)
        insKey = getNote(startI+8,-12) if self.mid_c else getNote(startI+8,0)
        self.label3 = "Advance Factor= "+advFac+" | Retard Factor= "+retFac+" | "
        self.label3 = self.label3 + "Advance Frame= "+addFrm+" | Retard Frame= "+retFrm
        self.label3 = self.label3 + "| Insert Keyframe= "+insKey

        if len(input) > 0:
            if self.assignedType == 'Bone List':
                self.label = "MIDAS - MIDI Animation Assistant"+" Working with "+str(len(input))+" Bones"
            else:
                self.label = "MIDAS - MIDI Animation Assistant"+" Working with "+str(len(input))+" Objects"
        else:
            self.label = "Clockworx MIDAS - MIDI Animation Assistant"+" No Bones, or Selected Objects - Node is Sleeping!"
            return
        if noteIn >= startI and noteIn <= startI + 33:
            if noteIn == startI + 3:                   # Increase, or Decrease Offset
                self.advanceFact()
            elif noteIn == startI + 1:
                self.retardFact()
            elif noteIn == startI + 10:                # Advance, or retard Fact
                self.advanceFrame()
            elif noteIn == startI + 6:
                self.retardFrame()
            elif noteIn == startI:                     # Set Transform Vectors with keys (location)
                self.locVec.x = self.locVec.x - offset
            elif noteIn == startI + 2:
                self.locVec.y = self.locVec.y - offset
            elif noteIn == startI + 4:
                self.locVec.z = self.locVec.z - offset
            elif noteIn == startI + 5:
                self.locVec.x = self.locVec.x + offset
            elif noteIn == startI + 7:
                self.locVec.y = self.locVec.y + offset
            elif noteIn == startI + 9:
                self.locVec.z = self.locVec.z + offset
            elif noteIn == startI+12:                  # Set Rotation Vectors
                self.rotVec.x = self.rotVec.x - (offset * pi / 180)
                self.quaVec.x = self.quaVec.x - offset
            elif noteIn == startI + 14:
                self.rotVec.y = self.rotVec.y - (offset * pi / 180)
                self.quaVec.y = self.quaVec.y - offset
            elif noteIn == startI + 16:
                self.rotVec.z = self.rotVec.z - (offset * pi / 180)
                self.quaVec.z = self.quaVec.z - offset
            elif noteIn == startI + 15:
                self.quaVec.w = self.quaVec.w - offset
            elif noteIn == startI + 17:
                self.rotVec.x = self.rotVec.x + (offset * pi / 180)
                self.quaVec.x = self.quaVec.x + offset
            elif noteIn == startI + 19:
                self.rotVec.y = self.rotVec.y + (offset * pi / 180)
                self.quaVec.y = self.quaVec.y + offset
            elif noteIn == startI + 21:
                self.rotVec.z = self.rotVec.z + (offset * pi / 180)
                self.quaVec.z = self.quaVec.z + offset
            elif noteIn == startI + 20:
                self.quaVec.w = self.quaVec.w + offset
            elif noteIn == startI+24:                  # Set Scale Vectors
                self.sclVec.x = self.sclVec.x - offset
            elif noteIn == startI + 26:
                self.sclVec.y = self.sclVec.y - offset
            elif noteIn == startI + 28:
                self.sclVec.z = self.sclVec.z - offset
            elif noteIn == startI + 29:
                self.sclVec.x = self.sclVec.x + offset
            elif noteIn == startI + 31:
                self.sclVec.y = self.sclVec.y + offset
            elif noteIn == startI + 33:
                self.sclVec.z = self.sclVec.z + offset
            elif noteIn == startI + 8:                 # Insert keyframes
                for ob in input:
                    for i in range(0,3):
                        if self.keyLoc:
                            ob.keyframe_insert( data_path='location', index=i, frame=self.frameC )
                        if self.keyScl:
                            ob.keyframe_insert( data_path='scale', index=i, frame=self.frameC )
                        if self.keyRot:
                            if ob.rotation_mode is not 'QUATERNION':
                                ob.keyframe_insert( data_path='rotation_euler', index=i, frame=self.frameC )
                    if ob.rotation_mode == 'QUATERNION' and self.keyRot:
                        for i in range(0,4):
                            ob.keyframe_insert( data_path='rotation_quaternion', index=i, frame=self.frameC )
                return
            # Process Objects/Bones
            for ob in input:
                ob.location = ob.location+self.locVec
                if ob.rotation_mode == 'QUATERNION':
                    a = self.quaVec
                    i = ob.rotation_quaternion
                    ob.rotation_quaternion = i+a
                else:
                    a = self.rotVec
                    i = ob.rotation_euler
                    ob.rotation_euler = Euler((i[0]+a[0],i[1]+a[1],i[2]+a[2]),i.order)
                ob.scale = ob.scale+self.sclVec
            if not self.acuVal:
                self.resetLoc()
                self.resetRot()
                self.resetQua()
                self.resetScl()
        else:
            self.resetLoc()
            self.resetRot()
            self.resetQua()
            self.resetScl()

        return
