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
Custom FCurve classes for easier manipulation
with location and rotation keyframes.
"""

from typing import List
import bpy
from mathutils import Vector, Quaternion


def flat_zip(a, b):
    """
    Zip two iterables and flatten the result.
    Example: flat_zip([1, 2, 3], [4, 5, 6]) -> [1, 4, 2, 5, 3, 6]
    """
    return [item for pair in zip(a, b) for item in pair]


class LocationFCurves:
    """
    Stores the fcurves for the location of a single joint.
    """

    def __init__(self, action: bpy.types.Action, data_path: str, action_group: str):
        self.x = action.fcurves.new(
            data_path=data_path,
            index=0,
            action_group=action_group
        )
        self.y = action.fcurves.new(
            data_path=data_path,
            index=1,
            action_group=action_group
        )
        self.z = action.fcurves.new(
            data_path=data_path,
            index=2,
            action_group=action_group
        )
        for curve in self:
            curve.color_mode = 'AUTO_RGB'

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __getitem__(self, key):
        return (self.x, self.y, self.z)[key]

    def __setitem__(self, key, value):
        (self.x, self.y, self.z)[key] = value

    def set_keyframes(self, timestamps: List[float], locations: List[Vector]):
        """
        Set keyframes for the rotation of the joint.
        timestamps: List of timestamps of the keyframes.
        rotations: List rotations of the joint.
        """
        if locations is None:
            return
        for i in range(3):  # x, y, z
            self[i].keyframe_points.clear()
            self[i].keyframe_points.add(count=len(timestamps))
            self[i].keyframe_points.foreach_set(
                "co",
                flat_zip(
                    timestamps,
                    [loc[i] for loc in locations]
                )
            )
            self[i].update()


class RotationFCurves:
    """
    Stores the fcurves for the rotation of a single joint.
    """

    def __init__(self, action: bpy.types.Action, data_path: str, action_group: str):
        self.w = action.fcurves.new(
            data_path=data_path,
            index=0,
            action_group=action_group
        )
        self.x = action.fcurves.new(
            data_path=data_path,
            index=1,
            action_group=action_group
        )
        self.y = action.fcurves.new(
            data_path=data_path,
            index=2,
            action_group=action_group
        )
        self.z = action.fcurves.new(
            data_path=data_path,
            index=3,
            action_group=action_group
        )
        for curve in self:
            curve.color_mode = 'AUTO_YRGB'

    def __iter__(self):
        return iter((self.w, self.x, self.y, self.z))

    def __getitem__(self, key):
        return (self.w, self.x, self.y, self.z)[key]

    def __setitem__(self, key, value):
        (self.w, self.x, self.y, self.z)[key] = value

    def set_keyframes(self, timestamps: List[float], rotations: List[Quaternion]):
        """
        Set keyframes for the rotation of the joint.
        timestamps: List of timestamps of the keyframes.
        rotations: List rotations of the joint.
        """
        if rotations is None:
            return
        for i in range(4):  # w, x, y, z
            self[i].keyframe_points.clear()
            self[i].keyframe_points.add(count=len(timestamps))
            self[i].keyframe_points.foreach_set(
                "co",
                flat_zip(
                    timestamps,
                    [rot[i] for rot in rotations]
                )
            )
            self[i].update()


class JointFCurves:
    """
    Stores the fcurves for the location and rotatio of one joint.
    """

    def __init__(self, action: bpy.types.Action, data_path: str, action_group: str):
        """
        Initialize the fcurves for the location and rotation of one joint.
        Data path points only to the object, '.location' and '.rotation_quaternion' are appended automatically.
        """
        self.location = LocationFCurves(action, data_path + ".location", action_group)
        self.rotation = RotationFCurves(action, data_path + ".rotation_quaternion", action_group)

    def set_keyframes(self, timestamps: List[float], locations: List[Vector], rotations: List[Quaternion]):
        """
        Set keyframes for the location and rotation of the joint.
        timestamps: List of timestamps of the keyframes.
        locations: List locations of the joint.
        rotations: List rotations of the joint.
        """
        self.location.set_keyframes(timestamps, locations)
        self.rotation.set_keyframes(timestamps, rotations)
