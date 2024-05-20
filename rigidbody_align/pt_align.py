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

"""Panel for alligning Violin and Bow models with the captured data."""

import bpy
from .property_groups import ViolinAlignProps, BowAlignProps
from .ot_align_bow import MIC_OT_AlignBow
from .ot_align_violin import MIC_OT_AlignViolin


class MIC_PT_Align(bpy.types.Panel):
    """
    Panel for aligning the violin and the bow with the captured data.
    """
    bl_label = "Align Violin and Bow"
    bl_idname = "MIC_PT_Align"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Musical Instrument Animation"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        # Violin alignment
        violin_align_data = context.scene.violin_align_data
        assert isinstance(violin_align_data, ViolinAlignProps)
        layout.label(text="Violin:")
        violin_markers_box = layout.box()
        violin_markers_box.prop_search(violin_align_data, "rigidbody", bpy.data, "objects")
        violin_markers_box.label(text="Markers:")
        violin_markers_box.prop_search(violin_align_data, "plane_1", bpy.data, "objects")
        violin_markers_box.prop_search(violin_align_data, "plane_2", bpy.data, "objects")
        violin_markers_box.prop_search(violin_align_data, "plane_3", bpy.data, "objects")
        violin_markers_box.prop_search(violin_align_data, "bridge", bpy.data, "objects")
        violin_markers_box.prop_search(violin_align_data, "scroll", bpy.data, "objects")
        violin_markers_box.prop_search(violin_align_data, "reference_marker", bpy.data, "objects")
        violin_model = violin_align_data.reference_point.parent if violin_align_data.reference_point else None
        violin_markers_box.label(text=f"Model: {violin_model.name if violin_model else 'No reference point selected.'}")
        violin_markers_box.prop_search(violin_align_data, "reference_point", bpy.data, "objects")
        violin_markers_box.operator(MIC_OT_AlignViolin.bl_idname, text="Align Violin")

        # Bow alignment
        bow_align_data = context.scene.bow_align_data
        assert isinstance(bow_align_data, BowAlignProps)
        layout.label(text="Bow:")
        bow_markers_box = layout.box()
        bow_markers_box.prop_search(bow_align_data, "rigidbody", bpy.data, "objects")
        bow_markers_box.label(text="Markers:")
        bow_markers_box.prop_search(bow_align_data, "frog_bottom", bpy.data, "objects")
        bow_markers_box.prop_search(bow_align_data, "frog_top", bpy.data, "objects")
        bow_markers_box.prop_search(bow_align_data, "stick", bpy.data, "objects")
        bow_markers_box.prop_search(bow_align_data, "tip", bpy.data, "objects")
        bow_markers_box.prop_search(bow_align_data, "reference_marker", bpy.data, "objects")
        bow_model = bow_align_data.reference_point.parent if bow_align_data.reference_point else None
        bow_markers_box.label(text=f"Model: {bow_model.name if bow_model else 'No reference point selected.'}")
        bow_markers_box.prop_search(bow_align_data, "reference_point", bpy.data, "objects")
        bow_markers_box.operator(MIC_OT_AlignBow.bl_idname, text="Align Bow")
