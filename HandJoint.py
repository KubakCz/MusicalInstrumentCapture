from enum import Enum
from typing import Optional


class HandJoint(Enum):
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
        if (self.value == 0):
            return None
        return HandJoint._predecessors[self.value]

    def is_tip(self) -> bool:
        return self in HandJoint._tip_joints

    def __str__(self):
        return self.name.replace('_', ' ').title()


HandJoint._predecessors = [
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

HandJoint._tip_joints = [
    HandJoint.THUMB_TIP,
    HandJoint.INDEX_TIP,
    HandJoint.MIDDLE_TIP,
    HandJoint.RING_TIP,
    HandJoint.PINKY_TIP
]
