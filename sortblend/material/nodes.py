#    This file is a part of SORT(Simple Open Ray Tracing), an open-source cross
#    platform physically based renderer.
#
#    Copyright (c) 2011-2019 by Cao Jiayin - All rights reserved.
#
#    SORT is a free software written for educational purpose. Anyone can distribute
#    or modify it under the the terms of the GNU General Public License Version 3 as
#    published by the Free Software Foundation. However, there is NO warranty that
#    all components are functional in a perfect manner. Without even the implied
#    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with
#    this program. If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.

import bpy
import nodeitems_utils
from . import properties
from .. import base

class SORTPatternNodeCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'SORTPatternGraph'

class SORTMaterial(bpy.types.PropertyGroup):
    sortnodetree = bpy.props.StringProperty(name="Nodetree",default='')
    use_sort_nodes = bpy.props.BoolProperty(name="Nodetree",default=False)

# node tree for sort
@base.register_class
class SORTPatternGraph(bpy.types.NodeTree):
    bl_idname = 'SORTPatternGraph'
    bl_label = 'SORT Pattern Graph'
    bl_icon = 'MATERIAL'
    nodetypes = {}
    node_categories = {}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'SORT_RENDERER'

    # Return a node tree from the context to be used in the editor
    @classmethod
    def get_from_context(cls, context):
        ob = context.active_object
        if ob and ob.type not in {'LAMP', 'CAMERA'}:
            ma = ob.active_material
            if ma != None:
                nt_name = ma.sort_material.sortnodetree
                if nt_name != '':
                    return bpy.data.node_groups[nt_name], ma, ma
        return (None, None, None)

    @classmethod
    def register_node(cls, category):
        def registrar(nodecls):
            base.register_class(nodecls)
            d = cls.node_categories.setdefault(category, [])
            d.append(nodecls)
            return nodecls
        return registrar

    @classmethod
    def register(cls):
        bpy.types.Material.sort_material = bpy.props.PointerProperty(type=SORTMaterial, name="SORT Material Settings")
        cats = []
        for c, l in sorted(cls.node_categories.items()):
            cid = 'SORT_' + c.replace(' ', '').upper()
            items = [nodeitems_utils.NodeItem(nc.__name__) for nc in l]
            cats.append(SORTPatternNodeCategory(cid, c, items=items))

            cls.nodetypes[c] = []
            for item in l :
                cls.nodetypes[c].append((item.__name__,item.bl_label,item.output_type))
        nodeitems_utils.register_node_categories('SORTSHADERNODES', cats)

    @classmethod
    def unregister(cls):
        nodeitems_utils.unregister_node_categories('SORTSHADERNODES')
        del bpy.types.Material.sort_material

# sort material node root
class SORTShadingNode(bpy.types.Node):
    bl_label = 'ShadingNode'
    bl_idname = 'SORTShadingNode'
    bl_icon = 'MATERIAL'
    output_type = 'SORTNodeSocketColor'
    property_list = []

    # register all property and sockets
    def register_prop(self,disable_output = False):
        # register all sockets
        for socket in self.property_list:
            if socket['class'].is_socket() is False:
                continue
            self.inputs.new( socket['class'].__name__ , socket['name'] )
            if 'default' in socket:
                self.inputs[socket['name']].default_value = socket['default']
        if disable_output is False:
            self.outputs.new( self.output_type , 'Result' )

    # this is not an overriden interface
    # draw all properties ( not socket ) in material panel
    def draw_props(self, context, layout, indented_label):
        for prop in self.property_list:
            if prop['class'].is_socket():
                continue
            split = layout.split(0.3)
            row = split.row()
            indented_label(row)
            row.label(prop['name'])
            prop_row = split.row()
            prop_row.prop(self,prop['name'],text="")
        pass

    # override the base interface
    # draw all properties ( not socket ) in material nodes
    def draw_buttons(self, context, layout):
        for prop in self.property_list:
            if prop['class'].is_socket():
                continue
            layout.prop(self,prop['name'])
        pass

    # export data to pbrt
    def export_pbrt(self, output_pbrt_type , output_pbrt_prop):
        pass

    def serializae_prop(self, serialize_method):
        for prop in self.property_list:
            if prop['class'].is_socket():
                continue
            attr_wrapper = getattr(self, prop['name'] + '_wrapper' )
            attr = getattr(self, prop['name'])
            v = attr_wrapper.export_serialization_value(attr_wrapper,attr)
            serialize_method( prop['name'] , v )

    def serialize_prop(self, fs):
        fs.serialize( len( self.property_list ) )
        for prop in self.property_list:
            if prop['class'].is_socket():
                value = self.inputs[prop['name']].export_osl_value()
                fs.serialize( value )
            else:
                attr_wrapper = getattr(self, prop['name'] + '_wrapper' )
                attr = getattr(self, prop['name'])
                value = attr_wrapper.export_osl_value(attr_wrapper,attr)
                fs.serialize( value )

    # register all properties in the class
    @classmethod
    def register(cls):
        for props in cls.get_mro('property_list'):
            if not props:
                continue
            for prop in props:
                var_name = prop['name']
                value = prop['class']
                if value.is_socket():
                    continue
                value.setup( prop )
                if 'register_properties' in dir(value):
                    for kp, vp in value.get_properties(var_name):
                        setattr(cls, kp, vp)
                else:
                    setattr(cls, var_name + '_wrapper', value )
                    setattr(cls, var_name, value.default_value )

    # unregister all properties in the class
    @classmethod
    def unregister(cls):
        for props in cls.get_mro('property_list'):
            if not props:
                continue
            for prop in props:
                k = prop['name']
                v = prop['class']
                if v.is_socket():
                    continue
                if 'register_properties' in dir(v):
                    for kp, vp in v.get_properties(k):
                        delattr(cls, kp)
                else:
                    delattr(cls, k)

    @classmethod
    def get_mro(cls, attribname):
        for k in reversed(cls.__mro__):
            vs = vars(k)
            if attribname in vs:
                yield vs[attribname]
    # register all properties in constructor
    def init(self, context):
        def do_mro(self, methname, *args, **kwargs):
            for meth in self.get_mro(methname):
                yield meth(self, *args, **kwargs)
        for _ in do_mro(self, 'register_prop'):
            pass

