
# __author__ = 'sergey bashkirov'
# __version__ = '0.18'
# __email__ = "bashkirov.sergey@gmail.com"
# __bpydoc__ = \
# """
# This script exports a Blender content to NetRadiant
# map format for Nexuiz.
# It supports meshes, lights and nurbs surfaces.
# """

'''
    unsigned sqrt_cpu_newton(long L)
    {
        long temp, div = L; 
        unsigned rslt = (unsigned)L; 
        if (L <= 0) return 0; 
        while (l)
        {
            temp = L/div + div; 
            div = temp >> 1; 
            div += temp & 1; 
            if (rslt > div) rslt = (unsigned)div; 
            else 
            {
            if (l/rslt == rslt-1 && l%rslt==0) reslt--; 
            return rslt; 
            }
        }
    }
'''

import math
import os
from os import path


def nsqrt( L ):
    # x = long(L)
    # div = x
    # res = x
    # if ( x <= 0L ):
        # return 0L
    # while ( 1 ):
        # temp = x/div + div
        # div = temp / 2L + ( temp % 2L )
        # if ( res > div ):
            # res = div
        # else:
            # if ( L/res == res-1L ) and ( L % res == 0L ):
                # res -= 1L
            # return res
    return math.sqrt( L )


class CBTreeMesh:
    def __init__( self, nexify ):
        self.name        = 'Unnamed mesh'
        self.nexify      = nexify
        nexify.btreemesh = self
        self.planes      = []
        self.faces       = []
        self.verts       = []
        self.children    = []
        self.textures    = []
        self.planePoints = []
        
        self.surf = 0
        self.removeRemotePlanes = 0
        
        # It's of long type, not float!
        self.scale = 65536.0
        self.planeCosDiff  = long( math.cos( (90.0 - 3.0) / 180.0 * 3.1415926535 ) * self.scale )
        self.planeCosIdent = long( math.cos( 3.0 / 180.0 * 3.1415926535 ) * self.scale )
    
    
    
    def nprint( self, stri ):
        self.nexify.nprint( stri )
    
    
    
    def export( self, obj, nexuizPath ):
        '''
        This is the main function calling all others.
        '''
        # Mesh
        mesh = obj.getData()
        # Props
        pr = obj.getAllProperties()
        props = {}
        for prop in pr:
            props[ prop.getName() ] = prop.getData()
        if ( 'surf' in props ):
            self.surf = props[ 'surf' ]
        # Prepare material names.
        self.prepareTextures( mesh, nexuizPath, props )
        # Adding geometry
        self.setFaces( obj )
        
        # Splitting into convex regions.
        self.splitIntoConvex()
        
        # Exporting to string.
        self.stri = ''
        self.exportGeometry( self )
        return self.stri
    
    
    
    def setFaces( self, obj ):
        self.faces   = []
        self.facesUv = []
        self.verts   = []
        
        mesh = obj.getData()

        faces = mesh.faces
        for face in faces:
            f = []
            for v in face.v:
                f.append( v.index )
            self.faces.append( f )
            
            if len( face.uv ) == len( face.v ):
                uvList = []
                for uv in face.uv:
                    uvList.append( [ uv[0], uv[1], face.materialIndex ] )
                self.facesUv.append( uvList )
            else:
                uvList = []
                # By hands to avoid absence of inverse matrix
                uvList.append( [ 0, 0, face.materialIndex ] )
                uvList.append( [ 1, 0, face.materialIndex ] )
                uvList.append( [ 0, 1, face.materialIndex ] )
                if ( len( face ) > 3 ):
                    uvList.append( [ 1, 1, face.materialIndex ] )
                self.facesUv.append( uvList )
                
        
        m = obj.matrixWorld
        verts = mesh.verts
        for vert in verts:
            v = vert.co * m
            x, y, z = v.x * self.nexify.g_scale, \
                      v.y * self.nexify.g_scale, \
                      v.z * self.nexify.g_scale
            self.verts.append( [ x, y, z ] )
            
        self.triangulate()
        
        
    def triangulate( self ):
        faces = []
        facesUv = []
        for i in range( len( self.faces ) ):
            face   = self.faces[i]
            faceUv = self.facesUv[i]
            faces.append( [ face[0], face[1], face[2] ] )
            facesUv.append( [ faceUv[0], faceUv[1], faceUv[2] ] )
            if len( face ) > 3:
                faces.append( [ face[2], face[3], face[0] ] )
                facesUv.append( [ faceUv[2], faceUv[3], faceUv[0] ] )
        self.faces   = faces
        self.facesUv = facesUv
    
    def faceNormal( self, face ):
        x1, y1, z1 = self.verts[ face[0] ][0], self.verts[ face[0] ][1], self.verts[ face[0] ][2]
        x2, y2, z2 = self.verts[ face[1] ][0], self.verts[ face[1] ][1], self.verts[ face[1] ][2]
        x3, y3, z3 = self.verts[ face[2] ][0], self.verts[ face[2] ][1], self.verts[ face[2] ][2]
        nx = (y2-y1)*(z3-z1)-(y3-y1)*(z2-z1)
        ny = (x3-x1)*(z2-z1)-(x2-x1)*(z3-z1)
        nz = (x2-x1)*(y3-y1)-(x3-x1)*(y2-y1)
        return nx, ny, nz
    
    def cross( self, ax, ay, az, bx, by, bz ):
        cx = ay * bz - az * by
        cy = az * bx - ax * bz
        cz = ax * by - ay * bx
        return cx, cy, cz
        
    def normalize( self, x, y, z ):
        l = nsqrt( x * x + y * y + z * z )
        return x / l, \
               y / l, \
               z / l
    
    
    def cut( self, face ):
        self.nprint( "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" )
        self.nprint( "    cutting mesh into two submeshes:" )
        self.children = []
        # plane normal
        nx, ny, nz = self.faceNormal( face )
        # plane D coefficient
        i = face[0]
        d = -( self.verts[ i ][0] * nx + self.verts[ i ][1] * ny + self.verts[ i ][2] * nz )
        self.nprint( "plane:  %d, %d %d %d" % ( nx,  ny,  nz, d ) )
        
        i = self.faces.index( face )
        faceUv = self.facesUv[i]
        
        # Outwards plane.
        plA = CDivPlane()
        plA.set( nx, ny, nz, d )
        plA.face = face
        plA.faceUv = faceUv
        
        # Inwards plane.
        plB = CDivPlane()
        plB.set( -nx, -ny, -nz, -d )
        plB.face = face[ len(face)::-1 ]
        plB.faceUv = faceUv[ len(faceUv)::-1 ]
        
        # Remove face from faces list.
        # In each sumbesh it is substituted with sectioning plane.
        self.faces.remove( face )
        self.facesUv.remove( faceUv )
        
        meshA = CBTreeMesh( self.nexify )
        meshA.name = self.name + ".1"
        meshA.textures = self.textures
        meshA.planes.extend( self.planes )
        meshA.planes.append( plA )
        meshA.selectFacesEx( self.faces, self.facesUv, self.verts )
        if ( len( meshA.faces ) > 0 ):
            self.children.append( meshA )
            self.nprint( "mesh '%s' added" % ( meshA.name ) )
        
        meshB = CBTreeMesh( self.nexify )
        meshB.name = self.name + ".2"
        meshB.textures = self.textures
        meshB.planes.extend( self.planes )
        meshB.planes.append( plB )
        meshB.selectFacesEx( self.faces, self.facesUv, self.verts )
        if ( len( meshB.faces ) > 0 ):
            self.children.append( meshB )
            self.nprint( "mesh '%s' added" % ( meshB.name ) )
            
                    
                
    def faceConvex( self, face ):
        sz = len( face )
        for i1 in range( sz ):
            i2 = ( i1+1 ) % sz
            i3 = ( i2+1 ) % sz
            # Vertex indices
            ind1 = face[i1]
            ind2 = face[i2]
            ind3 = face[i3]
            # Face normal
            nx, ny, nz = self.faceNormal( face )
            nSz = nsqrt( nx * nx + ny * ny + nz * nz )
            for face1 in self.faces[:]:
                if ( face1.count( ind1 ) == 1 ) and ( face1.count( ind2 ) == 1 ) and ( face1.count( ind3 ) == 0 ):
                    for ind in range( len( face1 ) ):
                        if ( face1[ind] != ind1 ) and ( face1[ind] != ind2 ):
                            k = face1[ind]
                            x, y, z = self.verts[k][0] - self.verts[ind1][0], \
                                      self.verts[k][1] - self.verts[ind1][1], \
                                      self.verts[k][2] - self.verts[ind1][2]
                            vSz = nsqrt( x * x + y * y + z * z )
                            d0 = nSz * vSz * self.planeCosDiff / self.scale
                            d = x * nx + y * ny + z * nz
                            # 1 but not 0 because normal is fitted to self.scale
                            # because of integer divisions it bight appear slightly not 
                            # perpendicular.
                            # There could be an error in determining the exact normal direction.
                            # I should estimate this error and use it in concave text here!!!
                            if ( d > d0 ):
                                self.nprint( "face is concave:" )
                                self.nprint( "face normal:  %.7f %.7f %.7f" % ( nx, ny, nz ) )
                                self.nprint( "concave edge: %.7f %.7f %.7f" % ( x, y, z ) )
                                self.nprint( "n * a: %.7f" % ( d ) )
                                #a = c # Just raises an error I need stopping program here.
                                return 0
        return 1
        
    def splitIntoConvex( self ):
        res = self.isSurf()
        if ( not res ):
            # First split into isolated.
            submeshes = self.splitIntoIsolated()
            if ( len(submeshes) > 1 ):
                self.nprint( "found several isolated parts: %d" % ( len(submeshes) ) )
                # Subdivide this mesh into several and cut each one using 
                # their personal sectioning planes.
                for i in range( len(submeshes) ):
                    mesh = CBTreeMesh( self.nexify )
                    mesh.name     = self.name + (".%d" % (i))
                    mesh.verts    = self.verts
                    mesh.planes   = self.planes
                    mesh.textures = self.textures
                    mesh.faces    = submeshes[i][ 'faces' ]
                    mesh.facesUv  = submeshes[i][ 'facesUv' ]
                    # Find points for planes.
                    mesh.planesPoints()
                    self.children.append( mesh )
                for mesh in self.children:
                    mesh.splitIntoConvex()
            else:
                for face in self.faces[:]:
                    res = self.faceConvex( face );
                    if ( not res ):
                        self.nprint( "cut into parts using face % d, %d, %d" % ( face[0], face[1], face[2] ) )
                        for i in range(3):
                            self.nprint( "%d, %d, %d" % ( self.verts[face[i]][0], self.verts[face[i]][1], self.verts[face[i]][2] ) )
                        self.cut( face )
                        # Parse submeshes recursively.
                        for mesh in self.children:
                            mesh.splitIntoConvex()
                        break
    
    
    def splitIntoIsolated( self ):
        '''
        It's necessary to make it more intelligent by selecting joined faces using planes 
        also. Because it might be two faces anf three planes making a column for axample.
        '''
        assert( len( self.faces ) > 0 )
        # Copy faces to temoprary list.
        faces = []
        faces.extend( self.faces )
        facesUv = []
        facesUv.extend( self.facesUv )
        
        meshes = []
        while ( len( faces ) > 0 ):
            mesh = {}
            mesh[ "faces" ] = []
            mesh[ "facesUv" ] = []
            # Take one item
            mesh[ 'faces' ].append( faces.pop() )
            mesh[ 'facesUv' ].append( facesUv.pop() )
            # For while loop working.
            addedCnt = 1
            while addedCnt > 0:
                addedCnt = 0
                for face1 in mesh[ 'faces' ]:
                    for face2 in faces:
                        # Faces should have not only one common vertex, but common entire edge.
                        cnt = face2.count( face1[0] ) + \
                              face2.count( face1[1] ) + \
                              face2.count( face1[2] )
                        if cnt > 1:
                           ind = faces.index( face2 )
                           mesh[ 'faces' ].append( faces.pop( ind ) )
                           mesh[ 'facesUv' ].append( facesUv.pop( ind ) )
                           addedCnt += 1
                           break
                    if ( addedCnt > 0 ):
                        break
                if ( addedCnt == 0 ):
                    meshes.append( mesh )
                    
        # Checking if meshes are really isolated.
        if ( len( self.planes ) > 0 ):
            mergesCnt = 1
            while ( mergesCnt > 0 ):
                mergesCnt = 0
                for i1 in range( len(meshes)-1 ):
                    mesh1 = meshes[i1]
                    isolated = 1
                    for face1 in mesh[ 'faces' ]:
                        nx1, ny1, nz1 = self.faceNormal( face1 )
                        nSz = nsqrt( nx1 * nx1 + ny1 * ny1 + nz1 * nz1 )
                        x1, y1, z1 = self.verts[ face1[0] ][0], \
                                     self.verts[ face1[0] ][1], \
                                     self.verts[ face1[0] ][2]
                        for i2 in range( 1, len(meshes) ):
                            mesh2 = meshes[i2]
                            for face2 in mesh2[ 'faces' ]:
                                for ind in face2:
                                    x2, y2, z2 = self.verts[ind][0] - x1, \
                                                 self.verts[ind][1] - y1, \
                                                 self.verts[ind][2] - z1
                                    vSz = nsqrt( x2 * x2 + y2 * y2 + z2 * z2 )
                                    d = nx1 * x2 + ny1 * y2 + nz1 * z2
                                    d0 = nSz * vSz * self.planeCosDiff / self.scale
                                    if ( d < d0 ):
                                        isolated = 0
                                        break
                                if ( not isolated ):
                                    break
                            if ( not isolated ):
                                break
                        if ( not isolated ):
                            break
                    if ( not isolated ):
                        # Merge these two meshes.
                        mesh1[ 'faces' ].extend( mesh2[ 'faces' ] )
                        mesh2[ 'facesUv' ].extend( mesh2[ 'facesUv' ] )
                        # Removing mesh2.
                        meshes.pop( i2 )
                        mergesCnt += 1
                        break
            pass
        return meshes
    


