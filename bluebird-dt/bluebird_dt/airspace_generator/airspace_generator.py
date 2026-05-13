from abc import ABC, abstractmethod

from bluebird_dt.core import Airspace, Route


class AirspaceGenerator(ABC):
    """
    Airspace generator.
    """

    @abstractmethod
    def generate_airspace(self) -> tuple[Airspace, list[Route]] | Airspace:
        """
        Generate an Airspace and (optionally) a selection of Routes.

        Returns
        ----------
        Union[Tuple[Airspace, list[Route]], Airspace]
            A tuple with (Airspace, list of Routes) or an Airspace.
        """

        pass
