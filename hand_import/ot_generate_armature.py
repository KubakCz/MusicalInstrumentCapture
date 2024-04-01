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
from mathutils import Vector, Matrix, Quaternion

from .fcurves import JointFCurves
from .hand_joint import HandJoint
from .hand_types import HandFrame
from .import_hands_data import PreprocessedHandData, ProcessedHandData
from .ot_preprocess_data import PreprocessedData


def spawn_hand_armature(hand_data: PreprocessedHandData, location: Vector) -> bpy.types.Object:
    """Spawns an armature representing the hand joints."""
    # Create a new armature object
    bpy.ops.object.armature_add(location=location)
    armature = bpy.context.object
    armature.name = hand_data.name

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


def create_animation_data(hand_name: str, armature: bpy.types.Object) -> List[JointFCurves]:
    """
    Creates empty animation data for the given armature
    and returns location and rotation fcurves for each bone.
    """
    fcurves: List[JointFCurves] = []

    # Create one action for the whole armature
    action = bpy.data.actions.new(name=hand_name)
    armature.animation_data_create()
    armature.animation_data.action = action

    # Create fcurves for each bone
    for bone in armature.pose.bones:
        bone.rotation_mode = 'QUATERNION'
        fcurves.append(
            JointFCurves(action, f'pose.bones["{bone.name}"]', bone.name)
        )

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


def insert_keyframe(frame_data: HandFrame, average_joint_distances: List[float], fcurves):
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


def process_wrist_frame(
        wrist_loc: Vector,
        index_loc: Vector,
        middle_loc: Vector,
        ring_loc: Vector,
        is_left: bool) -> Matrix:
    """
    Returns the inverse rotation matrix of the wrist based on the given joint locations.
    Locations are in world space.
    """
    to_index = index_loc - wrist_loc
    to_middle = middle_loc - wrist_loc
    to_ring = ring_loc - wrist_loc

    # y-axis is the direction from the wrist to the middle finger
    y_axis = to_middle.normalized()

    if is_left:
        palm_dir = to_ring.cross(to_index).normalized()
    else:
        palm_dir = to_index.cross(to_ring).normalized()

    # x-axis is the direction perpendicular to the palm direction and y-axis
    x_axis = palm_dir.cross(y_axis).normalized()
    # z-axis is palm direction adjusted to be perpendicular to x and y axes
    z_axis = x_axis.cross(y_axis).normalized()

    return Matrix((x_axis, y_axis, z_axis))


def process_wrist(hand_data: PreprocessedHandData) -> List[Matrix]:
    """Returns list of wrist inverse rotation matrices for each frame."""
    is_left = hand_data.handedness == 'LEFT'
    result = [None] * len(hand_data)
    for i in range(len(hand_data)):
        result[i] = process_wrist_frame(
            hand_data.data[HandJoint.WRIST.value][i],
            hand_data.data[HandJoint.INDEX_1.value][i],
            hand_data.data[HandJoint.MIDDLE_1.value][i],
            hand_data.data[HandJoint.RING_1.value][i],
            is_left
        )
    return result


def process_1_joint_frame(
        joint_loc: Vector,
        wrist_loc: Vector,
        wrist_irot: Matrix,
        succ_loc: Vector,
        join_dist: Optional[float]) -> Tuple[Vector, Quaternion, Matrix]:
    """
    Returns locala location, local rotation, and global inverse rotation matrix
    of the first finger joint (parented to wrist).
    Inputs are in world space.
    If join_dist is not None, the joint location is scaled by this distance.
    """
    # Loc location
    to_joint = joint_loc - wrist_loc
    if join_dist is not None:
        to_joint = to_joint.normalized() * join_dist
    loc_loc = wrist_irot @ to_joint

    # Glob rotation
    to_succ = succ_loc - joint_loc
    wrist_z_ws = wrist_irot[2]  # palm direction
    y_axis_ws = to_succ.normalized()                      # joint -> successor
    x_axis_ws = y_axis_ws.cross(wrist_z_ws).normalized()  # perpendicular to y-axis and palm direction
    z_axis_ws = x_axis_ws.cross(y_axis_ws).normalized()
    ws_irot = Matrix((x_axis_ws, y_axis_ws, z_axis_ws))   # rot from local to world space

    # Loc rotation
    ws_rot = ws_irot.transposed()                         # rot from world to local space
    loc_rot = (wrist_irot @ ws_rot).to_quaternion()

    return loc_loc, loc_rot, ws_irot