# /*
# ComputeAxisBase()
# computes the base texture axis for brush primitive texturing
# note: ComputeAxisBase here and in editor code must always BE THE SAME!
# warning: special case behaviour of atan2( y, x ) <-> atan( y / x ) might not be the same everywhere when x == 0
# rotation by (0,RotY,RotZ) assigns X to normal
# */

# void ComputeAxisBase( vec3_t normal, vec3_t texX, vec3_t texY )
# {
    # vec_t	RotY, RotZ;
    
    
    # /* do some cleaning */
    # if( fabs( normal[ 0 ] ) < 1e-6 )
        # normal[ 0 ]= 0.0f;
    # if( fabs( normal[ 1 ] ) < 1e-6 )
        # normal[ 1 ]=0.0f;
    # if( fabs( normal[ 2 ] ) < 1e-6 )
        # normal[ 2 ] = 0.0f;
    
    # /* compute the two rotations around y and z to rotate x to normal */
    # RotY = -atan2( normal[ 2 ], sqrt( normal[ 1 ] * normal[ 1 ] + normal[ 0 ] * normal[ 0 ]) );
    # RotZ = atan2( normal[ 1 ], normal[ 0 ] );
    
    # /* rotate (0,1,0) and (0,0,1) to compute texX and texY */
    # texX[ 0 ] = -sin( RotZ );
    # texX[ 1 ] = cos( RotZ );
    # texX[ 2 ] = 0;
    
    # /* the texY vector is along -z (t texture coorinates axis) */
    # texY[ 0 ] = -sin( RotY ) * cos( RotZ );
    # texY[ 1 ] = -sin( RotY ) * sin( RotZ );
    # texY[ 2 ] = -cos( RotY );
