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

"""Classes for storing hand alignment data."""

from typing import List
import bpy
from .hand_types import HandAnimationData


class RawData:
    filename: str = None
    raw_data: List[HandAnimationData] = None


class PreprocessedHandData:
    """
    Class for storing preprocessed hand data.
    Contains the preprocessed data and average joint distances.
    """

    def __init__(self):
        self.data: HandAnimationData = None
        self.average_joint_distance: List[float] = None  # Average distance from previous joint


class PreprocessedData:
    """Class for storing preprocessed data."""
    data: List[PreprocessedHandData] = None


class HandAlignData(bpy.types.PropertyGroup):
    """Property group for storing hand alignment data."""
    # Data preprocessing
    low_pass_cutoff: bpy.props.FloatProperty(
        name="Low Pass Cutoff",  # noqa
        description="Low pass filter cutoff frequency.",  # noqa
        default=6,
        min=0)

    palm_size: bpy.props.FloatProperty(
        name="Palm Size",  # noqa
        description="Size of the palm.",  # noqa
        default=0.1,
        min=0,
        unit='LENGTH')  # noqa

    # Hand generation
    use_average_joint_distance: bpy.props.BoolProperty(
        name="Constant joint distance",  # noqa
        description="If enabled, hand joints will have constant distance throughout the animation. This distance is calculated as the average distance from the whole animation.",  # noqa
        default=True)