def process_1_joint(joint: HandJoint, hand_data: PreprocessedHandData, wrist_irots: List[Matrix], use_avg_dist: bool) \
        -> Tuple[List[Vector], List[Quaternion], List[Matrix]]:
    """
    Returns list of local locations, local rotations, and global inverse rotation matrices
    of the first finger joint (parented to wrist).
    """
    result = ([None] * len(hand_data), [None] * len(hand_data), [None] * len(hand_data))
    joint_locs = hand_data.data[joint.value]
    wrist_locs = hand_data.data[HandJoint.WRIST.value]
    succ_locs = hand_data.data[joint.successors()[0].value]
    join_dist = hand_data.average_joint_distance[joint.value] if use_avg_dist else None
    for i in range(len(hand_data)):
        result[0][i], result[1][i], result[2][i] = process_1_joint_frame(
            joint_locs[i], wrist_locs[i], wrist_irots[i], succ_locs[i], join_dist
        )
    return result


def process_23_joint_frame(
        joint_loc: Vector,
        pred_loc: Vector,
        pred_irot: Matrix,
        succ_loc: Vector,
        join_dist: Optional[float]) -> Tuple[Vector, Quaternion, Matrix]:
    """
    Returns locala location, local rotation, and global inverse rotation matrix
    of the second or third finger joint (parented to previous joint).
    Inputs are in world space.
    If join_dist is not None, the joint location is scaled by this distance.
    """
    # Finger plane
    # Note that we use joint location before avg distance scaling to preserve angles
    to_joint = joint_loc - pred_loc
    to_successor = succ_loc - joint_loc
    plane_normal = to_successor.cross(to_joint).normalized()

    # Loc location
    if join_dist is not None:
        to_joint = to_joint.normalized() * join_dist
    loc_loc = pred_irot @ to_joint

    # Glob rotation
    x_axis_ws = plane_normal
    y_axis_ws = to_successor.normalized()
    z_axis_ws = x_axis_ws.cross(y_axis_ws).normalized()
    ws_irot = Matrix((x_axis_ws, y_axis_ws, z_axis_ws))  # rot from local to world space

    # Loc rotation
    ws_rot = ws_irot.transposed()  # rot from world to local space
    loc_rot = (pred_irot @ ws_rot).to_quaternion()

    return loc_loc, loc_rot, ws_irot


def process_23_joint(joint: HandJoint, hand_data: PreprocessedHandData, pred_irots: List[Matrix], use_avg_dist: bool) \
        -> Tuple[List[Vector], List[Quaternion], List[Matrix]]:
    """
    Returns list of local locations, local rotations, and global inverse rotation matrices
    of the second or third finger joint (parented to previous joint).
    """
    result = ([None] * len(hand_data), [None] * len(hand_data), [None] * len(hand_data))
    joint_locs = hand_data.data[joint.value]
    pred_locs = hand_data.data[joint.predecessor().value]
    succ_locs = hand_data.data[joint.successors()[0].value]
    join_dist = hand_data.average_joint_distance[joint.value] if use_avg_dist else None
    for i in range(len(hand_data)):
        result[0][i], result[1][i], result[2][i] = process_23_joint_frame(
            joint_locs[i], pred_locs[i], pred_irots[i], succ_locs[i], join_dist
        )
    return result


def process_tip_frame(
        joint_loc: Vector,
        pred_loc: Vector,
        pred_irot: Matrix,
        join_dist: Optional[float]) -> Vector:
    """
    Returns locala location of the tip of the finger (parented to the previous joint).
    Inputs are in world space.
    If join_dist is not None, the joint location is scaled by this distance.
    """
    # Loc location
    to_joint = joint_loc - pred_loc
    if join_dist is not None:
        to_joint = to_joint.normalized() * join_dist
    return pred_irot @ to_joint