# }


    
    def transformUv( self, face, uv ):
        # I don't know how it works exactly. And the following code is just 
        # my guess on this.
        # Find the most like plane by comparing dot product with face normal.
        # Calculating normal:
        nx, ny, nz = self.faceNormal( face )
        nSz = nsqrt( nx * nx + ny * ny + nz * nz )
        if ( nSz == 0 ):
            self.nprint( "transformUv: zero area face, skipping calculations." )
            return 0, 0, 0, 1, 1
        nx, ny, nz = self.normalize( nx, ny, nz )


        # Texture reference frame origin is just ( 0, 0, 0 ) :) Thanks to divVerent !!!!!
        Ox, Oy, Oz = 0.0, 0.0, 0.0

        if( abs( nx ) < 1e-6 ):
            nx = 0.0
        if( abs( ny ) < 1e-6 ):
            ny = 0.0
        if( abs( nz ) < 1e-6 ):
            nz = 0.0
        
        # compute the two rotations around y and z to rotate x to normal
        RotY = -math.atan2( nz, nsqrt( ny * ny + nx * nx ) )
        RotZ = math.atan2( ny, nx )
        
        # rotate (0,1,0) and (0,0,1) to compute texX and texY
        ox = [ -math.sin( RotZ ), \
                math.cos( RotZ ), \
                0.0 ]
        
        # the texY vector is along -z (t texture coorinates axis)
        oy = [ -math.sin( RotY ) * math.cos( RotZ ), \
               -math.sin( RotY ) * math.sin( RotZ ), \
               -math.cos( RotY ) ]




        # Rename some variables to fit external soft output.
        oxx, oxy, oxz = ox[0], ox[1], ox[2]
        oyx, oyy, oyz = oy[0], oy[1], oy[2]
        
        # Matrix for transferring x,y,z to u0,v0.
        d = nx*(oxy*oyz-oxz*oyy)+oxx*(nz*oyy-ny*oyz)+(ny*oxz-nz*oxy)*oyx
        A = [ [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0] ]
        A[0][0] = (nz*oyy-ny*oyz) / d
        A[0][1] = (nx*oyz-nz*oyx) / d
        A[0][2] = (ny*oyx-nx*oyy) / d
        A[0][3] = (nx*(oyy*Oz-oyz*Oy)-oyx*(ny*Oz-nz*Oy)-(nz*oyy-ny*oyz)*Ox) / d
        A[1][0] = (ny*oxz-nz*oxy) / d
        A[1][1] = (nz*oxx-nx*oxz) / d
        A[1][2] = (nx*oxy-ny*oxx) / d
        A[1][3] = (-nx*(oxy*Oz-oxz*Oy)+oxx*(ny*Oz-nz*Oy)+(nz*oxy-ny*oxz)*Ox) / d
        A[2][0] = (oxy*oyz-oxz*oyy) / d
        A[2][1] = (oxz*oyx-oxx*oyz) / d
        A[2][2] = (oxx*oyy-oxy*oyx) / d
        A[2][3] = (-oxx*(oyy*Oz-oyz*Oy)+oyx*(oxy*Oz-oxz*Oy)-(oxy*oyz-oxz*oyy)*Ox) / d
        A[3][3] = (nx*(oxy*oyz-oxz*oyy)+oxx*(nz*oyy-ny*oyz)-(nz*oxy-ny*oxz)*oyx) / d
        # Calculating initial uv0
        xyz = []
        for i in range(3):
            x, y, z = float( self.verts[ face[i] ][0] ), \
                      float( self.verts[ face[i] ][1] ), \
                      float( self.verts[ face[i] ][2] )
            xyz.append( [ x, y, z, 1 ] )
        uv0 = [ [ 0, 0, 0, 0 ], [ 0, 0, 0, 0 ], [ 0, 0, 0, 0 ] ]
        for i in range(3):         # Vector number
            for j in range(4):     # Coordinate number
                for k in range(4): # Summing index
                    # nprint( "A[%d][%d] * xyz[%d][%d] = " % ( j, k, i, k ) )
                    # nprint( "                          %.8f   *   %.8f" % ( A[j][k], xyz[i][k] ) )
                    uv0[i][j] = uv0[i][j] + A[j][k] * xyz[i][k]
        # **********************************************
        # self.nprint( "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" )
        # self.nprint( "    checking coordinates transformation:" )
        # self.nprint( "ox: %.8f, %.8f, %.8f" % (ox[0], ox[1], ox[2]) )
        # self.nprint( "oy: %.8f, %.8f, %.8f" % (oy[0], oy[1], oy[2]) )
        # self.nprint( "O: %.8f, %.8f, %.8f" % (Ox, Oy, Oz) )
        # self.nprint( "coordinates xyz:" )
        # for i in range(3):
            # self.nprint( "xyz[%d][:]: %.8f, %.8f, %.8f, %.8f" % ( i, xyz[i][0], xyz[i][1], xyz[i][2], xyz[i][3] ) )
        # self.nprint( "coordinates uv:" )
        # for i in range(3):
            # self.nprint( "uv0[%d][:]: %.8f, %.8f, %.8f, %.8f" % ( i, uv0[i][0], uv0[i][1], uv0[i][2], uv0[i][3] ) )
        # it should be uv0[:][2] == 0 and uv0[:][3] == 1!!!!!
        # **********************************************
        
        # Initial UV coordinates after transferring xyz to uv according 
        # to initial guess.
        u0, v0 = uv0[0][0], uv0[0][1]
        u1, v1 = uv0[1][0], uv0[1][1]
        u2, v2 = uv0[2][0], uv0[2][1]
        # Real uv coordinates (it's necessary to multiply them on image size, I suppose):
        if ( len( self.textures ) > uv[0][0] ):
            texture, w, h = self.textures[ uv[0][2] ][0], \
                            self.textures[ uv[0][2] ][1], \
                            self.textures[ uv[0][2] ][2]
        else:
            texture, w, h = 'common/caulk', 32, 32
        
        U0, V0 = uv[0][0] * w, uv[0][1] * h
        U1, V1 = uv[1][0] * w, uv[1][1] * h
        U2, V2 = uv[2][0] * w, uv[2][1] * h
        # for i in range(3):
            # self.nprint( "uv[%d][:]: %.8f, %.8f" % ( i, uv[i][0] * w, uv[i][1] * h ) )
        # matrix for transferring uv to UV.
        a = [ [0, 0, 0], [0, 0, 0], [0, 0, 1] ]
        d = (u1-u0)*v2+(u0-u2)*v1+(u2-u1)*v0
        a[0][0] = -((v1-v0)*U2+(v0-v2)*U1+(v2-v1)*U0) / d
        a[0][1] = ((u1-u0)*U2+(u0-u2)*U1+(u2-u1)*U0) / d
        a[0][2] = ((u0*v1-u1*v0)*U2+(u2*v0-u0*v2)*U1+(u1*v2-u2*v1)*U0) / d
        a[1][0] = -((v1-v0)*V2+(v0-v2)*V1+(v2-v1)*V0) / d
        a[1][1] = ((u1-u0)*V2+(u0-u2)*V1+(u2-u1)*V0) / d
        a[1][2] = ((u0*v1-u1*v0)*V2+(u2*v0-u0*v2)*V1+(u1*v2-u2*v1)*V0) / d
        # self.nprint( "    matrix from uv0->uv:" )
        # for i in range(2):
            # self.nprint( "        a[%d][0], a[%d][1], a[%d][2] = %.8f, %.8f, %.8f" % ( i, i, i, a[i][0], a[i][1], a[i][2] ) )
        
        # To find scale, shift and rotation angle let's transform unit vectors. 
        r00x, r00y = a[0][2], a[1][2]
        a10x, a10y = a[0][0], a[1][0]
        a01x, a01y = a[0][1], a[1][1]
        # New reference frame orientation. (It's cross product third component.)
        d = a10x * a01y - a10y * a01x
        if d > 0:
            signScaleY = 1
        else:
            signScaleY = -1
            a01x, a01y = -a01x, -a01y
        lenX = math.sqrt( a10x * a10x + a10y * a10y )
        lenY = math.sqrt( a01x * a01x + a01y * a01y )
        # Calculating angle.
        angle = math.acos( a10x / lenX ) * 57.295779513082320876798154814105
        if ( a10y < 0 ):
            angle = 360 - angle
        # self.nprint( "angle = %.8f" % ( angle ) )
        scaleX = 1 / lenX
        scaleY = 1 / lenY
        # self.nprint( "scaleX, scaleY = %.8f, %.8f" % ( scaleX, scaleY ) )
        ang = angle / 57.295779513082320876798154814105
        c = math.cos( ang )
        s = math.sin( ang )
        inv_ang_sc = [ [c/scaleX, -s/scaleX, 0 ], [s/scaleY, c/scaleY, 0], [0, 0, 1] ]
        shift = [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ]
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    shift[i][j] = shift[i][j] + inv_ang_sc[i][k] * a[k][j]
        shiftX, shiftY = shift[0][2], shift[1][2]
        return shiftX, shiftY, angle, scaleX, scaleY        
    
    # nexuizPath for texture path subtracting.
    # props for texture overrides.
    def prepareTextures( self, mesh, nexuizPath, props ):
            self.textures = []
            materials = mesh.getMaterials()
            for i in range( len( materials ) ):
                material = materials[ i ]
                textures = material.getTextures()
                if ( ( textures ) and ( len(textures) > 0 ) and ( textures[0] != None ) ):
                    texture = textures[0].tex
                    if ( texture ):
                        image = texture.getImage()
                        if ( image != None ):
                            name = image.getFilename().lower()
                            if name and os.path.isfile( name ): 
                                sz = image.getSize()
                                name = name.replace( '\\', '/' )
                                # I need to cut off file extension and the 
                                # beginning "c:\programs\nexuiz\data\textures\".
                                tex_path = self.nexify.g_nexuiz_path.replace( '\\', '/' )
                                if ( tex_path[ len(tex_path)-1 ] == '/' ):
                                    tex_path = tex_path[:(len(tex_path)-1)]
                                tex_path = ( tex_path + "/data/textures/" ).lower()
                                self.nprint( "tex_path is '" + tex_path + "'" )
                                #os.path.relpath( tex_path, texture )
                                # Texture in on correct path.
                                if ( name.find( tex_path ) == 0 ):
                                    name = name[ len(tex_path): ]
                                    name, ext = os.path.splitext( name )
                                    self.nprint( "texture is: '" + name + "', file type is: " + ext[ 1: ] )
                                else:
                                    self.nprint( "Some misterious texture file path: '" + texture + "'" )
                                    name = 'common/caulk'
                                texture = [ name, sz[0], sz[1] ]
                            else:
                                self.nprint( "No such file: '" + name + "'" )
                                texture = [ 'common/caulk', 32, 32 ]
                        else:
                            texture = [ 'common/caulk', 32, 32 ]
                    else:
                        texture = [ 'common/caulk', 32, 32 ]
                else:
                    texture = [ 'common/caulk', 32, 32 ]
                self.textures.append( texture )
                # Overwrite texture if there is an appropriate property.
                stri = 'texture[%d]' % (i)
                if ( stri in props ):
                    self.textures[i][0] = props[ stri ]
            
            # Debug output: list of textures.
            for tex in self.textures:
                self.nprint( '%s, %d, %d' % ( tex[0], tex[1], tex[2] ) )
    
    def planesPoints( self ):
        self.planePoints = []
        for plInd in range( len(self.planes) ):
            pl = self.planes[ plInd ]
            # self.nprint( "plane is: ( %.3f, %.3f, %.3f %.3f )" % ( plane.a, plane.b, plane.c, plane.d ) )
            pts = []
            for i in range(3):
                j = pl.face[i]
                pts.append( [ self.verts[j][0], self.verts[j][1], self.verts[j][2] ] )
            pl.verts = pts
        
        
    def exportGeometry( self, root ):
        if ( len( self.children ) > 0 ):
            for child in self.children:
                child.exportGeometry( root )
        else:
            if ( self.surf ):
                self.writeSurf( root )
            else:
                self.writeMesh( root )
        
        
    def selectFacesEx( self, faces, facesUv, verts ):
        self.nprint( "============= Selecting faces EX ================" )
        assert( len( faces ) > 0 )
        self.verts   = verts
        self.faces   = []
        self.facesUv = []
        
        for i in range( len( faces ) ):
            face   = faces[i]
            faceUv = facesUv[i]
            res = self.selectFace( face )
            if res:
                self.faces.append( face )
                self.facesUv.append( faceUv )
                
        # Removing planes which is parallel to another and behind it.
        removed = 1
        while ( removed > 0 ):
            removed = 0
            sz = len( self.planes )
            for ind1 in range( sz-1 ):
                pl1 = self.planes[ ind1 ]
                a1, b1, c1, d1 = pl1.a, pl1.b, pl1.c, pl1.d
                sz1 = nsqrt( a1 * a1 + b1 * b1 + c1 * c1 )
                for ind2 in range( ind1+1, sz ):
                    pl2 = self.planes[ ind2 ]
                    a2, b2, c2, d2 = pl2.a, pl2.b, pl2.c, pl2.d
                    sz2 = nsqrt( a2 * a2 + b2 * b2 + c2 * c2 )
                    dot = a1 * a2 + b1 * b2 + c1 * c2
                    dot0 = sz1 * sz2 * self.planeCosIdent / self.scale
                    if ( dot >= dot0 ):
                        self.nprint( "removing parallel plane" )
                        self.nprint( "dot: %d,   dot0: %d" % ( dot, dot0 ) )
                        # Planes are parallel and directed to one and the same direction.
                        # We need to remove far one.
                        # Compare d coefs keeping in mind that d is negative dot product.
                        if ( d1 > d2 ):
                            # remove 1
                            self.planes.pop( ind1 )
                        else:
                            # remove 2
                            self.planes.pop( ind2 )
                        removed += 1
                        break
                if ( removed > 0 ):
                    break
                    
        # Removing unnecessary planes.
        # If Plane doesn't intersects or at least doesn't touches any face, 
        # then remove this plane.
        if ( self.removeRemotePlanes ):
            for plane in self.planes[:]:
                a, b, c, d = plane.a, plane.b, plane.c, plane.d
                accept = 0
                for face in self.faces:
                    for i in range(3):
                        ind1 = i
                        ind2 = (i+1) % 3;
                        d1 = a * verts[ind1][0] + b * verts[ind1][1] + c * verts[ind1][2] + d
                        d2 = a * verts[ind2][0] + b * verts[ind2][1] + c * verts[ind2][2] + d
                        if ( d1 * d2 <= 0 ):
                            accept = 1
                            break
                    if ( accept ):
                        break
                if ( not accept ):
                    self.planes.remove( plane )
        # Find points for planes.
        self.planesPoints()

                
    def selectFace( self, face ):
        rTri = []
        for i in range( len(face) ):
            rTri.append( [ self.verts[ face[i] ][0], self.verts[ face[i] ][1], self.verts[ face[i] ][2] ] )
        nTri = [ 0, 0, 0 ]
        # Face plane normal.
        nTri[0], nTri[1], nTri[2] = self.faceNormal( face )
        nSz = nsqrt( nTri[0] * nTri[0] + nTri[1] * nTri[1] + nTri[2] * nTri[2] )
        # Somewhy in Blender sometimes appear faces with 0 area.
        # Normal vector would be 0, 0, 0 also.
        # Let's skip such faces.
        if ( nTri[0] == 0 ) and ( nTri[1] == 0 ) and ( nTri[2] == 0 ):
            return 0
        
        # Loop over planes.
        for pl in self.planes:
            # Also I should skip faces with normal to exactly the same direction as plane.
            # Because they kill all geometry.
            sz = len(rTri)
            plSz = nsqrt( pl.a * pl.a + pl.b * pl.b + pl.c * pl.c )
            for i in range( sz ):
                r0 = rTri[i]
                dotR0 = r0[0] * pl.a + r0[1] * pl.b + r0[2] * pl.c + pl.d
                if ( dotR0 == 0 ):
                    dotTriPl = nTri[0] * pl.a + nTri[1] * pl.b + nTri[2] * pl.c
                    dotTriPlMax = nSz * plSz * self.planeCosIdent / self.scale
                    if ( dotTriPl >= dotTriPlMax ):
                        return 0
            
            # Refresh verts list for face according to appeared sectioning plane.
            rr = []
            sz = len(rTri)
            for i in range( sz ):
                r0 = rTri[i]
                dotR0 = r0[0] * pl.a + r0[1] * pl.b + r0[2] * pl.c + pl.d
                if ( dotR0 >= 0 ):
                    rr.append( r0 )
                    r1 = rTri[ (i+1) % sz ]
                    dotR1 = r1[0] * pl.a + r1[1] * pl.b + r1[2] * pl.c + pl.d
                    if ( dotR0 > 0 ) and ( dotR1 < 0 ):
                        # Adding middle point
                        mp = [ 0, 0, 0 ]
                        mp[0], mp[1], mp[2] = self.middlePoint( r1, r0, pl )
                        rr.append( mp )
                else:
                    r1 = rTri[ (i+1) % sz ]
                    dotR1 = r1[0] * pl.a + r1[1] * pl.b + r1[2] * pl.c + pl.d
                    if ( dotR1 > 0 ):
                        # Adding middle point
                        mp = [ 0, 0, 0 ]
                        mp[0], mp[1], mp[2] = self.middlePoint( r1, r0, pl )
                        rr.append( mp )
            # Remove too close points.
            removedCnt = 1
            while ( removedCnt > 0 ) and ( len(rr) > 2 ):
                removedCnt = 0
                sz = len(rr)
                for i in range( sz ):
                    j = ( i + 1 ) % sz
                    dr = [ rr[i][0] - rr[j][0], rr[i][1] - rr[j][1], rr[i][2] - rr[j][2] ]
                    l = nsqrt( dr[0] * dr[0] + dr[1] * dr[1] + dr[2] * dr[2] )
                    if ( l <= 1 ):
                        rr.pop( j )
                        removedCnt += 1
                        break
            # remove points on one line.
            removedCnt = 1
            while ( removedCnt > 0 ) and ( len(rr) > 2 ):
                removedCnt = 0
                sz = len(rr)
                for i in range( sz ):
                    j = ( i + 1 ) % sz
                    k = ( i + 2 ) % sz
                    dr1 = [ rr[i][0] - rr[j][0], rr[i][1] - rr[j][1], rr[i][2] - rr[j][2] ]
                    dr2 = [ rr[i][0] - rr[k][0], rr[i][1] - rr[k][1], rr[i][2] - rr[k][2] ]
                    x, y, z = self.cross( dr1[0], dr1[1], dr1[2], dr2[0], dr2[1], dr2[2] )
                    if ( abs( x ) <= 1 ) and ( abs( y ) <= 1 ) and ( abs( z ) <= 1 ):
                        rr.pop( j )
                        removedCnt += 1
                        break
                
            if ( len( rr ) < 3 ):
                return 0
            rTri = rr[:]
        return 1
        
        
        
        
    def middlePoint( self, r1, r0, pl ):
        # Substitute edge equation to plane equation.
        # n * ( (r1 - r0)t + r0 ) + d = 0
        # t = ( n * r0 + d ) / ( n * (r0 - r1) )
        denominator = (r0[0] - r1[0]) * pl.a + \
                      (r0[1] - r1[1]) * pl.b + \
                      (r0[2] - r1[2]) * pl.c
        if ( denominator == 0 ):
            return r1[0], r1[1], r1[2]
        numerator   = r0[0] * pl.a + r0[1] * pl.b + r0[2] * pl.c + pl.d
        # This is because precission leaves expect much to be desired :( :( :(.
        if ( numerator * denominator <= 0 ):
            return r0[0], r0[1], r0[2]
        elif ( abs(numerator) >= abs(denominator) ):
            return r1[0], r1[1], r1[2]
        # Actually this function is called only 
        # when r0 and r1 lay on different plane sides.
        # But due to ultra poor calculational quality
        # sometimes it appears that t might be beyond 
        # [0, 1] interval :(.
        res = [ ( ( r1[0] - r0[0] ) * numerator * self.scale / denominator + r0[0] * self.scale ) / self.scale, \
                ( ( r1[1] - r0[1] ) * numerator * self.scale / denominator + r0[1] * self.scale ) / self.scale, \
                ( ( r1[2] - r0[2] ) * numerator * self.scale / denominator + r0[2] * self.scale ) / self.scale ]
        return res[0], res[1], res[2]
        
    
    
    def isSurf( self ):
        # If it's overwritten, just return it.
        if ( self.surf ):
            return 1
        # Do not test if it has planes. Because it would be definitely surf 
        # in such case :)
        if ( len( self.planes ) > 0 ):
            return 0
        # Checking all edges to belong to exactly two faces.
        for face1 in self.faces:
            L = len(face1)
            for i in range( L ):
                j = (i+1) % L
                ind1 = face1[i]
                ind2 = face1[j]
                n = 0
                for face2 in self.faces:
                    if ( face2 != face1 ):
                        if ( face2.count( ind1 ) == 1 ) and ( face2.count( ind2 ) == 1 ):
                            n += 1
                if ( n != 1 ):
                    self.surf = 1
                    return 1
        self.surf = 0
        return 0
        
    def writeMesh( self, root ):
        stri = ''
        stri += '    // %s\n' % ( self.name )
        stri += '    {\n'
        uniquePlanes = []
        # Adding faces.
        for ind in range( len( self.faces ) ):
            face     = self.faces[ind]
            faceUv   = self.facesUv[ind]
            # Check if face plane is unique.
            # with normal outside.
            a, b, c = self.faceNormal( face )
            nSz = nsqrt( a * a + b * b + c * c )
            skip = 0
            for pl in uniquePlanes:
                dot = a * pl[0] + b * pl[1] + c * pl[2]
                dot0 = nSz * pl[3] * self.planeCosIdent / self.scale
                if ( dot > dot0 ):
                    skip = 1
                    break
            if ( not skip ):
                plane = [ a, b, c, nSz ]
                uniquePlanes.append( plane )
                
                # self.nprint( "faceUv len: %d" % ( len( faceUv ) ) )
                # self.nprint( "faceUv[0] len: %d" % ( len( faceUv[0] ) ) )
                if ( len( self.textures ) > faceUv[0][2] ):
                    texture  = self.textures[ faceUv[0][2] ][ 0 ]
                else:
                    # self.nprint( "texture absent, filling with 'common/caulk'" )
                    texture = 'common/caulk'
                vv = [ float(self.verts[ face[2] ][0]), \
                       float(self.verts[ face[2] ][1]), \
                       float(self.verts[ face[2] ][2]) ]
                stri += '        ( %.4f %.4f %.4f ) ' % ( vv[0], vv[1], vv[2] )
                vv = [ float(self.verts[ face[1] ][0]), \
                       float(self.verts[ face[1] ][1]), \
                       float(self.verts[ face[1] ][2]) ]
                stri += '( %.4f %.4f %.4f ) ' % ( vv[0], vv[1], vv[2] )
                vv = [ float(self.verts[ face[0] ][0]), \
                       float(self.verts[ face[0] ][1]), \
                       float(self.verts[ face[0] ][2]) ]
                stri += '( %.4f %.4f %.4f ) ' % ( vv[0], vv[1], vv[2] )
                stri += texture + ' '
                x, y, ang, w, h = self.transformUv( face, faceUv )
                stri += '%.4f %.4f %.4f %.4f %.4f 0 0 0\n' % ( x, y, ang, w, h )
        # Adding planes.
        stri += '        // Sectioning planes:\n'
        # Sectioning plane normals are directed inside.
        # To detect unique change sign
        for ind in range( len( self.planes ) ):
            pl = self.planes[ ind ]
            a, b, c = -pl.a, -pl.b, -pl.c
            nSz = nsqrt( a * a + b * b + c * c )
            skip = 0
            for pl2 in uniquePlanes:
                dot = a * pl2[0] + b * pl2[1] + c * pl2[2]
                dot0 = nSz * pl2[3] * self.planeCosIdent / self.scale
                if ( dot > dot0 ):
                    skip = 1
                    break
            if ( not skip ):
                plane = [ a, b, c, nSz ]
                uniquePlanes.append( plane )
                
                if ( len( self.textures ) > pl.faceUv[0][2] ):
                    texture  = self.textures[ pl.faceUv[0][2] ][ 0 ]
                else:
                    # self.nprint( "texture absent, filling with 'common/caulk'" )
                    texture = 'common/caulk'
                vv = [ pl.verts[0][0], \
                       pl.verts[0][1], \
                       pl.verts[0][2] ]
                stri += '        ( %.4f %.4f %.4f ) ' % ( vv[0], vv[1], vv[2] )
                vv = [ pl.verts[1][0], \
                       pl.verts[1][1], \
                       pl.verts[1][2] ]
                stri += '( %.4f %.4f %.4f ) ' % ( vv[0], vv[1], vv[2] )
                vv = [ pl.verts[2][0], \
                       pl.verts[2][1], \
                       pl.verts[2][2] ]
                stri += '( %.4f %.4f %.4f ) ' % ( vv[0], vv[1], vv[2] )
                stri += texture + ' '
                x, y, ang, w, h = self.transformUv( pl.face, pl.faceUv )
                stri += '%.4f %.4f %.4f %.4f %.4f 0 0 0\n' % ( x, y, ang, w, h )
        stri += '    }\n'
        root.stri += stri

        
    def writeSurf( self, root ):
        stri = ''
        for i in range( len(self.faces) ):
            face = self.faces[i]
            faceUv = self.facesUv[i]
            nx, ny, nz = self.faceNormal( face )
            nSz = nsqrt( nx * nx + ny * ny + nz * nz )
            # Don't event try exporting zero area faces.
            if ( nSz == 0 ):
                self.nprint( "writeSurf: zero area face, skipping calculations." )
                continue
            stri += '    // %s.%i\n' % ( self.name, self.faces.index(face) )
            stri += '    {\n'
            # Normalized normal.
            nx, ny, nz = float(nx), float(ny), float(nz)
            nSz = float( nSz )
            nx, ny, nz = nx * self.nexify.g_scale / nSz, ny * self.nexify.g_scale / nSz, nz * self.nexify.g_scale / nSz
            d = self.nexify.g_extrudeHeight
            if ( self.nexify.g_extrudeDownwards ):
                # Upper face comes with inverse verts order.
                stri += '        '
                for n in face[ 3::-1 ]:
                    vv = [ float(self.verts[ n ][0]), \
                           float(self.verts[ n ][1]), \
                           float(self.verts[ n ][2]) ]
                    stri += '( %.4f %.4f %.4f ) ' %( vv[0], vv[1], vv[2] )
                if ( len( self.textures ) > faceUv[0][2] ):
                    texture  = self.textures[ faceUv[0][2] ][ 0 ]
                else:
                    # self.nprint( "texture absent, filling with 'common/caulk'" )
                    texture = 'common/caulk'
                stri += texture + ' '
                x, y, ang, w, h = self.transformUv( face, faceUv )
                stri += '%.4f %.4f %.4f %.4f %.4f 0 0 0\n' % ( x, y, ang, w, h )
                
                # Point on distance d from plane of the face.
                v = [ 0, 0, 0 ]
                for i in face:
                    v[0] += self.verts[i][0]
                    v[1] += self.verts[i][1]
                    v[2] += self.verts[i][2]
                v = [ float(v[0]) / 3 - d * nx, \
                      float(v[1]) / 3 - d * ny, \
                      float(v[2]) / 3 - d * nz ]
                # Adding borders.
                sz = len(face)
                for n in range( sz ):
                    ind1 = face[n]
                    ind2 = face[( n + 1 ) % sz]
                    stri += '        '
                    vv = [ float(self.verts[ind1][0]), \
                           float(self.verts[ind1][1]), \
                           float(self.verts[ind1][2]) ]
                    stri += '( %.3f %.3f %.3f ) ' %( vv[0], vv[1], vv[2] )
                    vv = [ float(self.verts[ind2][0]), \
                           float(self.verts[ind2][1]), \
                           float(self.verts[ind2][2]) ]
                    stri += '( %.3f %.3f %.3f ) ' %( vv[0], vv[1], vv[2] )
                    stri += '( %.3f %.3f %.3f ) ' %( v[0], v[1], v[2] )
                    texture = 'common/caulk'
                    stri += texture + ' '
                    x, y, ang, w, h = 0, 0, 0, 1, 1
                    stri += '%.4f %.4f %.4f %.4f %.4f 0 0 0\n' % ( x, y, ang, w, h )

                
            else:
                # Upper face comes with normal verts order.
                stri += '        '
                for n in range( 3 ):
                    ind = face[n]
                    vv = [ float(self.verts[ind][0]), \
                           float(self.verts[ind][1]), \
                           float(self.verts[ind][2]) ]
                    stri += '( %.3f %.3f %.3f ) ' %( vv[0], vv[1], vv[2] )
                if ( len( self.textures ) > faceUv[0][2] ):
                    texture  = self.textures[ faceUv[0][2] ][ 0 ]
                else:
                    # self.nprint( "texture absent, filling with 'common/caulk'" )
                    texture = 'common/caulk'
                stri += texture + ' '
                x, y, ang, w, h = self.transformUv( face, faceUv )
                stri += '%.4f %.4f %.4f %.4f %.4f 0 0 0\n' % ( x, y, ang, w, h )
                
                # Point on distance d from plane of the face.
                v = [ 0, 0, 0 ]
                for i in face:
                    v[0] += self.verts[i][0]
                    v[1] += self.verts[i][1]
                    v[2] += self.verts[i][2]
                v = [ float(v[0]) / 3 + d * nx, \
                      float(v[1]) / 3 + d * ny, \
                      float(v[2]) / 3 + d * nz ]
                # Adding borders.
                sz = len(face)
                for n in range( sz ):
                    ind2 = face[n]
                    ind1 = face[( n + 1 ) % sz]
                    stri += '        '
                    vv = [ float(self.verts[ind1][0]), \
                           float(self.verts[ind1][1]), \
                           float(self.verts[ind1][2]) ]
                    stri += '( %.4f %.4f %.4f ) ' %( vv[0], vv[1], vv[2] )
                    vv = [ float(self.verts[ind2][0]), \
                           float(self.verts[ind2][1]), \
                           float(self.verts[ind2][2]) ]
                    stri += '( %.4f %.4f %.4f ) ' %( vv[0], vv[1], vv[2] )
                    stri += '( %.4f %.4f %.4f ) ' %( v[0], v[1], v[2] )
                    texture = 'common/caulk'
                    stri += texture + ' '
                    x, y, ang, w, h = 0, 0, 0, 1, 1
                    stri += '%.4f %.4f %.4f %.4f %.4f 0 0 0\n' % ( x, y, ang, w, h )
            stri += '    }\n'
        root.stri += stri

        
        
        
        
        
class CDivPlane:
    def __init__( self ):
        self.a = 1
        self.b = 1
        self.c = 1
        self.d = 0
        
    def set( self, a, b, c, d ):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        
        
        
        