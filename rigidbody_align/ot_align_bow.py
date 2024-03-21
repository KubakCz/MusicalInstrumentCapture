import bpy
from .align_data import BowAlignData


class MIC_OT_AlignBow(bpy.types.Operator):
    """Aligns the bow according to the given rigidbody and markers."""
    bl_idname = "mic.align_bow"
    bl_label = "Align Bow"
    bl_options = {'REGISTER'}

    def execute(self, context: bpy.types.Context) -> set[str]:
        print("----------------- Executing Align Bow -----------------")
        bow_align_data: BowAlignData = context.scene.bow_align_data  # type: ignore

        model = context.active_object
        if not isinstance(model, bpy.types.Object):
            self.report({'ERROR'}, "Invalid object selected. Please select the bow model.")
            return {'CANCELLED'}

        model.location = (0, 0, 0)

        # setup child_of constraint
        child_of = model.constraints.new(type='CHILD_OF')
        assert isinstance(child_of, bpy.types.ChildOfConstraint)
        child_of.target = bow_align_data.rigidbody
        child_of.use_scale_x = False
        child_of.use_scale_y = False
        child_of.use_scale_z = False
        child_of.set_inverse_pending = False

        return {'FINISHED'}
