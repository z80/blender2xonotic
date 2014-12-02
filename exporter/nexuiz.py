#!BPY

"""
Name:    'Nexuiz (.map)'
Blender: 243
Group:   'Export'
Tooltip: 'Export to Nexuiz map format'
"""

__author__ = 'sergey bashkirov'
__version__ = '0.17'
__email__ = "bashkirov.sergey@gmail.com"
__bpydoc__ = \
"""
This script exports a Blender geometry to NetRadiant
map format for Nexuiz.
It supports meshes, lights and nurbs surfaces.
In uses Blender logic properties to store additional 
parameters for texture shaders and light properties.
"""

#Created with The_Nerd's GUI creator V2.500000

import Blender
from Blender import Draw, BGL, Window
from Blender.BGL import *
from nexify import CNexify
# Debuggind tools.
# import rpdb2; rpdb2.start_embedded_debugger( "1" )

nexify = CNexify()

EVENT_gui_exit = 10
EVENT_gui_instruction = 11
EVENT_gui_prepare = 12
EVENT_gui_export = 13
EVENT_gui_nexuizPath = 14
EVENT_gui_fileName = 15
EVENT_Text = 16
EVENT_Text_0 = 17
EVENT_gui_scale = 18
EVENT_Text_1 = 19
EVENT_gui_extrudeHeight = 20
EVENT_Text_2 = 21
EVENT_gui_extrudeDownwards = 22
EVENT_Text_3 = 23
EVENT_gui_echo = 24
EVENT_Text_4 = 25
EVENT_Text_5 = 26
EVENT_Text_6 = 27
EVENT_Text_7 = 28
EVENT_Text_8 = 29
EVENT_Text_9 = 30
EVENT_Text_10 = 31
EVENT_Text_11 = 32
EVENT_Text_12 = 33
EVENT_Text_13 = 34
EVENT_Text_14 = 35
EVENT_Text_15 = 36
EVENT_gui_version = 37
EVENT_Text_16 = 38
EVENT_gui_exportSurf = 39
EVENT_Text_17 = 40
EVENT_gui_textureStri = 41
EVENT_name_textureInd = 42
EVENT_Text_18 = 43
EVENT_gui_textureBtn = 44
Object_gui_exit = Draw.Create(0.0)
Object_gui_instruction = Draw.Create(0)
Object_gui_prepare = Draw.Create(0.0)
Object_gui_export = Draw.Create(0.0)
Object_gui_nexuizPath = Draw.Create( nexify.g_nexuiz_path )
Object_gui_fileName = Draw.Create( nexify.g_fname )
Object_Text = Draw.Create(0)
Object_Text_0 = Draw.Create(0)
Object_gui_scale = Draw.Create( nexify.g_scale )
Object_Text_1 = Draw.Create(0)
Object_gui_extrudeHeight = Draw.Create( nexify.g_extrudeHeight )
Object_Text_2 = Draw.Create(0)
Object_gui_extrudeDownwards = Draw.Create( nexify.g_extrudeDownwards )
Object_Text_3 = Draw.Create(0)
Object_gui_echo = Draw.Create( nexify.g_print )
Object_Text_4 = Draw.Create(0)
Object_Text_5 = Draw.Create(0)
Object_Text_6 = Draw.Create(0)
Object_Text_7 = Draw.Create(0)
Object_Text_8 = Draw.Create(0)
Object_Text_9 = Draw.Create(0)
Object_Text_10 = Draw.Create(0)
Object_Text_11 = Draw.Create(0)
Object_Text_12 = Draw.Create(0)
Object_Text_13 = Draw.Create(0)
Object_Text_14 = Draw.Create(0)
Object_Text_15 = Draw.Create(0)
Object_gui_version = Draw.Create("")
Object_Text_16 = Draw.Create("")
Object_gui_exportSurf = Draw.Create(0.0)
Object_Text_17 = Draw.Create("")
Object_gui_textureStri = Draw.Create( nexify.g_def_texture )
Object_name_textureInd = Draw.Create( nexify.g_def_texture_ind )
Object_Text_18 = Draw.Create("")
Object_gui_textureBtn = Draw.Create(0)


