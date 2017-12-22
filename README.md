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
    

These nodes are to add to Version 2.0 or Animation Nodes, which requires official releases from Blender, i.e. NOT Buildbot versions!

They come with no warranty, but have been extensively tested. I will produce a help file later, as time permits.

The bone.py file should go in this directory:

.../Blender/[version number]/scripts/addons/animation_nodes/sockets

The node_menu.py should go in this directory:

.../Blender/[version number]/scripts/addons/animation_nodes/ui

to replace the one that is already there - keep a backup copy of the original in a safe place somewhere else.

The other files should go into a new folder in this directory:

.../Blender/[version number]/scripts/addons/animation_nodes/nodes

That new directory should contain an empty file named \_init_\.py - create this with any text editor or copy one from another AN directory.

Have fun and mail me clockmender@icloud.com with any questions. Operation is fairly intuitive, but be aware that the MIDI nodes require MIDI files in CSV format, not generic MIDI - search the web for a good converter - there are several out there, but this is the one I use:

http://www.fourmilab.ch/webtools/midicsv/

Comments will be gratefully received, along with improvement/enhancement suggestions.

Cheers, Clock.

PS, there are examples of the use of these nodes in my Youtube:

https://www.youtube.com/channel/UCfOCIvThm1sCoG0NqZkgaAg/videos?shelf_id=0&view=0&sort=dd

Or look on https://blenderartists.org/forum/forumdisplay.php?16-Works-in-Progress - just search for me by name: "clockmender"
