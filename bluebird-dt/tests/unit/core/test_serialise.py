import json

import numpy as np
import pytest

from bluebird_dt.core import (
    Action,
    Aircraft,
    Airspace,
    Airway,
    AirwayLeg,
    Area,
    Coordination,
    Environment,
    Fixes,
    FlightPlan,
    Pos2D,
    Pos3D,
    Pos4D,
    Route,
    Sector,
    Volume,
    WindField,
)

class_dict = {}
class_dict["Action"] = Action
class_dict["Aircraft"] = Aircraft
class_dict["Airspace"] = Airspace
class_dict["Airway"] = Airway
class_dict["AirwayLeg"] = AirwayLeg
class_dict["Area"] = Area
class_dict["Coordination"] = Coordination
class_dict["Environment"] = Environment
class_dict["Fixes"] = Fixes
class_dict["FlightPlan"] = FlightPlan
class_dict["Pos2D"] = Pos2D
class_dict["Pos3D"] = Pos3D
class_dict["Pos4D"] = Pos4D
class_dict["Route"] = Route
class_dict["Sector"] = Sector
class_dict["Volume"] = Volume
class_dict["WindField"] = WindField

def check_instances_equal(instance_1, instance_2):
    """Check if two instances have all the same attributes"""
    for k, v in instance_1.__dict__.items():
        # Ignore hidden attributes for example the cached _control_points for the Trajectory
        if not k.startswith("_"):
            # Check that the both values have the same type, whatever that is
            assert type(v) == type(instance_2.__dict__[k])  # noqa: E721

            if isinstance(v, dict):
                # if we have a nested dictionary check that the dictionaries are the same
                check_dicts_equal(v, instance_2.__dict__[k])
            elif isinstance(v, np.ndarray):
                # if we have a np.array check the values in each array are the same
                np.testing.assert_array_equal(v, instance_2.__dict__[k])
            elif isinstance(v, list):
                # if we have a list check that all members of the list match
                check_lists_equal(v, instance_2.__dict__[k])
            else:
                try:
                    # for any other case check the values match for each key value pair
                    assert v == instance_2.__dict__[k], f"Key {k} does not match"
                except AssertionError:
                    # If a starling object is returned, try recursively checking the attributes
                    # for example Routes returned from the FlightPlan
                    check_instances_equal(v, instance_2.__dict__[k])


def check_dicts_equal(dict_1, dict_2):
    """When given two dictionaries, ensures they contain the same keys and values"""
    for k, v in dict_1.items():
        # Check both the dict values have the same type, whatever that is
        assert type(dict_1[k]) == type(dict_2[k])  # noqa: E721

        if isinstance(v, dict):
            # Use recursion if have a nested dictionary
            check_dicts_equal(v, dict_2[k])

        elif isinstance(v, np.ndarray):
            # check values of np.array are the same
            np.testing.assert_array_equal(v, dict_2[k])

        elif hasattr(v, "__dict__"):
            # if the value can be expressed as a dictionary do so and use recursion
            check_dicts_equal(v.__dict__, dict_2[k].__dict__)

        elif isinstance(v, list):
            # if we have a list check that all members of the list match
            check_lists_equal(v, dict_2[k])

        else:
            # for any other case check the values match for each key value pair
            assert v == dict_2[k], f"key {k} does not match"


def check_lists_equal(list_1, list_2):
    """Check the length and contents of two lists"""

    # check length is the same
    assert len(list_1) == len(list_2), f"lists are of differing lengths {len(list_1)} and {len(list_2)}"

    # check each element is the same
    for obj_1, obj_2 in zip(list_1, list_2, strict=False):
        assert type(obj_1) == type(obj_2), f"elements are of differing types {type(obj_1)} and {type(obj_2)}"  # noqa: E721

        # check the value of the elements
        try:
            if hasattr(obj_1, "__dict__"):
                for attr in obj_1.__dict__:
                    check_instances_equal(getattr(obj_1, attr), getattr(obj_2, attr))
        except AttributeError:
            assert obj_1 == obj_2, f"elements are not equal {obj_1} and {obj_2}"


# populate the parameters for the tests
params_json = [(class_str, class_type, "json") for class_str, class_type in class_dict.items()]
params_instance = [(class_str, class_type, "inst") for class_str, class_type in class_dict.items()]


@pytest.mark.parametrize("build_random_full_instance_or_json_list", params_json, indirect=True)
def test_full_description(build_random_full_instance_or_json_list):
    """
    Test that the instance created has no 'None' values. This ensures if new optional
    attributes added this test will fail until they are explicitly added to the conftest
    """
    json_list, (class_str, _) = build_random_full_instance_or_json_list

    for json_str in json_list:
        parsed_json = json.loads(json_str)
        if isinstance(parsed_json, list):
            # PosND and Area return a list of values and need to be checked separately
            assert None not in json.loads(json_str), f"failed for class {class_str}"
            assert "null" not in json.loads(json_str), f"failed for class {class_str}"
            assert [] not in json.loads(json_str), f"failed for class {class_str}"
            assert {} not in json.loads(json_str), f"failed for class {class_str}"
        else:
            # for rest of starling objects
            assert None not in json.loads(json_str).values(), f"failed for class {class_str}"

            # Check that the json string does not contain empty lists or dictionaries
            assert [] not in json.loads(json_str).values(), f"failed for class {class_str}"
            assert {} not in json.loads(json_str).values(), f"failed for class {class_str}"


@pytest.mark.parametrize("build_random_full_instance_or_json_list", params_instance, indirect=True)
def test_serialisation(build_random_full_instance_or_json_list):
    """Test the instance -> json -> instance pipeline"""
    instance_list, (class_str, class_type) = build_random_full_instance_or_json_list

    for instance in instance_list:
        json_str = instance.to_json()

        rebuilt_instance = class_type.from_json(json_str)

        # Check the instance types
        assert isinstance(instance, class_type)
        assert isinstance(rebuilt_instance, class_type)
        assert isinstance(json_str, str)

        check_instances_equal(instance, rebuilt_instance)


@pytest.mark.parametrize("build_random_full_instance_or_json_list", params_json, indirect=True)
def test_deserialisation(build_random_full_instance_or_json_list):
    """Test the json -> instance -> json pipeline"""
    json_list, (class_str, class_type) = build_random_full_instance_or_json_list

    for json_str in json_list:
        built_instance = class_type.from_json(json_str)
        rebuilt_json_str = built_instance.to_json()

        # Check the types
        assert isinstance(json_str, str)
        assert isinstance(rebuilt_json_str, str)
        assert isinstance(built_instance, class_type)

        # Check that the initial and rebuilt json str are the same
        assert json_str == rebuilt_json_str