# Base class for SORT BXDF Node
class SORTShadingNode_BXDF(SORTShadingNode):
    bl_label = 'ShadingNode'
    bl_idname = 'SORTShadingNode'
    bl_icon = 'MATERIAL'
    output_type = 'SORTNodeSocketBxdf'
    bxdf_property_list = [ { 'class' : properties.SORTNodeSocketNormal , 'name' : 'Normal' } ]
    pbrt_bxdf_type = ''
    disable_normal = False

    def register_prop(self):
        if self.disable_normal is True:
            return
        # register all sockets in BXDF
        for prop in SORTShadingNode_BXDF.bxdf_property_list:
            self.inputs.new( prop['class'].__name__ , prop['name'] )
            if 'default' in prop:
                self.inputs[prop['name']].default_value = prop['default']

    def export_pbrt(self, output_pbrt_type , output_pbrt_prop):
        # disable pbrt export by default, not all materials are supported in pbrt
        if self.pbrt_bxdf_type is '':
            # fall back to a default grey matte material
            output_pbrt_type( 'matte' )
            return
        # output pbrt properties
        output_pbrt_type( self.pbrt_bxdf_type )
        for prop in self.property_list:
            if 'pbrt_name' in prop:
                n = prop['pbrt_name']
                t = self.inputs[prop['name']].export_pbrt_socket_type()
                v = self.inputs[prop['name']].export_socket_value()
                output_pbrt_prop( n , t , v )

#------------------------------------------------------------------------------------------------------------------------------------
#                                               Material Nodes for SORT
#------------------------------------------------------------------------------------------------------------------------------------
@SORTPatternGraph.register_node('Materials')
class SORTNode_Material_Principle(SORTShadingNode_BXDF):
    bl_label = 'Principle'
    bl_idname = 'SORTNode_Material_Principle'
    sort_bxdf_type = 'PrincipleMaterialNode'
    property_list = [ { 'class' : properties.SORTNodeSocketFloat , 'name' : 'RoughnessU' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'RoughnessV' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Metallic' , 'default' : 1.0 } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Specular' } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'BaseColor' } ]
    osl_shader = '''
        shader Principle( float RoughnessU = @ ,
                          float RoughnessV = @ ,
                          float Metallic = @ ,
                          float Specular = @ ,
                          color BaseColor = @ ,
                          output closure color Result = color(0) ){
            // UE4 PBS model
            Result = lambert( BaseColor , N ) * ( 1 - Metallic ) * 0.92 + microfacetReflection( "GGX", color( 0.37 ), color( 2.82 ), RoughnessU, RoughnessV, BaseColor , N ) * ( Metallic * 0.92 + 0.08 * Specular );
        }
    '''

@SORTPatternGraph.register_node('Materials')
class SORTNode_Material_DisneyBRDF(SORTShadingNode_BXDF):
    bl_label = 'Disney BRDF'
    bl_idname = 'SORTNode_Material_DisneyBRDF'
    sort_bxdf_type = 'DisneyPrincipleNode'
    pbrt_bxdf_type = 'disney'
    property_list = [ { 'class' : properties.SORTNodeSocketFloat , 'name' : 'SubSurface' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Metallic' , 'default' : 1.0 , 'pbrt_name' : 'metallic' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Specular' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'SpecularTint' , 'pbrt_name' : 'speculartint' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Roughness' , 'pbrt_name' : 'roughness' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Anisotropic' , 'pbrt_name' : 'anisotropic' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Sheen' , 'pbrt_name' : 'sheen' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'SheenTint' , 'pbrt_name' : 'sheentint' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Clearcoat' , 'pbrt_name' : 'clearcoat' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'ClearcoatGloss' , 'pbrt_name' : 'clearcoatgloass' } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'BaseColor' , 'pbrt_name' : 'color' } ]
    osl_shader = '''
        shader Disney( float SubSurface = @ ,
                       float Metallic = @ ,
                       float Specular = @ ,
                       float SpecularTint = @ ,
                       float Roughness = @ ,
                       float Anisotropic = @ ,
                       float Sheen = @ ,
                       float SheenTint = @ ,
                       float Clearcoat = @ ,
                       float ClearcoatGloss = @ ,
                       color BaseColor = @ ,
                       output closure color Result = color(0) ){
            Result = disney( SubSurface , Metallic , Specular , SpecularTint , Roughness , Anisotropic , Sheen , SheenTint , Clearcoat , ClearcoatGloss , BaseColor , N );
        }
    '''

