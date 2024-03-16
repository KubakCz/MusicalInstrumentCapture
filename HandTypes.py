from dataclasses import dataclass
from typing import List
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Vector3:
    x: float
    y: float
    z: float


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class HandFrame:
    timestamp: float
    normalized_positions: List[Vector3]
    world_positions: List[Vector3]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class HandAnimationData:
    name: str
    animation_data: List[HandFrame]
