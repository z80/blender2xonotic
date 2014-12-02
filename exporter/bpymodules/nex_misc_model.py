
# import mathutils
import nex_ase_model
import Blender
from Blender import Scene

class MiscModel():
    def __init__( self, obj, nexify ):
        self.obj = obj
        self.nexify = nexify
    
    def write( self, file ):
        name = self.obj.getName()
        model_name = "models/nexify/" + name + ".ase"
        file_name = self.nexify.g_nexuiz_path + "/data/" + model_name
        
        
        stri =  ( '// misc_model entity from mesh "%s"\n' % ( name ) )
        stri +=   '{\n    "classname" "misc_model"\n'
        #stri += ( '    "model" "%s"\n' % model_name )
        # tail =  ( '    "scale" "%.6f"\n' % self.nexify.g_scale )
        tail = ""
        propsList = self.obj.getAllProperties()
        
        make_model = 1
        ref_name = ""
        for prop in propsList:
            prop_name = prop.getName()
            prop_value = prop.getData()
            if ( prop_name == 'ref_to' ):
                ref_name = prop_value
                # Overwrite model_name.
                model_name = "models/nexify/" + prop_value + ".ase"
                make_model = 0
            elif ( prop_name != 'classname' ):
                tail += ( '    "%s" "%s"\n' % ( prop_name, prop_value ) )
        tail += '}\n\n'
        
        stri += ( '    "model" "%s"\n' % ( model_name ) )
        
        # Look for reference object. If ref_to points to not existing object, ASE will be created.
        if ( not make_model ):
            scn = Blender.Scene.GetCurrent()
            objects = scn.objects
            obj_found = 0
            for o in objects:
                n = o.getName()
                if ( n == ref_name ):
                    obj_found = 1
                    ref_obj = o
            if ( not obj_found ):
                make_model = 1
            
        # Making model itself.
        if ( make_model ):
            w = nex_ase_model.AseWriter( file_name, name )
            del w
        # Calculate relative transformation.
        m = self.obj.getMatrix().copy()
        # Extract translation.
        rel_r = m.translationPart()
        rel_x = self.nexify.g_scale * rel_r.x
        rel_y = self.nexify.g_scale * rel_r.y
        rel_z = self.nexify.g_scale * rel_r.z
        # Extract scale.
        scale_r = m.scalePart()
        scale_x = self.nexify.g_scale * scale_r.x
        scale_y = self.nexify.g_scale * scale_r.y
        scale_z = self.nexify.g_scale * scale_r.z
        # Extract rotation.
        rotM = m.rotationPart()
        e = rotM.toEuler()
        yaw   = e.x
        pitch = e.y
        roll  = e.z
            
        # From relative matrix calculate displacement, zoom and rotation
        stri += ( '    "origin" "%.6f %.6f %.6f"\n' % ( rel_x, rel_y, rel_z ) )
        # stri += ( '    "modelscale" "%.6f"\n' % ( scale_z ) )
        stri += ( '    "modelscale_vec" "%.6f %.6f %.6f"\n' % ( scale_x, scale_y, scale_z ) )
        # stri += ( '    "angle" "%.6f"\n' % ( roll ) )
        stri += ( '    "angles" "%.6f %.6f %.6f"\n' % ( pitch, roll, yaw ) )
        stri += tail
        
        
        file.write( stri )
        
