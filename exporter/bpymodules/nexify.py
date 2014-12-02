# #!BPY

# """
# Name:    'Nexuiz (.map)'
# Blender: 243
# Group:   'Export'
# Tooltip: 'Export to Nexuiz map format'
# """

# __author__ = 'sergey bashkirov'
# __version__ = '0.14'
# __email__ = "bashkirov.sergey@gmail.com"
# __bpydoc__ = \
# """
# This script exports a Blender content to NetRadiant
# map format for Nexuiz.
# It supports meshes, lights and nurbs surfaces.
# """

from Blender import *
import BPyMesh
import os
import math
import string
from os import path
import btreemesh

class CNexify:
    def __init__( self ):
        # export options.
        self.g_nexuiz_path = "c:/programs/nexuiz"
        self.g_fname       = "mymap.map"
        self.g_scale = 64
        self.g_extrudeHeight = 0.3
        self.g_extrudeDownwards = 1
        self.g_print = 1
        self.g_def_texture = 'common/caulk'
        self.g_def_texture_ind = 1
        self.readRegistry()
        

    def nprint( self, stri ):
        if ( self.g_print ):
            print( stri )

    def readRegistry( self ):
        rdict = Registry.GetKey( 'nexify', True )
        if rdict:
            try:
                self.g_nexuiz_path      = rdict[ 'nexuiz_path' ]
                self.g_fname            = rdict[ 'file_name' ]
                self.g_scale            = rdict[ 'scale' ]
                self.g_extrudeHeight    = rdict[ 'extrude_height' ]
                self.g_extrudeDownwards = rdict[ 'extrude_downwards' ]
                self.g_print            = rdict[ 'print' ]
                self.g_def_texture      = rdict[ 'def_texture' ]
                self.g_def_texture_ind  = rdict[ 'def_texture_ind' ]
            except:
                self.updateRegistry()
        
    def updateRegistry( self ):
        d = {}
        d[ 'nexuiz_path' ]       = self.g_nexuiz_path
        d[ 'file_name' ]         = self.g_fname
        d[ 'scale' ]             = self.g_scale
        d[ 'extrude_height' ]    = self.g_extrudeHeight
        d[ 'extrude_downwards' ] = self.g_extrudeDownwards
        d[ 'print' ]             = self.g_print
        d[ 'def_texture' ]       = self.g_def_texture
        d[ 'def_texture_ind' ]   = self.g_def_texture_ind
        Registry.SetKey( 'nexify', d, True )


    def nexifyVector( self, x, y, z ):
        a = long( round( x * self.g_scale ) )
        b = long( round( y * self.g_scale ) )
        c = long( round( z * self.g_scale ) )
        return a, b, c


    def forceSelectedSurf( self ):
        #List copy because I modify it inside the loop.
        selList = Object.GetSelected()
        for obj in selList:
            if ( obj.getType() == 'Mesh' ):
                propsList = obj.getAllProperties()
                for prop in propsList:
                    if ( prop.getName() == 'surf' ):
                        obj.removeProperty( 'surf' )
                obj.addProperty( 'surf', '1', 'BOOL' )
                obj.makeDisplayList()
                
                
    def setTexture( self, index, texture ):
        selList = Object.GetSelected()
        for obj in selList:
            tp = obj.getType()
            if ( tp == 'Mesh' ):
                name = 'texture[%d]' % (index - 1)
                propsList = obj.getAllProperties()
                for prop in propsList:
                    if ( name == prop.getName() ):
                        obj.removeProperty( 'name' )
                        break
                obj.addProperty( name, texture )
                obj.makeDisplayList()
            elif ( tp == 'Surf' ):
                name = 'texture'
                propsList = obj.getAllProperties()
                for prop in propsList:
                    if ( name == prop.getName() ):
                        obj.removeProperty( 'name' )
                        break
                obj.addProperty( name, texture )
                obj.makeDisplayList()
                

    def prepare( self ):
        self.nprint( "*************************************************************" )
        self.nprint( "******************* Export to Nexuiz MAP ********************" )
        self.nprint( "*************************************************************" )
        res = 1
        # Disable edit mode!!!!
        edMode = Window.EditMode()
        if edMode:
            Window.EditMode( 0 )
        scene = Scene.GetCurrent()
        #List copy because I modify it inside the loop.
        objList = scene.objects
        extrudeList = []
        for obj in objList:
            self.nprint( "\n____________________________________________" )
            self.nprint( "inspecting object: " )
            self.nprint( "        type = " + obj.getType() )
            self.nprint( "        name = " + obj.getName() )
            if ( obj.getType() == 'Mesh' ):
                propsList = obj.getAllProperties()
                self.nprint( "        object properties:" )
                for prop in propsList:
                    self.nprint( "        " + prop.getName() + " = " + str( prop.getData() ) )
                skipObject = 0
                for prop in propsList:
                    if prop.getName() == 'ignore':
                        if prop.getData():
                            skipObject = 1
                            break
                if ( skipObject ):
                    self.nprint( "skipping this object due to 'ignore' property" )
                    continue
            elif ( obj.getType() == "Lamp" ):
                self.setLightDefaultFlags( obj );
        
        if ( edMode ):
            Window.EditMode( 1 )
        Window.RedrawAll()
        Redraw()
        return res


    def setLightDefaultFlags( self, obj ):
        propsList = obj.getAllProperties()
        # Currently I add special props: sun, has_target, target_x, target_y, target_z, radius.
        propsToAdd = [ "sun", "has_target", "target_x", "target_y", "target_z", "radius" ]
        propsAlreadyExist = []
        for prop in propsList:
            if ( propsToAdd.count( prop.getName() ) > 0 ):
                propsAlreadyExist.append( prop.getName() )
        for prop in propsToAdd:
            # If not exist
            if ( propsAlreadyExist.count( prop ) == 0 ):
                if ( prop == "sun" ):
                    obj.addProperty( prop, 0, 'BOOL' )
                elif ( prop == "has_target" ):
                    obj.addProperty( prop, 0, 'BOOL' )
                elif ( prop == "target_x" ):
                    obj.addProperty( prop, 0.0, 'FLOAT' )
                elif ( prop == "target_y" ):
                    obj.addProperty( prop, 0.0, 'FLOAT' )
                elif ( prop == "target_z" ):
                    obj.addProperty( prop, 0.0, 'FLOAT' )
                elif ( prop == "radius" ):
                    obj.addProperty( prop, 0.0, 'FLOAT' )
        obj.makeDisplayList()
    
    
    
    
    def writeFile( self ):
        self.nprint( 'Exporting:' )
        fname = self.g_nexuiz_path + "/data/maps/" + self.g_fname
        file = open( fname, 'w' )
        
        scene = Scene.GetCurrent()
        objList = scene.objects
        # Writing meshes.
        file.write( "// entity 0\n" )
        file.write( "{\n" )
        file.write( '    "classname" "worldspawn"\n' )
        for obj in objList:
            if ( obj.getType() == 'Mesh' ):
                skipObject = 0
                propList = obj.getAllProperties()
                for prop in propList:
                    if prop.getName() == 'ignore':
                        if prop.getData():
                            skipObject = 1
                            break
                if ( skipObject ):
                    self.nprint( "skipping this object due to 'ignore' property" )
                    continue
                self.writeMesh( file, obj )
        
        # Writing NURBS surfaces
        for obj in objList:
            if ( obj.getType() == 'Surf' ):
                skipObject = 0
                propList = obj.getAllProperties()
                for prop in propList:
                    if prop.getName() == 'ignore':
                        if prop.getData():
                            skipObject = 1
                            break
                if ( skipObject ):
                    self.nprint( "skipping this object due to 'ignore' property" )
                    continue
                self.writeSurf( file, obj )
                
        # End of worldspawn
        file.write( '}\n' )
        
        # Writing lamps.
        for obj in objList:
            if ( obj.getType() == "Lamp" ):
                propsList = obj.getAllProperties()
                skipObject = 0
                for prop in propsList:
                    if prop.getName() == 'ignore':
                        if prop.getData():
                            skipObject = 1
                            break
                if ( skipObject ):
                    self.nprint( "skipping this object due to 'ignore' property" )
                    continue
                self.writeLamp( file, obj )
                
        file.close()
    
    
    def writeMesh( self, file, obj ):
        btMesh = btreemesh.CBTreeMesh( self )
        btMesh.name = obj.getName()
        stri = btMesh.export( obj, self.g_nexuiz_path )
        file.write( stri )
    
    
    def writeLamp( self, file, obj ):
        lamp = obj.data
        stri = '{\n    "classname" "light"\n'
        stri = stri + '    "light" %.6f\n' % ( lamp.dist * self.g_scale )
        r = obj.getLocation( 'worldspace' )
        x, y, z = self.nexifyVector( r[0], r[1], r[2] )
        stri = stri + ( '    "origin" "%d %d %d"\n' % (x, y, z) )
        stri = stri + ( '    "_color" "%.6f %.6f %.6f"\n' % tuple(lamp.col) )
        stri = stri + ( '    "style" "0"\n' )
        propsList = obj.getAllProperties()
        has_target = 0
        for prop in propsList:
            name = prop.getName()
            if ( name == "sun" ):
                if ( prop.getData() ):
                    stri = stri + '    "sun" "1"\n'
            elif ( name == "has_target" ):
                if ( prop.getData() ):
                    has_target = 1
                    target_x, target_y, targer_z = 0, 0, 0
                    radius = 0
            elif ( name == "target_x" ):
                target_x = prop.getData()
            elif ( name == "target_y" ):
                target_y = prop.getData()
            elif ( name == "target_z" ):
                target_z = prop.getData()
            elif ( name == "radius" ):
                radius = prop.getData()
        if ( has_target ):
            stri = stri + ( '    "target" "%.8f %.8f %.8f"' % ( target_x, target_y, target_z ) )
            stri = stri + ( '    "radius" "%.8f"\n' % ( radius ) )
        
        stri = stri + "}\n"
        file.write( stri )
    

    def writeSurf( self, file, obj ):
        data  = obj.getData()
        matr     = obj.matrixWorld
        
        nurbsList = []
        for curve in data:
            t = str( type( curve ) )
            self.nprint( "type is: " + t )
            
            if ( t.find( 'SurfNurb' ) >= 0 ):
                nurbsList.append( curve )
        
        stri = ""
        for nurb in nurbsList:
            u, v = nurb.pointsU, nurb.pointsV
            if ( u > 2 ) and ( v > 2 ):
                uOrig = u
                # NetRadiant doesn't understand surfs with resolution more then 31
                if ( u > 31 ):
                    self.nprint( "WARNING: surface U resolution reduced to 31" )
                    u = 31
                if ( v > 31 ):
                    self.nprint( "WARNING: surface V resolution reduced to 31" )
                    v = 31
                # NetRadiant understands only odd resolution
                if ( u % 2 ) == 0:
                    u -= 1
                    self.nprint( "WARNING: surface U resolution reduced to " + str( u ) )
                if ( v % 2 ) == 0:
                    v -= 1
                    self.nprint( "WARNING: surface V resolution reduced to " + str( v ) )
                
                stri = stri + "    // patch from surface '" + obj.getName() + "'\n"
                stri = stri + "    {\n"
                stri = stri + "        patchDef2\n"
                stri = stri + "        {\n"
                
                # Somewhy there are 0 materials even if object has a few.
                # using prop to store texture.
                texture = 'common/caulk'
                propsList = obj.getAllProperties()
                for prop in propsList:
                    name = prop.getName()
                    if ( name == 'texture' ):
                        texture = prop.getData()
                        break
                
                stri = stri + "            " + texture + "\n"
                
                # patch resolution
                stri = stri + ( "            ( %d %d 0 0 0 )\n" % ( u, v ) )
                stri = stri +   "            (\n"
                
                for i in range(v):
                    for j in range(u):
                        ptInd = uOrig * i + j
                        
                        if ( j == 0 ):
                            stri = stri + "                ("
                            
                        pt = nurb[ptInd]
                        x, y, z, tu, tv = pt[0:5]
                        vect = Mathutils.Vector( (x, y, z) ) * matr
                        x, y, z = self.nexifyVector( vect.x, vect.y, vect.z )
                        
                        stri = stri + ( " ( %d %d %d %.8f %.8f )" % ( x, y, z, tu, tv ) )
                        
                        if ( j == u-1 ):
                            stri = stri + " )\n"
                        
                stri = stri + "            )\n"
                stri = stri + "        }\n"
                stri = stri + "    }\n"
        file.write( stri )


