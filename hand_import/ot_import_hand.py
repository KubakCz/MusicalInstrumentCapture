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
from typing import Optional


from .property_groups import PreprocessProps
from .hand_loading import InvalidDataError, load_json
from .hand_preprocessing import preprocess_data


class MIC_OT_ImportHands(bpy.types.Operator):
    """Operator for Importing hands."""
    bl_idname = "mic.import_hands"
    bl_label = "Import Hands"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")  # type: ignore # noqa

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context: bpy.types.Context) -> set[str]:
        print("--- Executing ImportHands ---")
        print("Loading data from file:", self.filepath)
        try:
            hands = load_json(self.filepath)
        except InvalidDataError as e:
            messages = []
            exception: Optional[BaseException] = e
            while exception:
                messages.append(str(exception))
                exception = exception.__cause__
            self.report({'ERROR'}, '\nCaused by:\n'.join(messages))
            return {'CANCELLED'}

        print("Preprocessing data...")

        preprocess_props = context.scene.preprocess_props
        assert isinstance(preprocess_props, PreprocessProps)
        preprocessed_hands = preprocess_data(hands, preprocess_props)

        print("--- ImportHands finished ---")

        return {'FINISHED'}