@SORTPatternGraph.register_node('Materials')
class SORTNode_Material_Glass(SORTShadingNode_BXDF):
    bl_label = 'Glass'
    bl_idname = 'SORTNode_Material_Glass'
    sort_bxdf_type = 'GlassMaterialNode'
    pbrt_bxdf_type = 'glass'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Reflectance' , 'pbrt_name' : 'Kr' } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'Transmittance' , 'pbrt_name' : 'Kt' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'RoughnessU' , 'pbrt_name' : 'uroughness' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'RoughnessV' , 'pbrt_name' : 'vroughness' } ]
    osl_shader = '''
        shader Glass( color Reflectance = @ ,
                      color Transmittance = @ ,
                      float RoughnessU = @ ,
                      float RoughnessV = @ ,
                      output closure color Result = color(0) ){
            Result = dieletric( Reflectance , Transmittance , RoughnessU , RoughnessV , N );
        }
    '''

@SORTPatternGraph.register_node('Materials')
class SORTNode_Material_Plastic(SORTShadingNode_BXDF):
    bl_label = 'Plastic'
    bl_idname = 'SORTNode_Material_Plastic'
    sort_bxdf_type = 'PlasticMaterialNode'
    pbrt_bxdf_type = 'plastic'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Diffuse' , 'pbrt_name' : 'Kd' } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'Specular' , 'pbrt_name' : 'Ks' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Roughness' , 'default' : 0.2 , 'pbrt_name' : 'roughness' } ]
    osl_shader = '''
        shader Plastic( color Diffuse = @ ,
                        color Specular = @ ,
                        float Roughness = @ ,
                        output closure color Result = color(0) ){
            if( Diffuse[0] != 0 || Diffuse[1] != 0 || Diffuse[2] != 0 )
                Result += lambert( Diffuse , N );
            if( Specular[0] != 0 || Specular[1] != 0 || Specular[2] != 0 )
                Result += microfacetReflectionDieletric( "GGX", 1.0, 1.5, Roughness, Roughness, Specular , N );
        }
    '''

@SORTPatternGraph.register_node('Materials')
class SORTNode_Material_Matte(SORTShadingNode_BXDF):
    bl_label = 'Matte'
    bl_idname = 'SORTNode_Material_Matte'
    sort_bxdf_type = 'MatteMaterialNode'
    pbrt_bxdf_type = 'matte'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'BaseColor' , 'pbrt_name' : 'Kd' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Roughness' , 'pbrt_name' : 'sigma' } ]
    osl_shader = '''
        shader Matte( color BaseColor = @ ,
                      float Roughness = @ , 
                      output closure color Result = color(0)){
            if( Roughness == 0.0 )
                Result = lambert( BaseColor , N );
            else
                Result = orenNayar( BaseColor , Roughness , N );
        }
    '''

@SORTPatternGraph.register_node('Materials')
class SORTNode_Material_Mirror(SORTShadingNode_BXDF):
    bl_label = 'Mirror'
    bl_idname = 'SORTNode_Material_Mirror'
    sort_bxdf_type = 'MirrorMaterialNode'
    pbrt_bxdf_type = 'mirror'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'BaseColor' , 'pbrt_name' : 'Kd' } ]
    osl_shader = '''
        shader Mirror( color BaseColor = @ , 
                       output closure color Result = color(0) ){
            Result = microfacetReflection( "GGX" , 1.0 , 1.0 , 0.0 , 0.0 , BaseColor , N );
        }
    '''

