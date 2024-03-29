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

"""Operator for transforming preprocessed data into armature with animation."""

from typing import List, Optional, Tuple
import bpy
from mathutils import Vector, Matrix
from .hand_joint import HandJoint
from .hand_types import HandFrame
from .import_hands_data import PreprocessedHandData
from .ot_preprocess_data import PreprocessedData


def spawn_hand_armature(hand_data: PreprocessedHandData, location: Vector) -> bpy.types.Object:
    """Spawns an armature representing the hand joints."""
    # Create a new armature object
    bpy.ops.object.armature_add(location=location)
    armature = bpy.context.object
    armature.name = hand_data.data.name

    # Enter edit mode to add bones
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    # Remove the default bone
    armature.data.edit_bones.remove(armature.data.edit_bones[0])

    edit_bones = armature.data.edit_bones
    for joint in HandJoint:
        # Create a new bone for each joint
        bone = edit_bones.new(str(joint))
        bone.head = (0, 0, 0)
        if (joint == HandJoint.WRIST):
            bone.tail = (0, bpy.context.scene.hand_align_data.palm_size, 0)
        elif (joint.is_tip()):
            bone.tail = (0, 0.01, 0)
        else:
            bone.tail = (0, hand_data.average_joint_distance[joint.successors()[0].value], 0)

        # Assign the parent to the bone
        parent = joint.predecessor()
        if parent is not None:
            bone.parent = edit_bones[str(parent)]

    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    return armature


LocFCurves = List[Tuple[bpy.types.FCurve, bpy.types.FCurve, bpy.types.FCurve]]
RotFCurves = List[Tuple[bpy.types.FCurve, bpy.types.FCurve, bpy.types.FCurve, bpy.types.FCurve]]
FCurves = Tuple[LocFCurves, RotFCurves]


def create_animation_data(hand_name: str, armature: bpy.types.Object) -> FCurves:
    """
    Creates empty animation data for the given armature
    and returns location and rotation fcurves for each bone.
    """
    loc_fcurves = []
    rot_fcurves = []

    # Create one action for the whole armature
    action = bpy.data.actions.new(name=hand_name)
    armature.animation_data_create()
    armature.animation_data.action = action

    # Create fcurves for each bone
    for bone in armature.pose.bones:
        loc = tuple(
            action.fcurves.new(
                data_path=f'pose.bones["{bone.name}"].location',
                index=i,
                action_group=bone.name) for i in range(3)
        )
        for curve in loc:
            curve.color_mode = 'AUTO_RGB'
        loc_fcurves.append(loc)

        bone.rotation_mode = 'QUATERNION'
        rot = tuple(
            action.fcurves.new(
                data_path=f'pose.bones["{bone.name}"].rotation_quaternion',
                index=i,
                action_group=bone.name) for i in range(4)
        )
        for curve in rot:
            curve.color_mode = 'AUTO_YRGB'
        rot_fcurves.append(rot)
    return loc_fcurves, rot_fcurves


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


