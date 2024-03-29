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

"""Operator for transforming preprocessed data into emptys with animated locations."""

import bpy
from typing import List, Tuple
from mathutils import Vector, Matrix
from .hand_types import HandFrame
from .hand_joint import HandJoint
from .import_hands_data import PreprocessedData, PreprocessedHandData


def spawn_hand_empty(hand_data: PreprocessedHandData, location: Vector) -> List[bpy.types.Object]:
    """Spawns a list of empty objects representing the hand joints at the given location."""
    joints: List[bpy.types.Object] = []
    for joint in HandJoint:
        # Create an empty object for each joint
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', radius=0.01)
        empty = bpy.context.object

        # Assign the parent to the empty object
        parent = joint.predecessor()
        if parent is not None:
            empty.parent = joints[parent.value]

        # Rename the empty object to the joint name and add it to the list
        empty.name = joint.name
        joints.append(empty)

    # Move the wrist empty to the hand location and rename it to the hand name
    joints[HandJoint.WRIST.value].location = location
    joints[HandJoint.WRIST.value].name = hand_data.data.name
    return joints


LocFCurves = List[Tuple[bpy.types.FCurve, bpy.types.FCurve, bpy.types.FCurve]]


def create_animation_data(hand_name: str, joint_empty_list: List[bpy.types.Object]) -> List[LocFCurves]:
    """
    Creates empty animation data for the given list of emptys.
    Returns location fcurves for each empty.
    """
    fcurves = []
    for empty in joint_empty_list:
        empty.animation_data_create()
        action = bpy.data.actions.new(name=f"{hand_name}_{empty.name}")  # Each empty has its own action
        empty.animation_data.action = action
        loc = tuple(
            action.fcurves.new(
                data_path='location',
                index=i,
                action_group=empty.name) for i in range(3)
        )
        for curve in loc:
            curve.color_mode = 'AUTO_RGB'
        fcurves.append(loc)
    return fcurves


def get_hand_rotation_matrix(data: HandFrame, handedness) -> Matrix:
    """Computes the rotation of the wrist based on the given frame data."""
    to_index = data.world_positions[HandJoint.INDEX_1.value] - data.world_positions[HandJoint.WRIST.value]
    to_middle = data.world_positions[HandJoint.MIDDLE_1.value] - data.world_positions[HandJoint.WRIST.value]
    to_ring = data.world_positions[HandJoint.RING_1.value] - data.world_positions[HandJoint.WRIST.value]

    y_axis = to_middle.normalized()  # y-axis is the direction from the wrist to the middle finger

    if handedness == 'LEFT':
        palm_dir = to_ring.cross(to_index).normalized()
    else:
        palm_dir = to_index.cross(to_ring).normalized()

    # x-axis is the direction perpendicular to the palm direction and y-axis
    x_axis = palm_dir.cross(y_axis).normalized()
    # z-axis is palm direction adjusted to be perpendicular to x and y axes
    z_axis = x_axis.cross(y_axis).normalized()

    mat = Matrix((x_axis, y_axis, z_axis)).transposed()
    return mat


HAND_JOINTS_WITHOUT_WRIST = set(HandJoint) - {HandJoint.WRIST}


def insert_keyframe(frame_data: HandFrame, fcurves: List[LocFCurves]):
    """Inserts a keyframe for the given frame into the fcurves."""
    # Compute rotation of the hand in ws (this rotation is removed, so the hand points always in the same direction)
    wrist_rot_ws = get_hand_rotation_matrix(frame_data, 'LEFT')  # TODO: handedness should be a parameter
    wrist_irot = wrist_rot_ws.transposed()

    frame_time = frame_data.timestamp * bpy.context.scene.render.fps + bpy.context.scene.frame_start

    for joint in HAND_JOINTS_WITHOUT_WRIST:
        predecessor = joint.predecessor()
        joint_offset = frame_data.world_positions[joint.value] - frame_data.world_positions[predecessor.value]
        # Rotate the joint offset to the wrist space (other emptys do not have rotation)
        location = wrist_irot @ joint_offset

        curves = fcurves[joint.value]
        curves[0].keyframe_points.insert(frame_time, location.x, options={'FAST'})
        curves[1].keyframe_points.insert(frame_time, location.y, options={'FAST'})
        curves[2].keyframe_points.insert(frame_time, location.z, options={'FAST'})


def generate_hand(hand_data: PreprocessedHandData, location: Vector) -> List[bpy.types.Object]:
    joint_empty_list = spawn_hand_empty(hand_data, location)
    fcurves = create_animation_data(hand_data.data.name, joint_empty_list)
    last_timestamp = hand_data.data.animation_data[-1].timestamp
    for frame in hand_data.data.animation_data:
        insert_keyframe(frame, fcurves)
        print(frame.timestamp / last_timestamp)
    return joint_empty_list


class MIC_OT_GenerateEmpty(bpy.types.Operator):
    """Imports hand animation data from selected json file generated by Hand Capture."""
    bl_idname = "mic.generate_empty"
    bl_label = "Generate Empty"
    bl_options = {'REGISTER'}

    def execute(self, context):
        print("--- Executing GenerateEmpty ---")
        if PreprocessedData.data is None:
            self.report({'ERROR'}, "No data loaded.")
            return {'CANCELLED'}

        preprocessed_data = PreprocessedData.data
        i = 0
        for preprocessed_hand_data in preprocessed_data:
            print(f"Generating hand {preprocessed_hand_data.data.name}...")
            generate_hand(preprocessed_hand_data, (i/4, 0, 0))
            i += 1

        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}
