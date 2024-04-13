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

import bpy
from typing import List, Optional
from dataclasses import dataclass
from mathutils import Vector, Quaternion

from .hand_joint import HandJoint
from .hand_types import HandAnimationData, HandFrame


class RawData:
    filename: Optional[str] = None
    raw_data: Optional[List[HandAnimationData]] = None


@dataclass
class PreprocessedHandData:
    """
    Class for storing preprocessed data of a single hand.
    Contains the preprocessed data and average joint distances.
    Data are stored as world space positions of the joints.
    """
    name: str
    handedness: str

    # List of timestamps of the frames
    timestamps: List[float]

    # List of world position in data[joint][frame] format
    data: List[List[Vector]]

    # Average distance from previous joint
    average_joint_distance: List[float]

    def __len__(self):
        """Return the number of frames in the data."""
        return len(self.timestamps)


class PreprocessedData:
    """
    Class for storing preprocessed data of multiple hands.
    Data are stored as world space positions of the joints.
    """
    hands: Optional[List[PreprocessedHandData]] = None


@dataclass
class ProcessedHandData:
    """
    Class for storing processed data of one hand.
    Data are stored as lists of local locations and rotations for each joint.
    """
    frame_numbers: List[float]
    local_locations: List[Optional[List[Vector]]]
    local_rotations: List[Optional[List[Quaternion]]]


def get_ws_pos(hand_data: PreprocessedHandData, frame_idx: int) -> List[Vector]:
    return [hand_data.data[joint.value][frame_idx] for joint in HandJoint]


def preprocessed_2_hand_anim(hand_data: PreprocessedHandData) -> HandAnimationData:
    """Temporary function to convert preprocessed hand data to HandAnimationData."""
    frames = [
        HandFrame(
            timestamp=hand_data.timestamps[i],
            normalized_positions=[],
            world_positions=get_ws_pos(hand_data, i)
        ) for i in range(len(hand_data.timestamps))
    ]
    return HandAnimationData(name=hand_data.name, animation_data=frames)


class HandAlignData(bpy.types.PropertyGroup):
    """Property group for storing hand alignment data."""
    # Data preprocessing
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

    # Hand generation
    use_average_joint_distance: bpy.props.BoolProperty(
        name="Constant joint distance",  # noqa
        description="If enabled, hand joints will have constant distance throughout the animation. This distance is calculated as the average distance from the whole animation.",  # noqa
        default=True)

    target_aramture: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Target Armature",  # noqa
        description="Armature to which the hands will be attached.",  # noqa
        poll=lambda self, obj: obj.type == 'ARMATURE')

    left_hand_target: bpy.props.StringProperty(
        name="Left Hand Target Bone",  # noqa
        description="Bone to which the left hand will be aligned.")  # noqa

    right_hand_target: bpy.props.StringProperty(
        name="Right Hand Target Bone",  # noqa
        description="Bone to which the right hand will be aligned.")  # noqa
