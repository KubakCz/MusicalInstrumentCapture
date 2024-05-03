# Musical Instrument Capture
# Copyright (C) 2024  Jakub Slezáček
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Operator for aligning the bow with the captured data."""

import bpy
from mathutils import Matrix

from .property_groups import BowAlignProps


class MIC_OT_AlignBow(bpy.types.Operator):
    """
    Aligns the bow according to the given rigidbody and markers.
    """
    bl_idname = "mic.align_bow"
    bl_label = "Align Bow"
    bl_description = "Align the bow model according to the given rigidbody and markers"
    bl_options = {'REGISTER', 'UNDO'}

    def any_none(self, data: BowAlignProps) -> bool:
        """
        Check if any of the bow alignment data is None.
        :param data: Bow alignment data.
        :return: True if any of the data is None, False otherwise.
        """
        if data.reference_point is None:
            self.report({'ERROR'}, "Reference point is not set.")
            return True
        if data.reference_point.parent is None:
            self.report({'ERROR'}, "Reference point must be parented to the bow model.")
            return True
        if data.reference_marker is None:
            self.report({'ERROR'}, "Reference marker is not set.")
            return True
        if data.rigidbody is None:
            self.report({'ERROR'}, "Rigidbody object is not set.")
            return True
        if data.stick is None:
            self.report({'ERROR'}, "Stick marker is not set.")
            return True
        if data.tip is None:
            self.report({'ERROR'}, "Tip marker is not set.")
            return True
        return False

    def execute(self, context: bpy.types.Context) -> set[str]:
        """
        Aligns the bow according to the given rigidbody and markers.
        """
        print("--- Executing Align Bow ---")
        bow_align_props = context.scene.bow_align_data
        assert isinstance(bow_align_props, BowAlignProps)

        if self.any_none(bow_align_props):
            return {'CANCELLED'}

        model = bow_align_props.reference_point.parent
        assert isinstance(model, bpy.types.Object)

        # setup child_of constraint
        for constraint in model.constraints:
            if constraint.type == 'CHILD_OF':
                model.constraints.remove(constraint)

        child_of_constraint = model.constraints.new(type='CHILD_OF')
        child_of_constraint.target = bow_align_props.rigidbody
        child_of_constraint.use_scale_x = False
        child_of_constraint.use_scale_y = False
        child_of_constraint.use_scale_z = False
        child_of_constraint.set_inverse_pending = True

        # get world space positions of the markers
        m_stick_ws = bow_align_props.stick.matrix_world.decompose()[0]
        m_tip_ws = bow_align_props.tip.matrix_world.decompose()[0]
        m_reference_marker_ws = bow_align_props.reference_marker.matrix_world.decompose()[0]

        # compute rotation matrix of the bow model
        rb_rotation_mat = bow_align_props.rigidbody.matrix_world.decompose()[1].to_matrix()
        bow_z = rb_rotation_mat.col[1]                          # vertical axis is the same as of the rigidbody
        stick_direction = (m_tip_ws - m_stick_ws).normalized()  # dir of the bow - markers can be in different heights
        bow_x = stick_direction.cross(bow_z)
        bow_y = bow_z.cross(bow_x)

        bow_rotation_mat = Matrix((bow_x, bow_y, bow_z)).transposed()
        original_rot_mode = model.rotation_mode
        model.rotation_mode = 'QUATERNION'
        model.rotation_quaternion = bow_rotation_mat.to_quaternion()
        model.rotation_mode = original_rot_mode

        # force Blender to update 'matrix_world' of the violin model
        bpy.context.view_layer.update()

        # compute offset of the bridge marker and set the location of the violin model
        position_offset = m_reference_marker_ws - bow_align_props.reference_point.matrix_world.decompose()[0]
        model.location += position_offset

        return {'FINISHED'}