def saveParams():
    global nexify
    nexify.g_nexuiz_path      = Object_gui_nexuizPath.val
    nexify.g_fname            = Object_gui_fileName.val
    nexify.g_scale            = Object_gui_scale.val
    nexify.g_extrudeHeight    = Object_gui_extrudeHeight.val
    nexify.g_extrudeDownwards = Object_gui_extrudeDownwards.val
    nexify.g_print            = Object_gui_echo.val
    nexify.g_def_texture      = Object_gui_textureStri.val
    nexify.g_def_texture_ind  = Object_name_textureInd.val
    nexify.updateRegistry()


def draw():
    global EVENT_gui_exit
    global EVENT_gui_instruction
    global EVENT_gui_prepare
    global EVENT_gui_export
    global EVENT_gui_nexuizPath
    global EVENT_gui_fileName
    global EVENT_Text
    global EVENT_Text_0
    global EVENT_gui_scale
    global EVENT_Text_1
    global EVENT_gui_extrudeHeight
    global EVENT_Text_2
    global EVENT_gui_extrudeDownwards
    global EVENT_Text_3
    global EVENT_gui_echo
    global EVENT_Text_4
    global EVENT_Text_5
    global EVENT_Text_6
    global EVENT_Text_7
    global EVENT_Text_8
    global EVENT_Text_9
    global EVENT_Text_10
    global EVENT_Text_11
    global EVENT_Text_12
    global EVENT_Text_13
    global EVENT_Text_14
    global EVENT_Text_15
    global EVENT_gui_version
    global EVENT_Text_16
    global EVENT_gui_exportSurf
    global EVENT_Text_17
    global EVENT_gui_textureStri
    global EVENT_name_textureInd
    global EVENT_Text_18
    global EVENT_gui_textureBtn
    global Object_gui_exit
    global Object_gui_instruction
    global Object_gui_prepare
    global Object_gui_export
    global Object_gui_nexuizPath
    global Object_gui_fileName
    global Object_Text
    global Object_Text_0
    global Object_gui_scale
    global Object_Text_1
    global Object_gui_extrudeHeight
    global Object_Text_2
    global Object_gui_extrudeDownwards
    global Object_Text_3
    global Object_gui_echo
    global Object_Text_4
    global Object_Text_5
    global Object_Text_6
    global Object_Text_7
    global Object_Text_8
    global Object_Text_9
    global Object_Text_10
    global Object_Text_11
    global Object_Text_12
    global Object_Text_13
    global Object_Text_14
    global Object_Text_15
    global Object_gui_version
    global Object_Text_16
    global Object_gui_exportSurf
    global Object_Text_17
    global Object_gui_textureStri
    global Object_name_textureInd
    global Object_Text_18
    global Object_gui_textureBtn
    
    global nexify

    BGL.glClearColor(0.500000, 0.500000, 0.500000, 0.0)
    BGL.glClear(GL_COLOR_BUFFER_BIT)

    BGL.glColor3f(0.000000, 0.000000, 0.000000)
    Object_gui_exit = Draw.Button("Exit", EVENT_gui_exit, 8, 8, 76, 44, "Exit exporter")
    BGL.glRasterPos2i(64, 560)
    Object_gui_instruction = Draw.Text("Exporter  to MAP format for Nexuiz community")
    Object_gui_prepare = Draw.Button("Prepare", EVENT_gui_prepare, 88, 8, 76, 44, "Prepares for export: checks is all meshes are convex")
    Object_gui_export = Draw.Button("Export", EVENT_gui_export, 168, 8, 76, 44, "Exports prepared scene to a MAP file")
    Object_gui_nexuizPath = Draw.String("", EVENT_gui_nexuizPath, 152, 320, 148, 20, Object_gui_nexuizPath.val, 399, "Nexuiz absolute path")
    Object_gui_fileName = Draw.String("", EVENT_gui_fileName, 152, 296, 148, 20, Object_gui_fileName.val, 399, "MAP file name")
    BGL.glRasterPos2i(16, 328)
    Object_Text = Draw.Text("Nexuiz absolute path")
    BGL.glRasterPos2i(16, 304)
    Object_Text_0 = Draw.Text("MAP file name")
    Object_gui_scale = Draw.Number("", EVENT_gui_scale, 152, 272, 76, 20, Object_gui_scale.val, 0.000000, 1024.000000, "")
    BGL.glRasterPos2i(16, 280)
    Object_Text_1 = Draw.Text("Scale factor")
    Object_gui_extrudeHeight = Draw.Number("", EVENT_gui_extrudeHeight, 152, 248, 76, 20, Object_gui_extrudeHeight.val, 0.000000, 1024.000000, "")
    BGL.glRasterPos2i(16, 256)
    Object_Text_2 = Draw.Text("Extrude height")
    Object_gui_extrudeDownwards = Draw.Toggle("downwards", EVENT_gui_extrudeDownwards, 152, 224, 76, 20, Object_gui_extrudeDownwards.val, "")
    BGL.glRasterPos2i(16, 232)
    Object_Text_3 = Draw.Text("Extrude downwards")
    Object_gui_echo = Draw.Toggle("echo", EVENT_gui_echo, 152, 200, 76, 20, Object_gui_echo.val, "")
    BGL.glRasterPos2i(16, 208)
    Object_Text_4 = Draw.Text("Console echo")
    BGL.glRasterPos2i(32, 536)
    Object_Text_5 = Draw.Text("Brief instruction:")
    BGL.glRasterPos2i(8, 504)
    Object_Text_6 = Draw.Text("Exporter currently work with meshes, lights and nurbs surfaces.")
    BGL.glRasterPos2i(368, 504)
    Object_Text_7 = Draw.Text("As far as meshes are converted into NetRadiant brushes they should be convex")
    BGL.glRasterPos2i(8, 480)
    Object_Text_8 = Draw.Text("Concave meshes are splitted into individual faces. Faces after that are extruded on \"Extrude height\" parameter (see below).")
    BGL.glRasterPos2i(8, 456)
    Object_Text_9 = Draw.Text("As far as objects in NetRadiant may have properties different then objects in Blender game logic properties are used to store such params.")
    BGL.glRasterPos2i(8, 432)
    Object_Text_10 = Draw.Text("Possible mesh params: ignore(BOOL), convex(BOOL)")
    BGL.glRasterPos2i(8, 408)
    Object_Text_11 = Draw.Text("Possible light params: sun(BOOL), has_target(BOOL), target_x, target_y, target_z(FLOAT), radius(float)")
    BGL.glRasterPos2i(8, 64)
    Object_Text_12 = Draw.Text("First press PREPARE, then press EXPORT.")
    BGL.glRasterPos2i(8, 384)
    Object_Text_13 = Draw.Text("Due to Blender doesn't understand Radiant shaders one may use texture[i](STRING) properties, to overwrite texture files with shaders(i = material index).")
    BGL.glRasterPos2i(8, 84)
    Object_Text_14 = Draw.Text("REMEMBER: textures are to be on \".../nexuiz/data/textures\" subpath!")
    BGL.glRasterPos2i(272, 24)
    Object_Text_15 = Draw.Text("Ver")
    BGL.glRasterPos2i(304, 24)
    Object_gui_version = Draw.Text( __version__ )
    BGL.glRasterPos2i(16, 176)
    Object_Text_16 = Draw.Text("Focre selected surf")
    Object_gui_exportSurf = Draw.Button("Treat selected as surf when export", EVENT_gui_exportSurf, 152, 168, 212, 20, "")
    BGL.glRasterPos2i(16, 136)
    Object_Text_17 = Draw.Text("Overwrite texture")
    Object_gui_textureStri = Draw.String("", EVENT_gui_textureStri, 192, 132, 104, 20, Object_gui_textureStri.val, 399, "")
    Object_name_textureInd = Draw.Number("", EVENT_name_textureInd, 392, 132, 60, 20, Object_name_textureInd.val, 1.000000, 128.000000, "")
    BGL.glRasterPos2i(304, 140)
    Object_Text_18 = Draw.Text("material index")
    Object_gui_textureBtn = Draw.Button("over", EVENT_gui_textureBtn, 152, 132, 32, 20, "Overwrite selected object texture with the following.")


