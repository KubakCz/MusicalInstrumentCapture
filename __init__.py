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

"""Entry point for the Musical Instrument Capture add-on."""

import bpy

bl_info = {
    "name": "Musical Instrument Capture",
    "author": "Jakub Slezáček",
    "description": "",
    "blender": (2, 91, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "Requires installation of dependencies",
    "category": "Generic"
}


def get_classes_to_register():
    """
    Declare all classes that should be registered with Blender.
    This is a separate function because the imported modules might
    require the dependencies to be installed first.
    """
    from .import_hands import MESH_OT_ImportHands
    from .musical_instrument_capture import VIEW3D_PT_MusicalInstrumentCapture

    return [VIEW3D_PT_MusicalInstrumentCapture, MESH_OT_ImportHands]


class DEPENDENCY_PT_Warning(bpy.types.Panel):
    """Panel that warns the user about missing dependencies."""
    bl_label = "Musical Instrument Capture"
    bl_category = "Musical Instrument Capture"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        lines = [f"Please install the missing dependencies for the \"{bl_info.get('name')}\" add-on.",
                 "TODO: Tutorial on how to install the dependencies manually."]

        for line in lines:
            layout.label(text=line)


dependencies_installed = False


def register():
    """Try to register the classes, or register the warning panel if the dependencies are not installed."""
    try:
        # Try to register the classes.
        for cls in get_classes_to_register():
            bpy.utils.register_class(cls)
        global dependencies_installed
        dependencies_installed = True
    except ImportError:
        # If the dependencies are not installed, register the warning panel.
        bpy.utils.register_class(DEPENDENCY_PT_Warning)
        return


def unregister():
    """Unregister the classes, or the warning panel if the dependencies are not installed."""
    if not dependencies_installed:
        bpy.utils.unregister_class(DEPENDENCY_PT_Warning)
        return

    for cls in get_classes_to_register():
        bpy.utils.unregister_class(cls)
