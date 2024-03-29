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

"""Operator for loading hand data to memory."""

import bpy
from .import_hands_data import PreprocessedData, PreprocessedHandData
from .hand_joint import HandJoint
from .hand_types import HandAnimationData, HandFrame
from .ot_load_data import RawData


JOINTS_WITHOUT_WRIST = set(HandJoint) - {HandJoint.WRIST}


def preprocess_frame(frame: HandFrame) -> HandFrame:
    """Preprocess the given hand frame."""
    # Scale the hand data to match the palm size
    palm_size = bpy.context.scene.hand_align_data.palm_size
    data_palm_size = (frame.world_positions[HandJoint.INDEX_1.value] -
                      frame.world_positions[HandJoint.WRIST.value]).length
    multiplier = palm_size / data_palm_size
    new_frame = HandFrame(
        frame.timestamp,
        None,
        [multiplier * pos for pos in frame.world_positions])
    return new_frame


def preprocess(hand_data: HandAnimationData) -> PreprocessedHandData:
    """Preprocess the given hand data."""
    new_data = HandAnimationData(hand_data.name, [])
    dist_sums = [0 for _ in HandJoint]
    last_timestamp = hand_data.animation_data[-1].timestamp

    for frame in hand_data.animation_data:
        # preprocess frame
        new_frame = preprocess_frame(frame)
        # compute joint distances
        for joint in JOINTS_WITHOUT_WRIST:
            dist_sums[joint.value] += (new_frame.world_positions[joint.value] -
                                       new_frame.world_positions[joint.predecessor().value]).length

        new_data.animation_data.append(new_frame)
        print(frame.timestamp / last_timestamp)

    # calculate average joint distances
    average_dist = [dist / len(new_data.animation_data) for dist in dist_sums]

    preprocessed_data = PreprocessedHandData()
    preprocessed_data.data = new_data
    preprocessed_data.average_joint_distance = average_dist
    return preprocessed_data


class MIC_OT_PreprocessData(bpy.types.Operator):
    """Operator for preprocessing loaded data."""
    bl_idname = "mic.preprocess_data"
    bl_label = "Preprocess Data"
    bl_options = {'REGISTER'}

    def execute(self, context):
        print("--- Executing PreprocessData ---")
        if RawData.raw_data is None:
            self.report({'ERROR'}, "No data loaded.")
            return {'CANCELLED'}

        PreprocessedData.data = []
        for hand_data in RawData.raw_data:
            print(f"Preprocessing data for hand: {hand_data.name}")
            new_hand_data = preprocess(hand_data)
            PreprocessedData.data.append(new_hand_data)

        return {'FINISHED'}
