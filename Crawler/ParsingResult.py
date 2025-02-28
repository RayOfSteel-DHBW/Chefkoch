from dataclasses import dataclass
from typing import TypeVar, Generic, List

# Define a type variable that's constrained to ChefkochEntityModel or its subclasses
T = TypeVar('T', bound=ChefkochEntityModel)

@dataclass
class ParsingResult(Generic[T]):
    def __init__(self):
        self.entity = None
        self.foundRecipes = []
        self.foundCategories = []

    entity: T
    foundRecipes: List[str]
    foundCategories: List[str]