def event(event, value):
    _Input_Events_Callback(event, value)

def b_event(event):
    global EVENT_gui_exit
    global EVENT_gui_instruction
    global EVENT_gui_prepare
    global EVENT_gui_export
    global EVENT_gui_nexuizPath
    global EVENT_gui_fileName
    global EVENT_Text
    global EVENT_Text_0
    global EVENT_gui_scale
    global EVENT_Text_1
    global EVENT_gui_extrudeHeight
    global EVENT_Text_2
    global EVENT_gui_extrudeDownwards
    global EVENT_Text_3
    global EVENT_gui_echo
    global EVENT_Text_4
    global EVENT_Text_5
    global EVENT_Text_6
    global EVENT_Text_7
    global EVENT_Text_8
    global EVENT_Text_9
    global EVENT_Text_10
    global EVENT_Text_11
    global EVENT_Text_12
    global EVENT_Text_13
    global EVENT_Text_14
    global EVENT_Text_15
    global EVENT_gui_version
    global EVENT_Text_16
    global EVENT_gui_exportSurf
    global EVENT_Text_17
    global EVENT_gui_textureStri
    global EVENT_name_textureInd
    global EVENT_Text_18
    global EVENT_gui_textureBtn
    global Object_gui_exit
    global Object_gui_instruction
    global Object_gui_prepare
    global Object_gui_export
    global Object_gui_nexuizPath
    global Object_gui_fileName
    global Object_Text
    global Object_Text_0
    global Object_gui_scale
    global Object_Text_1
    global Object_gui_extrudeHeight
    global Object_Text_2
    global Object_gui_extrudeDownwards
    global Object_Text_3
    global Object_gui_echo
    global Object_Text_4
    global Object_Text_5
    global Object_Text_6
    global Object_Text_7
    global Object_Text_8
    global Object_Text_9
    global Object_Text_10
    global Object_Text_11
    global Object_Text_12
    global Object_Text_13
    global Object_Text_14
    global Object_Text_15
    global Object_gui_version
    global Object_Text_16
    global Object_gui_exportSurf
    global Object_Text_17
    global Object_gui_textureStri
    global Object_name_textureInd
    global Object_Text_18
    global Object_gui_textureBtn

    if event == 0: pass
    elif event == EVENT_gui_exit:
        gui_exit_Callback()
    elif event == EVENT_gui_instruction:
        gui_instruction_Callback()
    elif event == EVENT_gui_prepare:
        gui_prepare_Callback()
    elif event == EVENT_gui_export:
        gui_export_Callback()
    elif event == EVENT_gui_nexuizPath:
        gui_nexuizPath_Callback()
    elif event == EVENT_gui_fileName:
        gui_fileName_Callback()
    elif event == EVENT_Text:
        Text_Callback()
    elif event == EVENT_Text_0:
        Text_0_Callback()
    elif event == EVENT_gui_scale:
        gui_scale_Callback()
    elif event == EVENT_Text_1:
        Text_1_Callback()
    elif event == EVENT_gui_extrudeHeight:
        gui_extrudeHeight_Callback()
    elif event == EVENT_Text_2:
        Text_2_Callback()
    elif event == EVENT_gui_extrudeDownwards:
        gui_extrudeDownwards_Callback()
    elif event == EVENT_Text_3:
        Text_3_Callback()
    elif event == EVENT_gui_echo:
        gui_echo_Callback()
    elif event == EVENT_Text_4:
        Text_4_Callback()
    elif event == EVENT_Text_5:
        Text_5_Callback()
    elif event == EVENT_Text_6:
        Text_6_Callback()
    elif event == EVENT_Text_7:
        Text_7_Callback()
    elif event == EVENT_Text_8:
        Text_8_Callback()
    elif event == EVENT_Text_9:
        Text_9_Callback()
    elif event == EVENT_Text_10:
        Text_10_Callback()
    elif event == EVENT_Text_11:
        Text_11_Callback()
    elif event == EVENT_Text_12:
        Text_12_Callback()
    elif event == EVENT_Text_13:
        Text_13_Callback()
    elif event == EVENT_Text_14:
        Text_14_Callback()
    elif event == EVENT_Text_15:
        Text_15_Callback()
    elif event == EVENT_gui_version:
        gui_version_Callback()
    elif event == EVENT_Text_16:
        Text_16_Callback()
    elif event == EVENT_gui_exportSurf:
        gui_exportSurf_Callback()
    elif event == EVENT_Text_17:
        Text_17_Callback()
    elif event == EVENT_gui_textureStri:
        gui_textureStri_Callback()
    elif event == EVENT_name_textureInd:
        name_textureInd_Callback()
    elif event == EVENT_Text_18:
        Text_18_Callback()
    elif event == EVENT_gui_textureBtn:
        gui_textureBtn_Callback()
    Draw.Draw()

