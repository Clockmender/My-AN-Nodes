# My-AN-Nodes

Copyright (C) 2017 Alan Odom
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
    
AIMS & OBJECTIVES:

The initial reason behind developing these nodes was to provide a system to read MIDI files and produce animations from them, rather than having to keyframe everything - a long and labour intensive process.

From there, I have developed other nodes that take complex tasks, with standard nodes, and turn them into easily achievable node trees. Everything these nodes do can be done with either script nodes, or expression nodes, but that requires a great deal of knowledge of Python and Blender structures, so these nodes take all that away.

I also added a "Bone" socket to allow for easy manipulation of bones in AN. I know this can be done without the new socket and nodes built around it. However, the collection of bone nodes make it easier to animate bones without having to use script, or expression nodes.

Some of the nodes are very "niche" in what they do, but they make my life as an animator easier, in that they take away the need to develop complex python code in script nodes each time I want to do something out of the ordinary (this happens a lot!).

Some nodes, particularly the DAW ones, may be "experimental" and are included for collaboration purposes, they are not yet ready for full production. On-going experimentation has always been part of my IT objectives and I am quite happy to share this code here and open it up to critique and comment.

If you would like to help with development, or suggest more nodes you would find useful, please contact me via email.

GENERAL:

These nodes are to add to Version 2.0 or Animation Nodes, which requires official releases from Blender, i.e. NOT Buildbot versions!

They come with no warranty, but have been extensively tested. I will produce a help file later, as time permits.

INSTALLATION

The bone.py file should go in this directory:

.../Blender/[version number]/scripts/addons/animation_nodes/sockets

The node_menu.py should go in this directory:

.../Blender/[version number]/scripts/addons/animation_nodes/ui

to replace the one that is already there - keep a backup copy of the original in a safe place somewhere else.

The other files should go into a new folder in this directory:

.../Blender/[version number]/scripts/addons/animation_nodes/nodes

That new directory should contain an empty file named \_init_\.py - create this with any text editor or copy one from another AN directory.

COMMENTS

Have fun and mail me clockmender@icloud.com with any questions. Operation is fairly intuitive, but be aware that the MIDI nodes require MIDI files in CSV format, not generic MIDI - search the web for a good converter - there are several out there, but this is the one I use:

http://www.fourmilab.ch/webtools/midicsv/

Comments will be gratefully received, along with improvement/enhancement suggestions.

RELEASE NOTES

EDIT 12 Feb 2018:

I have added the Materials nodes, Input and Output, don't forget that if you only want one or two of these, just load these into an empty folder in animation_nodes/nodes directory and don't forget the empty \_init_\.py file in the folder, or they won't work.

Some updates may not be included in the latest release, the code can be obtained from the idividual files if required. All updates have a date when they were uploaded.

EDIT 26 Feb 2019:

Updated the repo with the latest nodes today. MIDI nodes have been altered to reflect increased knowledge by myself and better working methods. MIDI/AUDO Live nodes are now loaded for user testing, these nodes are designed to take input from MIDI devices and sound input to drive animations.

DAW nodes are new and VERY EXPERIMENTAL, i.e. not ready for use, they are here for collaboration purposes just now and require a great deal more work.

Menu has been altered to separate the "Clockworx" and "ZeeCee MIDI" sections, DAW nodes are not in the menu yet.

I have not included a relaease at this stage, nor have I updated the manual pages on my website yet.

I need to make the Live MIDI into an Add-on at some stage, or maybe even all the nodes, but this will require more time.

My Vimeo Channel https://vimeo.com/user85352464

EDIT 28 Feb 2019:

Major revisions and new release- 2.0.3

EDIT 3 Mar 2019:

Changed directory structure to separate nodes, menus and sockets, searated ndoes in DAW, MIDI and General

Cheers, Clock.

PS. I am rebuilding my website: https://clockmender.uk but it will take some time. There will be a set of pages explaining how to use these nodes, I have started though!

PPS, there are examples of the use of these nodes in my Youtube:

https://www.youtube.com/channel/UCfOCIvThm1sCoG0NqZkgaAg/videos?shelf_id=0&view=0&sort=dd

Or look on https://blenderartists.org/forum/forumdisplay.php?16-Works-in-Progress - just search for me by name: "clockmender"
