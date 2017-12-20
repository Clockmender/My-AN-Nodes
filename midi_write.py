import bpy
import os
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
from ... utils.sequence_editor import getOrCreateSequencer, getEmptyChannel
from ... utils.path import getAbsolutePathOfSound

class MidiControlNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiControlNode"
    bl_label = "MIDI Control Node; Version 1.1 (Multi Channel)"
    bl_width_default = 450

    useV = BoolProperty(name = "Use MIDI Velocity", default = False, update = propertyChanged)
    square = BoolProperty(name = "Use Square Waveform", default = True, update = propertyChanged)
    offset = IntProperty(name = "Offset", default = 0, min = -1000, max = 10000)
    easing = FloatProperty(name = "Easing", default = 0.2, precision = 3)
    soundName = StringProperty(name = "Sound")
    message1 = StringProperty("")
    message2 = StringProperty("")
    midiFilePath = StringProperty()
    midiName = StringProperty()

    def draw(self, layout):
        col = layout.column()
        col.scale_y = 1.5
        self.invokeSelector(col, "PATH", "loadMidi",
            text = "Load MIDI CSV File", icon = "NEW")
        self.invokeSelector(col, "PATH", "loadSound",
            text = "Load Sound for MIDI File (Uses Offset)", icon = "NEW")
        self.invokeFunction(col, "createControls", icon = "NEW",
            text = "Create MIDI Controls on Active Layer(s)")

        self.invokeFunction(col, "resetNode", icon = "X",
            text = "Reset Node for new CSV File")

        layout.prop(self, "square")
        layout.prop(self, "useV")
        layout.prop(self, "easing")
        layout.prop(self, "offset")

        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")

        if (self.message2 != ""):
            layout.label(self.message2, icon = "INFO")

    def loadMidi(self, path):
        self.message1 = "Midi File Loaded: " + str(os.path.basename(path))
        self.message2 = "Check/Load Sound File, Use Velocity, Easing & Offset"
        self.midiFilePath = str(path)
        self.midiName = str(os.path.basename(path))

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

    def resetNode(self):
        self.midiFilePath = ""
        self.message1 = "Node Reset - Load CSV File Again."
        self.message2 = "Check Sound File."
        self.useV = False
        self.offset = 0
        self.easing = 0.2

    def createControls(self):
        # Run my script here.
        if (self.midiFilePath == ""):
            self.message1 = "Load MIDI CSV File First! Have you set Use Velocity, Easing & Offset?"
        else:
            self.message1 = "Making Controls for: " + self.midiName
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
                            bpm = float( round( (60000000 / int(tempo)), 5) )
                            bps = float( round( (bpm / 60), 5) )

                        else:
                            # Add Tempo Changes to events list.
                            events_list.append(in_l)

                    elif (in_l[2] == 'Title_t') and (int(in_l[0]) > 1) and (in_l[3] != "Master Section"):
                        t_name = in_l[3].strip('"')
                        # Get First Track Title
                        if (not t_name):
                            t_name = 'Channel_' + str(t_ind)
                            t_ind = t_ind + 1
                            control_list.append([t_name])
                        else:
                            control_list.append([t_name])

                    # Only process note events, ignore control events.
                    if ( len(in_l) == 6) and ( in_l[2].split('_')[0] == 'Note'):
                        note_n = note_list[(int(in_l[4]) - 21)]
                        in_n = [ in_l[0] , in_l[1] , in_l[2] , note_n , in_l[5] ]
                        events_list.append(in_n)
                        control = [ in_n[0] , note_n , int(in_l[4]) ]
                        if control not in control_list:
                            control_list.append(control)

            # Generate the controls from control_list, so each track starts at X = 0.
            # Keyframe all controls at frame 1 to be Z = 0.
            cnt  = -2
            prev = int(control_list[2][0])

            # Delete last entry if no note events follow the channel name.
            last_c = len(control_list) - 1
            if (len(control_list[last_c]) == 1):
                control_list.pop()

            control_Objs = []
            for control in control_list:
                if (len(control) == 1):
                    # Sort out the group names.
                    t_name = control[0]
                    grp = bpy.data.groups.get(t_name)
                    grp = str(grp).find(t_name)
                    if (grp == -1):
                        bpy.data.groups.new(t_name)
                else:
                    name = 't' + str(control[0]) + '_' + control[1]
                    track = int(control[0])
                    if (track == prev):
                        cnt = cnt + 2
                    else:
                        cnt = 0

                    bpy.ops.object.add(type='EMPTY',location=(cnt,(track * 2),0))
                    bpy.context.active_object.name = name
                    bpy.context.active_object.empty_draw_type = "SINGLE_ARROW"
                    bpy.context.active_object.show_name = True
                    bpy.ops.object.group_link(group=t_name)
                    bpy.context.active_object.location.z = 0
                    bpy.context.active_object.keyframe_insert( data_path='location', index=2, frame=1 )
                    control_Objs.append(bpy.context.active_object)
                    bpy.context.active_object.select = False
                    prev = track

            # Get Frames Per Second from Blender.
            fps = bpy.context.scene.render.fps

            # Get MIDI Events list length.
            len_l = len(events_list)

            # Get General/First MIDI event conversion factor.
            conv = (60 / (bpm * pulse))

            # Process Events List to keyframe controls (Z value only).
            # Range used so checking can be done with a small number of lines.

            for i in range(0,len_l):
                line = events_list[i]
                if (line[2] == 'Tempo'):
                    # Get new Tempo.
                    tempo = line[3]
                    bpm = float( round( (60000000 / int(tempo)), 5) )
                    bps = float( round( (bpm / 60), 5) )
                    # Change Frame conversion factor.
                    conv = (60 / (bpm * pulse))
                else:
                    ob_nm  = 't' + str(line[0]) + '_' + line[3]
                    frame  = round( (int(line[1]) * fps * conv), 2)
                    frame = frame + offsetp
                    on_off = line[2].split('_')[1]
                    velo   = round( (int(line[4]) / 127), 2)
                    ob = bpy.data.objects[ob_nm]
                    ob.select = True
                    if (on_off == 'on'):
                        # Note On event.
                        if self.square:
                            ob.location.z = 0
                            ob.keyframe_insert( data_path='location', index=2, frame=(frame - easingp) )
                        if (velp):
                            # Use Velocity.
                            ob.location.z = velo
                        else:
                            ob.location.z = 1

                        ob.keyframe_insert( data_path='location', index=2, frame=(frame + easingp) )

                    else:
                        # Note Off Event.
                        frame = frame - (easingp / 2)
                        if self.square:
                            ob.keyframe_insert( data_path='location', index=2, frame=(frame - easingp) )
                        ob.location.z = 0
                        ob.keyframe_insert( data_path='location', index=2, frame=(frame + easingp) )
                    ob.select = False

            # MIDI Event Process complete, use controls to drive animations, they are named by track and note.

            numb = ""
            numb = str(len(control_Objs))
            self.message1 = "Process Complete - " + numb + " controls on active layer(s)."
            self.message2 = ""
