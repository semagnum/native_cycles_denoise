if 'bpy' in locals():
    import importlib
    import os
    import sys
    import types

    def reload_package(package):
        assert (hasattr(package, '__package__'))
        fn = package.__file__
        fn_dir = os.path.dirname(fn) + os.sep
        module_visit = {fn}
        del fn

        def reload_recursive_ex(module):
            module_iter = (
                module_child
                for module_child in vars(module).values()
                if isinstance(module_child, types.ModuleType)
            )
            for module_child in module_iter:
                fn_child = getattr(module_child, '__file__', None)
                if (fn_child is not None) and fn_child.startswith(fn_dir) and fn_child not in module_visit:
                    logger.debug('Reloading: ' + fn_child + ' from ' + module)
                    module_visit.add(fn_child)
                    reload_recursive_ex(module_child)

            importlib.reload(module)

        return reload_recursive_ex(package)

    reload_package(sys.modules[__name__])


import bpy


def after_render_denoise_handler(_scene, _dummy):
    bpy.ops.cycles.denoise_animation()


def viable_for_denoise(context):
    return (
            context.scene.render.engine == 'CYCLES' and
            hasattr(bpy.ops.cycles, 'denoise_animation') and
            context.scene.render.image_settings.file_format == 'OPEN_EXR_MULTILAYER' and
            all(
                view_layer.use_pass_vector and view_layer.cycles.denoising_store_passes
                for view_layer in context.scene.view_layers
            )
    )

DENOISE_MESSAGE = """To use native Cycles denoising, you must:
1. Use Cycles
2. Enable 'Vector' and 'Denoising Data' render passes
3. Set the export format to multilayer EXR

If it is still not available, then the operator does not exist in this Blender version
"""


class RenderThenDenoiseOperator(bpy.types.Operator):
    bl_idname = 'render.animation_temporal_denoise'
    bl_label = 'Render Animation + Temporal Denoise'
    bl_description = 'Renders animation, then runs temporal denoising on the output'

    @classmethod
    def poll(cls, context):
        result = viable_for_denoise(context)
        if not result:
            cls.poll_message_set(DENOISE_MESSAGE)
        return result

    def execute(self, context):
        bpy.ops.render.render(animation=True)
        bpy.app.handlers.render_complete.append(after_render_denoise_handler)
        return {'FINISHED'}


class DenoiseSequenceOperator(bpy.types.Operator):
    bl_idname = 'render.temporal_denoise_sequence'
    bl_label = 'Temporal Denoise Image Sequence'
    bl_description = 'Denoise an existing EXR image sequence'

    @classmethod
    def poll(cls, context):
        result = viable_for_denoise(context)
        if not result:
            cls.poll_message_set(DENOISE_MESSAGE)
        return result

    def execute(self, context):
        return bpy.ops.cycles.denoise_animation()


def draw_custom_menu(self, context):
    self.layout.operator(RenderThenDenoiseOperator.bl_idname)
    self.layout.operator(DenoiseSequenceOperator.bl_idname)


classes_to_register = (
    RenderThenDenoiseOperator,
    DenoiseSequenceOperator,
)


def register():
    for cls in classes_to_register:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_render.append(draw_custom_menu)


def unregister():
    bpy.types.TOPBAR_MT_render.remove(draw_custom_menu)
    for cls in classes_to_register:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()