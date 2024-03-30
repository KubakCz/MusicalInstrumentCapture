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

"""
Operator for preprocessing hand data.
This step includes scaling and filtering the data.
"""

import bpy
from mathutils import Vector
from .import_hands_data import HandAlignData, PreprocessedData, PreprocessedHandData
from .hand_joint import HandJoint
from .hand_types import HandAnimationData
from .ot_load_data import RawData


JOINTS_WITHOUT_WRIST = set(HandJoint) - {HandJoint.WRIST}


def preprocess(hand_data: HandAnimationData) -> PreprocessedHandData:
    """Preprocess the given hand data."""
    frame_count = len(hand_data.animation_data)

    # Create an object to hold the action
    if bpy.context.active_object is not None:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.empty_add()
    obj = bpy.context.object

    # Create an action and fcurves for the world positions of the hand joints
    action = bpy.data.actions.new(name="preprocessed_data")
    obj.animation_data_create()
    obj.animation_data.action = action
    fcurves = [
        tuple(
            action.fcurves.new(
                data_path=f"{joint.value}_{i}",
                index=i,
                action_group=joint.name
            ) for i in range(3)
        ) for joint in HandJoint
    ]

    original_area_type = bpy.context.area.type
    bpy.context.area.type = 'GRAPH_EDITOR'

    # Fix scaling and add the data to the fcurves
    print("Creating fcurves")
    for i, frame in enumerate(hand_data.animation_data):
        palm_size = (frame.world_positions[HandJoint.INDEX_1.value] -
                     frame.world_positions[HandJoint.WRIST.value]).length
        scale_multiplier = bpy.context.scene.hand_align_data.palm_size / palm_size
        frame_time = frame.timestamp * bpy.context.scene.render.fps + bpy.context.scene.frame_start
        for joint in HandJoint:
            ws_loc = frame.world_positions[joint.value] * scale_multiplier
            fcurves[joint.value][0].keyframe_points.insert(frame_time, ws_loc[0], options={'FAST'})
            fcurves[joint.value][1].keyframe_points.insert(frame_time, ws_loc[1], options={'FAST'})
            fcurves[joint.value][2].keyframe_points.insert(frame_time, ws_loc[2], options={'FAST'})
        print(i / frame_count * 100, "%", sep='')

    # Select all fcurves
    for curve_tuple in fcurves:
        for curve in curve_tuple:
            curve.update()
            curve.select = True

    # Filter the data (done on selected fcurves)
    print("Filtering data")
    filter_settings: HandAlignData = bpy.context.scene.hand_align_data
    bpy.ops.graph.select_all(action='SELECT')
    bpy.ops.graph.butterworth_smooth(
        cutoff_frequency=filter_settings.cutoff_frequency,
        filter_order=filter_settings.filter_order,
        samples_per_frame=filter_settings.samples_per_frame)

    # Return the area type to the original value
    bpy.context.area.type = original_area_type

    # Convert the fcurves to a list of vectors
    print("Converting fcurves to vectors")
    keyframe_points = [[0] * 2 * frame_count for _ in range(3)]
    anim_data = [[None] * frame_count for _ in HandJoint]
    for joint in HandJoint:
        curves = fcurves[joint.value]
        curves[0].keyframe_points.foreach_get("co", keyframe_points[0])
        curves[1].keyframe_points.foreach_get("co", keyframe_points[1])
        curves[2].keyframe_points.foreach_get("co", keyframe_points[2])
        for i in range(frame_count):
            anim_data[joint.value][i] = Vector((
                keyframe_points[0][i * 2 + 1],
                keyframe_points[1][i * 2 + 1],
                keyframe_points[2][i * 2 + 1]
            ))

    # Calculate the average joint distances
    print("Calculating average joint distances")
    avg_dists = [0 for _ in HandJoint]
    for joint in JOINTS_WITHOUT_WRIST:
        predecessor_idx = joint.predecessor().value
        idx = joint.value
        distances = map(lambda vec_pair: (vec_pair[0] - vec_pair[1]).length,
                        zip(anim_data[predecessor_idx], anim_data[idx]))
        avg_dists[idx] = sum(distances) / frame_count

    # Delete the action
    bpy.data.actions.remove(action)
    bpy.data.objects.remove(obj, do_unlink=True)

    # Return the preprocessed hand data
    preprocessed_hand_data = PreprocessedHandData(
        hand_data.name,
        'LEFT',  # TODO: handedness
        list(map(lambda frame: frame.timestamp, hand_data.animation_data)),
        anim_data,
        avg_dists)
    return preprocessed_hand_data


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

        PreprocessedData.hands = []
        for hand_data in RawData.raw_data:
            print(f"Preprocessing data for hand: {hand_data.name}")
            new_hand_data = preprocess(hand_data)
            PreprocessedData.hands.append(new_hand_data)

        return {'FINISHED'}
