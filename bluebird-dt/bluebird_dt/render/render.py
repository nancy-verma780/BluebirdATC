from abc import ABC, abstractmethod

from bluebird_dt.core import Environment


class Render(ABC):
    """
    Renders data into an image.
    """

    @abstractmethod
    def draw(self, environment: Environment):
        """
        Draw the Environment.
        """

        pass

    @abstractmethod
    def save(self, filename: str):
        """
        Generate an image image.
        """

        pass
