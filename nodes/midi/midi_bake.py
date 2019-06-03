import bpy
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures import DoubleList
from ... events import propertyChanged
from ... utils.sequence_editor import getOrCreateSequencer, getEmptyChannel
from ... utils.path import getAbsolutePathOfSound
from . midi_functions import getNote, getIndex

dataD = {}
eventD = {}

class MidiNoteData(bpy.types.PropertyGroup):
    noteName  : StringProperty()
    noteIndex : IntProperty()
    # This value can be keyframed.
    value     : FloatProperty()

class MidiBakeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiBakeNode"
    bl_label = "MIDI Bake Controls"
    bl_width_default = 300

    midC         : BoolProperty(name = "Middle C = C4", default = True, update = propertyChanged)
    useV         : BoolProperty(name = "Use MIDI Velocity", default = False, update = propertyChanged)
    squV         : BoolProperty(name = "Use Square Waveforms", default = True, update = propertyChanged)
    offSet       : IntProperty(name = "Offset - Anim Start Frame", default = 0, min = -1000, max = 10000)
    easing       : FloatProperty(name = "Easing - Slopes Curves", default = 1, precision = 1, min = 0.1)
    spacing      : FloatProperty(name = "Note Spacing", default = 0, precision =1, min = 0)
    chnN         : IntProperty(name = "Process Channel", min = 2, default = 2)
    suffix       : StringProperty(name = "Note Suffix")
    midiFilePath : StringProperty()
    midiName     : StringProperty()
    message1     : StringProperty()
    message2     : StringProperty()
    notes        : CollectionProperty(type = MidiNoteData)
    channels     : StringProperty()

    def draw(self,layout):
        layout.prop(self, "midC")
        layout.prop(self, "useV")
        layout.prop(self, "squV")
        layout.prop(self, "chnN")
        #layout.prop(self, "suffix")
        layout.prop(self, "easing")
        layout.prop(self, "spacing")
        layout.prop(self, "offSet")
        col = layout.column()
        col.scale_y = 1.2
        self.invokeSelector(col, "PATH", "loadMidi",
            text = "Load MIDI CSV File", icon = "FILE_NEW")
        self.invokeSelector(col, "PATH", "loadSound",
            text = "Load Sound for MIDI File (Uses Offset)", icon = "SOUND")
        self.invokeFunction(col, "resetNode", icon = "CANCEL",
            text = "Reset Node for new CSV File")
        self.invokeFunction(col, "createControls", icon = "ADD",
            text = "Create MIDI Controls in Active Collection")
        #self.invokeFunction(col, "bakeMidi", icon = "FCURVE",
        #    text = "Bake MIDI F-Curves")
        if (self.message1 is not ""):
            layout.label(text = self.message1, icon = "INFO")
        if (self.message2 is not ""):
            layout.label(text = self.message2, icon = "INFO")

    def create(self):
        self.newOutput("Integer", "Animation Offset Frame", "ot_off")
        self.newOutput("Text", "Channels List", "chanList")
        #self.newOutput("Text List", "Note Mesh Names", "notesO")
        #self.newOutput("Float List", "Note Curve Values", "values")
        #self.newOutput("Integer List", "Note Indices Values", "indXs")
        #self.newOutput("an_GenericSocket","Event Dict","evD")

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.85,0.75,0.5)
        self.message1 = 'NO Data Stored' if 'TimeSig' not in dataD.keys() else self.message1
        if '&' in self.channels:
            chanList = self.channels.split("&")
        else:
            chanList = [[self.channels]]
        notesO = [item.noteName+'_'+self.suffix for item in self.notes]
        values = [item.value for item in self.notes]
        indXs = [item.noteIndex for item in self.notes]
        return self.offSet, chanList
        #return self.offSet, chanList, notesO, DoubleList.fromValues(values), indXs

    def loadMidi(self, path):
        # Load MIDI file and write basic info to dataD Dictionary
        self.message1 = "Midi File Loaded: " + str(os.path.basename(path))
        self.message2 = "Check/Load Sound File, Use Velocity, Easing & Offset"
        self.midiFilePath = str(path)
        self.midiName = str(os.path.basename(path))
        fps = bpy.context.scene.render.fps
        dataD.clear()
        # Populate the dictionaries for processing.
        with open(path) as f1:
            for line in f1:
                in_l = [elt.strip() for elt in line.split(',')]
                if (in_l[2] == 'Header'):
                    # Get Pulse variable.
                    pulse = int(in_l[5])
                    dataD['Pulse'] = pulse
                elif (in_l[2] == 'Tempo'):
                    if (in_l[1] == '0'):
                        # Get Initial Tempo.
                        tempo = in_l[3]
                        bpm = float( round( (60000000 / int(tempo)), 3) )
                        dataD['BPM'] = bpm
                        dataD['Tempo'] = [[0,tempo]]
                    elif in_l[0] == '1' and in_l[2] == 'Tempo':
                        # Add Tempo Changes & timings to Tempo Key in dataD.
                        frame = round(int(in_l[1]) * (60 * fps) / (bpm * pulse),2)
                        dataD.get('Tempo').append([str(frame),in_l[3]])
                elif (in_l[2] == 'Time_signature'):
                    # Get Time Signature
                    dataD['TimeSig'] = [int(in_l[3]),int(in_l[4])]
                elif (in_l[2] == 'Title_t') and (int(in_l[0]) > 1) and (in_l[3] != "Master Section"):
                    # Get Track Names & Numbers
                    if (in_l[0] == str(self.chnN)):
                        tName = in_l[3].strip('"')
                        dataD['Track Name'] = tName
                    otName = in_l[3].strip('"')
                    if 'Tracks' not in dataD.keys():
                        dataD['Tracks'] = [[otName,int(in_l[0])]]
                        self.channels = in_l[0]+' - '+otName
                    else:
                        dataD.get('Tracks').append([otName,int(in_l[0])])
                        self.channels = self.channels+'&'+in_l[0]+' - '+otName

    def removeFCurvesOfThisNode(self):
        try: action = self.id_data.animation_data.action
        except: return
        if action is None:
            return

        fCurvesToRemove = []
        pathPrefix = "nodes[\"{}\"]".format(self.name)
        for fCurve in action.fcurves:
            if fCurve.data_path.startswith(pathPrefix):
                fCurvesToRemove.append(fCurve)

        print(len(fCurvesToRemove))
        for fCurve in fCurvesToRemove:
            action.fcurves.remove(fCurve)

    def loadSound(self, path):
        editor = getOrCreateSequencer(self.nodeTree.scene)
        channel = getEmptyChannel(editor)
        sequence = editor.sequences.new_sound(
            name = os.path.basename(path),
            filepath = path,
            channel = channel,
            frame_start = self.offSet)
        self.soundName = sequence.sound.name
        self.message2 = "Sound Loaded."

    def resetNode(self):
        self.midiFilePath = ""
        self.midiName = ""
        self.message1 = "All Params Reset, Load MIDI File Again."
        self.message2 = "Check Sound File."
        self.useV = False
        self.offSet = 0
        self.easing = 0.2
        self.spacing = 0
        self.suffix = ''
        self.channels = ''
        self.removeFCurvesOfThisNode()
        self.notes.clear()
        dataD.clear()
        eventD.clear()

    def writeEvents(self):
        # Read MIDI file and write Note Events to eventD Dictionary
        fps = bpy.context.scene.render.fps
        with open(self.midiFilePath) as f1:
            for line in f1:
                in_l = [elt.strip() for elt in line.split(',')]
                if (len(in_l) == 6) and (in_l[2].split('_')[0] == 'Note') and (in_l[0] == str(self.chnN)):
                    # Note events for the chosen channel
                    noteNum = int(in_l[4]) - 12 if self.midC else int(in_l[4])
                    noteName = getNote(noteNum, 0)
                    if self.useV:
                        velo = round(int(in_l[5]) / 127,3)
                        onOff = velo if in_l[2] == 'Note_on_c' else 0.0
                    else:
                        onOff = 1.0 if in_l[2] == 'Note_on_c' else 0.0
                    frame = int(in_l[1]) * (60 * fps) / (dataD.get('BPM') * dataD.get('Pulse'))
                    # Check frame does not overlap last entry
                    # Note cannot start before previous same note has finished!
                    if noteName in eventD.keys(): # Is not the first note event
                        lastFrame = eventD.get(noteName)[-1][0]
                        if frame <= lastFrame:
                            frame = lastFrame + self.spacing if self.spacing > 0 else lastFrame + self.easing
                    frame = frame + self.offSet
                    if noteName not in eventD.keys():
                        eventD[noteName] = [[frame,onOff]]
                    else:
                        # Add records for events
                        if self.squV:
                            if in_l[2] == 'Note_on_c':
                                eventD[noteName].append([(frame-self.easing),0.0])
                            else:
                                if self.useV:
                                    velo = eventD.get(noteName)[-1][1]
                                    eventD[noteName].append([(frame-self.easing),velo])
                                else:
                                    eventD[noteName].append([(frame-self.easing),1.0])
                        eventD[noteName].append([frame,onOff])

    def createControls(self):
        # Create Controls from eventD Dictionary
        if (self.midiFilePath == "") or 'TimeSig' not in dataD.keys():
            self.message1 = "Load MIDI File, Check All Parameters?"
        else:
            eventD.clear()
            self.writeEvents()
            # Make Control Empties.
            xLoc = 0
            for k in eventD.keys():
                bpy.ops.object.empty_add(type='SINGLE_ARROW',location=(xLoc,self.chnN/10,0),radius = 0.03)
                bpy.context.active_object.name = str(k)+'_'+self.suffix+str(self.chnN)
                bpy.context.active_object.show_name = True
                indV = True
                for v in eventD.get(k):
                    frm = v[0]
                    val = v[1]
                    if indV:
                        # add keyframe just before first Note On
                        bpy.context.active_object.location.z = 0
                        bpy.context.active_object.keyframe_insert( data_path='location', index=2, frame=frm-self.easing )
                        indV = False
                    bpy.context.active_object.location.z = val/10
                    bpy.context.active_object.keyframe_insert( data_path='location', index=2, frame=frm )
                bpy.context.active_object.select_set(state=False)
                xLoc = xLoc + 0.1
                self.message2 = 'Channel '+str(self.chnN)+' Processed, Events: '+str(sum(len(v) for v in eventD.values()))

    def bakeMidi(self):
        # Create F-Curves from eventD Dictionary
        # remove previously baked data
        if self.chnN == '':
            self.message1 = 'Set Channel Number'
            self.message2 = ''
        elif (self.midiFilePath == "") or 'TimeSig' not in dataD.keys():
            self.message1 = 'Load MIDI File, Check All Parameters?'
            self.message2 = ''
        else:
            # Clear out all F-Curve Data
            self.notes.clear()
            self.removeFCurvesOfThisNode()
            eventD.clear()
            # Read Channel from MIDI file and polulate eventD dictionary
            self.writeEvents()
            # This function creates an abstraction for the somewhat complicated stuff
            # that is needed to insert the keyframes. It is needed because in Blender
            # custom node trees don't work well with fcurves yet.
            def createNote(name):
                dataPath = "nodes[\"{}\"].notes[{}].value".format(self.name, len(self.notes))
                item = self.notes.add()
                item.noteName = name

                def insertKeyframe(value, noteIndex, frame):
                    item.value = value
                    item.noteIndex = noteIndex
                    self.id_data.keyframe_insert(dataPath, frame = round(frame,2))
                    print(value,noteIndex,round(frame,2))

                return insertKeyframe

            # Process EventD to make F-curves.
            for rec in eventD.keys():
                ind = getIndex(str(rec))
                addKeyframe = createNote(str(rec))
                indV = True
                for i in eventD[rec]:
                    frame = i[0]
                    val = i[1]
                    if indV:
                        addKeyframe(value = 0.0, noteIndex = ind, frame = (frame-self.easing))
                        indV = False
                    addKeyframe(value = val, noteIndex = ind, frame = frame)
            self.message1 = 'Channel '+str(self.chnN)+' Processed, Notes '+str(len(eventD.keys()))+' Events: '+str(sum(len(v) for v in eventD.values()))
            self.message2 = 'Complete'
