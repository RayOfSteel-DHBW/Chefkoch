from dataclasses import dataclass
from typing import List

from ChefkochDataService import ChefkochEntityModel

@dataclass
class ParsingResult():
    def __init__(self, entity):
        self.entity = entity
        self.foundRecipes = []
        self.foundCategories = []

    entity: ChefkochEntityModel
    foundRecipes: List[str]
    foundCategories: List[str]