@SORTPatternGraph.register_node('Materials')
class SORTNode_Material_Hair(SORTShadingNode_BXDF):
    bl_label = 'Hair'
    bl_idname = 'SORTNode_Material_Hair'
    sort_bxdf_type = 'HairMaterialNode'
    disable_normal = True       # No normal map support for hair rendering, it is meaningless
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'HairColor' },
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Longtitudinal Roughness' },
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Azimuthal Roughness' },
                      { 'class' : properties.SORTNodeSocketLargeFloat , 'name' : 'Index of Refraction' , 'default' : 1.55 } ]
    osl_shader = '''
        float helper( float x , float inv ){
            float y = log(x) * inv;
            return y * y;
        }
        shader Hair( color HairColor = @ ,
                     float LongtitudinalRoughness = @ ,
                     float AzimuthalRoughness = @ ,
                     float IndexofRefraction = @ , 
                     output closure color Result = color(0) ){
            // A Practical and Controllable Hair and Fur Model for Production Path Tracing
            // https://disney-animation.s3.amazonaws.com/uploads/production/publication_asset/147/asset/siggraph2015Fur.pdf
            float inv = 1.0 / ( 5.969 - 0.215 * AzimuthalRoughness + 2.532 * pow(AzimuthalRoughness,2.0) - 10.73 * pow(AzimuthalRoughness,3.0) + 
                        5.574 * pow(AzimuthalRoughness,4.0) + 0.245 * pow(AzimuthalRoughness, 5.0) );
            color sigma = color( helper(HairColor[0],inv) , helper(HairColor[1],inv) , helper(HairColor[2],inv) );
            Result = hair( sigma , LongtitudinalRoughness , AzimuthalRoughness , IndexofRefraction );
        }
    '''

@SORTPatternGraph.register_node('Materials')
class SORTNode_Material_Measured(SORTShadingNode_BXDF):
    bl_label = 'Measured'
    bl_idname = 'SORTNode_Material_Measured'
    sort_bxdf_type = 'MeasuredMaterialNode'
    property_list = [ { 'class' : properties.SORTNodePropertyEnum , 'name' : 'Type' , 'items' : [ ("Fourier", "Fourier", "", 1) , ("MERL" , "MERL" , "", 2) ] , 'default' : 'Fourier' } ,
                      { 'class' : properties.SORTNodePropertyPath , 'name' : 'Filename' } ]
    def export_pbrt(self, output_pbrt_type , output_pbrt_prop):
        abs_file_path = bpy.path.abspath( self.Filename )
        if self.Type == 'Fourier':
            output_pbrt_type( 'fourier' )
        else:
            output_pbrt_type( 'matte' )
        output_pbrt_prop( n , 'string' , abs_file_path.replace( '\\' , '/' ) )

@SORTPatternGraph.register_node('Materials')
class SORTNode_Material_Blend(SORTShadingNode_BXDF):
    bl_label = 'Blend'
    bl_idname = 'SORTNode_Material_Blend'
    sort_bxdf_type = 'BlendMaterialNode'
    disable_normal = True
    property_list = [ { 'class' : properties.SORTNodeSocketBxdf , 'name' : 'Bxdf0' } ,
                      { 'class' : properties.SORTNodeSocketBxdf , 'name' : 'Bxdf1' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Factor' } ]
    osl_shader = '''
        shader MaterialBlend(  closure color Bxdf0 = @ ,
                               closure color Bxdf1 = @ ,
                               float Factor = @ ,
                               output closure color Result = color(0) ){
            Result = Bxdf0 * ( 1.0 - Factor ) + Bxdf1 * Factor;
        }
    '''

@SORTPatternGraph.register_node('Materials')
class SORTNode_Material_DoubleSided(SORTShadingNode_BXDF):
    bl_label = 'Double-Sided'
    bl_idname = 'SORTNode_Material_DoubleSided'
    sort_bxdf_type = 'DoubleSidedMaterialNode'
    disable_normal = True
    property_list = [ { 'class' : properties.SORTNodeSocketBxdf , 'name' : 'Bxdf0' } ,
                      { 'class' : properties.SORTNodeSocketBxdf , 'name' : 'Bxdf1' } ]

#------------------------------------------------------------------------------------------------------------------------------------
#                                               BXDF Nodes for SORT
#------------------------------------------------------------------------------------------------------------------------------------
@SORTPatternGraph.register_node('BXDFs')
class SORTNode_BXDF_MicrofacetReflection(SORTShadingNode_BXDF):
    bl_label = 'MicrofacetRelection'
    bl_idname = 'SORTNode_BXDF_MicrofacetReflection'
    sort_bxdf_type = 'MicrofacetReflectionNode'
    property_list = [ { 'class' : properties.SORTNodePropertyEnum , 'name' : 'MicroFacetDistribution' , 'default' : 'GGX' , 'items' : [ ("Blinn", "Blinn", "", 1), ("Beckmann" , "Beckmann" , "", 2), ("GGX" , "GGX" , "" , 3) ] } ,
                      { 'class' : properties.SORTNodePropertyFloatVector , 'name' : 'Interior_IOR' , 'default' : (0.37, 0.37, 0.37) , 'min' : 0.1 , 'max' : 10.0 } ,
                      { 'class' : properties.SORTNodePropertyFloatVector , 'name' : 'Absorption_Coefficient' , 'default' : (2.82, 2.82, 2.82) , 'min' : 0.1 , 'max' : 10.0 },
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'RoughnessU' , 'default' : 0.1 } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'RoughnessV' , 'default' : 0.1 } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'BaseColor' } ]
    osl_shader = '''
        shader MicrofacetRelection(  string MicroFacetDistribution = @ ,
                                     color  Interior_IOR = @ ,
                                     color  Absorption_Coefficient = @ ,
                                     float  RoughnessU = @ ,
                                     float  RoughnessV = @ ,
                                     color  BaseColor = @ ,
                                     output closure color Result = color(0) ){
            Result = microfacetReflection( MicroFacetDistribution , Interior_IOR , Absorption_Coefficient , RoughnessU , RoughnessV , BaseColor , N );
        }
    '''

