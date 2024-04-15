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

"""Functions for preprocessing loaded hand data."""

import bpy
from typing import List
from mathutils import Vector


from .hand_joint import HandJoint
from .hand_type import HandType
from .hand_loading import Hand, Frame, PositionList
from .fcurves import LocationFCurves
from .property_groups import PreprocessProps


class PreprocessedHand(Hand):
    """
    Data class for storing a hand with animation data.
    In addition to the data stored in Hand, it also contains average joint distances.
    """

    def __init__(self, name: str, hand_type: HandType, frames: List[Frame], average_joint_distance: List[float]):
        """
        Initialize the PreprocessedHand with the given data.
        :param name: Name of the hand.
        :param hand_type: Type of the hand.
        :param frames: List of frames containing the animation data.
        :param average_joint_distance: List of average distances between joints.
        """
        super().__init__(name, hand_type, frames)

        if len(average_joint_distance) != len(HandJoint):
            raise ValueError(f"Wrong number of average joint distances in the list "
                             f"(has {len(average_joint_distance)}, expected {len(HandJoint)}).")
        self.average_joint_distance = average_joint_distance


def _scale_positions(positions: PositionList, palm_size: float) -> PositionList:
    """
    Scale the positions to match the palm size.
    :param positions: List of positions to scale.
    :param palm_size: Size of the palm.
    :return: List of scaled positions.
    """
    current_palm_size = (positions[HandJoint.MIDDLE_1.value] - positions[HandJoint.WRIST.value]).length
    scale_multiplayer = palm_size / current_palm_size
    return PositionList([pos * scale_multiplayer for pos in positions])


def _convert_to_fcurves(action: bpy.types.Action, frames: List[Frame]) -> List[LocationFCurves]:
    """
    Convert the world positions of the frames to fcurves.
    :param frames: List of frames to convert.
    :return: List of fcurves, idx corresponds to the joint.
    """
    # Create fcurves for each joint
    fcurves = [
        LocationFCurves(
            action,
            str(joint.value),
            joint.name
        ) for joint in HandJoint
    ]

    # Convert world positions from list of frames of positions to list of joints of positions
    frame_timestamps: List[float] = []  # Timestamps in "frame" units
    positions_joints: List[List[Vector]] = [[] for _ in range(len(HandJoint))]
    for frame in frames:
        frame_timestamps.append(frame.timestamp * bpy.context.scene.render.fps)
        for i in range(len(HandJoint)):
            positions_joints[i].append(frame.world_positions[i])

    # Set keyframes for the fcurves
    for i in range(len(HandJoint)):
        fcurves[i].set_keyframes(frame_timestamps, positions_joints[i])

    return fcurves


def _convert_from_fcurves(fcurves: List[LocationFCurves], frames: List[Frame]) -> None:
    """
    Fill world positions of the frames with data from fcurves.
    :param fcurves: List of fcurves, idx corresponds to the joint.
    :param frames: List of frames to which assign the positions.
    """
    if len(fcurves) != len(HandJoint):
        raise ValueError(f"Wrong number of fcurves in the list (has {len(fcurves)}, expected {len(HandJoint)}).")

    # Convert fcurves to list[joint][frame]
    keyframes_joints = [curve.get_keyframes() for curve in fcurves]

    # Check if the number of keyframes matches the number of frames for each joint
    if any(map(lambda keyfreame_list: len(keyfreame_list) != len(frames), keyframes_joints)):
        raise ValueError("Number of keyframes does not match the number of frames.")

    # Assign the keyframes to the frames
    for i, frame in enumerate(frames):
        for joint in HandJoint:
            frame.world_positions[joint.value] = keyframes_joints[joint.value][i]


def _compute_average_joint_distances(frames: List[Frame]) -> List[float]:
    """
    Compute average joint distances from the given frames.
    :param frames: List of frames to compute the distances from.
    :return: List of average joint distances.
    """
    dist_sums = [0.0 for _ in HandJoint]
    for frame in frames:
        for joint in set(HandJoint) - {HandJoint.WRIST}:  # Skip the wrist
            predecessor = joint.predecessor()
            assert predecessor is not None
            dist_sums[joint.value] += (frame.world_positions[joint.value] -
                                       frame.world_positions[predecessor.value]).length
    return [dist / len(frames) for dist in dist_sums]


def _preprocess_hand(hand: Hand, preprocess_properties: PreprocessProps) -> PreprocessedHand:
    """
    Preprocess the given hand by scaling and filtering world space positions
    and calculating average joint distances.
    :param hand: Hand to preprocess.
    :param preprocess_properties: Properties for preprocessing the data.
    :return: Preprocessed hand.
    """
    # Create list of new frames with scaled positions
    new_frames = [
        Frame(
            frame.timestamp,
            frame.normalized_positions,
            _scale_positions(frame.world_positions, preprocess_properties.palm_size)
        ) for frame in hand.frames
    ]

    # Create an object to hold an animation action
    if bpy.context.active_object is not None:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.empty_add()
    obj = bpy.context.object
    action = bpy.data.actions.new(name="preprocessed_data")
    obj.animation_data_create()
    obj.animation_data.action = action

    # Transform the scaled data to fcurves
    fcurves = _convert_to_fcurves(action, new_frames)

    # Change window type to graph editor
    original_area_type = bpy.context.area.type
    bpy.context.area.type = 'GRAPH_EDITOR'

    # Select all fcurves
    for curve_tuple in fcurves:
        for curve in curve_tuple:
            curve.update()
            curve.select = True  # Select fcurve
    bpy.ops.graph.select_all(action='SELECT')  # Select keyframes on selected fcurves

    # Filter the data
    bpy.ops.graph.butterworth_smooth(
        cutoff_frequency=preprocess_properties.cutoff_frequency,
        filter_order=preprocess_properties.filter_order,
        samples_per_frame=preprocess_properties.samples_per_frame)

    # Return the area type to the original value
    bpy.context.area.type = original_area_type

    # Convert the filtered data back to frames
    _convert_from_fcurves(fcurves, new_frames)

    # Delete the animation action
    bpy.data.actions.remove(action)
    bpy.data.objects.remove(obj, do_unlink=True)

    # Calculate average joint distances
    avg_dists = _compute_average_joint_distances(new_frames)

    return PreprocessedHand(hand.name, hand.hand_type, new_frames, avg_dists)


def preprocess_data(hands: List[Hand], preprocess_properties: PreprocessProps) -> List['PreprocessedHand']:
    """
    Preprocess the loaded hand data by scaling and filtering world space positions
    and calculating average joint distances.
    :param hands: List of hands to preprocess.
    :param preprocess_properties: Properties for preprocessing the data.
    :return: List of preprocessed hands.
    """
    return [_preprocess_hand(hand, preprocess_properties) for hand in hands]