Draw.Register(draw, event, b_event)

##---Begin user code---

def _Input_Events_Callback(Event, Value):
    if Event == Draw.ESCKEY and not Value: Draw.Exit()

def gui_exit_Callback():
    #***Place your code for Object gui_exit here***#
    Draw.Exit()
    pass

def gui_instruction_Callback():
    #***Place your code for Object gui_instruction here***#
    pass

def gui_prepare_Callback():
    #***Place your code for Object gui_prepare here***#
    global nexify
    saveParams()
    nexify.prepare()
    pass

def gui_export_Callback():
    #***Place your code for Object gui_export here***#
    global nexify
    saveParams()
    nexify.writeFile()
    pass

def gui_nexuizPath_Callback():
    #***Place your code for Object gui_nexuizPath here***#
    pass

def gui_fileName_Callback():
    #***Place your code for Object gui_fileName here***#
    pass

def Text_Callback():
    #***Place your code for Object Text here***#
    pass

def Text_0_Callback():
    #***Place your code for Object Text_0 here***#
    pass

def gui_scale_Callback():
    #***Place your code for Object gui_scale here***#
    pass

def Text_1_Callback():
    #***Place your code for Object Text_1 here***#
    pass

def gui_extrudeHeight_Callback():
    #***Place your code for Object gui_extrudeHeight here***#
    pass

