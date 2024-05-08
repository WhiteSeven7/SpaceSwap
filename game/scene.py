from abc import ABC, abstractmethod


class Scene(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def run(self, game):
        ...


class PopUp(ABC):
    ...
