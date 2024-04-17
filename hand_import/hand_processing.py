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

"""Functions for computing local positions and locations from world space data."""

from typing import List, Tuple
from mathutils import Vector, Matrix, Quaternion


from .hand_preprocessing import PreprocessedHand
from .hand_joint import HandJoint, first_finger_joints, second_and_third_finger_joints, tip_joints
from .hand_loading import PositionList
from .hand_type import HandType


def _get_inverse_hand_rotation(
        wrist_loc: Vector,
        index_loc: Vector,
        middle_loc: Vector,
        ring_loc: Vector,
        hand_type: HandType) -> Matrix:
    """
    Calculate the invers rotation matrix for the hand based on the given world positions.
    :param world_positions: List of world positions of the hand joints.
    :param hand_type: Type of the hand (left or right).
    :return: Inverse rotation matrix (local -> world) of the hand. Axis of the hand are rows of the matrix.
    """
    to_index = index_loc - wrist_loc
    to_middle = middle_loc - wrist_loc
    to_ring = ring_loc - wrist_loc

    # y-axis is the direction from the wrist to the middle finger
    y_axis = to_middle.normalized()

    if hand_type == HandType.LEFT:
        palm_dir = to_index.cross(to_ring).normalized()
    else:
        palm_dir = to_ring.cross(to_index).normalized()

    # z-axis is the direction perpendicular to the palm direction and y-axis
    z_axis = y_axis.cross(palm_dir).normalized()
    # x-axis is -palm direction adjusted to be perpendicular to z and y axes
    x_axis = y_axis.cross(z_axis).normalized()

    return Matrix((x_axis, y_axis, z_axis))


def _process_1_joint_frame(
        joint_loc: Vector,
        wrist_loc: Vector,
        wrist_irot: Matrix,
        succ_loc: Vector,
        join_dist: float) -> Tuple[Vector, Quaternion, Matrix]:
    """
    Computes locala location, local rotation, and global inverse rotation matrix
    of the first finger joint (parented to wrist).
    :param joint_loc: World location of the joint.
    :param wrist_loc: World location of the wrist.
    :param wrist_irot: Inverse rotation matrix of the wrist.
    :param succ_loc: World location of the successor joint.
    :param join_dist: Distance of the joint from the wrist.
    :return: Tuple of local location, local rotation, and global inverse rotation matrix.
    """
    # Loc location
    to_joint = (joint_loc - wrist_loc).normalized() * join_dist
    loc_loc = wrist_irot @ to_joint
    assert isinstance(loc_loc, Vector)

    # Glob rotation
    to_succ = succ_loc - joint_loc
    up_dir_ws = wrist_irot[0]
    y_axis_ws = to_succ.normalized()                       # joint -> successor
    x_axis_ws = y_axis_ws.cross(up_dir_ws).normalized()    # perpendicular to y-axis and up direction
    z_axis_ws = x_axis_ws.cross(y_axis_ws).normalized()
    ws_irot = Matrix((x_axis_ws, y_axis_ws, z_axis_ws))    # rot from local to world space

    # Loc rotation
    ws_rot = ws_irot.transposed()                          # rot from world to local space
    loc_rot_mat = wrist_irot @ ws_rot
    assert isinstance(loc_rot_mat, Matrix)
    loc_rot = loc_rot_mat.to_quaternion()

    return loc_loc, loc_rot, ws_irot


def _process_23_joint_frame(
        joint_loc: Vector,
        pred_loc: Vector,
        pred_irot: Matrix,
        succ_loc: Vector,
        join_dist: float) -> Tuple[Vector, Quaternion, Matrix]:
    """
    Computes locala location, local rotation, and global inverse rotation matrix
    of the second or third finger joint (parented to previous joint).
    :param joint_loc: World location of the joint.
    :param pred_loc: World location of the predecessor joint.
    :param pred_irot: Inverse rotation matrix of the predecessor joint.
    :param succ_loc: World location of the successor joint.
    :param join_dist: Distance of the joint from the predecessor joint.
    :return: Tuple of local location, local rotation, and global inverse rotation matrix.
    """
    # Finger plane
    # Note that we use joint location before avg distance scaling to preserve angles
    to_joint = joint_loc - pred_loc
    to_successor = succ_loc - joint_loc
    plane_normal = to_successor.cross(to_joint).normalized()

    # Loc location
    to_joint = to_joint.normalized() * join_dist
    loc_loc = pred_irot @ to_joint
    assert isinstance(loc_loc, Vector)

    # Glob rotation
    x_axis_ws = plane_normal
    y_axis_ws = to_successor.normalized()
    z_axis_ws = x_axis_ws.cross(y_axis_ws).normalized()
    ws_irot = Matrix((x_axis_ws, y_axis_ws, z_axis_ws))  # rot from local to world space

    # Loc rotation
    ws_rot = ws_irot.transposed()  # rot from world to local space
    loc_rot_mat = pred_irot @ ws_rot
    assert isinstance(loc_rot_mat, Matrix)
    loc_rot = loc_rot_mat.to_quaternion()

    return loc_loc, loc_rot, ws_irot


