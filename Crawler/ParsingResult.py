from dataclasses import dataclass
from typing import TypeVar, Generic, List

from ChefkochModels import ChefkochEntityModel

# Define a type variable that's constrained to ChefkochEntityModel or its subclasses
T = TypeVar('T', bound=ChefkochEntityModel)

@dataclass
class ParsingResult(Generic[T]):
    def __init__(self, entity: T):
        self.entity = entity
        self.foundRecipes = []
        self.foundCategories = []
    """Generic result container that can hold any ChefkochEntityModel subclass"""
    entity: T
    foundRecipes: List[str]
    foundCategories: List[str]