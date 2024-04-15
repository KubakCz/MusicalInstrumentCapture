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

"""Property groups for storing hand import properties."""


import bpy


class PreprocessProps(bpy.types.PropertyGroup):
    """
    Property group for storing preprocessing properties.
    """
    palm_size: bpy.props.FloatProperty(
        name="Palm Size",  # noqa
        description="Size of the palm.",  # noqa
        default=0.1,
        min=0,
        unit='LENGTH')  # noqa

    cutoff_frequency: bpy.props.FloatProperty(
        name="Frequency Cutoff (Hz)",  # noqa
        description="Lower values give a smoother curve.",  # noqa
        default=6,
        min=0)

    filter_order: bpy.props.IntProperty(
        name="Filter Order",  # noqa
        description="Higher values produce a harder frequency cutoff.",  # noqa
        default=6,
        min=1)

    samples_per_frame: bpy.props.IntProperty(
        name="Samples per Frame",  # noqa
        description="How many samples to calculate per frame, helps with subframe data.",  # noqa
        default=2,
        min=1)
