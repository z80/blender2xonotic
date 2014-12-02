

class ItemAll():
    def __init__( self, obj, nexify ):
        self.obj = obj
        self.nexify = nexify
    
    def write( self, file ):
        propsList = self.obj.getAllProperties()
        en_type = "ERROR"
        tail = ""
        for prop in propsList:
            prop_name = prop.getName()
            prop_value = prop.getData()
            if ( prop_name == 'classname' ):
                en_type = prop_value
            elif ( prop_name != 'origin' ):
                tail += ( '    "%s" "%s"\n' % ( prop_name, prop_value ) )
        
        name = self.obj.getName()
        prefix = en_type[ 0:5 ]
        if ( prefix == "item_" ):
            # Calculating angle
            m = self.obj.matrixWorld.copy()
            # Translation.
            rel_r = m.translationPart()
            rel_x = self.nexify.g_scale * rel_r.x
            rel_y = self.nexify.g_scale * rel_r.y
            rel_z = self.nexify.g_scale * rel_r.z
            
            stri =  ( '// %s entity from mesh "%s"\n' % ( en_type, name ) )
            stri += ( '{\n    "classname" "%s"\n' % ( en_type ) )
            stri += ( '    "origin" "%.6f %.6f %.6f"\n' % ( rel_x, rel_y, rel_z ) )
            stri += tail
            stri += '}\n\n'
        
            file.write( stri )
        else:
            print( "ERROR: " + prefix )
        
