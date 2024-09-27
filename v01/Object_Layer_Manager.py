bl_info = {
    "name": "AJO Object Layer Manager",
    "blender": (4, 2, 0),
    "category": "Object",
}

import bpy

class LayerObject(bpy.types.PropertyGroup):
    object_name: bpy.props.StringProperty(name="Object Name")

class ObjectLayer(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Layer Name")
    objects: bpy.props.CollectionProperty(type=LayerObject)
    selected: bpy.props.BoolProperty(name="Selected", default=False)
    hidden: bpy.props.BoolProperty(name="Hidden", default=False)
    disabled: bpy.props.BoolProperty(name="Disabled", default=False)
    viewport_disabled: bpy.props.BoolProperty(name="Viewport Disabled", default=False)
    modifiers_enabled: bpy.props.BoolProperty(name="Modifiers Enabled", default=True)

class OBJECT_OT_create_layer(bpy.types.Operator):
    bl_idname = "object.create_layer"
    bl_label = "Create Layer"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        layer = context.scene.object_layers.add()
        layer.name = f"Layer {len(context.scene.object_layers)}"
        context.scene.object_layers_index = len(context.scene.object_layers) - 1

        selected_objects = context.selected_objects
        for obj in selected_objects:
            if obj.type == 'MESH':
                item = layer.objects.add()
                item.object_name = obj.name
                self.report({'INFO'}, f"Added {obj.name} to {layer.name}")

        self.report({'INFO'}, f"Created: {layer.name}")
        return {'FINISHED'}

class OBJECT_OT_delete_layer(bpy.types.Operator):
    bl_idname = "object.delete_layer"
    bl_label = "Delete Layer"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        index = context.scene.object_layers_index
        if len(context.scene.object_layers) > index:
            removed_layer = context.scene.object_layers[index].name
            context.scene.object_layers.remove(index)
            context.scene.object_layers_index = max(0, index - 1)
            self.report({'INFO'}, f"Deleted: {removed_layer}")
        else:
            self.report({'WARNING'}, "Layer index out of range.")
        return {'FINISHED'}

class OBJECT_OT_add_object_to_layer(bpy.types.Operator):
    bl_idname = "object.add_object_to_layer"
    bl_label = "Add Object to Layer"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        layer = context.scene.object_layers[context.scene.object_layers_index]

        for obj in selected_objects:
            if obj.type == 'MESH':
                item = layer.objects.add()
                item.object_name = obj.name
                self.report({'INFO'}, f"Added {obj.name} to {layer.name}")

        return {'FINISHED'}

class OBJECT_OT_remove_object_from_layer(bpy.types.Operator):
    bl_idname = "object.remove_object_from_layer"
    bl_label = "Remove Object from Layer"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        layer = context.scene.object_layers[context.scene.object_layers_index]

        if len(layer.objects) > self.index:
            removed_object = layer.objects[self.index].object_name
            layer.objects.remove(self.index)
            self.report({'INFO'}, f"Removed {removed_object} from {layer.name}")
        else:
            self.report({'WARNING'}, "Object index out of range.")
        return {'FINISHED'}

class OBJECT_OT_toggle_modifiers_in_layer(bpy.types.Operator):
    bl_idname = "object.toggle_modifiers_in_layer"
    bl_label = "Toggle Geometry Nodes in Layer"
    bl_options = {'REGISTER', 'UNDO'}

    layer_index: bpy.props.IntProperty()

    def execute(self, context):
        layer = context.scene.object_layers[self.layer_index]
        is_enabled = False

        for item in layer.objects:
            obj = bpy.data.objects.get(item.object_name)
            if obj and obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.type == 'NODES' and modifier.show_viewport:
                        is_enabled = True
                        break
                if is_enabled:
                    break

        for item in layer.objects:
            obj = bpy.data.objects.get(item.object_name)
            if obj and obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.type == 'NODES':
                        modifier.show_viewport = not is_enabled

        self.report({'INFO'}, f"Toggled Geometry Nodes modifiers in {layer.name}")
        return {'FINISHED'}

class OBJECT_OT_select_layer_objects(bpy.types.Operator):
    bl_idname = "object.select_layer_objects"
    bl_label = "Select Layer Objects"
    bl_options = {'REGISTER', 'UNDO'}

    layer_index: bpy.props.IntProperty()

    def execute(self, context):
        layer = context.scene.object_layers[self.layer_index]
        layer.selected = not layer.selected

        if layer.selected:
            for item in layer.objects:
                obj = bpy.data.objects.get(item.object_name)
                if obj and obj.type == 'MESH':
                    obj.select_set(True)
            self.report({'INFO'}, f"Selected all objects in {layer.name}")
        else:
            for item in layer.objects:
                obj = bpy.data.objects.get(item.object_name)
                if obj:
                    obj.select_set(False)
            self.report({'INFO'}, f"Deselected all objects in {layer.name}")

        return {'FINISHED'}

class OBJECT_OT_hide_layer(bpy.types.Operator):
    bl_idname = "object.hide_layer"
    bl_label = "Hide Layer"
    bl_options = {'REGISTER', 'UNDO'}

    layer_index: bpy.props.IntProperty()

    def execute(self, context):
        layer = context.scene.object_layers[self.layer_index]
        layer.hidden = not layer.hidden

        for item in layer.objects:
            obj = bpy.data.objects.get(item.object_name)
            if obj and obj.type == 'MESH':
                obj.hide_set(layer.hidden)

        self.report({'INFO'}, f"{'Hidden' if layer.hidden else 'Shown'} layer {layer.name}")
        return {'FINISHED'}

class OBJECT_OT_disable_layer(bpy.types.Operator):
    bl_idname = "object.disable_layer"
    bl_label = "Disable Layer"
    bl_options = {'REGISTER', 'UNDO'}

    layer_index: bpy.props.IntProperty()

    def execute(self, context):
        layer = context.scene.object_layers[self.layer_index]
        layer.disabled = not layer.disabled

        for item in layer.objects:
            obj = bpy.data.objects.get(item.object_name)
            if obj and obj.type == 'MESH':
                obj.hide_render = layer.disabled

        self.report({'INFO'}, f"{'Disabled' if layer.disabled else 'Enabled'} layer {layer.name}")
        return {'FINISHED'}

class OBJECT_OT_viewport_disable_layer(bpy.types.Operator):
    bl_idname = "object.viewport_disable_layer"
    bl_label = "Disable in Viewport"
    bl_options = {'REGISTER', 'UNDO'}

    layer_index: bpy.props.IntProperty()

    def execute(self, context):
        layer = context.scene.object_layers[self.layer_index]
        layer.viewport_disabled = not layer.viewport_disabled

        for item in layer.objects:
            obj = bpy.data.objects.get(item.object_name)
            if obj and obj.type == 'MESH':
                obj.hide_viewport = layer.viewport_disabled

        self.report({'INFO'}, f"{'Disabled in Viewport' if layer.viewport_disabled else 'Enabled in Viewport'} layer {layer.name}")
        return {'FINISHED'}
    
class OBJECT_OT_toggle_modifiers_in_layer_except_geo(bpy.types.Operator):
    bl_idname = "object.toggle_modifiers_in_layer_except_geo"
    bl_label = "Toggle All Modifiers Except Geometry Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    layer_index: bpy.props.IntProperty()

    def execute(self, context):
        layer = context.scene.object_layers[self.layer_index]
        layer.modifiers_enabled = not layer.modifiers_enabled

        for item in layer.objects:
            obj = bpy.data.objects.get(item.object_name)
            if obj and obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.type != 'NODES':
                        modifier.show_viewport = layer.modifiers_enabled

        self.report(
            {'INFO'},
            f"{'Enabled' if layer.modifiers_enabled else 'Disabled'} all modifiers except Geometry Nodes in {layer.name}"
        )
        return {'FINISHED'}

class OBJECT_UL_layer_list(bpy.types.UIList):
    bl_idname = "OBJECT_UL_layer_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layer_name = item.name
        layer_index = context.scene.object_layers.find(layer_name)

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            if context.scene.object_layers_index == layer_index:
                row.prop(item, "name", text="", icon='GROUP', emboss=False)
            else:
                row.label(text=layer_name, icon='GROUP')

            select_icon = "RESTRICT_SELECT_ON" if item.selected else "RESTRICT_SELECT_OFF"
            row.operator("object.select_layer_objects", text="", icon=select_icon).layer_index = layer_index
            
            hide_icon = 'HIDE_ON' if item.hidden else 'HIDE_OFF'
            row.operator("object.hide_layer", text="", icon=hide_icon).layer_index = layer_index

            disable_icon = 'RESTRICT_RENDER_ON' if item.disabled else 'RESTRICT_RENDER_OFF'
            row.operator("object.disable_layer", text="", icon=disable_icon).layer_index = layer_index

            viewport_disable_icon = 'RESTRICT_VIEW_ON' if item.viewport_disabled else 'RESTRICT_VIEW_OFF'
            row.operator("object.viewport_disable_layer", text="", icon=viewport_disable_icon).layer_index = layer_index

            is_enabled = any(
                bpy.data.objects.get(obj.object_name) and
                any(modifier.type == 'NODES' and modifier.show_viewport for modifier in bpy.data.objects.get(obj.object_name).modifiers)
                for obj in context.scene.object_layers[layer_index].objects
            )
            
            modifier_icon = 'MODIFIER_ON' if item.modifiers_enabled else 'MODIFIER_OFF'
            row.operator("object.toggle_modifiers_in_layer_except_geo", text="", icon=modifier_icon).layer_index = layer_index

            toggle_icon = "PROP_ON" if is_enabled else "PROP_OFF"
            row.operator("object.toggle_modifiers_in_layer", text="", icon=toggle_icon).layer_index = layer_index
            
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="")

