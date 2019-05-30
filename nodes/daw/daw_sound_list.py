import bpy
import aud
import os
from pathlib import Path
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class soundList(bpy.types.Node, AnimationNode):
    bl_idname = "an_soundList"
    bl_label = "DAW Sound Files"
    bl_width_default = 170

    indexD    : IntProperty(name="Index",min=0,max=11)
    message   : StringProperty()
    reLoad    : BoolProperty()

    store = {}
    sndStore = {}

    def draw(self,layout):
        if self.message is not '':
            layout.label(text=self.message,icon="NONE")
        layout.prop(self,"indexD")
        col = layout.column()
        col.scale_y = 1.2
        self.invokeSelector(col, "PATH", "loadFile",
            text = "Load Sound File", icon = "FILE_NEW")
        self.invokeFunction(col, "loadStore",
            text = "Load Store File", icon = "FILE_NEW")
        self.invokeFunction(col, "clearSound",
            text = "Clear Sound Store", icon = "EVENT_X", confirm = True)
        self.invokeFunction(col, "clearFile",
            text = "Clear Sound List", icon = "EVENT_X", confirm = True)

    def clearSound(self):
        self.sndStore.clear
        self.message = "Sound Store Cleared"

    def loadStore(self):
        pathF = bpy.data.filepath[:-6]+"_snds.txt"
        my_file = Path(pathF)
        if my_file.is_file():
            f = open(pathF,'r')
            data=f.read()
            f.close()
            self.store = eval(data)
        self.message = "Store File loaded"
        self.reLoad = True

    def loadFile(self,path):
        if '.' in self.name:
            name = 'SoundSet_'+self.name.split('.')[1]
        else:
            name = 'SoundSet_000'
        if name not in self.store:
            self.store[name] = ["","","","","","","","","","","",""]
        self.store[name][self.indexD] = str(path)
        pathF = bpy.data.filepath[:-6]+"_snds.txt"
        f = open(pathF,"w")
        f.write(str(self.store))
        f.close()
        self.message = 'File Loaded: '+str(os.path.basename(pathF))

    def clearFile(self):
        if '.' in self.name:
            name = 'SoundSet_'+self.name.split('.')[1]
        else:
            name = 'SoundSet_000'
        if name in self.store:
            del self.store[name]
        pathF = bpy.data.filepath[:-6]+"_snds.txt"
        f = open(pathF,"w")
        f.write(str(self.store))
        f.close()
        self.message = "Sound Store "+name+" Cleared"
        self.color = (0.75,1,0.75)

    def create(self):
        self.newInput("an_IntegerListSocket","Sound Data","sndList")
        self.newInput("an_FloatSocket","Max Length","maxL",minValue=0.1,value=1)
        self.newInput("an_IntegerSocket","Fadeout %","fadP",minValue=1,maxValue=50,value=5)
        self.newInput("an_IntegerSocket","Samples","samples",value=44100,minValue=5000)
        self.newOutput("an_SoundSocket","Sound O","sndO")

    def execute(self,sndList,maxL,fadP,samples):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.message = ""
        if '.' in self.name:
            name = 'SoundSet_'+self.name.split('.')[1]
        else:
            name = 'SoundSet_000'
        if name not in self.store:
            pathF = bpy.data.filepath[:-6]+"_snds.txt"
            my_file = Path(pathF)
            if not my_file.is_file():
                self.color = (0.75,1,0.75)
                self.message = "No Saved Sounds File"
                return None
            else:
                f = open(pathF,'r')
                data=f.read()
                f.close()
                self.store = eval(data)
        if name not in self.sndStore or self.reLoad:
            sndS = []
            for r in self.store[name]:
                if r is not "":
                    snd = aud.Sound.file(r).resample(samples,False)
                    sndS.append(snd)
            self.sndStore[name] = sndS
            self.reLoad = False
        self.color = (1,0.8,1)
        lenST = len(self.sndStore[name])
        self.label = "DAW Sound Files "+str(lenST)
        for i in range(0,len(sndList)):
            r = sndList[i][0]
            if r < lenST:
                snd = self.sndStore[name][r].rechannel(2)
                if sndList[i][1] > 0:
                    snd = snd.delay(sndList[i][1])
                snd = snd.volume(sndList[i][2])
                durT = snd.length / snd.specs[0]
                fp = fadP / 100
                if durT >= maxL:
                    snd = snd.limit(0,maxL).fadeout((maxL*(1-fp)),(maxL*fp))
            if i == 0:
                sndM = snd
            else:
                sndM = sndM.mix(snd)
        return sndM if len(sndList) > 0 else None