def _process_tip_frame(
        joint_loc: Vector,
        pred_loc: Vector,
        pred_irot: Matrix,
        join_dist: float) -> Vector:
    """
    Computes locala location of the tip of the finger (parented to the previous joint).
    :param joint_loc: World location of the joint.
    :param pred_loc: World location of the predecessor joint.
    :param pred_irot: Inverse rotation matrix of the predecessor joint.
    :param join_dist: Distance of the joint from the predecessor joint.
    :return: Local location of the tip of the finger.
    """
    # Loc location
    to_joint = joint_loc - pred_loc
    if join_dist is not None:
        to_joint = to_joint.normalized() * join_dist
    loc_loc = pred_irot @ to_joint
    assert isinstance(loc_loc, Vector)
    return loc_loc


def _process_frame(
        world_positions: PositionList,
        hand_type: HandType,
        average_joint_distances: List[float]) -> List[Tuple[Vector, Quaternion]]:
    """
    Convert the world positions of the hand joints to local positions and rotations.
    :param world_positions: List of world positions of the hand joints.
    :param hand_type: Type of the hand (left or right).
    :param average_joint_distances: List of average distances between the joints.
    :return: Local location and rotation tuple for each joint. (result[joint][loc|rot])
    """
    # Preinitialize result lists
    results = [(Vector(), Quaternion())] * len(HandJoint)
    ws_irots: List[Matrix] = [Matrix()] * len(HandJoint)

    # Compute inverse rotation of the hand
    ws_irots[HandJoint.WRIST.value] = _get_inverse_hand_rotation(
        world_positions[HandJoint.WRIST.value],
        world_positions[HandJoint.INDEX_1.value],
        world_positions[HandJoint.MIDDLE_1.value],
        world_positions[HandJoint.RING_1.value],
        hand_type
    )

    # Process 1st finger joints
    for joint in first_finger_joints:
        successor = joint.successors()[0]
        assert isinstance(successor, HandJoint)
        loc, rot, irot = _process_1_joint_frame(
            world_positions[joint.value],
            world_positions[HandJoint.WRIST.value],
            ws_irots[HandJoint.WRIST.value],
            world_positions[successor.value],
            average_joint_distances[joint.value]
        )
        ws_irots[joint.value] = irot
        results[joint.value] = loc, rot

    # Process 2nd and 3rd finger joints
    for joint in second_and_third_finger_joints:
        predecessor = joint.predecessor()
        assert predecessor is not None
        successor = joint.successors()[0]
        assert isinstance(successor, HandJoint)
        loc, rot, irot = _process_23_joint_frame(
            world_positions[joint.value],
            world_positions[predecessor.value],
            ws_irots[predecessor.value],
            world_positions[successor.value],
            average_joint_distances[joint.value]
        )
        ws_irots[joint.value] = irot
        results[joint.value] = loc, rot

    # Process tip joints
    for joint in tip_joints:
        predecessor = joint.predecessor()
        assert predecessor is not None
        loc = _process_tip_frame(
            world_positions[joint.value],
            world_positions[predecessor.value],
            ws_irots[predecessor.value],
            average_joint_distances[joint.value]
        )
        results[joint.value] = loc, Quaternion()

    return results


def process_hand(hand: PreprocessedHand) -> List[Tuple[List[Vector], List[Quaternion]]]:
    """
    Convert the world positions of the hand joints to local positions and rotations.
    :param hand: Preprocessed hand data.
    :return: Tuple of lists with local positions and rotations of each frame for each joint.
    (result[joint][loc|rot][frame])
    """
    result: List[Tuple[List[Vector], List[Quaternion]]] = [([], []) for _ in HandJoint]
    for frame in hand.frames:
        frame_anim_data = _process_frame(frame.world_positions, hand.hand_type, hand.average_joint_distance)
        for joint_idx, (loc, rot) in enumerate(frame_anim_data):
            result[joint_idx][0].append(loc)
            result[joint_idx][1].append(rot)
    return result