class OBJECT_UL_layer_object_list(bpy.types.UIList):
    bl_idname = "OBJECT_UL_layer_object_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        obj = bpy.data.objects.get(item.object_name)
        if obj:
            layout.label(text=obj.name, icon='OBJECT_DATA')

class OBJECT_PT_layer_manager_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_layer_manager_panel"
    bl_label = "Object Layer Manager"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'view_layer'  # Show in ViewLayer

    def draw(self, context):
        layout = self.layout

        # Create a row for side-by-side layer management buttons
        row = layout.row(align=True)

        # Create a distinct button for 'Create Layer'
        create_button = row.box()  # Create a box around the button
        create_button.scale_x = 1.5  # Increase button width
        create_button.scale_y = 1.4  # Increase button height
        create_button.operator("object.create_layer", text="Create Layer", icon="ADD")

        # Create a distinct button for 'Delete Layer'
        delete_button = row.box()  # Create a box around the button
        delete_button.scale_x = 1.5  # Increase button width
        delete_button.scale_y = 1.4  # Increase button height
        delete_button.operator("object.delete_layer", text="Delete Layer", icon="REMOVE")

        # Layer list UI
        row = layout.row()
        row.template_list("OBJECT_UL_layer_list", "", context.scene, "object_layers", context.scene, "object_layers_index")

        # Create a row for object management buttons
        row = layout.row(align=True)

        # Create a distinct button for 'Link Object'
        link_object_button = row.box()  # Create a box around the button
        link_object_button.scale_x = 1.5  # Increase button width
        link_object_button.scale_y = 1.1  # Increase button height
        link_object_button.operator("object.add_object_to_layer", text="Link Object", icon="LINKED")

        # Create a distinct button for 'Unlink Object'
        unlink_object_button = row.box()  # Create a box around the button
        unlink_object_button.scale_x = 1.5  # Increase button width
        unlink_object_button.scale_y = 1.1  # Increase button height
        unlink_object_button.operator("object.remove_object_from_layer", text="Unlink Object", icon="UNLINKED").index = context.scene.group_objects_index

        # Check if there are layers to display objects in the selected layer
        if context.scene.object_layers:
            layer = context.scene.object_layers[context.scene.object_layers_index]
            if layer.objects:
                # Object list UI
                row = layout.row()
                row.template_list("OBJECT_UL_layer_object_list", "", layer, "objects", context.scene, "group_objects_index")
            else:
                layout.label(text="No objects in the selected layer.")
        else:
            layout.label(text="No layers available.")

