import bpy
import aud
import os
from pathlib import Path
from ... utils.sequence_editor import getOrCreateSequencer, getEmptyChannel
from ... utils.path import getAbsolutePathOfSound
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . utils_setup import getSysData

store = {}

class slicerSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_slicerSound"
    bl_label = "SOUND Slicer, Complete Steps 1-6, or just 6 for Saved File"
    bl_width_default = 500

    message   : StringProperty()
    message1  : StringProperty()
    soundFile : StringProperty()
    soundName : StringProperty()
    timeM     : FloatProperty(name="Sound Time (s)",default=5,min=1)
    timeS     : FloatProperty(name="Start Time (s)",default=0,min=0)
    fileOut   : StringProperty(name="Name",default="sliced")
    orderL    : StringProperty(name="ReSlice Order",default="1,2,3,4,5,6,7,8,9,10")
    reverseL  : StringProperty(name="Reverse Clips (use ,)",default="")
    pitchV    : FloatProperty(name="Pitch Value",default=1,min=0.25,max=4)
    volOut    : FloatProperty(name="Volume",default=1.0,min=0.5,max=10)
    useSys    : BoolProperty(name="Use System Beat",default=False)
    beatM     : IntProperty(name="System Beat Multipler",default=1,min=1,max=64)
    vseChn    : IntProperty(name="VSE Channel",default=0,min=0)
    vseLoc    : IntProperty(name="VSE Frame",default=0,min=0)
    numbD     : IntProperty(name="Divisions",default=10,min=3,max=16)

    def draw(self,layout):
        colM = layout.column()
        row = colM.row()
        col = row.column()
        col.prop(self,"numbD")
        col = row.column()
        col.prop(self,"timeS")
        col = row.column()
        col.prop(self,"timeM")
        row = colM.row()
        row = colM.row()
        col = row.column()
        self.invokeSelector(col, "PATH", "loadFile",
            text = "1a: Load New Sound File", icon = "FILE_NEW")
        col = row.column()
        self.invokeSelector(col, "PATH", "loadCut",
            text = "1b: Load Cut Sound File", icon = "FILE_NEW")
        col = row.column()
        self.invokeFunction(col, "clearFile",
            text = "1opt: Reset Node", icon = "EVENT_X")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "cutSound", text = "2: Cut Sound", icon = "FILE_SOUND")
        col = row.column()
        self.invokeFunction(col, "playSound", data = "cut", text = "2opt: Play Cut Sound", icon = "OUTLINER_OB_SPEAKER")
        col = row.column()
        self.invokeFunction(col, "writeSound",data = "cut", text="2opt: Write Cut File", icon="FILE_NEW")

        row = colM.row()
        if self.message is not '':
            row.label(text=self.message,icon="INFO")
        row = colM.row()
        row.prop(self,"orderL")
        row = colM.row()
        row.prop(self,"reverseL")
        row = colM.row()
        col = row.column()
        col.prop(self,"useSys")
        col = row.column()
        col.prop(self,"beatM")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "sliceSound", text = "3: Slice Sound", icon = "FILE_SOUND")
        col = row.column()
        col.prop(self,"pitchV")
        col = row.column()
        self.invokeFunction(col, "joinSound", text = "4: Join Sliced Sounds", icon = "FILE_SOUND")
        row = colM.row()
        col = row.column()
        col.prop(self,"fileOut")
        col = row.column()
        col.prop(self,"volOut")
        row = colM.row()
        col = row.column()
        self.invokeFunction(col, "writeSound",data="slice", text="5: Write Joined File", icon="FILE_NEW")
        col = row.column()
        self.invokeFunction(col, "playSound", data="sliced", text="5opt: Play Joined Sound", icon="OUTLINER_OB_SPEAKER")
        col = row.column()
        self.invokeSelector(col, "PATH", "addSound", text="6: Add Saved File to VSE", icon="SPEAKER")
        row = colM.row()
        col = row.column()
        col.prop(self,"vseLoc")
        col = row.column()
        col.prop(self,"vseChn")
        row = colM.row()
        if self.message1 is not '':
            row.label(text=self.message1,icon="ERROR")

    def clearFile(self):
        store.clear()
        self.soundFile = ""
        self.soundName = ""
        self.message = ""
        self.message1 = ""

    def loadFile(self,path):
        self.soundFile = str(path)
        self.soundName = str(os.path.basename(path))
        self.message = 'File Loaded: '+self.soundName
        self.message1 = ""

    def addSound(self,path):
        frameC = bpy.context.scene.frame_current
        editor = getOrCreateSequencer(self.nodeTree.scene)
        channel = getEmptyChannel(editor) if self.vseChn == 0 else self.vseChn
        offSet = bpy.context.scene.frame_current if self.vseLoc == 0 else self.vseLoc
        sequence = editor.sequences.new_sound(
            name = os.path.basename(path),
            filepath = path,
            channel = channel,
            frame_start = offSet)
        sequence.show_waveform = True
        self.message = "File "+str(path)+" Added to VSE"

    def playSound(self,data):
        dev = aud.Device()
        if data == "cut" and "SoundCut" in store:
            self.message = "Playing Cut File"
            sndO = store['SoundCut']
            sndO = sndO.volume(self.volOut)
            if sndO.specs[1] != 2:
                sndO = sndO.rechannel(2)
            try: play = dev.play(sndO)
            except: self.message = "Invalid Sound File"
        elif data == "sliced" and "sndO" in store:
            self.message = "Playing Sliced/Re-Joined File"
            sndO = store['sndO']
            sndO = sndO.volume(self.volOut)
            if sndO.specs[1] != 2:
                sndO = sndO.rechannel(2)
            try: play = dev.play(sndO)
            except:self.message = "Invalid Sound File"
        else:
            self.message1 = "No Files in Store:"

    def loadCut(self,path):
        try:
            sndCut = aud.Sound.file(path)
        except:
            self.message = ""
            self.message1 = "Not Valid Sound File"
            return
        if sndCut.specs[1] != 2:
            sndCut = sndCut.rechannel(2)
        store["SoundCut"] = sndCut
        self.message = "Cut Sound Stored - Slice Next, Length: "+str(sndCut.length / sndCut.specs[0])
        self.message1 = ""

    def cutSound(self):
        if self.soundFile is not '':
            sndCut = aud.Sound.file(self.soundFile)
            # Limit to Start Time, Start Time + (Number of Divisions * Shortest Note Time)
            if self.useSys:
                data = getSysData(self)
                if "Time_NL" in data:
                    # Shortest Note Time * Beat Multiplier
                    cut = data["Time_NL"] * self.beatM
                else:
                    self.message = ""
                    self.message1 = "No System Setup Data"
                    return
            else:
                cut = self.timeM / self.numbD
                sndCut = sndCut.limit(self.timeS,(self.timeS+(self.numbD*cut)))
            if sndCut.specs[1] != 2:
                sndCut = sndCut.rechannel(2)
            store["SoundCut"] = sndCut
            self.message = "Cut Sound Stored Start: "+str(self.timeS)+", Cuts: "+str(self.numbD)+", Cut Time: "+str(cut)
            self.message1 = ""
        else:
            self.message1 = "No Sound, or bad Values"

    def sliceSound(self):
        if "SoundCut" in store:
            tot = 0
            inSnd = store["SoundCut"]
            len = inSnd.length / inSnd.specs[0]
            if self.useSys:
                data = getSysData(self)
                if "Time_NL" in data:
                    cut = data["Time_NL"] * self.beatM
                    timeM = cut * self.numbD
                else:
                    self.message = ""
                    self.message1 = "No System Setup Data"
                    return
            else:
                cut = self.timeM / self.numbD
                timeM = self.timeM
            if len < timeM:
                self.message = ""
                self.message1 = "Cut Sound Too Short: "+str(len)
                return
            store["TimeS"] = round(cut,5)
            for i in range(1,(self.numbD+1)):
                tot = tot + cut
                snd = inSnd.limit((i*cut),(cut+(i*cut)))
                store["snd"+str(i)] = snd
            self.message = "Sound Sliced, Slice Time: "+str(round(cut,5))+"s, Total Time: "+str(round(tot,5))+"s"
            self.message1 = ""
        else:
            self.message1 = "No Sound Processed, or Bad Values"

    def joinSound(self):
        self.message1 = ""
        tot = 0
        if "snd1" in store and "snd2" in store and "snd3" in store:
            if self.useSys:
                cut = getSysData(self)["Time_NL"] * self.beatM
            else:
                cut = self.timeM / self.numbD
            if "," in self.reverseL:
                revList = self.reverseL.split(",")
            else:
                revList = [self.reverseL]
            if "," in self.orderL:
                orderList = self.orderL.split(",")
                first = True
                for i in orderList:
                    tot = tot + cut
                    if first:
                        sndO = store["snd"+i]
                        if str(i) in revList:
                            sndO = sndO.reverse()
                        first = False
                    else:
                        if "snd"+i in store:
                            snd = store["snd"+i]
                        else:
                            self.message1 = "Requested Sound: snd"+i+" Not in Store"
                            snd = None
                        if snd is not None:
                            if str(i) in revList:
                                snd = snd.reverse()
                            sndO = sndO.join(snd)
                if self.pitchV != 1:
                    sndO = sndO.pitch(self.pitchV)
                if sndO.specs[1] != 2:
                    sndO = sndO.rechannel(2)
                store["sndO"] = sndO
                self.message = "Slices Joined/Reversed/Pitched, Total Time: "+str(round(tot,5))+"s"
            else:
                self.message1 = "Incorrect Order Format (numbers & ,)"
        else:
            self.message1 = "No Sliced Sounds in Store"

    def writeSound(self,data):
        if "sndO" in store or "SoundCut" in store and self.fileOut is not "":
            if data == "cut":
                pathF = bpy.data.filepath[:-6]+"_Cut_"+self.fileOut+".flac"
                if "SoundCut" in store:
                    snd = store["SoundCut"]
                else:
                    self.message1 = "Not Cut Sound Stored"
                    return
            else:
                pathF = bpy.data.filepath[:-6]+"_Slice_"+self.fileOut+".flac"
                if "sndO" in store:
                    snd = store["sndO"]
                else:
                    self.message1 = "No Sliced Sound Stored"
                    return
            my_file = Path(pathF)
            if my_file.is_file():
                self.message1 = "File "+str(pathF)+" Exists, Enter New Name/Delete it"
                return
            snd = snd.volume(self.volOut)
            if snd.specs[1] != 2:
                snd = snd.rechannel(2)
            sndW = snd.write(pathF,aud.RATE_16000,aud.CHANNELS_STEREO,aud.FORMAT_FLOAT32,aud.CONTAINER_FLAC,aud.CODEC_FLAC)
            self.message = "File Written "+pathF
            self.message1 = ""
        else:
            self.message1 = "No Sound to Write/No Filename"

    def create(self):
        self.newOutput("an_GenericSocket","Store","store")

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        if "SoundCut" in store:
            self.message = ""
            self.message1 = ""
            return store
        else:
            self.message = ""
            self.message1 = "No Stored Data"
            return None
