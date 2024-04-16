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

from .property_groups import PreprocessProps
from .ot_import_hands import MIC_OT_ImportHands

from .ot_generate_empty import MIC_OT_GenerateEmpty
from .ot_generate_armature import MIC_OT_GenerateArmature
from .ot_preprocess_data import MIC_OT_PreprocessData, PreprocessedData
from .ot_load_data import MIC_OT_LoadData, RawData


class MIC_PT_MusicalInstrumentCapture(bpy.types.Panel):
    """Main panel for the Musical Instrument Capture add-on."""
    bl_label = "Import Hand Animation"
    bl_idname = "VIEW3D_PT_MusicalInstrumentCapture"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Musical Instrument Capture"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        # Preprocess props
        preprocess_props = context.scene.preprocess_props
        assert isinstance(preprocess_props, PreprocessProps)
        layout.prop(preprocess_props, "palm_size")
        layout.prop(preprocess_props, "cutoff_frequency")
        layout.prop(preprocess_props, "filter_order")
        layout.prop(preprocess_props, "samples_per_frame")

        layout.operator(MIC_OT_ImportHands.bl_idname)
        layout.separator()

        # OLD CODE:

        hand_align_data = context.scene.hand_align_data
        layout.label(text="No data loaded." if RawData.raw_data is None else f"Loaded data: {RawData.filename}")
        layout.operator(MIC_OT_LoadData.bl_idname)

        # if RawData.raw_data is None:
        #     return

        layout.separator()
        layout.prop(hand_align_data, "palm_size")
        layout.prop(hand_align_data, "cutoff_frequency")
        layout.prop(hand_align_data, "filter_order")
        layout.prop(hand_align_data, "samples_per_frame")
        layout.label(text="Preprocessed data: None" if PreprocessedData.hands is None else "Preprocessed data: Ready")
        layout.operator(MIC_OT_PreprocessData.bl_idname)

        # if PreprocessedData.hands is None:
        #     return

        layout.separator()
        layout.prop_search(hand_align_data, "target_aramture", bpy.data, "armatures", icon='ARMATURE_DATA')
        if hand_align_data.target_aramture is not None:
            layout.prop_search(hand_align_data, "left_hand_target", hand_align_data.target_aramture.pose, "bones")
            layout.prop_search(hand_align_data, "right_hand_target", hand_align_data.target_aramture.pose, "bones")
        layout.prop(hand_align_data, "use_average_joint_distance")
        layout.operator(MIC_OT_GenerateArmature.bl_idname)
        layout.operator(MIC_OT_GenerateEmpty.bl_idname)