def Text_2_Callback():
    #***Place your code for Object Text_2 here***#
    pass

def gui_extrudeDownwards_Callback():
    #***Place your code for Object gui_extrudeDownwards here***#
    pass

def Text_3_Callback():
    #***Place your code for Object Text_3 here***#
    pass

def gui_echo_Callback():
    #***Place your code for Object gui_echo here***#
    pass

def Text_4_Callback():
    #***Place your code for Object Text_4 here***#
    pass

def Text_5_Callback():
    #***Place your code for Object Text_5 here***#
    pass

def Text_6_Callback():
    #***Place your code for Object Text_6 here***#
    pass

def Text_7_Callback():
    #***Place your code for Object Text_7 here***#
    pass

def Text_8_Callback():
    #***Place your code for Object Text_8 here***#
    pass

def Text_9_Callback():
    #***Place your code for Object Text_9 here***#
    pass

def Text_10_Callback():
    #***Place your code for Object Text_10 here***#
    pass

def Text_11_Callback():
    #***Place your code for Object Text_11 here***#
    pass

def Text_12_Callback():
    #***Place your code for Object Text_12 here***#
    pass

def Text_13_Callback():
    #***Place your code for Object Text_13 here***#
    pass

def Text_14_Callback():
    #***Place your code for Object Text_14 here***#
    pass

def Text_15_Callback():
    #***Place your code for Object Text_15 here***#
    pass

def gui_version_Callback():
    #***Place your code for Object gui_version here***#
    pass

def Text_16_Callback():
    #***Place your code for Object Text_16 here***#
    pass

def gui_exportSurf_Callback():
    #***Place your code for Object gui_exportSurf here***#
    global nexify
    nexify.forceSelectedSurf()
    pass

def Text_17_Callback():
    #***Place your code for Object Text_17 here***#
    pass

def gui_textureStri_Callback():
    #***Place your code for Object gui_textureStri here***#
    pass

def name_textureInd_Callback():
    #***Place your code for Object name_textureInd here***#
    pass

def Text_18_Callback():
    #***Place your code for Object Text_18 here***#
    pass

def gui_textureBtn_Callback():
    #***Place your code for Object gui_textureBtn here***#
    global nexify
    saveParams()
    nexify.setTexture( Object_name_textureInd.val, Object_gui_textureStri.val )
    pass