@SORTPatternGraph.register_node('BXDFs')
class SORTNode_BXDF_MicrofacetRefraction(SORTShadingNode_BXDF):
    bl_label = 'MicrofacetRefraction'
    bl_idname = 'SORTNode_BXDF_MicrofacetRefraction'
    sort_bxdf_type = 'MicrofacetRefractionNode'
    property_list = [ { 'class' : properties.SORTNodePropertyEnum , 'name' : 'MicroFacetDistribution' , 'default' : 'GGX' , 'items' : [ ("Blinn", "Blinn", "", 1), ("Beckmann" , "Beckmann" , "", 2), ("GGX" , "GGX" , "" , 3) ] } ,
                      { 'class' : properties.SORTNodePropertyFloat , 'name' : 'Interior_IOR' , 'default' : 1.1 , 'min' : 1.0 , 'max' : 10.0 } ,
                      { 'class' : properties.SORTNodePropertyFloat , 'name' : 'Exterior_IOR' , 'default' : 1.0 , 'min' : 1.0 , 'max' : 10.0 } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'RoughnessU' , 'default' : 0.1 } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'RoughnessV' , 'default' : 0.1 } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'BaseColor' } ]
    osl_shader = '''
        shader MicrofacetRefraction( string MicroFacetDistribution = @ ,
                                     float  Interior_IOR = @ ,
                                     float  Exterior_IOR = @ ,
                                     float  RoughnessU = @ ,
                                     float  RoughnessV = @ ,
                                     color  BaseColor = @ , 
                                     output closure color Result = color(0) ){
            Result = microfacetRefraction( MicroFacetDistribution , Interior_IOR , Exterior_IOR , RoughnessU , RoughnessV , BaseColor , N );
        }
    '''

@SORTPatternGraph.register_node('BXDFs')
class SORTNode_BXDF_AshikhmanShirley(SORTShadingNode_BXDF):
    bl_label = 'AshikhmanShirley'
    bl_idname = 'SORTNode_BXDF_AshikhmanShirley'
    sort_bxdf_type = 'AshikhmanShirleyNode'
    property_list = [ { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Specular' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'RoughnessU' , 'default' : 0.1 } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'RoughnessV' , 'default' : 0.1 } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'Diffuse' } ]
    osl_shader = '''
        shader AshikhmanShirley( float Specular = @ ,
                                 float RoughnessU = @ ,
                                 float RoughnessV = @ ,
                                 color Diffuse = @ ,
                                 output closure color Result = color(0) ){
            Result = ashikhmanShirley( Specular , RoughnessU , RoughnessV , Diffuse , N );
        }
    '''

@SORTPatternGraph.register_node('BXDFs')
class SORTNode_BXDF_Phong(SORTShadingNode_BXDF):
    bl_label = 'Phong'
    bl_idname = 'SORTNode_BXDF_Phong'
    sort_bxdf_type = 'PhongNode'
    property_list = [ { 'class' : properties.SORTNodeSocketLargeFloat , 'name' : 'SpecularPower' , 'default' : 32.0 } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'DiffuseRatio' , 'default' : 0.2 } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'Specular' } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'Diffuse' } ]
    osl_shader = '''
        shader Phong( float SpecularPower = @ ,
                      float DiffuseRatio = @ ,
                      color Specular = @ ,
                      color Diffuse = @ ,
                      output closure color Result = color(0) ){
            Result = phong( Diffuse * DiffuseRatio , ( 1.0 - DiffuseRatio ) * Specular , SpecularPower , N );
        }
    '''

@SORTPatternGraph.register_node('BXDFs')
class SORTNode_BXDF_Lambert(SORTShadingNode_BXDF):
    bl_label = 'Lambert'
    bl_idname = 'SORTNode_BXDF_Lambert'
    sort_bxdf_type = 'LambertNode'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Diffuse' } ]
    osl_shader = '''
        shader Lambert( color Diffuse = @ ,
                        output closure color Result = color(0) ){
            Result = lambert( Diffuse , N );
        }
    ''' 

@SORTPatternGraph.register_node('BXDFs')
class SORTNode_BXDF_LambertTransmission(SORTShadingNode_BXDF):
    bl_label = 'Lambert Transmission'
    bl_idname = 'SORTNode_BXDF_LambertTransmission'
    sort_bxdf_type = 'LambertTransmissionNode'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Diffuse' } ]
    osl_shader = '''
        shader LambertTransmission( color Diffuse = @ ,
                                    output closure color Result = color(0) ){
            Result = lambertTransmission( Diffuse , N );
        }
    '''

