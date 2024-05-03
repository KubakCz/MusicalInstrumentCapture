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


class HandAlignProps(bpy.types.PropertyGroup):
    """
    Property group for storing alignment properties.
    """
    start_frame: bpy.props.IntProperty(  # type: ignore
        name="Start Frame",  # noqa
        description="Frame at which the hand animation should start",  # noqa
        default=1)

    target_aramture: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Object,
        name="Target Armature",  # noqa
        description="Armature to which the hands will be attached",  # noqa
        poll=lambda self, obj: obj.type == 'ARMATURE')

    left_hand_target: bpy.props.StringProperty(  # type: ignore
        name="Left Hand Target Bone",  # noqa
        description="Bone to which the left hand will be aligned")  # noqa

    right_hand_target: bpy.props.StringProperty(  # type: ignore
        name="Right Hand Target Bone",  # noqa
        description="Bone to which the right hand will be aligned")  # noqa

    def prop_not_set(self) -> str | None:
        """
        If any of the properties is not set, return the name of the property.
        Else return None.
        """
        if self.target_aramture is None:
            return "Target Armature"
        if not self.left_hand_target:
            return "Left Hand Target Bone"
        if not self.right_hand_target:
            return "Right Hand Target Bone"
        return None


class PreprocessProps(bpy.types.PropertyGroup):
    """
    Property group for storing preprocessing properties.
    """
    palm_size: bpy.props.FloatProperty(  # type: ignore
        name="Palm Size",  # noqa
        description="Size of the palm",  # noqa
        default=0.1,
        min=0,
        unit='LENGTH')  # noqa

    cutoff_frequency: bpy.props.FloatProperty(  # type: ignore
        name="Frequency Cutoff (Hz)",  # noqa
        description="Lower values give a smoother curve",  # noqa
        default=6,
        min=0)

    filter_order: bpy.props.IntProperty(  # type: ignore
        name="Filter Order",  # noqa
        description="Higher values produce a harder frequency cutoff",  # noqa
        default=6,
        min=1,
        max=32)

    samples_per_frame: bpy.props.IntProperty(  # type: ignore
        name="Samples per Frame",  # noqa
        description="How many samples to calculate per frame, helps with subframe data",  # noqa
        default=2,
        min=1,
        max=64)
