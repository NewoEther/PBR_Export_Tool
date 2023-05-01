import bpy

def Export(self,context,export_path,texture_resolution,device,material,export_items):
    #acquire language settings
    lang = bpy.app.translations.locale

    #deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    #delete temp collection if exists
    for collection in bpy.data.collections:
        if collection.name == 'PBR_Export_Temp':
            for obj in collection.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(collection)
    
    #delete temp plane if exists
    for object in bpy.data.objects:
        if object.name == 'Temp_Plane':
            bpy.data.objects.remove(obj, do_unlink=True)

    #create initial plane
    temp_collection = bpy.data.collections.new('PBR_Export_Temp')
    bpy.context.scene.collection.children.link(temp_collection)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children['PBR_Export_Temp']
    bpy.ops.mesh.primitive_plane_add()
    bpy.context.active_object.name = 'Temp_Plane'

    #save previous rendering settings
    
    previous_render_engine = bpy.context.scene.render.engine
    previous_device = bpy.context.scene.cycles.device
    previous_is_using_adaptive_sampling = bpy.context.scene.cycles.use_adaptive_sampling
    previous_samples = bpy.context.scene.cycles.samples
    previous_min_samples = bpy.context.scene.cycles.adaptive_min_samples
    previous_is_using_denoising = bpy.context.scene.cycles.use_denoising
    previous_time_limit = bpy.context.scene.cycles.time_limit
    previous_display_device = bpy.context.scene.display_settings.display_device
    previous_view_transform = bpy.context.scene.view_settings.view_transform
    previous_look = bpy.context.scene.view_settings.look
    previous_exposure = bpy.context.scene.view_settings.exposure
    previous_gamma = bpy.context.scene.view_settings.gamma
    previous_sequencer_colorspace = bpy.context.scene.sequencer_colorspace_settings.name
    previous_use_curve_mapping = bpy.context.scene.view_settings.use_curve_mapping

    #change rendering settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = device
    bpy.context.scene.cycles.use_adaptive_sampling = False
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.cycles.adaptive_min_samples = 1
    bpy.context.scene.cycles.use_denoising = False
    bpy.context.scene.cycles.time_limit = 0
    bpy.context.scene.display_settings.display_device = 'sRGB'
    bpy.context.scene.view_settings.view_transform = 'Standard'
    bpy.context.scene.view_settings.look = 'None'
    bpy.context.scene.view_settings.exposure = 0
    bpy.context.scene.view_settings.gamma = 1
    bpy.context.scene.sequencer_colorspace_settings.name = 'sRGB'
    bpy.context.scene.view_settings.use_curve_mapping = False

    #assign materials
    mat = material
    bpy.context.active_object.data.materials.append(mat)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    #check nodes
    for m in nodes:
        if m.name == 'PBR_Bake_Node':
            nodes.remove(m)
    count = 0
    for node in nodes:
        if node.type == 'OUTPUT_MATERIAL':
            material_output_node = node
            count = count + 1
    if count == 0:
        bpy.context.scene.cycles.use_adaptive_sampling = previous_is_using_adaptive_sampling
        bpy.context.scene.cycles.samples = previous_samples
        bpy.context.scene.cycles.adaptive_min_samples = previous_min_samples
        bpy.context.scene.cycles.use_denoising = previous_is_using_denoising
        bpy.context.scene.cycles.time_limit = previous_time_limit
        bpy.context.scene.render.engine = previous_render_engine
        bpy.ops.object.delete()
        bpy.data.collections.remove(temp_collection)
        if lang == 'zh_CN':
            msg = "选择的材质没有材质输出节点！"
        else:
            msg = "Selected material doesn't contain a material output node!"
        self.report({'ERROR'}, msg)
        return {'FINISHED'}
    if count > 1:
        bpy.context.scene.cycles.use_adaptive_sampling = previous_is_using_adaptive_sampling
        bpy.context.scene.cycles.samples = previous_samples
        bpy.context.scene.cycles.adaptive_min_samples = previous_min_samples
        bpy.context.scene.cycles.use_denoising = previous_is_using_denoising
        bpy.context.scene.cycles.time_limit = previous_time_limit
        bpy.context.scene.render.engine = previous_render_engine
        bpy.ops.object.delete()
        bpy.data.collections.remove(temp_collection)
        if lang == 'zh_CN':
            msg = "选择的材质包含多余一个材质输出节点！"
        else:
            msg = "Selected material contain multiple material output nodes!"
        self.report({'ERROR'}, msg)
        return {'FINISHED'}
    material_output_socket = material_output_node.inputs['Surface']
    if len(material_output_socket.links) == 0:
        bpy.context.scene.cycles.use_adaptive_sampling = previous_is_using_adaptive_sampling
        bpy.context.scene.cycles.samples = previous_samples
        bpy.context.scene.cycles.adaptive_min_samples = previous_min_samples
        bpy.context.scene.cycles.use_denoising = previous_is_using_denoising
        bpy.context.scene.cycles.time_limit = previous_time_limit
        bpy.context.scene.render.engine = previous_render_engine
        bpy.ops.object.delete()
        bpy.data.collections.remove(temp_collection)
        if lang == 'zh_CN':
            msg = "选择的材质未指定着色器！"
        else:
            msg = "Selected material doesn't contain a shader!"
        self.report({'ERROR'}, msg)
        return {'FINISHED'}
    shader_node = material_output_socket.links[0].from_node
    if shader_node.type != "BSDF_PRINCIPLED":
        bpy.context.scene.cycles.use_adaptive_sampling = previous_is_using_adaptive_sampling
        bpy.context.scene.cycles.samples = previous_samples
        bpy.context.scene.cycles.adaptive_min_samples = previous_min_samples
        bpy.context.scene.cycles.use_denoising = previous_is_using_denoising
        bpy.context.scene.cycles.time_limit = previous_time_limit
        bpy.context.scene.render.engine = previous_render_engine
        bpy.ops.object.delete()
        bpy.data.collections.remove(temp_collection)
        if lang == 'zh_CN':
            msg = "仅支持使用原理化着色器的材质！"
        else:
            msg = "Only supports the material which uses the Principle shader!"
        self.report({'ERROR'}, msg)
        return {'FINISHED'}

    if export_items[0]:
        #add empty image texture node
        texture_node = nodes.new('ShaderNodeTexImage')
        texture_node.name = 'PBR_Bake_Node'
        texture_node.select = True
        nodes.active = texture_node
        img = bpy.data.images.new(material.name + '_' + str(texture_resolution) + 'x' + str(texture_resolution) +'_BaseColor',texture_resolution,texture_resolution)
        texture_node.image = img
        #change colorspace to sRGB
        previous_colorspace_list = []
        image_list = bpy.data.images
        for i in range(0,len(image_list)):
            previous_colorspace_list.append(image_list[i].colorspace_settings.name)
            if image_list[i].colorspace_settings.name != '':
                image_list[i].colorspace_settings.name = 'sRGB'
        #bake base color
        base_color_socket = shader_node.inputs['Base Color']
        emission_socket = shader_node.inputs['Emission']
        is_emission_socket_linked = False
        emission_color_value = [0.0, 0.0, 0.0, 1.0]
        for i in range(0,4):
            emission_color_value[i] = emission_socket.default_value[i]
        if len(emission_socket.links) != 0:
            is_emission_socket_linked = True
            before_emission_socket = emission_socket.links[0].from_socket
            mat.node_tree.links.remove(emission_socket.links[0])
        if len(base_color_socket.links) == 0:
            base_color_value = [0.0, 0.0, 0.0, 1.0]
            for i in range(0,4):
                base_color_value[i] = base_color_socket.default_value[i]
            emission_socket.default_value = base_color_value
        else:
            last_socket = base_color_socket.links[0].from_socket
            mat.node_tree.links.new(last_socket,emission_socket)
        bpy.ops.object.bake(type='EMIT',save_mode='EXTERNAL',width=texture_resolution,height=texture_resolution)
        img.save_render(filepath = export_path + material.name + '\\' + material.name + '_' + str(texture_resolution) + 'x' + str(texture_resolution) +'_BaseColor.png')
        #restore nodes
        nodes.remove(texture_node)
        emission_socket.default_value = emission_color_value
        if is_emission_socket_linked:
            mat.node_tree.links.new(before_emission_socket,emission_socket)
        else:
            if len(emission_socket.links) != 0:
                mat.node_tree.links.remove(emission_socket.links[0])
        #restore colorspace
        image_list = bpy.data.images
        for i in range(0,len(image_list)):
            if previous_colorspace_list[i] != '':
                image_list[i].colorspace_settings.name = previous_colorspace_list[i]

    if export_items[1]:
        #add empty image texture node
        texture_node = nodes.new('ShaderNodeTexImage')
        texture_node.name = 'PBR_Bake_Node'
        texture_node.select = True
        nodes.active = texture_node
        img = bpy.data.images.new(material.name + '_' + str(texture_resolution) + 'x' + str(texture_resolution) +'_Metallic',texture_resolution,texture_resolution)
        texture_node.image = img
        #change colorspace to sRGB
        previous_colorspace_list = []
        image_list = bpy.data.images
        for i in range(0,len(image_list)):
            previous_colorspace_list.append(image_list[i].colorspace_settings.name)
            if image_list[i].colorspace_settings.name != '':
                image_list[i].colorspace_settings.name = 'sRGB'
        #bake metallic
        metallic_socket = shader_node.inputs['Metallic']
        emission_socket = shader_node.inputs['Emission']
        is_emission_socket_linked = False
        is_bw_node_exist = False
        emission_color_value = [0.0, 0.0, 0.0, 1.0]
        for i in range(0,4):
            emission_color_value[i] = emission_socket.default_value[i]
        if len(emission_socket.links) != 0:
            is_emission_socket_linked = True
            before_emission_socket = emission_socket.links[0].from_socket
            mat.node_tree.links.remove(emission_socket.links[0])
        if len(metallic_socket.links) == 0:
            metallic_value = metallic_socket.default_value
            emission_socket.default_value = [metallic_value,metallic_value,metallic_value,1.0]
        else:
            is_bw_node_exist = True
            last_socket = metallic_socket.links[0].from_socket
            bw_node = nodes.new('ShaderNodeRGBToBW')
            bw_node.name = 'RGB_to_BW_Node'
            bw_node_input_socket = bw_node.inputs['Color']
            bw_node_output_socket = bw_node.outputs['Val']
            mat.node_tree.links.new(last_socket,bw_node_input_socket)
            mat.node_tree.links.new(bw_node_output_socket,emission_socket)
        bpy.ops.object.bake(type='EMIT',save_mode='EXTERNAL',width=texture_resolution,height=texture_resolution)
        img.save_render(filepath = export_path + material.name + '\\' + material.name + '_' + str(texture_resolution) + 'x' + str(texture_resolution) +'_Metallic.png')
        #restore nodes
        nodes.remove(texture_node)
        emission_socket.default_value = emission_color_value
        if is_bw_node_exist:
            nodes.remove(bw_node)
        if is_emission_socket_linked:
            mat.node_tree.links.new(before_emission_socket,emission_socket)
        else:
            if len(emission_socket.links) != 0:
                mat.node_tree.links.remove(emission_socket.links[0])
        #restore colorspace
        image_list = bpy.data.images
        for i in range(0,len(image_list)):
            if previous_colorspace_list[i] != '':
                image_list[i].colorspace_settings.name = previous_colorspace_list[i]

    if export_items[2]:
        #add empty image texture node
        texture_node = nodes.new('ShaderNodeTexImage')
        texture_node.name = 'PBR_Bake_Node'
        texture_node.select = True
        nodes.active = texture_node
        img = bpy.data.images.new(material.name + '_' + str(texture_resolution) + 'x' + str(texture_resolution) +'_Roughness',texture_resolution,texture_resolution)
        texture_node.image = img
        #change colorspace to sRGB
        previous_colorspace_list = []
        image_list = bpy.data.images
        for i in range(0,len(image_list)):
            previous_colorspace_list.append(image_list[i].colorspace_settings.name)
            if image_list[i].colorspace_settings.name != '':
                image_list[i].colorspace_settings.name = 'sRGB'
        #bake roughness
        roughness_socket = shader_node.inputs['Roughness']
        emission_socket = shader_node.inputs['Emission']
        is_emission_socket_linked = False
        is_bw_node_exist = False
        emission_color_value = [0.0, 0.0, 0.0, 1.0]
        for i in range(0,4):
            emission_color_value[i] = emission_socket.default_value[i]
        if len(emission_socket.links) != 0:
            is_emission_socket_linked = True
            before_emission_socket = emission_socket.links[0].from_socket
            mat.node_tree.links.remove(emission_socket.links[0])
        if len(roughness_socket.links) == 0:
            roughness_value = roughness_socket.default_value
            emission_socket.default_value = [roughness_value,roughness_value,roughness_value,1.0]
        else:
            is_bw_node_exist = True
            last_socket = roughness_socket.links[0].from_socket
            bw_node = nodes.new('ShaderNodeRGBToBW')
            bw_node.name = 'RGB_to_BW_Node'
            bw_node_input_socket = bw_node.inputs['Color']
            bw_node_output_socket = bw_node.outputs['Val']
            mat.node_tree.links.new(last_socket,bw_node_input_socket)
            mat.node_tree.links.new(bw_node_output_socket,emission_socket)
        bpy.ops.object.bake(type='EMIT',save_mode='EXTERNAL',width=texture_resolution,height=texture_resolution)
        img.save_render(filepath = export_path + material.name + '\\' + material.name + '_' + str(texture_resolution) + 'x' + str(texture_resolution) +'_Roughness.png')
        #restore nodes
        nodes.remove(texture_node)
        emission_socket.default_value = emission_color_value
        if is_bw_node_exist:
            nodes.remove(bw_node)
        if is_emission_socket_linked:
            mat.node_tree.links.new(before_emission_socket,emission_socket)
        else:
            if len(emission_socket.links) != 0:
                mat.node_tree.links.remove(emission_socket.links[0])
        #restore colorspace
        image_list = bpy.data.images
        for i in range(0,len(image_list)):
            if previous_colorspace_list[i] != '':
                image_list[i].colorspace_settings.name = previous_colorspace_list[i]

    if export_items[3]:
        #add empty image texture node
        texture_node = nodes.new('ShaderNodeTexImage')
        texture_node.name = 'PBR_Bake_Node'
        texture_node.select = True
        nodes.active = texture_node
        img = bpy.data.images.new(material.name + '_' + str(texture_resolution) + 'x' + str(texture_resolution) +'_Normal',texture_resolution,texture_resolution)
        texture_node.image = img
        #change colorspace to Non-Color
        previous_colorspace_list = []
        image_list = bpy.data.images
        for i in range(0,len(image_list)):
            previous_colorspace_list.append(image_list[i].colorspace_settings.name)
            if image_list[i].colorspace_settings.name != '':
                image_list[i].colorspace_settings.name = 'Non-Color'
        #bake normal
        bpy.ops.object.bake(type='NORMAL',save_mode='EXTERNAL',width=texture_resolution,height=texture_resolution)
        img.save_render(filepath = export_path + material.name + '\\' + material.name + '_' + str(texture_resolution) + 'x' + str(texture_resolution) +'_Normal.png')
        #restore nodes
        nodes.remove(texture_node)
        #restore colorspace
        image_list = bpy.data.images
        for i in range(0,len(image_list)):
            if previous_colorspace_list[i] != '':
                image_list[i].colorspace_settings.name = previous_colorspace_list[i]

    #restore rendering settings
    bpy.context.scene.cycles.use_adaptive_sampling = previous_is_using_adaptive_sampling
    bpy.context.scene.cycles.device = previous_device
    bpy.context.scene.cycles.samples = previous_samples
    bpy.context.scene.cycles.adaptive_min_samples = previous_min_samples
    bpy.context.scene.cycles.use_denoising = previous_is_using_denoising
    bpy.context.scene.cycles.time_limit = previous_time_limit
    bpy.context.scene.render.engine = previous_render_engine
    bpy.context.scene.display_settings.display_device = previous_display_device
    bpy.context.scene.view_settings.view_transform = previous_view_transform
    bpy.context.scene.view_settings.look = previous_look
    bpy.context.scene.view_settings.exposure = previous_exposure
    bpy.context.scene.view_settings.gamma = previous_gamma
    bpy.context.scene.sequencer_colorspace_settings.name = previous_sequencer_colorspace
    bpy.context.scene.view_settings.use_curve_mapping = previous_use_curve_mapping

    #delete initial plane
    bpy.ops.object.delete()
    bpy.data.collections.remove(temp_collection)