@SORTPatternGraph.register_node('BXDFs')
class SORTNode_BXDF_OrenNayar(SORTShadingNode_BXDF):
    bl_label = 'OrenNayar'
    bl_idname = 'SORTNode_BXDF_OrenNayar'
    sort_bxdf_type = 'OrenNayarNode'
    property_list = [ { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Roughness' } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'Diffuse' } ]
    osl_shader = '''
        shader OrenNayar( float roughness = @,
                          color Diffuse = @ ,
                          output closure color Result = color(0) ){
            Result = orenNayar( Diffuse , roughness , N );
        }
    '''

@SORTPatternGraph.register_node('BXDFs')
class SORTNode_BXDF_Coat(SORTShadingNode_BXDF):
    bl_label = 'Coat'
    bl_idname = 'SORTNode_BXDF_Coat'
    sort_bxdf_type = 'CoatNode'
    property_list = [ { 'class' : properties.SORTNodePropertyFloat  , 'name' : 'IOR'        , 'default' : 1.5 , 'min' : 1.0 , 'max' : 10.0 } ,
                      { 'class' : properties.SORTNodeSocketFloat    , 'name' : 'Roughness'  , 'default' : 0.0 } ,
                      { 'class' : properties.SORTNodeSocketColor    , 'name' : 'ColorTint' } ,
                      { 'class' : properties.SORTNodeSocketBxdf     , 'name' : 'Surface' } ]
    osl_shader = '''
    '''

@SORTPatternGraph.register_node('BXDFs')
class SORTNode_BXDF_MERL(SORTShadingNode_BXDF):
    bl_label = 'MERL'
    bl_idname = 'SORTNode_BXDF_MERL'
    sort_bxdf_type = 'MerlNode'
    property_list = [ { 'class' : properties.SORTNodePropertyPath , 'name' : 'Filename' } ]

@SORTPatternGraph.register_node('BXDFs')
class SORTNode_BXDF_Fourier(SORTShadingNode_BXDF):
    bl_label = 'Fourier BXDF'
    bl_idname = 'SORTNode_BXDF_Fourier'
    sort_bxdf_type = 'FourierBxdfNode'
    property_list = [ { 'class' : properties.SORTNodePropertyPath , 'name' : 'Filename' } ]

#------------------------------------------------------------------------------------------------------------------------------------
#                                               Operator Nodes for SORT
#------------------------------------------------------------------------------------------------------------------------------------
@SORTPatternGraph.register_node('Operator')
class SORTNodeAdd(SORTShadingNode):
    bl_label = 'Add'
    bl_idname = 'SORTNodeAdd'
    sort_bxdf_type = 'AddNode'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color1' } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color2' } ]
    osl_shader = '''
        shader Add( color Color1 = @ ,
                    color Color2 = @ ,
                    output color Result = color( 0.0 , 0.0 , 0.0 ) ){
            Result = Color1 + Color2;
        }
    '''

@SORTPatternGraph.register_node('Operator')
class SORTNodeOneMinus(SORTShadingNode):
    bl_label = 'One Minus'
    bl_idname = 'SORTNodeOneMinus'
    sort_bxdf_type = 'SORTNodeOneMinus'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color' } ]
    osl_shader = '''
        shader OneMinus( color Color = @ ,
                         output color Result = color( 0.0 , 0.0 , 0.0 ) ){
            Result = color( 1.0 ) - Color;
        }
    '''

@SORTPatternGraph.register_node('Operator')
class SORTNodeMultiply(SORTShadingNode):
    bl_label = 'Multiply'
    bl_idname = 'SORTNodeMultiply'
    sort_bxdf_type = 'MutiplyNode'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color1' } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color2' } ]
    osl_shader = '''
        shader Multiply( color Color1 = @ ,
                         color Color2 = @ ,
                         output color Result = color( 0.0 , 0.0 , 0.0 ) ){
            Result = Color1 * Color2;
        }
    '''

@SORTPatternGraph.register_node('Operator')
class SORTNodeBlend(SORTShadingNode):
    bl_label = 'Blend'
    bl_idname = 'SORTNodeBlend'
    sort_bxdf_type = 'BlendNode'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color1' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Factor1' } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color2' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Factor2' } ]
    osl_shader = '''
        shader Blend( color Color1 = @ ,
                      float Factor1 = @ ,
                      color Color2 = @ ,
                      float Factor2 = @ ,
                      output color Result = color( 0.0 , 0.0 , 0.0 ) ){
            Result = Color1 * Factor1 + Color2 * Factor2;
        }
    '''

@SORTPatternGraph.register_node('Operator')
class SORTNodeLerp(SORTShadingNode):
    bl_label = 'Lerp'
    bl_idname = 'SORTNodeLerp'
    sort_bxdf_type = 'LerpNode'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color1' } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color2' } ,
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Factor' } ]
    osl_shader = '''
        shader Lerp( color Color1 = @ ,
                     color Color2 = @ ,
                     float Factor = @ ,
                     output color Result = color( 0.0 , 0.0 , 0.0 ) ){
            Result = Color1 * ( 1.0 - Factor ) + Color2 * Factor;
        }
    '''

