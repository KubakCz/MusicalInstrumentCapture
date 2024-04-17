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

"""Functions for generating and aligning armatures from preprocessed hand data."""

import bpy
from typing import List
from mathutils import Vector

from .hand_processing import process_hand
from .hand_joint import HandJoint
from .hand_type import HandType
from .hand_preprocessing import PreprocessedHand
from .fcurves import JointFCurves


def _generate_bones(
        hand: PreprocessedHand,
        armature: bpy.types.Object,
        target_bone: str) -> List[bpy.types.PoseBone]:
    """
    Generate bones for the given hand and add them to the given armature.
    :param hand: Preprocessed hand data.
    :param armature: Armature object to which the bones should be added.
    :param target_bone: Name of the wrist bone in the armature to which the hand should be aligned.
    :return: List of generated pose bones.
    """
    # Enter edit mode
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature.data.edit_bones
    assert isinstance(edit_bones, bpy.types.bpy_prop_collection)

    # Scale the wrist bone to match the palm size
    wrist_bone = edit_bones[target_bone]
    assert isinstance(wrist_bone, bpy.types.EditBone)
    wrist_bone.length = hand.average_joint_distance[HandJoint.MIDDLE_1.value]

    # Generate bones for the hand
    hand_edit_bones = [wrist_bone]
    tail_offset_multiplier = 1.0 if hand.hand_type == HandType.LEFT else -1.0
    for joint in HandJoint:
        if joint == HandJoint.WRIST:
            continue

        # Create a new bone for each joint
        bone = edit_bones.new(hand.name + "_" + str(joint))

        # Assign the parent to the bone
        parent_joint = joint.predecessor()
        assert parent_joint is not None
        if parent_joint is HandJoint.WRIST:
            bone.parent = wrist_bone
        else:
            bone.parent = hand_edit_bones[parent_joint.value]

        bone.head = bone.parent.head + Vector((0, 0, 0))
        bone.tail = bone.head
        if (joint.is_tip()):
            bone.tail += Vector((tail_offset_multiplier * 0.01, 0, 0))
        else:
            bone.tail += Vector((tail_offset_multiplier *
                                hand.average_joint_distance[joint.successors()[0].value], 0, 0))

        hand_edit_bones.append(bone)

    bone_names = [bone.name for bone in hand_edit_bones]

    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    return [armature.pose.bones[name] for name in bone_names]


def _create_animation_data(
        hand: PreprocessedHand,
        armature_object: bpy.types.Object,
        bones: List[bpy.types.PoseBone]) -> List[JointFCurves | None]:
    """
    Create animation data for the given hand and bones.
    :param hand: Preprocessed hand data.
    :param bones: List of bones in the armature corresponding to the hand.
    """
    if len(bones) != len(HandJoint):
        raise ValueError(
            f"Wrong number of bones in the list (has {len(bones)}, expected {len(HandJoint)}).")

    # Create or get animation action
    if armature_object.animation_data is None:
        armature_object.animation_data_create()
    if armature_object.animation_data.action is None:
        action = bpy.data.actions.new(name=hand.name)
        armature_object.animation_data.action = action
    else:
        action = armature_object.animation_data.action

    # Create fcurves for each bone
    fcurves: List[JointFCurves | None] = [None]  # None for wrist (uses animation from the armature)
    for bone_idx in range(1, len(bones)):
        bone = bones[bone_idx]
        bone.rotation_mode = 'QUATERNION'
        fcurves.append(
            JointFCurves(action, f'pose.bones["{bone.name}"]', bone.name)
        )

    return fcurves


def add_hand_to_armature(
        hand: PreprocessedHand,
        armature_object: bpy.types.Object,
        target_bone: str,
        scene_fps: float,
        start_frame: float) -> None:
    """
    Convert the preprocessed hand data to hand armature connected to the target bone and animate it.
    :param hand: Preprocessed hand data.
    :param armature_object: Armature object to which the hand should be added.
    :param target_bone: Name of the wrist bone in the armature to which the hand should be aligned.
    :param scene_fps: Frames per second of the scene.
    :param start_frame: Frame at which the animation should start.
    """
    bones = _generate_bones(hand, armature_object, target_bone)
    joint_fcurves = _create_animation_data(hand, armature_object, bones)
    joint_animation_data = process_hand(hand)
    timestamps = [frame.timestamp * scene_fps + start_frame for frame in hand.frames]
    for joint_fcurve, joint_data in zip(joint_fcurves, joint_animation_data):
        if joint_fcurve is not None:
            joint_fcurve.set_keyframes(
                timestamps,
                joint_data[0],
                joint_data[1]
            )
