"""
This module contains all the routers for the different features available in BluebirdATC. Note that, unlike in compiled
programming languages where disabled features are not included in the machine code, not including certain routers just
means that the endpoint is not available but the logic will continue to be available in BluebirdATC,
and therefore logged.

All the following routers are independent on the implementation of the storage of the runners and get this through the
fastapi dependency. See the respective documentation in ../runnerabc.py.

Note the endpoint for loading a run, that the HMI and most clients expect, is not included here as they are dependent on
the implementation of the store, which is dependent on the use case. An example of this endpoint, and any other
endpoints not included within the groups defined here are available in ../routes.py
"""

from .core import core_router

__all__ = [
    "core_router",
]