@SORTPatternGraph.register_node('Operator')
class SORTNodeLinearToGamma(SORTShadingNode):
    bl_label = 'LinearToGamma'
    bl_idname = 'SORTNodeLinearToGamma'
    sort_bxdf_type = 'LinearToGammaNode'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color' } ]
    osl_shader = '''
        shader LinearToGamma( color Color = @ ,
                              output color Result = color( 0.0 , 0.0 , 0.0 ) ){
            Result = pow( Color , 1.0/2.2 );
        }
    '''

@SORTPatternGraph.register_node('Operator')
class SORTNodeGammaToLinear(SORTShadingNode):
    bl_label = 'GammaToLinear'
    bl_idname = 'SORTNodeGammaToLinear'
    sort_bxdf_type = 'GammaToLinearNode'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color' } ]
    osl_shader = '''
        shader GammaToLinear( color Color = @ ,
                              output color Result = color( 0.0 , 0.0 , 0.0 ) ){
            Result = pow( Color , 2.2 );
        }
    '''

@SORTPatternGraph.register_node('Operator')
class SORTNodeDecodeNormal(SORTShadingNode):
    bl_label = 'DecodeNormal'
    bl_idname = 'SORTNodeDecodeNormal'
    sort_bxdf_type = 'NormalDecoderNode'
    output_type = 'SORTNodeSocketNormal'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color' } ]
    osl_shader = '''
        shader DecodeNormal( color Color = @ ,
                             output color Result = color( 0.0 , 0.0 , 0.0 ) ){
            Result = 2.0 * iColor - 1.0;
        }
    '''

#------------------------------------------------------------------------------------------------------------------------------------
#                                               Texture Nodes for SORT
#------------------------------------------------------------------------------------------------------------------------------------
@SORTPatternGraph.register_node('Image')
class SORTNodeGrid(SORTShadingNode):
    bl_label = 'Grid'
    bl_idname = 'SORTNodeGrid'
    sort_bxdf_type = 'GridTexNode'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color1' , 'default' : ( 0.2 , 0.2 , 0.2 ) } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color2' },
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Treshold' , 'default' : 0.1 , 'min' : 0.0 , 'max' : 1.0 },
                      { 'class' : properties.SORTNodeSocketUV , 'name' : 'UV Mapping' } ]
    osl_shader = '''
        shader CheckerBoard( color Color1 = @ ,
                             color Color2 = @ ,
                             float Treshold = @ ,
                             vector UVMapping = @ ,
                             output color Result = color( 0.0 , 0.0 , 0.0 ) ){
            float fu = UVMapping[0] - floor( UVMapping[0] ) - 0.5;
            float fv = UVMapping[1] - floor( UVMapping[1] ) - 0.5;
            float half_threshold = ( 1.0 - Treshold ) * 0.5;
            if( fu <= half_threshold && fu >= -half_threshold && fv <= half_threshold && fv >= -half_threshold )
                Result = Color1;
            else
                Result = Color2;
        }
    '''
    
@SORTPatternGraph.register_node('Image')
class SORTNodeCheckerBoard(SORTShadingNode):
    bl_label = 'CheckerBoard'
    bl_idname = 'SORTNodeCheckerBoard'
    sort_bxdf_type = 'CheckerBoardTexNode'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color1' , 'default' : ( 0.2 , 0.2 , 0.2 ) } ,
                      { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color2' } ,
                      { 'class' : properties.SORTNodeSocketUV , 'name' : 'UV Mapping' } ]
    osl_shader = '''
        shader CheckerBoard( color Color1 = @ ,
                             color Color2 = @ ,
                             vector UVMapping = @ ,
                             output color Result = color( 0.0 , 0.0 , 0.0 ) ){
            float fu = UVMapping[0] - floor( UVMapping[0] );
            float fv = UVMapping[1] - floor( UVMapping[1] );
            if( ( fu > 0.5 && fv > 0.5 ) || ( fu < 0.5 && fv < 0.5 ) )
                Result = Color1;
            else
                Result = Color2;
        }
    '''

@SORTPatternGraph.register_node('Image')
class SORTNodeImage(SORTShadingNode):
    bl_label = 'Image'
    bl_idname = 'SORTNodeImage'
    sort_bxdf_type = 'ImageTexNode'
    property_list = [ { 'class' : properties.SORTNodePropertyPath , 'name' : 'Filename' },
                      { 'class' : properties.SORTNodeSocketUV , 'name' : 'UV' } ]
    osl_shader = '''
        
    '''

