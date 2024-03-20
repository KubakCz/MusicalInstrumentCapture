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

plane_marker_name = "Plane marker"
plane_marker_description = "Marker defining plane orientation of the top plate of the violin."


class ViolinMarkers(bpy.types.PropertyGroup):
    """Property group for storing violin markers."""
    plane_1: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name=plane_marker_name + " 1",  # noqa
        description=plane_marker_description)
    plane_2: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name=plane_marker_name + " 2",  # noqa
        description=plane_marker_description)
    plane_3: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name=plane_marker_name + " 3",  # noqa
        description=plane_marker_description)

    bridge: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Bridge marker",  # noqa
        description="Marker above the center of the bridge.")  # noqa
    bridge_offset: bpy.props.FloatProperty(  # type: ignore
        name="Bridge Marker Offset",  # noqa
        description="Vertical offset of the bridge marker from the top of the bridge.",  # noqa
        default=0.0,
        min=0.0)  # type: ignore

    scroll: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Scroll marker",  # noqa
        description="Marker above the scroll.")  # noqa


class BowMarkers(bpy.types.PropertyGroup):
    """Property group for storing bow markers."""
    frog: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Frog marker",  # noqa
        description="Marker at the bottom of the frog.")  # noqa
    tip: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Tip marker",  # noqa
        description="Marker at the tip of the bow.")  # noqa


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
        layout.label(text="Violin markers:")
        violin_markers_box = layout.box()
        violin_markers_box.prop_search(context.scene.violin_markers, "plane_1", bpy.data, "objects")
        violin_markers_box.prop_search(context.scene.violin_markers, "plane_2", bpy.data, "objects")
        violin_markers_box.prop_search(context.scene.violin_markers, "plane_3", bpy.data, "objects")
        violin_markers_box.separator()
        violin_markers_box.prop_search(context.scene.violin_markers, "bridge", bpy.data, "objects")
        violin_markers_box.prop(context.scene.violin_markers, "bridge_offset")
        violin_markers_box.separator()
        violin_markers_box.prop_search(context.scene.violin_markers, "scroll", bpy.data, "objects")
        violin_markers_box.separator()
        violin_markers_box.operator("object.select_all", text="Align Violin")

        # Bow alignment
        layout.label(text="Bow markers:")
        bow_markers_box = layout.box()
        bow_markers_box.prop_search(context.scene.bow_markers, "frog", bpy.data, "objects")
        bow_markers_box.prop_search(context.scene.bow_markers, "tip", bpy.data, "objects")
        bow_markers_box.separator()
        bow_markers_box.operator("object.select_all", text="Align Bow")