def register():
    bpy.utils.register_class(LayerObject)
    bpy.utils.register_class(ObjectLayer)
    
    bpy.types.Scene.object_layers = bpy.props.CollectionProperty(type=ObjectLayer)
    bpy.types.Scene.object_layers_index = bpy.props.IntProperty(default=0)
    
    # Add the missing property to track selected object index in each layer
    bpy.types.Scene.group_objects_index = bpy.props.IntProperty(default=0)

    bpy.utils.register_class(OBJECT_OT_create_layer)
    bpy.utils.register_class(OBJECT_OT_delete_layer)
    bpy.utils.register_class(OBJECT_OT_add_object_to_layer)
    bpy.utils.register_class(OBJECT_OT_remove_object_from_layer)
    bpy.utils.register_class(OBJECT_OT_toggle_modifiers_in_layer)
    bpy.utils.register_class(OBJECT_OT_select_layer_objects)
    bpy.utils.register_class(OBJECT_OT_hide_layer)
    bpy.utils.register_class(OBJECT_OT_disable_layer)
    bpy.utils.register_class(OBJECT_OT_viewport_disable_layer)
    bpy.utils.register_class(OBJECT_OT_toggle_modifiers_in_layer_except_geo)
    bpy.utils.register_class(OBJECT_UL_layer_list)
    bpy.utils.register_class(OBJECT_UL_layer_object_list)
    bpy.utils.register_class(OBJECT_PT_layer_manager_panel)

def unregister():
    bpy.utils.unregister_class(LayerObject)
    bpy.utils.unregister_class(ObjectLayer)
    del bpy.types.Scene.object_layers
    del bpy.types.Scene.object_layers_index
    
    # Unregister the group_objects_index
    del bpy.types.Scene.group_objects_index

    bpy.utils.unregister_class(OBJECT_OT_create_layer)
    bpy.utils.unregister_class(OBJECT_OT_delete_layer)
    bpy.utils.unregister_class(OBJECT_OT_add_object_to_layer)
    bpy.utils.unregister_class(OBJECT_OT_remove_object_from_layer)
    bpy.utils.unregister_class(OBJECT_OT_toggle_modifiers_in_layer)
    bpy.utils.unregister_class(OBJECT_OT_select_layer_objects)
    bpy.utils.unregister_class(OBJECT_OT_hide_layer)
    bpy.utils.unregister_class(OBJECT_OT_disable_layer)
    bpy.utils.unregister_class(OBJECT_OT_viewport_disable_layer)
    bpy.utils.unregister_class(OBJECT_OT_toggle_modifiers_in_layer_except_geo)
    bpy.utils.unregister_class(OBJECT_UL_layer_list)
    bpy.utils.unregister_class(OBJECT_UL_layer_object_list)
    bpy.utils.unregister_class(OBJECT_PT_layer_manager_panel)

if __name__ == "__main__":
    register()
