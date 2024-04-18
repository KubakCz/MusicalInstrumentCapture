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

"""HandJoint enum for indexing of joints and methods for working with this enum."""

from enum import Enum
from typing import List, Optional


class HandJoint(Enum):
    """
    Enum representing the joints of the hand.
    Used to index the hand pose data.
    """
    WRIST = 0
    THUMB_1 = 1
    THUMB_2 = 2
    THUMB_3 = 3
    THUMB_TIP = 4
    INDEX_1 = 5
    INDEX_2 = 6
    INDEX_3 = 7
    INDEX_TIP = 8
    MIDDLE_1 = 9
    MIDDLE_2 = 10
    MIDDLE_3 = 11
    MIDDLE_TIP = 12
    RING_1 = 13
    RING_2 = 14
    RING_3 = 15
    RING_TIP = 16
    PINKY_1 = 17
    PINKY_2 = 18
    PINKY_3 = 19
    PINKY_TIP = 20

    def predecessor(self) -> Optional['HandJoint']:
        """
        Returns the predecessor of this joint.
        The predecessor of the wrist is None.
        """
        if self.value == 0:
            return None
        return predecessors[self.value]

    def successors(self) -> List['HandJoint']:
        """
        Returns all successors of this joint.
        The successors of the tip joints are an empty list.
        """
        return successors[self.value]

    def is_tip(self) -> bool:
        """
        Returns whether this joint is a tip joint.
        """
        return self in tip_joints

    def __str__(self) -> str:
        return self.name.replace('_', ' ').title()


predecessors = [
    None,                # WRIST
    HandJoint.WRIST,     # THUMB1
    HandJoint.THUMB_1,   # THUMB2
    HandJoint.THUMB_2,   # THUMB3
    HandJoint.THUMB_3,   # THUMB_TIP
    HandJoint.WRIST,     # INDEX1
    HandJoint.INDEX_1,   # INDEX2
    HandJoint.INDEX_2,   # INDEX3
    HandJoint.INDEX_3,   # INDEX_TIP
    HandJoint.WRIST,     # MIDDLE1
    HandJoint.MIDDLE_1,  # MIDDLE2
    HandJoint.MIDDLE_2,  # MIDDLE3
    HandJoint.MIDDLE_3,  # MIDDLE_TIP
    HandJoint.WRIST,     # RING1
    HandJoint.RING_1,    # RING2
    HandJoint.RING_2,    # RING3
    HandJoint.RING_3,    # RING_TIP
    HandJoint.WRIST,     # PINKY1
    HandJoint.PINKY_1,   # PINKY2
    HandJoint.PINKY_2,   # PINKY3
    HandJoint.PINKY_3,   # PINKY_TIP
]

successors: List[List[HandJoint]] = [
    [HandJoint.THUMB_1, HandJoint.INDEX_1, HandJoint.MIDDLE_1, HandJoint.RING_1, HandJoint.PINKY_1],  # WRIST
    [HandJoint.THUMB_2],     # THUMB1
    [HandJoint.THUMB_3],     # THUMB2
    [HandJoint.THUMB_TIP],   # THUMB3
    [],                      # THUMB_TIP
    [HandJoint.INDEX_2],     # INDEX1
    [HandJoint.INDEX_3],     # INDEX2
    [HandJoint.INDEX_TIP],   # INDEX3
    [],                      # INDEX_TIP
    [HandJoint.MIDDLE_2],    # MIDDLE1
    [HandJoint.MIDDLE_3],    # MIDDLE2
    [HandJoint.MIDDLE_TIP],  # MIDDLE3
    [],                      # MIDDLE_TIP
    [HandJoint.RING_2],      # RING1
    [HandJoint.RING_3],      # RING2
    [HandJoint.RING_TIP],    # RING3
    [],                      # RING_TIP
    [HandJoint.PINKY_2],     # PINKY1
    [HandJoint.PINKY_3],     # PINKY2
    [HandJoint.PINKY_TIP],   # PINKY3
    []                       # PINKY_TIP
]

first_finger_joints = [
    HandJoint.THUMB_1,
    HandJoint.INDEX_1,
    HandJoint.MIDDLE_1,
    HandJoint.RING_1,
    HandJoint.PINKY_1
]

second_and_third_finger_joints = [
    HandJoint.THUMB_2,
    HandJoint.THUMB_3,
    HandJoint.INDEX_2,
    HandJoint.INDEX_3,
    HandJoint.MIDDLE_2,
    HandJoint.MIDDLE_3,
    HandJoint.RING_2,
    HandJoint.RING_3,
    HandJoint.PINKY_2,
    HandJoint.PINKY_3
]

tip_joints = [
    HandJoint.THUMB_TIP,
    HandJoint.INDEX_TIP,
    HandJoint.MIDDLE_TIP,
    HandJoint.RING_TIP,
    HandJoint.PINKY_TIP
]
