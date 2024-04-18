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

"""Panel for importing hand animation data and aligning it with the motion capture data."""

import bpy

from .property_groups import HandAlignProps, PreprocessProps
from .ot_import_hands import MIC_OT_ImportHands


class MIC_PT_MusicalInstrumentCapture(bpy.types.Panel):
    """
    Panel for importing hand animation data and aligning it with the motion capture data.
    """
    bl_label = "Import Hand Animation"
    bl_idname = "MIC_PT_MusicalInstrumentCapture"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Musical Instrument Capture"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        # Preprocess props
        preprocess_props = context.scene.preprocess_props
        assert isinstance(preprocess_props, PreprocessProps)
        layout.label(text="Preprocessing settings:")
        layout.prop(preprocess_props, "palm_size")
        layout.prop(preprocess_props, "cutoff_frequency")
        layout.prop(preprocess_props, "filter_order")
        layout.prop(preprocess_props, "samples_per_frame")

        # Align props
        hand_align_props = context.scene.hand_align_props
        assert isinstance(hand_align_props, HandAlignProps)
        layout.separator()
        layout.label(text="Align hands settings:")
        layout.prop_search(hand_align_props, "target_aramture", bpy.data, "armatures", icon='ARMATURE_DATA')
        if hand_align_props.target_aramture is not None:
            layout.prop_search(hand_align_props, "left_hand_target", hand_align_props.target_aramture.pose, "bones")
            layout.prop_search(hand_align_props, "right_hand_target", hand_align_props.target_aramture.pose, "bones")
        layout.prop(hand_align_props, "start_frame")

        layout.operator(MIC_OT_ImportHands.bl_idname)
