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


class DEPENDENCY_PT_Warning(bpy.types.Panel):
    """Panel that warns the user about missing dependencies."""
    bl_label = "Musical Instrument Capture"
    bl_category = "Musical Instrument Capture"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        layout.label(text=f"Please install the missing dependencies for the \"{bl_info.get('name')}\" add-on.")
        layout.label(text="TODO: Tutorial on how to install the dependencies manually.")


dependencies_installed = False


def register():
    """Try to register the classes, or register the warning panel if the dependencies are not installed."""
    try:
        from .hand_import import pt_import_hands
        bpy.utils.register_class(pt_import_hands.MIC_PT_MusicalInstrumentCapture)

        from .hand_import import ot_import_hands
        bpy.utils.register_class(ot_import_hands.MIC_OT_ImportHands)

        from .rigidbody_align import pt_align
        bpy.utils.register_class(pt_align.MIC_PT_Align)

        from .rigidbody_align import ot_align_bow
        bpy.utils.register_class(ot_align_bow.MIC_OT_AlignBow)

        from .rigidbody_align import ot_align_violin
        bpy.utils.register_class(ot_align_violin.MIC_OT_AlignViolin)

        from .rigidbody_align import align_data
        bpy.utils.register_class(align_data.ViolinAlignData)
        bpy.types.Scene.violin_align_data = bpy.props.PointerProperty(type=align_data.ViolinAlignData)

        bpy.utils.register_class(align_data.BowAlignData)
        bpy.types.Scene.bow_align_data = bpy.props.PointerProperty(type=align_data.BowAlignData)
    except ImportError:
        # If the dependencies are not installed, unregister already registered classes
        # and register the warning panel.
        unregister()
        bpy.utils.register_class(DEPENDENCY_PT_Warning)
        return


def unregister():
    """Unregister the classes, or the warning panel if the dependencies are not installed."""
    from .hand_import import pt_import_hands
    if pt_import_hands.MIC_PT_MusicalInstrumentCapture.is_registered:
        bpy.utils.unregister_class(pt_import_hands.MIC_PT_MusicalInstrumentCapture)

    from .hand_import import ot_import_hands
    if ot_import_hands.MIC_OT_ImportHands.is_registered:
        bpy.utils.unregister_class(ot_import_hands.MIC_OT_ImportHands)

    from .rigidbody_align import pt_align
    if pt_align.MIC_PT_Align.is_registered:
        bpy.utils.unregister_class(pt_align.MIC_PT_Align)

    from .rigidbody_align import ot_align_bow
    if ot_align_bow.MIC_OT_AlignBow.is_registered:
        bpy.utils.unregister_class(ot_align_bow.MIC_OT_AlignBow)

    from .rigidbody_align import ot_align_violin
    if ot_align_violin.MIC_OT_AlignViolin.is_registered:
        bpy.utils.unregister_class(ot_align_violin.MIC_OT_AlignViolin)

    from .rigidbody_align import align_data
    if align_data.ViolinAlignData.is_registered:
        bpy.utils.unregister_class(align_data.ViolinAlignData)
        del bpy.types.Scene.violin_align_data  # type: ignore
    if align_data.BowAlignData.is_registered:
        bpy.utils.unregister_class(align_data.BowAlignData)
        del bpy.types.Scene.bow_align_data  # type: ignore

    if DEPENDENCY_PT_Warning.is_registered:
        bpy.utils.unregister_class(DEPENDENCY_PT_Warning)
