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
    bl_label = "MIDI Bake-To-Curve Node (Single Channel)"
    bl_width_default = 400

    # Setup variables
    mid_c = BoolProperty(name = "Middle C = C4", default = True, update = propertyChanged)
    useV = BoolProperty(name = "Use MIDI Velocity", default = False, update = propertyChanged)
    square = BoolProperty(name = "Use Square Waveforms", default = True, update = propertyChanged)
    offset = IntProperty(name = "Offset - Anim Start Frame", default = 0, min = -1000, max = 10000)
    spacing = IntProperty(name = "Spacing - Separates Notes", default = 0, min = 0)
    bpm = IntProperty(name = "Beats Per Minute", default = 1, min = 1)
    nn = IntProperty(name = "Time Sig Numerator", default = 1, min = 1)
    dd = IntProperty(name = "Time Sig Denominator", default = 1, min = 1)
    easing = FloatProperty(name = "Easing - Slopes Curves", default = 1, precision = 1, min = 0.1)
    soundName = StringProperty(name = "Sound")
    message1 = StringProperty("")
    message2 = StringProperty("")
    message3 = StringProperty("")
    midiFilePath = StringProperty()
    midiName = StringProperty()
    suffix = StringProperty(name = "Suffix", update = propertyChanged)

    # I'd suggest to bake one channel per node for now.
    # You can have multiple nodes of course.
    Channel_Number = StringProperty(name = "MIDI Channel Number",default = "2") # e.g. Piano, ...
    notes = CollectionProperty(type = MidiNoteData)

    def create(self):
        self.newOutput("Text List", "Details of Notes Played", "notes")
        self.newOutput("Text List", "Note Names", "notes_s")
        self.newOutput("Float List", "Note Curve Values", "values")
        self.newOutput("Integer", "Beats Per Minute", "bpm_int")
        self.newOutput("Integer", "Time Sig Numerator", "nn_int")
        self.newOutput("Integer", "Time Sig Denominator", "dd_int")
        self.newOutput("Integer", "Animation Offset Frame", "ot_off")

    def draw(self, layout):
        layout.prop(self,"mid_c")
        layout.prop(self, "suffix")
        layout.label('(Uses C3 if Unchecked), Suffix added at Execute', icon = "INFO")
        layout.label('')
        layout.prop(self, "Channel_Number")
        layout.prop(self, "square")
        layout.prop(self, "useV")
        layout.prop(self, "easing")
        layout.prop(self, "offset")
        layout.prop(self, "spacing")
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
        if (self.message3 != ""):
            layout.label(self.message3, icon = "ERROR")

    def execute(self):
        notes = [item.noteName for item in self.notes]
        notes_s = [item.noteName.split(' ')[2].split('_')[1]+self.suffix for item in self.notes]
        values = [item.value for item in self.notes]
        bpm_int = int(self.bpm)
        nn_int = self.nn
        dd_int = self.dd
        ot_off = self.offset
        return notes, notes_s, DoubleList.fromValues(values), bpm_int, nn_int, dd_int, ot_off

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
        if self.Channel_Number == '':
            self.message1 = ''
            self.message2 = ''
            self.message3 = 'Set Channel Number First'
            return
        else:
            self.message3 = ''
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
                        # Use C4 if mid_c is True, else C3
                        note_num = int(in_l[4])
                        if self.mid_c:
                            note_n = note_list[(note_num - 12)]
                        else:
                            note_n = note_list[note_num]

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
                            in_e = [str(pon_off), str(frame_p), note_n, note_num]
                            events_list.append(in_e)
                        in_n = [str(on_off), str(frame_e), note_n, note_num]
                        events_list.append(in_n)
                        control = note_n
                        if control not in control_list:
                            control_list.append(control)

            # Get list lengths
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
        # Loop through Notes
        for rec in range(0, (numb_1 - 1)):
            f_n = control_list[rec]
            name = channelName + "_" + f_n
            ev_list = [bit for bit in events_list if bit[2] == f_n]
            addKeyframe = createNote(name)
            # Value, then noteindex, then Frame
            # Fix value 0 at frame 1
            addKeyframe(value = 0, noteIndex = int(ev_list[0][3]), frame = 1)
            # Range used so I can test a small section:
            for ind in range(0,len(ev_list)):
                addKeyframe(value = float(ev_list[ind][0]), noteIndex = int(ev_list[ind][3]), frame = float(ev_list[ind][1]) )
