from abc import ABC, abstractmethod


class Entity(ABC):
    @abstractmethod
    def create_schema(db): raise NotImplementedError()
