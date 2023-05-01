bl_info = {
    "name": "PBR Export Tool",
    "author": "Newo Ether",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N",
    "description": "A Convenient Tool for Exporting PBR Textures from Blender Materials",
    "category": "Material",
}


import bpy
import os.path
from bpy.types import (Panel,Operator)
from bpy_extras.io_utils import ImportHelper
from . import export

lang = ''

def getLanguage():
    global lang
    lang = bpy.app.translations.locale

def getMaterialList():
    global _materials
    _materials = []
    for i in range(0,len(bpy.data.materials)):
        mat = bpy.data.materials[i]
        if mat.name != 'Dots Stroke':
            _materials.append((str(i),mat.name+' ',''))

def GenerateProperty():
    bpy.types.Scene.ExportPath = bpy.props.StringProperty(name="Export Path", default='')
    bpy.types.Scene.Materials = bpy.props.EnumProperty(name="Material", items=lambda self, context: _materials)
    bpy.types.Scene.BaseColor = bpy.props.BoolProperty(name="Base Color", default=True)
    bpy.types.Scene.Metallic = bpy.props.BoolProperty(name="Metallic", default=True)
    bpy.types.Scene.Roughness = bpy.props.BoolProperty(name="Roughness", default=True)
    bpy.types.Scene.Normal = bpy.props.BoolProperty(name="Normal", default=True)
    bpy.types.Scene.Resolution = bpy.props.EnumProperty(name="Resolution", items=_resolutions)
    bpy.types.Scene.RenderDevice = bpy.props.EnumProperty(name="Render Device", items=_render_devices)


class SelectFolderOperator(bpy.types.Operator, ImportHelper):
    global lang
    getLanguage()
    bl_idname = "select.folder"
    if lang == 'zh_CN':
        bl_label = "选择输出文件夹"
    else:
        bl_label = "Select Export Folder"
    filename_ext = "."
    use_filter_folder = True
    
    def execute(self, context):
        export_path = self.properties.filepath
        len_path = len(export_path)
        if export_path != '':
            i=-1
            while export_path[i] != '\\' and export_path[i] != '/':
                if abs(i-1) > len_path:
                    return {'FINISHED'}
                i=i-1
            export_path = export_path[0:len_path-abs(i+1)]
            if os.path.isdir(export_path):
                context.scene.ExportPath = export_path
        return {'FINISHED'}


class ExportOperator(bpy.types.Operator):
    bl_idname = "export.folder"
    bl_label = "Export"
    use_filter_folder = True
    
    def execute(self, context):
        global lang
        getLanguage()
        resolution_dic = {
            '256x256' : 256,
            '512x512' : 512,
            '1024x1024' : 1024,
            '2048x2048' : 2048,
            '4096x4096' : 4096,
            '8192x8192' : 8192
        }
        path = context.scene.ExportPath
        if not os.path.exists(path):
            if lang == 'zh_CN':
                msg = "输出路径无效！"
            else:
                msg = "Invalid export path!"
            self.report({'ERROR'}, msg)
            return {'FINISHED'}
        if path[-1] != '\\' and path[-1] != '/':
            path = path + '\\'
        resolution = resolution_dic[context.scene.Resolution]
        device = context.scene.RenderDevice
        material = context.scene.Materials
        if len(material) == 0:
                if lang == 'zh_CN':
                    msg = "未选择材质！"
                else:
                    msg = "Material not selected!"
                self.report({'ERROR'}, msg)
                return {'FINISHED'}
        base_color = context.scene.BaseColor
        metallic = context.scene.Metallic
        roughness = context.scene.Roughness
        normal = context.scene.Normal
        if not(base_color) and not(metallic) and not(roughness) and not(normal):
            if lang == 'zh_CN':
                msg = "至少选择一个输出类型！"
            else:
                msg = "Select at least one export layer!"
            self.report({'ERROR'}, msg)
            return {'FINISHED'}
        export_items = [base_color,metallic,roughness,normal]
        export.Export(self,context,path,resolution,device,bpy.data.materials[int(material)],export_items)
        return {'FINISHED'}


class MainPanel(bpy.types.Panel):
    bl_label = "PBR Export Tool"
    bl_idname = "PBR_PT_Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PBR Export Tool"

    def draw(self, context):
        global lang
        getLanguage()
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        row = layout.row(align=True)

        if lang == 'zh_CN':
            row.prop(context.scene, 'ExportPath', text='输出路径')
        else:
            row.prop(context.scene, 'ExportPath', text='Export Path')

        row.operator(SelectFolderOperator.bl_idname, text="", icon="FILEBROWSER")
        getMaterialList()
        
        if lang == 'zh_CN':
            layout.prop(context.scene, 'Materials', text='选择材质')
        else:
            layout.prop(context.scene, 'Materials', text='Material')

        if lang == 'zh_CN':
            layout.prop(context.scene, 'RenderDevice', text='烘焙设备')
        else:
            layout.prop(context.scene, 'RenderDevice', text='Render Device')

        col_option = layout.column()
        
        if lang == 'zh_CN':
            col_option.label(text="导出选项")
        else:
            col_option.label(text="Export Options")

        box = col_option.box()

        if lang == 'zh_CN':
            sub_col = box.column(heading='输出类型')
            sub_col.prop(context.scene, 'BaseColor', text="基础色")
            sub_col.prop(context.scene, 'Metallic', text="金属度")
            sub_col.prop(context.scene, 'Roughness', text="粗糙度")
            sub_col.prop(context.scene, 'Normal', text="法向")
            box.prop(context.scene, 'Resolution', text='输出分辨率')
            layout.operator(ExportOperator.bl_idname, text='导出 PBR 贴图')
        else:
            sub_col = box.column(heading='Export layers')
            sub_col.prop(context.scene, 'BaseColor', text="Base Color")
            sub_col.prop(context.scene, 'Metallic', text="Metallic")
            sub_col.prop(context.scene, 'Roughness', text="Roughness")
            sub_col.prop(context.scene, 'Normal', text="Normal")
            box.prop(context.scene, 'Resolution', text='Resolution')
            layout.operator(ExportOperator.bl_idname, text='Export')


_classes = [
    SelectFolderOperator,
    ExportOperator,
    MainPanel
]


_materials = []


_resolutions = [
    ('256x256','256x256',''),
    ('512x512','512x512',''),
    ('1024x1024','1024x1024',''),
    ('2048x2048','2048x2048',''),
    ('4096x4096','4096x4096',''),
    ('8192x8192','8192x8192','')
]


_render_devices = [
    ('CPU','CPU',''),
    ('GPU','GPU','')
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    GenerateProperty()


def unregister():
    for cls in _classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    getLanguage()
    register()
