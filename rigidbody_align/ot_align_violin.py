import bpy
from mathutils import Matrix
from .property_groups import ViolinAlignProps


class MIC_OT_AlignViolin(bpy.types.Operator):
    """
    Aligns the violin according to the given rigidbody and markers.
    """
    bl_idname = "mic.align_violin"
    bl_label = "Align Violin"
    bl_description = "Align the violin model according to the given rigidbody and markers"
    bl_options = {'REGISTER', 'UNDO'}

    def any_none(self, data: ViolinAlignProps) -> bool:
        """
        Check if any of the violin alignment data is None.
        :param data: Violin alignment data.
        :return: True if any of the data is None, False otherwise.
        """
        if data.reference_point is None:
            self.report({'ERROR'}, "Reference point is not set.")
            return True
        if data.reference_point.parent is None:
            self.report({'ERROR'}, "Reference point must be parented to the violin model.")
            return True
        if data.reference_marker is None:
            self.report({'ERROR'}, "Reference marker is not set.")
            return True
        if data.rigidbody is None:
            self.report({'ERROR'}, "Rigidbody object is not set.")
            return True
        if data.plane_1 is None or data.plane_2 is None or data.plane_3 is None:
            self.report({'ERROR'}, "One or more plane markers are not set.")
            return True
        if data.bridge is None:
            self.report({'ERROR'}, "Bridge marker is not set.")
            return True
        if data.scroll is None:
            self.report({'ERROR'}, "Scroll marker is not set.")
            return True
        return False

    def execute(self, context: bpy.types.Context) -> set[str]:
        """
        Aligns the violin according to the given rigidbody and markers.
        """
        print("--- Executing Align Violin ---")
        violin_align_data = context.scene.violin_align_data
        assert isinstance(violin_align_data, ViolinAlignProps)

        if self.any_none(violin_align_data):
            return {'CANCELLED'}

        model = violin_align_data.reference_point.parent

        # setup child_of constraint
        for constraint in model.constraints:
            if constraint.type == 'CHILD_OF':
                model.constraints.remove(constraint)

        child_of_constraint = model.constraints.new(type='CHILD_OF')
        child_of_constraint.target = violin_align_data.rigidbody
        child_of_constraint.use_scale_x = False
        child_of_constraint.use_scale_y = False
        child_of_constraint.use_scale_z = False
        child_of_constraint.set_inverse_pending = True

        # get world space positions of the markers
        m_plane_1_ws = violin_align_data.plane_1.matrix_world.decompose()[0]
        m_plane_2_ws = violin_align_data.plane_2.matrix_world.decompose()[0]
        m_plane_3_ws = violin_align_data.plane_3.matrix_world.decompose()[0]
        m_bridge_ws = violin_align_data.bridge.matrix_world.decompose()[0]
        m_scroll_ws = violin_align_data.scroll.matrix_world.decompose()[0]
        m_reference_ws = violin_align_data.reference_marker.matrix_world.decompose()[0]

        # calculate normal of the top plate (pointing upwards)
        plane_vec_1 = m_plane_2_ws - m_plane_1_ws
        plane_vec_2 = m_plane_3_ws - m_plane_1_ws
        plane_normal = plane_vec_2.cross(plane_vec_1).normalized()

        # compute direction of the width axis
        neck_direction = m_scroll_ws - m_bridge_ws
        width_direction = neck_direction.cross(plane_normal)

        # compute direction of the "neck" axis
        neck_direction = plane_normal.cross(width_direction)

        # set the rotation of the violin model
        rot_matrix = Matrix((width_direction, neck_direction, plane_normal)).transposed()
        model.rotation_euler = rot_matrix.to_euler()

        # force Blender to update 'matrix_world' of the violin model
        bpy.context.view_layer.update()

        # compute offset of the reference marker and set the location of the violin model
        position_offset = m_reference_ws - violin_align_data.reference_point.matrix_world.decompose()[0]
        model.location += position_offset

        return {'FINISHED'}
