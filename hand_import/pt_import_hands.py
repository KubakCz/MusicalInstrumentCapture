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
from .ot_import_hands import MIC_OT_ImportHands


class MIC_PT_MusicalInstrumentCapture(bpy.types.Panel):
    """Main panel for the Musical Instrument Capture add-on."""
    bl_label = "Musical Instrument Capture"
    bl_idname = "VIEW3D_PT_MusicalInstrumentCapture"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Musical Instrument Capture"

    def draw(self, context):
        layout = self.layout
        layout.operator(MIC_OT_ImportHands.bl_idname, text="Import Hands")
