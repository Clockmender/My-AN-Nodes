import bpy
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures import DoubleList
from ... events import propertyChanged
from ... utils.sequence_editor import getOrCreateSequencer, getEmptyChannel
from ... utils.path import getAbsolutePathOfSound

class MidiNoteData(bpy.types.PropertyGroup):
    noteName = StringProperty() # e.g. C4, B5, ...
    noteIndex = IntProperty()
    # This value can be keyframed.
    # It is possible but not easy to 'find' the fcurve of this property.
    # Therefor only the value in the current frame can be accessed efficiently.
    # In most use cases this should be enough, otherwise you'll have to find another alternative.
    value = FloatProperty()

class MidiInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiInputNode"
    bl_label = "MIDI Bake-To-Curve Node, Vers 1.1 (Single Channel)"
    bl_width_default = 450

    # Setup variables
    useV = BoolProperty(name = "Use MIDI Velocity", default = False, update = propertyChanged)
    square = BoolProperty(name = "Use Square Waveforms", default = True, update = propertyChanged)
    offset = IntProperty(name = "Offset - Anim Start Frame", default = 0, min = -1000, max = 10000)
    spacing = IntProperty(name = "Spacing - Separates Notes", default = 0, min = 0)
    bpm = IntProperty(name = "Beats Per Minute", default = 1, min = 1)
    nn = IntProperty(name = "Time Sig Numerator", default = 1, min = 1)
    dd = IntProperty(name = "Time Sig Denominator", default = 1, min = 1)
    easing = FloatProperty(name = "Easing - Slopes Curves", default = 1, precision = 1, min = 0.1)
    soundName = StringProperty(name = "Sound")
    keys_grp = StringProperty(name = "Keys Group")
    message1 = StringProperty("")
    message2 = StringProperty("")
    midiFilePath = StringProperty()
    midiName = StringProperty()

    # I'd suggest to bake one channel per node for now.
    # You can have multiple nodes of course.
    Channel_Number = StringProperty(name = "MIDI Channel Number") # e.g. Piano, ...
    notes = CollectionProperty(type = MidiNoteData)

    def create(self):
        self.newOutput("Text List", "Notes Played", "notes")
        self.newOutput("Float List", "Note Curve Values", "values")
        self.newOutput("Integer List", "Keys Indices", "indices")
        self.newOutput("Integer", "Beats Per Minute", "bpm_int")
        self.newOutput("Integer", "Time Sig Numerator", "nn_int")
        self.newOutput("Integer", "Time Sig Denominator", "dd_int")
        self.newOutput("Integer", "Animation Offset Frame", "ot_off")

    def draw(self, layout):
        layout.prop(self, "Channel_Number")
        layout.prop(self, "square")
        layout.prop(self, "useV")
        layout.prop(self, "easing")
        layout.prop(self, "offset")
        layout.prop(self, "spacing")
        layout.prop(self, "keys_grp")
        layout.separator()
        col = layout.column()
        col.scale_y = 1.5
        self.invokeSelector(col ,"PATH", "bakeMidi", icon = "NEW",
            text = "Select MIDI CSV & Bake Midi")
        layout.separator()
        self.invokeSelector(col, "PATH", "loadSound",
            text = "Load Sound for MIDI File (Uses Offset)", icon = "NEW")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")
        if (self.message2 != ""):
            layout.label(self.message2, icon = "INFO")

    def execute(self):
        notes = [item.noteName for item in self.notes]
        values = [item.value for item in self.notes]
        indices = [item.noteIndex for item in self.notes]
        bpm_int = int(self.bpm)
        nn_int = self.nn
        dd_int = self.dd
        ot_off = self.offset
        return notes, DoubleList.fromValues(values), indices, bpm_int, nn_int, dd_int, ot_off

    def loadSound(self, path):
        editor = getOrCreateSequencer(self.nodeTree.scene)
        channel = getEmptyChannel(editor)
        sequence = editor.sequences.new_sound(
            name = os.path.basename(path),
            filepath = path,
            channel = channel,
            frame_start = self.offset)
        self.soundName = sequence.sound.name
        self.message2 = "Sound Loaded."

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

        for fCurve in fCurvesToRemove:
            action.fcurves.remove(fCurve)

    def bakeMidi(self, path):
        # remove previously baked data
        self.notes.clear()
        self.removeFCurvesOfThisNode()

        self.midiFilePath = str(path)
        self.midiName = str(os.path.basename(path)).split(".")[0]
        self.message1 = "Midi File Loaded: " + str(os.path.basename(path)) + "MIDI File"

        if (self.midiFilePath == ""):
            self.message1 = "Load MIDI CSV File First! Have you set Use Velocity, Easing & Offset?"
        else:
            self.message1 = ""
            self.message2 = ""

            note_list = ['a0','a0s','b0','c1','c1s','d1','d1s','e1','f1','f1s','g1','g1s','a1','a1s','b1','c2','c2s','d2','d2s','e2','f2','f2s','g2','g2s','a2','a2s','b2','c3','c3s','d3','d3s','e3','f3','f3s','g3','g3s','a3','a3s','b3',
                'c4','c4s','d4','d4s','e4','f4','f4s','g4','g4s','a4','a4s','b4','c5','c5s','d5','d5s','e5','f5','f5s','g5','g5s','a5','a5s','b5','c6','c6s','d6','d6s','e6','f6','f6s','g6','g6s','a6','a6s','b6',
                    'c7','c7s','d7','d7s','e7','f7','f7s','g7','g7s','a7','a7s','b7','c8']

            events_list = []
            control_list = []
            midi_file = self.midiFilePath
            offsetp = self.offset
            velp = self.useV
            easingp = self.easing
            t_name = 'Unknown'
            t_ind = 2
            fps = bpy.context.scene.render.fps

            #This section Opens and reads the MIDI file.
            with open(midi_file) as f1:
                for line in f1:
                    in_l = [elt.strip() for elt in line.split(',')]
                    if (in_l[2] == 'Header'):
                        # Get Pulse variable.
                        pulse = int(in_l[5])

                    elif (in_l[2] == 'Tempo'):
                        if (in_l[0] == '1'):
                            # Get Initial Tempo.
                            tempo = in_l[3]
                            self.bpm = float( round( (60000000 / int(tempo)), 5) )
                            bps = float( round( (self.bpm / 60), 5) )
                        else:
                            # Add Tempo Changes to events list.
                            events_list.append(in_l)

                    elif (len(in_l) == 4) and (in_l[2] == 'Title_t') and (int(in_l[0]) > 1) and (in_l[3] != "Master Section") and (in_l[0] == self.Channel_Number):
                        t_name = in_l[3].strip('"')
                        # Get First Track Title
                        if (not t_name):
                            t_name = 'Channel_' + str(t_ind)
                            t_ind = t_ind + 1
                            control_list.append(t_name)
                        else:
                            control_list.append(t_name)

                    elif (in_l[2] == 'Time_signature'):
                        self.nn = int(in_l[3])
                        self.dd = int(in_l[4])

                    # Only process note events, ignore control events.
                    if ( len(in_l) == 6) and ( in_l[2].split('_')[0] == 'Note') and (in_l[0] == self.Channel_Number):
                        note_n = note_list[(int(in_l[4]) - 21)]
                        on_off = in_l[2]
                        velo = int(in_l[5]) / 127
                        if on_off == "Note_on_c":
                            l_easing = self.easing
                            l_spacing = self.spacing
                            if velp:
                                on_off = velo
                                pon_off = 0
                            else:
                                on_off = 1
                                pon_off = 0
                        elif on_off == "Note_off_c":
                            l_easing = self.easing * 2
                            l_spacing = 0 - self.spacing
                            on_off = 0
                            if velp:
                                pon_off = 0.8
                            else:
                                pon_off = 1
                        # On-Off, Frame, Note, Velocity
                        conv = (60 / (self.bpm * pulse))
                        frame_e = int(in_l[1])
                        frame_e = frame_e * conv * fps
                        frame_e = round(frame_e, 1) + self.offset
                        frame_p = frame_e - l_easing
                        if self.spacing > 0:
                            frame_e = frame_e + l_spacing
                            frame_p = frame_p + l_spacing
                        if self.square:
                            in_e = [str(pon_off), str(frame_p), note_n]
                            events_list.append(in_e)
                        in_n = [str(on_off), str(frame_e), note_n]
                        events_list.append(in_n)
                        control = note_n
                        if control not in control_list:
                            control_list.append(control)

            # Get list lengths
            numb_1 = 0
            numb_2 = 0
            numb_1 = len(control_list)
            numb_2 = int(len(events_list))
            if self.square:
                numb_2 = int(numb_2 / 2)
            self.message1 = "Baked File: " + self.midiName + ", Notes = " + str(numb_1 - 1) + ", Channel No = " + self.Channel_Number
            if numb_2 == 0:
                self.message2 = "Note Events = " +str(numb_2) + " Check Channel Number with CSV File."
            else:
                self.message2 = "Note Events = " +str(numb_2) + ", Pulse = " + str(pulse) + ", BPM = " + str(int(self.bpm)) + ", Tempo = " + str(tempo)

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
                self.id_data.keyframe_insert(dataPath, frame = frame)

            return insertKeyframe

        # Get Channel Name and process events for each note
        channelName = control_list[0]
        control_list.pop(0)
        ke_names = []
        group = bpy.data.groups.get(self.keys_grp)
        if group is not None:
            keys_objs = group.objects
            for obj in keys_objs:
                note = obj.name.split("_")[0]
                ke_names.append(note)
        # Loop through Notes
        for rec in range(0, (numb_1 - 1)):
            f_n = control_list[rec]
            name = channelName + "_" + f_n
            indx = 0
            for i in range( 0, len(ke_names)):
                if ke_names[i] == f_n:
                    indx = i

            ev_list = [bit for bit in events_list if bit[2] == f_n]
            addKeyframe = createNote(name)
            # Value, then noteindex, then Frame
            # Fix value 0 at frame 1
            addKeyframe(value = 0, noteIndex = indx, frame = 1)
            # Range used so I can test a small section:
            for ind in range(0,len(ev_list)):
                addKeyframe(value = float(ev_list[ind][0]), noteIndex = indx, frame = float(ev_list[ind][1]) )
