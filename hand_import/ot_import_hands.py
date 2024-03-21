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

"""Contains import hand opertator used to import hand animation data from a json file."""

from typing import Dict, List, Tuple
import bpy
import marshmallow
from mathutils import Quaternion, Vector, Matrix

from .hand_types import HandAnimationData, HandFrame
from .hand_joint import HandJoint


def spawn_hand_empty(hand_name: str, location: Tuple[float, float, float] = (0, 0, 0)) \
        -> List[bpy.types.Object]:
    """Spawns a list of empty objects representing the hand joints."""
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
    joints[HandJoint.WRIST.value].name = hand_name
    return joints


# List of fcurves for each joint
# FCurvesList[JOINT_INDEX]['LOC'|'ROT'][0|1|2|3]
FCurvesList = List[Dict[str, List[bpy.types.FCurve]]]


def create_animation_data(hand_name: str, joint_empty_list: List[bpy.types.Object]) -> FCurvesList:
    """Creates empty animation data for the given joint empty list and returns the fcurves for each joint."""
    fcurves = []
    for joint_empty in joint_empty_list:
        joint_empty.rotation_mode = 'QUATERNION'
        joint_empty.animation_data_create()
        action = bpy.data.actions.new(name=hand_name + " " + joint_empty.name)
        joint_empty.animation_data.action = action
        curves = {
            'LOC': [
                action.fcurves.new(data_path='location', index=0, action_group=joint_empty.name),
                action.fcurves.new(data_path='location', index=1, action_group=joint_empty.name),
                action.fcurves.new(data_path='location', index=2, action_group=joint_empty.name)
            ],
            'ROT': [
                action.fcurves.new(data_path='rotation_quaternion', index=0, action_group=joint_empty.name),
                action.fcurves.new(data_path='rotation_quaternion', index=1, action_group=joint_empty.name),
                action.fcurves.new(data_path='rotation_quaternion', index=2, action_group=joint_empty.name),
                action.fcurves.new(data_path='rotation_quaternion', index=3, action_group=joint_empty.name)
            ]
        }
        for curve in curves['LOC']:
            curve.color_mode = 'AUTO_RGB'
        for curve in curves['ROT']:
            curve.color_mode = 'AUTO_YRGB'

        fcurves.append(curves)
    return fcurves


def compute_hand_rotation(data: HandFrame) -> Quaternion:
    """Computes the rotation of the hand based on the given frame data."""
    to_index = data.world_positions[HandJoint.INDEX_1.value] - data.world_positions[HandJoint.WRIST.value]
    to_pinky = data.world_positions[HandJoint.PINKY_1.value] - data.world_positions[HandJoint.WRIST.value]
    x_axis = Vector.cross(to_index, to_pinky).normalized()

    to_middle = (to_index + to_pinky) / 2
    z_axis = Vector.cross(to_middle, x_axis).normalized()

    y_axis = Vector.cross(z_axis, x_axis).normalized()

    mat = Matrix((x_axis, y_axis, z_axis)).transposed()
    return mat.to_quaternion()


def insert_keyframe(fcurves: FCurvesList, data: HandFrame):
    """Inserts a keyframe for the given frame data into the fcurves."""
    frame_time = data.timestamp * bpy.context.scene.render.fps + bpy.context.scene.frame_start

    wrist_rot = compute_hand_rotation(data)
    ws_rot = [wrist_rot]

    # Insert local rotation keyframe for the wrist joint
    # fcurves[0]['ROT'][0].keyframe_points.insert(frame_time, wrist_rot.w)
    # fcurves[0]['ROT'][1].keyframe_points.insert(frame_time, wrist_rot.x)
    # fcurves[0]['ROT'][2].keyframe_points.insert(frame_time, wrist_rot.y)
    # fcurves[0]['ROT'][3].keyframe_points.insert(frame_time, wrist_rot.z)

    for i in range(1, len(fcurves)):  # Skip the wrist joint
        predecessor = HandJoint(i).predecessor()
        assert predecessor is not None

        predecessor_ws_pos = data.world_positions[predecessor.value]
        predecessor_ws_rot = ws_rot[predecessor.value]

        joint_loc_rot = Quaternion()  # use identity quaternion for now
        joint_ws_rot = ws_rot[predecessor.value] @ joint_loc_rot
        ws_rot.append(joint_ws_rot)

        joint_ws_pos = data.world_positions[i]
        joint_loc_offset = joint_ws_pos - predecessor_ws_pos
        joint_loc_pos = predecessor_ws_rot.inverted() @ joint_loc_offset

        # Insert local position keyframe
        fcurves[i]['LOC'][0].keyframe_points.insert(frame_time, joint_loc_pos.x)
        fcurves[i]['LOC'][1].keyframe_points.insert(frame_time, joint_loc_pos.y)
        fcurves[i]['LOC'][2].keyframe_points.insert(frame_time, joint_loc_pos.z)

        # Insert local rotation keyframe
        fcurves[i]['ROT'][0].keyframe_points.insert(frame_time, joint_loc_rot.w)
        fcurves[i]['ROT'][1].keyframe_points.insert(frame_time, joint_loc_rot.x)
        fcurves[i]['ROT'][2].keyframe_points.insert(frame_time, joint_loc_rot.y)
        fcurves[i]['ROT'][3].keyframe_points.insert(frame_time, joint_loc_rot.z)


def animate_hand(hand_data: HandAnimationData, joint_empty_list: List[bpy.types.Object]):
    """Animates the hand joints based on the given hand data."""
    fcurves = create_animation_data(hand_data.name, joint_empty_list)
    for frame in hand_data.animation_data:
        insert_keyframe(fcurves, frame)


def generate_hand(hand_data: HandAnimationData, location: Tuple[float, float, float] = (0, 0, 0)):
    """Generates an animated hand based on the given hand data."""
    joint_empty_list = spawn_hand_empty(hand_data.name, location)
    animate_hand(hand_data, joint_empty_list)


class MIC_OT_ImportHands(bpy.types.Operator):
    """Operator for importing hand animation data from a json file."""
    bl_idname = "mesh.import_hands"
    bl_label = "Import Hands"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")  # type: ignore # noqa

    def execute(self, context: bpy.types.Context) -> set[str]:
        print("----------------- Executing Import Hands -----------------")
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                print("Reading file...")
                json_string = file.read()
                print("Loading data...")
                data: List[HandAnimationData] = HandAnimationData.schema().loads(  # type: ignore
                    json_string,
                    many=True)
        except marshmallow.exceptions.ValidationError:
            self.report({'ERROR'}, "The selected file is not in the correct format.")
            return {'CANCELLED'}

        i = 0
        for hand_data in data:
            print(f"Generating hand {hand_data.name}...")
            generate_hand(hand_data, (i/4, 0, 0))
            i += 1

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