def insert_keyframe(frame_data: HandFrame, average_joint_distances: List[float], fcurves: FCurves):
    """
    Inserts a keyframe for the given frame data into the fcurves.
    The average_joint_distances are used to scale the joint positions.
    If average_joint_distances is None, the joint positions are not scaled.
    """
    loc_fcurves, rot_fcurves = fcurves

    # Inverse rotations from local to world space
    ws_irots: List[Optional[Matrix]] = [None for _ in HandJoint]

    # Compute rotation of the hand in ws (this rotation is removed, so the hand points always in the same direction)
    wrist_loc_ws = frame_data.world_positions[HandJoint.WRIST.value]
    wrist_rot_ws = get_hand_rotation_matrix(frame_data, 'LEFT')  # TODO: handedness should be a parameter
    wrist_z_ws = wrist_rot_ws.col[2]  # palm direction
    ws_irots[0] = wrist_rot_ws.transposed()

    frame_time = frame_data.timestamp * bpy.context.scene.render.fps + bpy.context.scene.frame_start

    # Compute loc position and rotation for the 1st joint of each finger
    for joint in HandJoint.get_first_finger_joints():
        assert isinstance(joint, HandJoint)

        # Loc position
        to_joint = frame_data.world_positions[joint.value] - wrist_loc_ws
        if average_joint_distances is not None:
            to_joint = to_joint.normalized() * average_joint_distances[joint.value]
        location = ws_irots[0] @ to_joint

        curves = loc_fcurves[joint.value]
        curves[0].keyframe_points.insert(frame_time, location.x, options={'FAST'})
        curves[1].keyframe_points.insert(frame_time, location.y, options={'FAST'})
        curves[2].keyframe_points.insert(frame_time, location.z, options={'FAST'})

        # Loc rotation
        successor = joint.successors()[0]
        successor_loc_ws = frame_data.world_positions[successor.value]
        to_successor = successor_loc_ws - frame_data.world_positions[joint.value]
        y_axis_ws = to_successor.normalized()                 # from the joint to the successor
        x_axis_ws = y_axis_ws.cross(wrist_z_ws).normalized()  # perpendicular to the y-axis and palm direction
        z_axis_ws = x_axis_ws.cross(y_axis_ws).normalized()
        ws_irot = Matrix((x_axis_ws, y_axis_ws, z_axis_ws))   # rot from local to world space
        ws_irots[joint.value] = ws_irot
        ws_rot = ws_irot.transposed()                         # rot from world to local space
        loc_rot = (ws_irots[0] @ ws_rot).to_quaternion()

        curves = rot_fcurves[joint.value]
        curves[0].keyframe_points.insert(frame_time, loc_rot.w, options={'FAST'})
        curves[1].keyframe_points.insert(frame_time, loc_rot.x, options={'FAST'})
        curves[2].keyframe_points.insert(frame_time, loc_rot.y, options={'FAST'})
        curves[3].keyframe_points.insert(frame_time, loc_rot.z, options={'FAST'})

    for joint in HandJoint.get_second_and_third_finger_joints():
        predecessor = joint.predecessor()
        successor = joint.successors()[0]  # all joints have only one successor

        # Define finger plane
        to_predecessor = frame_data.world_positions[predecessor.value] - frame_data.world_positions[joint.value]
        to_successor = frame_data.world_positions[successor.value] - frame_data.world_positions[joint.value]
        finger_plane_normal = to_predecessor.cross(to_successor).normalized()

        # Loc position
        to_joint = -to_predecessor
        if average_joint_distances is not None:
            to_joint = to_joint.normalized() * average_joint_distances[joint.value]
        location = ws_irots[predecessor.value] @ to_joint
        curves = loc_fcurves[joint.value]
        curves[0].keyframe_points.insert(frame_time, location.x, options={'FAST'})
        curves[1].keyframe_points.insert(frame_time, location.y, options={'FAST'})
        curves[2].keyframe_points.insert(frame_time, location.z, options={'FAST'})

        # Loc rotation
        x_axis_ws = finger_plane_normal
        y_axis_ws = to_successor.normalized()
        z_axis_ws = x_axis_ws.cross(y_axis_ws).normalized()
        ws_irot = Matrix((x_axis_ws, y_axis_ws, z_axis_ws))   # rot from local to world space
        ws_irots[joint.value] = ws_irot
        ws_rot = ws_irot.transposed()                         # rot from world to local space
        loc_rot = (ws_irots[predecessor.value] @ ws_rot).to_quaternion()

        curves = rot_fcurves[joint.value]
        curves[0].keyframe_points.insert(frame_time, loc_rot.w, options={'FAST'})
        curves[1].keyframe_points.insert(frame_time, loc_rot.x, options={'FAST'})
        curves[2].keyframe_points.insert(frame_time, loc_rot.y, options={'FAST'})
        curves[3].keyframe_points.insert(frame_time, loc_rot.z, options={'FAST'})

    for joint in HandJoint.get_tips():
        predecessor = joint.predecessor()

        # Loc position
        to_joint = frame_data.world_positions[joint.value] - frame_data.world_positions[predecessor.value]
        if average_joint_distances is not None:
            to_joint = to_joint.normalized() * average_joint_distances[joint.value]
        location = ws_irots[predecessor.value] @ to_joint

        curves = loc_fcurves[joint.value]
        curves[0].keyframe_points.insert(frame_time, location.x, options={'FAST'})
        curves[1].keyframe_points.insert(frame_time, location.y, options={'FAST'})
        curves[2].keyframe_points.insert(frame_time, location.z, options={'FAST'})

        # Loc rotation
        curves = rot_fcurves[joint.value]
        curves[0].keyframe_points.insert(frame_time, 1, options={'FAST'})
        curves[1].keyframe_points.insert(frame_time, 0, options={'FAST'})
        curves[2].keyframe_points.insert(frame_time, 0, options={'FAST'})
        curves[3].keyframe_points.insert(frame_time, 0, options={'FAST'})


def generate_hand(hand_data: PreprocessedHandData, use_avg_distance: bool, location: Vector) -> bpy.types.Object:
    """Generates an animated hand based on the given hand data."""
    hand_armature = spawn_hand_armature(hand_data, location)
    fcurves = create_animation_data(hand_data.data.name, hand_armature)
    last_timestamp = hand_data.data.animation_data[-1].timestamp
    avg_distances = hand_data.average_joint_distance if use_avg_distance else None
    for frame in hand_data.data.animation_data:
        insert_keyframe(frame, avg_distances, fcurves)
        print(frame.timestamp / last_timestamp)
    return hand_armature


class MIC_OT_GenerateArmature(bpy.types.Operator):
    """Operator for generating an armature from the hand data."""
    bl_idname = "mic.generate_armature"
    bl_label = "Generate Armature"
    bl_options = {'REGISTER'}

    def execute(self, context):
        print("--- Executing GenerateArmature ---")
        if PreprocessedData.data is None:
            self.report({'ERROR'}, "No data loaded.")
            return {'CANCELLED'}

        preprocessed_data = PreprocessedData.data
        i = 0
        for preprocessed_hand_data in preprocessed_data:
            print(f"Generating hand {preprocessed_hand_data.data.name}...")
            generate_hand(preprocessed_hand_data, context.scene.hand_align_data.use_average_joint_distance, (i/4, 0, 0))
            i += 1

        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}
