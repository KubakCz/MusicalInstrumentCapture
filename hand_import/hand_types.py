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

"""Data classes for loading hand animation data from json."""

from dataclasses import dataclass, field
from typing import List
from dataclasses_json import dataclass_json, LetterCase, config
from mathutils import Vector


def decode_vector_list(data):
    """Decodes a list of vectors from a dictionary list."""
    result = [Vector((v["x"], v["y"], v["z"])) for v in data]
    return result


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class HandFrame:
    """Data class for a single frame of hand animation."""
    timestamp: float
    normalized_positions: List[Vector] = field(metadata=config(decoder=decode_vector_list))
    world_positions: List[Vector] = field(metadata=config(decoder=decode_vector_list))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class HandAnimationData:
    """Data class for a complete animation of one hand."""
    name: str
    animation_data: List[HandFrame]
