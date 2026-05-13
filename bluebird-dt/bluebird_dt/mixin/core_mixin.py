import math
from functools import total_ordering
from typing import TypeVar

from typing_extensions import override

T = TypeVar("T", bound="Comparison")


@total_ordering
class Comparison:
    """Mixin to enable an attribute level comparison between
    any two class instances with a data() method.

    Method may be SLOW and may need to be overridden by some subclasses
    to optimise performance"""

    @override
    def __eq__(self: T, other: T) -> bool:
        """
        Check if two class instances are equal.  This should work on
        any class that has a data() method for serialization (i.e. can
        be expressed as nested structure of dicts and lists).
        However, it may be slow, and it may be preferable for derived
        classes to override this with custom logic if speed is important.

        Parameters
        ----------
        other: Any
            Another class instance

        Returns
        -------
        bool
        """

        def lists_equal(l1: list, l2: list) -> bool:
            if len(l1) != len(l2):
                return False
            are_equal = True
            for i in range(len(l1)):
                if type(l1[i]) is not type(l2[i]):
                    return False
                if isinstance(l1[i], list):
                    are_equal &= lists_equal(l1[i], l2[i])
                elif isinstance(l1[i], dict):
                    are_equal &= dicts_equal(l1[i], l2[i])
                elif isinstance(l1[i], float | int):
                    are_equal &= math.isclose(l1[i], l2[i])
                elif isinstance(l1[i], str):
                    are_equal &= l1[i] == l2[i]
                # if we have any False, the whole comparison is False
                if not are_equal:
                    return False
            return are_equal

        def dicts_equal(d1: dict, d2: dict) -> bool:
            if set(d1) != set(d2):
                return False
            are_equal = True
            for k in d1:
                if type(d1[k]) is not type(d2[k]):
                    return False
                if isinstance(d1[k], list):
                    are_equal &= lists_equal(d1[k], d2[k])
                elif isinstance(d1[k], dict):
                    are_equal &= dicts_equal(d1[k], d2[k])
                elif isinstance(d1[k], float | int):
                    are_equal &= math.isclose(d1[k], d2[k])
                elif isinstance(d1[k], str):
                    are_equal &= d1[k] == d2[k]
                # if we have any False, the whole comparison is False
                if not are_equal:
                    return False
            return are_equal

        if not ("data" in vars(self) and "data" in vars(other)):
            # fallback method
            return self._vars_equal(other)
        # compare nested structure of dicts and lists
        this_data = self.data()
        if isinstance(this_data, dict):
            return dicts_equal(this_data, other.data())
        return lists_equal(this_data, other.data())

    def _vars_equal(self: T, other: T) -> bool:
        """
        Fallback method, if no "data" attribute of T.
        """
        equality = False

        if (self is not None) and (other is not None):
            equality = str(vars(self)) == str(vars(other))

        return equality

    def __gt__(self: T, other: T) -> bool:
        """
        Check if one class instance is "greater" than another by
        comparing their variables as strings

        Parameters
        ----------
        other: Any
            Another class instance

        Returns
        -------
        bool
        """
        return str(vars(self)) > str(vars(other))

    def __lt__(self: T, other: T) -> bool:
        """
        Check if one class instance is "less" than another by
        comparing their variables as strings

        Parameters
        ----------
        other: Any
            Another class instance

        Returns
        -------
        bool
        """
        return str(vars(self)) < str(vars(other))

    @override
    def __hash__(self: T) -> int:
        """
        Compute the hash value of an instance

        Returns
        -------
        int
        """
        return hash(tuple(sorted(self.data().items())))
