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

"""Operator for Importing hands."""

import bpy

from .property_groups import HandAlignProps, PreprocessProps
from .hand_loading import InvalidDataError, load_json
from .hand_preprocessing import preprocess_data
from .armature_generation import add_hand_to_armature
from .hand_type import HandType


class MIC_OT_ImportHands(bpy.types.Operator):
    """Operator for Importing hands."""
    bl_idname = "mic.import_hands"
    bl_label = "Import Hands"
    bl_description = "Import hand animation data and align it with the motion capture data"
    bl_options = {'REGISTER', 'UNDO'}

    # Filepath property filled by the file dialog
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")  # type: ignore # noqa

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        # Check props
        hand_align_props = context.scene.hand_align_props
        assert isinstance(hand_align_props, HandAlignProps)
        prop_not_set = hand_align_props.prop_not_set()
        if prop_not_set:
            self.report({'ERROR'}, f"Property {prop_not_set} is not set.")
            return {'CANCELLED'}

        # Open file dialog
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context: bpy.types.Context) -> set[str]:
        print("--- Executing ImportHands ---")

        print("Loading data from file:", self.filepath)
        try:
            hands = load_json(self.filepath)
        except InvalidDataError as e:
            messages = []
            exception: BaseException | None = e
            while exception:
                messages.append(str(exception))
                exception = exception.__cause__
            self.report({'ERROR'}, '\nCaused by:\n'.join(messages))
            return {'CANCELLED'}

        # For now, only one left and one right hand is supported
        # => filter out all other hands before preprocessing
        l_idx = next((i for i, hand in enumerate(hands) if hand.hand_type ==
                     HandType.LEFT and not hand.is_empty()), None)
        r_idx = next((i for i, hand in enumerate(hands) if hand.hand_type ==
                     HandType.RIGHT and not hand.is_empty()), None)
        left_hand_count = sum(1 for hand in hands if hand.hand_type == HandType.LEFT)
        right_hand_count = len(hands) - left_hand_count
        if left_hand_count > 1:
            self.report({'WARNING'}, "Detected more than one left hand. Only the first one will be used.")
        if right_hand_count > 1:
            self.report({'WARNING'}, "Detected more than one right hand. Only the first one will be used.")
        if left_hand_count == 0:
            self.report({'WARNING'}, "No left hand detected.")
        if right_hand_count == 0:
            self.report({'WARNING'}, "No right hand detected.")

        selected_hands = []
        if l_idx is not None:
            selected_hands.append(hands[l_idx])
        if r_idx is not None:
            selected_hands.append(hands[r_idx])

        print("Preprocessing data...")
        preprocess_props = context.scene.preprocess_props
        assert isinstance(preprocess_props, PreprocessProps)
        preprocessed_hands = preprocess_data(selected_hands, preprocess_props)

        print("Generating armature...")
        hand_align_props = context.scene.hand_align_props
        assert isinstance(hand_align_props, HandAlignProps)
        fps = context.scene.render.fps
        for hand in preprocessed_hands:
            target_bone_name = \
                hand_align_props.left_hand_target \
                if hand.hand_type == HandType.LEFT \
                else hand_align_props.right_hand_target
            add_hand_to_armature(
                hand,
                hand_align_props.target_aramture,
                target_bone_name,
                fps,
                hand_align_props.start_frame)

        print("--- ImportHands finished ---")

        return {'FINISHED'}
