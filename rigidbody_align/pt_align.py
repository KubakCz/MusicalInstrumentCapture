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
from .ot_align_bow import MIC_OT_AlignBow
from .ot_align_violin import MIC_OT_AlignViolin


class MIC_PT_Align(bpy.types.Panel):
    """Main panel for the Musical Instrument Capture add-on."""
    bl_label = "Align Violin and Bow"
    bl_idname = "VIEW3D_PT_Align"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Musical Instrument Capture"

    def draw(self, context):
        layout = self.layout

        # Violin alignment
        violin_align_data = context.scene.violin_align_data
        layout.label(text="Violin:")
        violin_markers_box = layout.box()
        violin_markers_box.label(text="Model:")
        violin_markers_box.prop_search(violin_align_data, "top_of_bridge", bpy.data, "objects")
        violin_model = violin_align_data.top_of_bridge.parent if violin_align_data.top_of_bridge else None
        violin_markers_box.label(text=f"Model: {violin_model.name if violin_model else 'No model selected.'}")
        violin_markers_box.separator()
        violin_markers_box.label(text="Mocap:")
        violin_markers_box.prop_search(violin_align_data, "rigidbody", bpy.data, "objects")
        violin_markers_box.prop_search(violin_align_data, "plane_1", bpy.data, "objects")
        violin_markers_box.prop_search(violin_align_data, "plane_2", bpy.data, "objects")
        violin_markers_box.prop_search(violin_align_data, "plane_3", bpy.data, "objects")
        violin_markers_box.prop_search(violin_align_data, "bridge", bpy.data, "objects")
        violin_markers_box.prop(violin_align_data, "bridge_offset")
        violin_markers_box.prop_search(violin_align_data, "scroll", bpy.data, "objects")
        violin_markers_box.operator(MIC_OT_AlignViolin.bl_idname, text="Align Violin")

        # Bow alignment
        bow_align_data = context.scene.bow_align_data
        layout.label(text="Bow:")
        bow_markers_box = layout.box()
        bow_markers_box.prop_search(bow_align_data, "rigidbody", bpy.data, "objects")
        bow_markers_box.separator()
        bow_markers_box.prop_search(bow_align_data, "frog", bpy.data, "objects")
        bow_markers_box.prop_search(bow_align_data, "tip", bpy.data, "objects")
        bow_markers_box.separator()
        bow_markers_box.operator(MIC_OT_AlignBow.bl_idname, text="Align Bow")
