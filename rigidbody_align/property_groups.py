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

"""Property groups for storing alignment data for the violin and the bow."""

import bpy

plane_marker_name = "Plane marker"
plane_marker_description = "Marker defining plane orientation of the top plate of the violin"


class ViolinAlignProps(bpy.types.PropertyGroup):
    """Property group for storing violin markers."""
    reference_point: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Reference Point",  # noqa
        description="Reference object placed on the violin model. Must be child of the model")  # noqa
    reference_marker: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Reference Marker",  # noqa
        description="Marker to be aligned with reference point")  # noqa

    rigidbody: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Rigidbody",  # noqa
        description="Rigidbody object representing the violin")  # noqa

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
        description="Marker above the center of the bridge")  # noqa
    scroll: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Scroll marker",  # noqa
        description="Marker above the scroll")  # noqa


class BowAlignProps(bpy.types.PropertyGroup):
    """Property group for storing bow markers."""
    reference_point: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
       name="Reference Point",  # noqa
        description="Reference object placed on the bow model. Must be child of the model")  # noqa
    reference_marker: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Reference Marker",  # noqa
        description="Marker to be aligned with reference point")  # noqa

    rigidbody: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Rigidbody",  # noqa
        description="Rigidbody object representing the bow")  # noqa

    frog_bottom: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Frog bottom marker",  # noqa
        description="Marker at the bottom of the frog")  # noqa
    frog_top: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Frog top marker",  # noqa
        description="Marker abowe the frog")  # noqa
    stick: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Stick marker",  # noqa
        description="Marker at stick")  # noqa
    tip: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Tip marker",  # noqa
        description="Marker at the tip of the bow")  # noqa
