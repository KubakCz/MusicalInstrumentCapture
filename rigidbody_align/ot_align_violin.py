import bpy
from mathutils import Matrix
from .align_data import ViolinAlignData


class MIC_OT_AlignViolin(bpy.types.Operator):
    """Aligns the violin according to the given rigidbody and markers."""
    bl_idname = "mic.align_violin"
    bl_label = "Align Violin"
    bl_options = {'REGISTER'}

    def any_none(self, data: ViolinAlignData) -> bool:
        """Check if any of the violin alignment data is None."""
        if data.top_of_bridge is None:
            self.report({'ERROR'}, "Top of the bridge marker is not set.")
            return True
        if data.top_of_bridge.parent is None:
            self.report({'ERROR'}, "Top of the bridge object must be parented to the violin model.")
        if data.rigidbody is None:
            self.report({'ERROR'}, "Rigidbody object is not set.")
            return True
        if data.plane_1 is None or data.plane_2 is None or data.plane_3 is None:
            self.report({'ERROR'}, "Plane markers are not set.")
            return True
        if data.bridge is None:
            self.report({'ERROR'}, "Bridge marker is not set.")
            return True
        if data.scroll is None:
            self.report({'ERROR'}, "Scroll marker is not set.")
            return True
        return False

    def execute(self, context: bpy.types.Context) -> set[str]:
        print("----------------- Executing Align Violin -----------------")
        violin_align_data = context.scene.violin_align_data

        if self.any_none(violin_align_data):
            return {'CANCELLED'}

        model = violin_align_data.top_of_bridge.parent

        # setup child_of constraint
        # child_of = model.constraints.new(type='CHILD_OF')
        # assert isinstance(child_of, bpy.types.ChildOfConstraint)
        # child_of.target = violin_align_data.rigidbody
        # child_of.use_scale_x = False
        # child_of.use_scale_y = False
        # child_of.use_scale_z = False
        # child_of.set_inverse_pending = True

        # get world space positions of the markers
        m_plane_1_ws = violin_align_data.plane_1.matrix_world.decompose()[0]
        m_plane_2_ws = violin_align_data.plane_2.matrix_world.decompose()[0]
        m_plane_3_ws = violin_align_data.plane_3.matrix_world.decompose()[0]
        m_bridge_ws = violin_align_data.bridge.matrix_world.decompose()[0]
        m_scroll_ws = violin_align_data.scroll.matrix_world.decompose()[0]

        # calculate normal of the top plate (pointing upwards)
        plane_vec_1 = m_plane_2_ws - m_plane_1_ws
        plane_vec_2 = m_plane_3_ws - m_plane_1_ws
        plane_normal = plane_vec_2.cross(plane_vec_1).normalized()

        # compute direction of the width axis
        bridge_loc = m_bridge_ws - violin_align_data.bridge_offset * plane_normal
        neck_direction = (m_scroll_ws - bridge_loc).normalized()
        width_direction = neck_direction.cross(plane_normal)

        # compute direction of the "neck" axis
        neck_direction = plane_normal.cross(width_direction)

        # set the rotation of the violin model
        rot_matrix = Matrix((width_direction, neck_direction, plane_normal)).transposed()
        model.rotation_euler = rot_matrix.to_euler()

        # compute offset of the bridge marker and set the location of the violin model
        bridge_offset = bridge_loc - violin_align_data.top_of_bridge.matrix_world.decompose()[0]
        model.location += bridge_offset

        return {'FINISHED'}
