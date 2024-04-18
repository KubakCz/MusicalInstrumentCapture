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
    "description": "A tool to make animating violin performances easier.",
    "blender": (4, 0, 0),
    "version": (0, 1, 0),
    "location": "View3D > Sidebar > Musical Instrument Capture",
    "warning": "",
    "doc_url": "https://github.com/KubakCz/MusicalInstrumentCapture/blob/main/README.md",
    "category": "Animation"
}


def register() -> None:
    # Hand import
    from .hand_import import property_groups as h_property_groups
    bpy.utils.register_class(h_property_groups.PreprocessProps)
    bpy.types.Scene.preprocess_props = bpy.props.PointerProperty(type=h_property_groups.PreprocessProps)
    bpy.utils.register_class(h_property_groups.HandAlignProps)
    bpy.types.Scene.hand_align_props = bpy.props.PointerProperty(type=h_property_groups.HandAlignProps)

    from .hand_import import ot_import_hands
    bpy.utils.register_class(ot_import_hands.MIC_OT_ImportHands)

    from .hand_import import pt_import_hands
    bpy.utils.register_class(pt_import_hands.MIC_PT_MusicalInstrumentCapture)

    # Rigid body align
    from .rigidbody_align import property_groups as r_property_groups
    bpy.utils.register_class(r_property_groups.ViolinAlignProps)
    bpy.types.Scene.violin_align_data = bpy.props.PointerProperty(type=r_property_groups.ViolinAlignProps)
    bpy.utils.register_class(r_property_groups.BowAlignProps)
    bpy.types.Scene.bow_align_data = bpy.props.PointerProperty(type=r_property_groups.BowAlignProps)

    from .rigidbody_align import ot_align_bow
    bpy.utils.register_class(ot_align_bow.MIC_OT_AlignBow)

    from .rigidbody_align import ot_align_violin
    bpy.utils.register_class(ot_align_violin.MIC_OT_AlignViolin)

    from .rigidbody_align import pt_align
    bpy.utils.register_class(pt_align.MIC_PT_Align)


def unregister() -> None:
    # Hand import
    from .hand_import import pt_import_hands
    if pt_import_hands.MIC_PT_MusicalInstrumentCapture.is_registered:
        bpy.utils.unregister_class(pt_import_hands.MIC_PT_MusicalInstrumentCapture)

    from .hand_import import ot_import_hands
    if ot_import_hands.MIC_OT_ImportHands.is_registered:
        bpy.utils.unregister_class(ot_import_hands.MIC_OT_ImportHands)

    from .hand_import import property_groups as h_property_groups
    if h_property_groups.HandAlignProps.is_registered:
        bpy.utils.unregister_class(h_property_groups.HandAlignProps)
        del bpy.types.Scene.hand_align_props
    if h_property_groups.PreprocessProps.is_registered:
        bpy.utils.unregister_class(h_property_groups.PreprocessProps)
        del bpy.types.Scene.preprocess_props

    # Rigid body align
    from .rigidbody_align import pt_align
    if pt_align.MIC_PT_Align.is_registered:
        bpy.utils.unregister_class(pt_align.MIC_PT_Align)

    from .rigidbody_align import ot_align_bow
    if ot_align_bow.MIC_OT_AlignBow.is_registered:
        bpy.utils.unregister_class(ot_align_bow.MIC_OT_AlignBow)

    from .rigidbody_align import ot_align_violin
    if ot_align_violin.MIC_OT_AlignViolin.is_registered:
        bpy.utils.unregister_class(ot_align_violin.MIC_OT_AlignViolin)

    from .rigidbody_align import property_groups as r_property_groups
    if r_property_groups.ViolinAlignProps.is_registered:
        bpy.utils.unregister_class(r_property_groups.ViolinAlignProps)
        del bpy.types.Scene.violin_align_data
    if r_property_groups.BowAlignProps.is_registered:
        bpy.utils.unregister_class(r_property_groups.BowAlignProps)
        del bpy.types.Scene.bow_align_data
