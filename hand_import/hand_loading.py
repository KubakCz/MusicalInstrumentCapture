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

"""Classes and functions for loading hand data from JSON files."""

import json
from typing import Dict, Iterator, List, Any, Optional
from mathutils import Vector

from .hand_joint import HandJoint
from .hand_type import HandType


class InvalidDataError(Exception):
    """
    Exception raised when the loaded json data is invalid and cannot be converted to the expected format.
    """

    def __init__(self, message: str):
        super().__init__(message)


class PositionList:
    """
    Data class for storing a list of positions.
    Esures correct number of elements in the list to match the number of bones in the hand.
    """

    def __init__(self, position_list: List[Vector]):
        """
        Initialize the PositionList with the given data.
        :param data: List of positions. Must contain the same number of elements as the number of bones in the hand.
        """
        if len(position_list) != len(HandJoint):
            raise ValueError(
                f"Wrong number of positions in the list (has {len(position_list)}, expected {len(HandJoint)}).")
        self.vector_list = position_list

    def __iter__(self) -> Iterator[Vector]:
        return iter(self.vector_list)

    def __getitem__(self, item: int) -> Vector:
        return self.vector_list[item]

    @staticmethod
    def from_data(data: List[Dict[str, float]]) -> 'PositionList':
        """
        Create a PositionList from a list of dictionaries containing x, y, and z values.
        :param data: The list of dictionaries containing serialized vectors to create the PositionList from.
        :return: A PositionList containing the converted data.
        """
        # Check input type
        if not isinstance(data, list):
            raise InvalidDataError(
                f"Could not convert data to a list of positions: data must be of type list (it is {type(data)}).")
        if len(data) != len(HandJoint):
            raise InvalidDataError(
                f"Could not convert data to a list of positions: invalid number of positions in the list "
                f"(has {len(data)}, expected {len(HandJoint)}).")

        # Convert data to list of vectors
        try:
            position_list = [Vector((v["x"], v["y"], v["z"])) for v in data]
        except (KeyError, TypeError):
            raise InvalidDataError("Could not convert data to a list of positions: invalid position data.")

        return PositionList(position_list)


class Frame:
    """
    Data class for storing a single frame of hand animation.
    """

    def __init__(self, timestamp: float, normalized_positions: Optional[PositionList], world_positions: PositionList):
        """
        Initialize the Frame with the given data.
        :param timestamp: The timestamp of the frame.
        :param normalized_positions: The normalized positions of the hand joints.
        :param world_positions: The world positions of the hand joints.
        """
        self.timestamp = timestamp
        self.normalized_positions = normalized_positions
        self.world_positions = world_positions

    @staticmethod
    def from_data(data: Dict[str, Any]) -> 'Frame':
        """
        Create a Frame from a dictionary containing timestamp, normalized positions (optional), and world positions.
        :param data: The dictionary containing the serialized frame data.
        :return: A Frame containing the converted data.
        """
        # Timestamp
        if "timestamp" not in data:
            raise InvalidDataError("Could not convert data to a frame: timestamp not found.")
        if not isinstance(data["timestamp"], (float, int)):
            raise InvalidDataError(
                f"Could not convert data to a frame: invalid timestamp type "
                f"(is {type(data['timestamp'])}, expects float or int).")
        timestamp = data["timestamp"]

        # Normalized positions
        if "normalizedPositions" in data:
            try:
                normalized_positions = PositionList.from_data(data["normalizedPositions"])
            except InvalidDataError as e:
                raise InvalidDataError("Could not convert data to a frame: invalid normalized positions list.") from e
        else:
            normalized_positions = None

        # World positions
        if "worldPositions" not in data:
            raise InvalidDataError("Could not convert data to a frame: world positions not found.")
        try:
            world_positions = PositionList.from_data(data["worldPositions"])
        except InvalidDataError as e:
            raise InvalidDataError("Could not convert data to a frame: invalid world position list.") from e

        return Frame(timestamp, normalized_positions, world_positions)


class Hand:
    """
    Data class for storing a hand with animation data.
    """

    def __init__(self, name: str, hand_type: HandType, frames: List[Frame]):
        """
        Initialize the Hand with the given data.
        :param name: The name of the hand.
        :param handedness: The handedness of the hand.
        :param animation: The animation data of the hand.
        """
        self.name = name
        self.hand_type = hand_type
        self.frames = frames

    @staticmethod
    def from_data(data: Dict[str, Any]) -> 'Hand':
        """
        Create a Hand from a dictionary containing name, hand type, and animation data.
        :param data: The dictionary containing the serialized hand data.
        :return: A Hand containing the converted data.
        """
        # Name
        if "name" not in data:
            raise InvalidDataError("Could not convert data to a hand: name not found.")
        if not isinstance(data["name"], str):
            raise InvalidDataError(
                f"Could not convert data to a hand: invalid name type (is {type(data['name'])}, expects str).")
        name = data["name"]

        # Handedness
        if "handType" not in data:
            raise InvalidDataError("Could not convert data to a hand: hand type not found.")
        if not isinstance(data["handType"], str) or data["handType"].upper() not in HandType.__members__:
            raise InvalidDataError(
                f"Could not convert data to a hand: unrecognized hand type ({data['handType']}).")
        handedness = HandType[data["handType"].upper()]

        # Animation data
        if "animationData" not in data:
            raise InvalidDataError("Could not convert data to a hand: animation data not found.")
        if not isinstance(data["animationData"], list):
            raise InvalidDataError(
                f"Could not convert data to a hand: animation data must be of type list (it is {type(data)}).")
        frames: List[Frame] = []
        for i, frame_data in enumerate(data["animationData"]):
            try:
                frame = Frame.from_data(frame_data)
            except InvalidDataError as e:
                raise InvalidDataError(f"Could not convert data to a hand: invalid frame {i}.") from e
            frames.append(frame)

        return Hand(name, handedness, frames)


def load_json(filepath: str) -> List['Hand']:
    """
    Load a JSON file and return its data as a list of Hand objects.
    : param filepath: The path to the JSON file.
    : return: A list of Hand objects containing the loaded data.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            json_string = file.read()
            raw_data = json.loads(json_string)
            if not isinstance(raw_data, list):
                raise InvalidDataError("Could not load data: root object must be of type list.")
            hands: List[Hand] = []
            for i, hand_data in enumerate(raw_data):
                try:
                    hand = Hand.from_data(hand_data)
                except InvalidDataError as e:
                    raise InvalidDataError(f"Could not load data for hand with index {i}.") from e
                hands.append(hand)
            return hands
    except Exception as e:
        raise InvalidDataError(f"Could not load data from file {filepath}") from e