#------------------------------------------------------------------------------------------------------------------------------------
#                                               Input Nodes for SORT
#------------------------------------------------------------------------------------------------------------------------------------
@SORTPatternGraph.register_node('Input')
class SORTNodeConstant(SORTShadingNode):
    bl_label = 'Constant Color'
    bl_idname = 'SORTNodeConstant'
    sort_bxdf_type = 'ConstantColorNode'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color' } ]
    osl_shader = '''
        shader ConstantColor( color Color = @ ,
                              output color Result = color( 0.0 , 0.0 , 0.0 ) ){
            Result = Color;
        }
    '''

@SORTPatternGraph.register_node('Input')
class SORTNodeConstantFloat(SORTShadingNode):
    bl_label = 'Constant Float'
    bl_idname = 'SORTNodeConstantFloat'
    output_type = 'SORTNodeSocketFloat'
    sort_bxdf_type = 'ConstantFloatNode'
    property_list = [ { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Value' } ]
    osl_shader = '''
        shader ConstantFloat( float Value = @ ,
                              output float Result = 0.0 ){
            Result = Value;
        }
    '''

@SORTPatternGraph.register_node('Input')
class SORTNodeUVMapping(SORTShadingNode):
    bl_label = 'UV Mapping'
    bl_idname = 'SORTNodeUVMapping'
    output_type = 'SORTNodeSocketUV'
    sort_bxdf_type = 'UVMappingNode'
    property_list = [ { 'class' : properties.SORTNodePropertyLargeFloat , 'name' : 'U Tiling' , 'default' : 1.0 , 'min' : -float('inf') , 'max' : float('inf') } ,
                      { 'class' : properties.SORTNodePropertyLargeFloat , 'name' : 'V Tiling' , 'default' : 1.0, 'min' : -float('inf') , 'max' : float('inf') } ,
                      { 'class' : properties.SORTNodePropertyLargeFloat , 'name' : 'U Offset' , 'default' : 0.0, 'min' : -float('inf') , 'max' : float('inf') } ,
                      { 'class' : properties.SORTNodePropertyLargeFloat , 'name' : 'V Offset' , 'default' : 0.0, 'min' : -float('inf') , 'max' : float('inf') } ]
    def init(self, context):
        super().register_prop(True)
        self.outputs.new( self.output_type , 'UV Mapping' )
    osl_shader = '''
        shader UVMappinp( float UTiling = @ ,
                          float VTiling = @ ,
                          float UOffset = @ ,
                          float VOffset = @ ,
                          output vector UVMapping = 0.0 ){
            UVMapping = vector( u * UTiling + UOffset , v * VTiling + VOffset , 0.0 );
        }
    '''

#------------------------------------------------------------------------------------------------------------------------------------
#                                               Convertor Nodes for SORT
#------------------------------------------------------------------------------------------------------------------------------------
@SORTPatternGraph.register_node('Convertor')
class SORTNodeComposite(SORTShadingNode):
    bl_label = 'Composite'
    bl_idname = 'SORTNodeComposite'
    sort_bxdf_type = 'SORTNodeComposite'
    property_list = [ { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Red' },
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Green' },
                      { 'class' : properties.SORTNodeSocketFloat , 'name' : 'Blue' } ]
    osl_shader = '''
        shader Composite( float Red = @ ,
                          float Green = @ ,
                          float Blue = @ ,
                          output color Result = color( 0.0 , 0.0 , 0.0 ) ){
            Result = color( Red , Green , Blue );
        }
    '''

@SORTPatternGraph.register_node('Convertor')
class SORTNodeExtract(SORTShadingNode):
    bl_label = 'Extract'
    bl_idname = 'SORTNodeExtract'
    output_type = 'SORTNodeSocketFloat'
    sort_bxdf_type = 'SORTNodeExtract'
    property_list = [ { 'class' : properties.SORTNodeSocketColor , 'name' : 'Color' } ]
    osl_shader = '''
        shader Extract( color Color = @,
                        output float Red = 0.0 ,
                        output float Green = 0.0 ,
                        output float Blue = 0.0 ,
                        output float Intensity = 0.0 ){
            Red = Color[0];
            Green = Color[1];
            Blue = Color[2];
            Intensity = Color[0] * 0.212671 + Color[1] * 0.715160 + Color[2] * 0.072169;
        }
    '''

    def init(self, context):
        super().register_prop(True)
        self.outputs.new( self.output_type , 'Red' )
        self.outputs.new( self.output_type , 'Green' )
        self.outputs.new( self.output_type , 'Blue' )
        self.outputs.new( self.output_type , 'Intensity' )

#------------------------------------------------------------------------------------------------------------------------------------
#                                               Output Nodes for SORT
#------------------------------------------------------------------------------------------------------------------------------------
class SORTNodeOutput(SORTShadingNode):
    bl_label = 'SORT_output'
    bl_idname = 'SORTNodeOutput'
    sort_bxdf_type = ''
    property_list = [ { 'class' : properties.SORTNodeSocketBxdf , 'name' : 'Surface' } ]
    osl_shader = '''
        shader SORT_Shader( closure color Surface = @ ){
            Ci = Surface;
        }
    '''

    def init(self, context):
        super().register_prop(True)
