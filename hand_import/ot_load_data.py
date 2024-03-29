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

"""Operator for loading hand data to memory."""

import os
import bpy
import marshmallow

from .import_hands_data import RawData
from .ot_preprocess_data import PreprocessedData
from .hand_types import HandAnimationData


class MIC_OT_LoadData(bpy.types.Operator):
    """Operator for loading hand data to memory."""
    bl_idname = "mic.load_data"
    bl_label = "Load Data"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")  # noqa

    def execute(self, context):
        print("--- Executing LoadData ---")
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                print("Loading data from file:", self.filepath)
                json_string = file.read()
                print("Deserializing data...")
                data = HandAnimationData.schema().loads(json_string, many=True)
                print("Data loaded successfully.")
                RawData.raw_data = data
                RawData.filename = os.path.basename(self.filepath)
                PreprocessedData.data = None  # Reset preprocessed data
        except marshmallow.exceptions.ValidationError:
            self.report({'ERROR'}, "The selected file is not in the correct format.")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