def process_tip(joint: HandJoint, hand_data: PreprocessedHandData, pred_irots: List[Matrix], use_avg_dist: bool) \
        -> List[Vector]:
    """
    Returns list of local locations of the tip of the finger (parented to the previous joint).
    """
    result = [None] * len(hand_data)
    joint_locs = hand_data.data[joint.value]
    pred_locs = hand_data.data[joint.predecessor().value]
    join_dist = hand_data.average_joint_distance[joint.value] if use_avg_dist else None
    for i in range(len(hand_data)):
        result[i] = process_tip_frame(
            joint_locs[i], pred_locs[i], pred_irots[i], join_dist
        )
    return result


def get_local_anim_data(hand_data: PreprocessedHandData, use_avg_distance: bool) -> ProcessedHandData:
    """
    Process worldspace hand data into local locations and rotations.
    """
    # list[joint][frame]
    loc_locations: List[Optional[List[Vector]]] = [None] * len(HandJoint)
    loc_rotations: List[Optional[List[Matrix]]] = [None] * len(HandJoint)
    ws_irots: List[Optional[List[Matrix]]] = [None] * len(hand_data)

    # Process wrist
    ws_irots[HandJoint.WRIST.value] = process_wrist(hand_data)

    # Process 1st finger joints
    for joint in HandJoint.get_first_finger_joints():
        loc_locations[joint.value], loc_rotations[joint.value], ws_irots[joint.value] = process_1_joint(
            joint, hand_data, ws_irots[HandJoint.WRIST.value], use_avg_distance
        )

    # Process 2nd and 3rd finger joints
    for joint in HandJoint.get_second_and_third_finger_joints():
        loc_locations[joint.value], loc_rotations[joint.value], ws_irots[joint.value] = process_23_joint(
            joint, hand_data, ws_irots[joint.predecessor().value], use_avg_distance
        )

    # Process tips
    for joint in HandJoint.get_tips():
        loc_locations[joint.value] = process_tip(
            joint, hand_data, ws_irots[joint.predecessor().value], use_avg_distance
        )

    frame_numbers = list(map(lambda timestamp: timestamp * bpy.context.scene.render.fps +
                         bpy.context.scene.frame_start, hand_data.timestamps))

    return ProcessedHandData(frame_numbers, loc_locations, loc_rotations)


def aply_local_anim_data(fcurves: List[JointFCurves], anim_data: ProcessedHandData):
    """Applies the local animation data to the fcurves."""
    for joint in HandJoint:
        fcurves[joint.value].set_keyframes(
            anim_data.frame_numbers,
            anim_data.local_locations[joint.value],
            anim_data.local_rotations[joint.value]
        )


def generate_hand(hand_data: PreprocessedHandData, use_avg_distance: bool, location: Vector) -> bpy.types.Object:
    """Generates an animated hand armature based on the given hand data."""
    hand_armature = spawn_hand_armature(hand_data, location)
    fcurves = create_animation_data(hand_data.name, hand_armature)
    anim_data = get_local_anim_data(hand_data, use_avg_distance)
    aply_local_anim_data(fcurves, anim_data)
    return hand_armature


class MIC_OT_GenerateArmature(bpy.types.Operator):
    """Operator for generating an armature from the hand data."""
    bl_idname = "mic.generate_armature"
    bl_label = "Generate Armature"
    bl_options = {'REGISTER'}

    def execute(self, context):
        print("--- Executing GenerateArmature ---")
        if PreprocessedData.hands is None:
            self.report({'ERROR'}, "No data loaded.")
            return {'CANCELLED'}

        preprocessed_data = PreprocessedData.hands
        i = 0
        for preprocessed_hand_data in preprocessed_data:
            print(f"Generating hand {preprocessed_hand_data.name}...")
            generate_hand(preprocessed_hand_data, context.scene.hand_align_data.use_average_joint_distance, (i/4, 0, 0))
            i += 1

        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}
