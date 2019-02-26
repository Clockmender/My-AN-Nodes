import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
from math import sin

class guitarPlayNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_guitarPlayNode"
    bl_label = "MIDI Play Guitar"
    bl_width_default = 200

    mess = StringProperty()
    suffix = StringProperty(name = 'String Suffix', update = propertyChanged)
    octS = IntProperty(name = 'Octave Shift', default = 0, min = -2, max = 2)
    sFrm = IntProperty(name = 'Note Change Frame', update = propertyChanged)
    cIdx = IntProperty(update = propertyChanged)

    def draw(self,layout):
        layout.prop(self, "suffix")
        layout.prop(self, "octS")
        if self.mess != '':
            layout.label(self.mess, icon = 'INFO')

    def create(self):
        self.newInput("Boolean", "6 String (4 String if False)", "sixBool", default = True)
        self.newInput("Object", "Finger Object", "finger")
        self.newInput("Object", "Plectrum Object", "plectrum")
        self.newInput("Float", "Nut Scale", "nutScale", minVaue = 0.7, maxValue = 1)
        self.newInput("Object List", "Control Objects", "contObjs")
        self.newInput("Generic", "String Material", "strMat")
        self.newInput("Generic", "Play Material", "plyMat")
        self.newOutput("Text", "Note, Fret & Idx", "noteFret")

    def execute(self, sixBool, finger, plectrum, nutScale, contObjs, strMat, plyMat):
        noteFret = 'None,None,0,None'
        brObj = bpy.data.objects.get('Bridge')
        nuObj = bpy.data.objects.get('NUT')
        if brObj is not None and nuObj is not None:
            dist = abs(brObj.location.x - nuObj.location.x)
        else:
            dist = 1
        if len(contObjs) == 0:
            self.mess = 'No Control Objects'
        else:
            self.mess = ''
            note_list = [
                'c0','cs0','d0','ds0','e0','f0','fs0','g0','gs0','a0','as0','b0',
                'c1','cs1','d1','ds1','e1','f1','fs1','g1','gs1','a1','as1','b1',
                'c2','cs2','d2','ds2','e2','f2','fs2','g2','gs2','a2','as2','b2',
                'c3','cs3','d3','ds3','e3','f3','fs3','g3','gs3','a3','as3','b3',
                'c4','cs4','d4','ds4','e4','f4','fs4','g4','gs4','a4','as4','b4',
                'c5','cs5','d5','ds5','e5','f5','fs5','g5','gs5','a5','as5','b5',
                'c6','cs6','d6','ds6','e6','f6','fs6','g6','gs6','a6','as6','b6',
                'c7','cs7','d7','ds7','e7','f7','fs7','g7','gs7','a7','as7','b7',
                'c8','cs8','d8','ds8','e8','f8','fs8','g8','gs8','a8','as8','b8',
                'c9','cs9','d9','ds9','e9','f9','fs9','g9']
            fretListS = [
                'NUT','F1','F2','F3','F4',
                'NUT','F1','F2','F3','F4',
                'NUT','F1','F2','F3','F4',
                'NUT','F1','F2','F3',
                'NUT','F1','F2','F3','F4',
                'NUT','F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
                'F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24']
            fretListB = [
                'NUT','F1','F2','F3','F4',
                'NUT','F1','F2','F3','F4',
                'NUT','F1','F2','F3','F4',
                'NUT','F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
                'F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24']
            if sixBool:
                for ob in [bpy.data.objects.get('El'+self.suffix),bpy.data.objects.get('A'+self.suffix),
                        bpy.data.objects.get('D'+self.suffix),bpy.data.objects.get('G'+self.suffix),
                            bpy.data.objects.get('B'+self.suffix),bpy.data.objects.get('Et'+self.suffix)]:
                    if ob is not None:
                        ob.material_slots[0].material = strMat
                    else:
                        self.mess = 'Some Strings are Missing'
                        return 'String,Error,0'
            else:
                for ob in [bpy.data.objects.get('El'+self.suffix),bpy.data.objects.get('A'+self.suffix),
                        bpy.data.objects.get('D'+self.suffix),bpy.data.objects.get('G'+self.suffix)]:
                    if ob is not None:
                        ob.material_slots[0].material = strMat
                    else:
                        self.mess = 'Some Strings are Missing!'
                        return 'String,Error,0'

            for obj in contObjs:
                zLoc = obj.location.z
                noteN = obj.name.split('_')[1]
                idx = next((i for i, x in enumerate(note_list) if x == noteN), -1)
                idx = idx + 12 + (self.octS * 12)
                if sixBool:
                    # Use 6 Strings Lead
                    if idx >= 52 and idx < 57:
                        string = 'El'+self.suffix
                    elif idx >= 57 and idx < 62:
                        string = 'A'+self.suffix
                    elif idx >= 62 and idx < 67:
                        string = 'D'+self.suffix
                    elif idx >= 67 and idx < 71:
                        string = 'G'+self.suffix
                    elif idx >= 71 and idx < 76:
                        string = 'B'+self.suffix
                    elif idx >= 76 and idx < 101:
                        string = 'Et'+self.suffix
                    else:
                        string = 'null'
                        fret = 'null'
                    # Get the Fret
                    if string != 'null':
                        fret = fretListS[idx - 52]
                else:
                    # Use 4 Strings Bass
                    if idx >= 40 and idx < 45:
                        string = 'El'+self.suffix
                    elif idx >= 45 and idx < 50:
                        string = 'A'+self.suffix
                    elif idx >= 50 and idx < 55:
                        string = 'D'+self.suffix
                    elif idx >= 55 and idx < 80:
                        string = 'G'+self.suffix
                    else:
                        string = 'null'
                        fret = 'null'
                    # Get the Fret
                    if string != 'null':
                        fret = fretListB[idx - 40]

                if string == 'null':
                    # Note is off guitar
                    strgObj = None
                    fretObj = None
                else:
                    # Move Plectrum
                    if string.split('_')[0] == 'El':
                        pObj = bpy.data.objects.get('elsP')
                    elif string.split('_')[0] == 'A':
                        pObj = bpy.data.objects.get('asP')
                    elif string.split('_')[0] == 'D':
                        pObj = bpy.data.objects.get('dsP')
                    elif string.split('_')[0] == 'G':
                        pObj = bpy.data.objects.get('gsP')
                    elif string.split('_')[0] == 'B':
                        pObj = bpy.data.objects.get('bsP')
                    elif string.split('_')[0] == 'Et':
                        pObj = bpy.data.objects.get('etsP')
                    # Set String Objects
                    strgObj = bpy.data.objects.get(string)
                    fretObj = bpy.data.objects.get(fret)

                if zLoc > 0:
                    if strgObj is not None and fretObj is not None:
                        yLoc = strgObj.location.y * nutScale
                        xLoc = fretObj.location.x
                        if fret != 'NUT':
                            finger.location = (xLoc,yLoc,(0.008* dist))
                        else:
                            finger.location.z = (0.012 * dist)
                        if pObj is not None and plectrum is not None:
                            plectrum.location = pObj.matrix_world.decompose()[0]
                            if idx is not self.cIdx:
                                self.cIdx = idx
                                self.sFrm = bpy.context.scene.frame_current
                            if bpy.context.scene.frame_current in range((self.sFrm +1), (self.sFrm + 2)):
                                plectrum.location.z = pObj.matrix_world.decompose()[0].z - (0.0015 * dist)
                            elif bpy.context.scene.frame_current == (self.sFrm + 3):
                                plectrum.location.z = pObj.matrix_world.decompose()[0].z

                        strgObj.material_slots[0].material = plyMat
                        noteFret = string+','+fret+',' + str(idx)+','+noteN

                    elif string == 'null':
                        noteFret = 'Info,Note off Guitar,' + str(idx)+','+noteN
                        self.cIdx = 0

        if noteFret == 'None,None,0,None':
            self.cIdx = 0
        return noteFret
