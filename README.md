# My-AN-Nodes for Blender 2.8, AN 2.1

Copyright (C) 2019 Alan Odom
clockmender@icloud.com

Created by Alan Odom

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
# AIMS & OBJECTIVES:

The initial reason behind developing these nodes was to provide a system to read MIDI files and produce animations from them, rather than having to keyframe everything - a long and labour intensive process.

From there, I have developed other nodes that take complex tasks, with standard nodes, and turn them into easily achievable node trees. Everything these nodes do can be done with either script nodes, or expression nodes, but that requires a great deal of knowledge of Python and Blender structures, so these nodes take all that away.

I also added a "Bone" socket to allow for easy manipulation of bones in AN. I know this can be done without the new socket and nodes built around it. However, the collection of bone nodes make it easier to animate bones without having to use script, or expression nodes.

Some of the nodes are very "niche" in what they do, but they make my life as an animator easier, in that they take away the need to develop complex python code in script nodes each time I want to do something out of the ordinary (this happens a lot!).

Some nodes, particularly the DAW ones, may be "experimental" and are included for collaboration purposes, they are not yet ready for full production. On-going experimentation has always been part of my IT objectives and I am quite happy to share this code here and open it up to critique and comment.

If you would like to help with development, or suggest more nodes you would find useful, please contact me via email.

# GENERAL:

These nodes are to add to Version 2.1 or Animation Nodes, which requires official releases from Blender 2.8, i.e. NOT Buildbot versions!

They come with no warranty, but have been extensively tested. I will produce a help file later, as time permits.

# INSTALLATION

The bone.py file should go in this directory:

.../Blender/[version number]/scripts/addons/animation_nodes/sockets

The node_menu.py should go in this directory:

.../Blender/[version number]/scripts/addons/animation_nodes/ui

to replace the one that is already there - keep a backup copy of the original in a safe place somewhere else.

The other files should go into a new folder in this directory:

.../Blender/[version number]/scripts/addons/animation_nodes/nodes

That new directory should contain an empty file named \_\_init\_\_.py - create this with any text editor or copy one from another AN directory. This can be downloaded from the top level directory as an option.

The zeecee_midi directory and its 3 .dae files should go in here:

.../Blender/[version number]/scripts/addons

Either clone the directory from here, or create a directory of this name and load the 3 .dae files into it.

# Update:

As of 18 April 2019, you will need to have PyGame and SoundDevice Python libraries loaded into Blender's Python area for the MIDI and Audio nodes to work. if you have these nodes installed and don't have these two libraries, Animation Nodes WILL NOT LOAD. Some day I will have a proper install for this, in the meantime I have added a zip file for MacOs ONLY that contains the site-packages directory for Blender 2.8, with the required libraries. Blender 2.8 now has pip so you can install these libraries much easier than in Blender 2.79.

I believe that these commands will successfully install the libraries:

You should make sure pip is installed by navigating to the blender python/bin directory then:

./python3.7m - m ensurepip

Then install the libraries (I think Windows might be python3.7m.exe)

./python3.7m -m pip install sounddevice

./python3.7m -m pip install pygame

NOTE! DAW nodes require PyPianoRoll and MatPlotLib:

./python3.7m -m pip install pypianoroll

./python3.7m -m pip install matplotlib


Let me know, via "Issues" if this fails and I will investigate.

# COMMENTS

Have fun and mail me clockmender@icloud.com with any questions. Operation is fairly intuitive, but be aware that the MIDI nodes require MIDI files in CSV format, not generic MIDI - search the web for a good converter - there are several out there, but this is the one I use:

http://www.fourmilab.ch/webtools/midicsv/

Comments will be gratefully received, along with improvement/enhancement suggestions.

# RELEASE NOTES

# INITIAL: 9 March 2019:

Opened branch for Blender 2.8, AN 2.1 All working nodes uploaded, there is one issue to resolve for the MIDI Bake Node in that the Bake to F-curve function is not yet fully functional. Tested against latest Blender 2.8 Beta form blender.org (dated 7 March 2019) and latest Test release of Animation Nodes 2.1 on MacOs only.

# EDIT: 25 March 2019:

Switch node added - switches between two inputs either at a fixed frame, or on an input condidtion. uses Dynamic Sockets, so first connected input determines socket type. To use Input condidtion, set frame to large number, e.g. beyond end frame of project as condition to switch from input A to input B is "Either Frame Exceeded, or Condition is True".

There are still some bugs in the nodes that create geometry as Blender methods have changed... I will look at these over the next week, or so.

# EDIT: 3 June 2019:

DAW Nodes and Base Blend file added, still experimental with no help files to date, _Caveat Emptor!_, but they have been checked to a reasonable degree. The containing folder, with its \_\_init\_\_.py file should be placed in the AN nodes directory.

Cheers, Clock.

PS. I am rebuilding my website: https://clockmender.uk but it will take some time. There will be a set of pages explaining how to use these nodes, I have started though!

PPS, there are examples of the use of these nodes in my Youtube:

https://www.youtube.com/channel/UCfOCIvThm1sCoG0NqZkgaAg/videos?shelf_id=0&view=0&sort=dd

Or look on https://blenderartists.org/forum/forumdisplay.php?16-Works-in-Progress - just search for me by name: "clockmender"
