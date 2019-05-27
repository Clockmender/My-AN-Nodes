import bpy
from bpy.props import *
from .... events import isRendering, propertyChanged
from .... base_types import AnimationNode
from .... utils.selection import getSortedSelectedObjects

enum = [('Objects','Objects','Mode','',0),
    ('Bones','Bones','Mode','',1)
    ]

class GetSelectedObjectsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetSelectedObjectsNode"
    bl_label = "Get Selected Objects"
    searchTags = ["Get Active Object"]
    bl_width_default = 200

    message: StringProperty()
    mode:   EnumProperty(name = "Mode", items = enum, update = AnimationNode.refresh)

    def draw(self, layout):
        layout.prop(self, "mode")
        if self.message is not '':
            layout.label(text = self.label, icon = "INFO")

    def create(self):
        if self.mode == 'Objects':
            self.newOutput("Object List", "Selected Objects", "selectedObjects")
        else:
            self.newOutput("Bone List", "Selected Objects", "selectedObjects")
        self.newOutput("Object", "Active Object", "activeObject")

    def execute(self):
        if isRendering():
            self.message = 'Disabled During Rendering'
            return [], None
        else:
            label = "'"+bpy.context.scene.name+"', "
            armObjName = ""
            sortedList = []
            # Get Selected Visible Objects in current View Layer.
            objsList = [ob for ob in bpy.context.view_layer.objects if ob.visible_get() and ob.select_get()]
            if self.mode == 'Objects':
                sortedList = sorted([ob for ob in objsList if ob.type != 'ARMATURE'], key=lambda x: x.name)
            else:
                # Get Pose Bone List from first Selected Armature.
                armObjs = [ob for ob in objsList if ob.type == 'ARMATURE']
                if len(armObjs) > 0:
                    # Get first Armature
                    armObj = armObjs[0]
                    armObjName = armObj.name
                    boneList = [b for b in armObj.data.bones if b.select]
                    pBoneList = []
                    for b in boneList:
                        pBoneList.append(armObj.pose.bones[b.name])
                        sortedList = sorted(pBoneList, key=lambda x: x.name)

            self.label = label+str(len(sortedList))+" "+self.mode+" "+armObjName
            return sortedList, bpy.context.view_layer.objects.active
