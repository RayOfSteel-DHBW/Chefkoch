from dataclasses import dataclass, field
from typing import List

@dataclass
class ChefkochObject:
    """Base class for all objects with only a name (mandatory)."""
    name: str

    def __str__(self) -> str:
        return self.name

@dataclass
class ChefkochEntity(ChefkochObject):
    """Extends ChefkochObject by adding a URL."""
    url: str

@dataclass
class Ingredient(ChefkochObject):
    """Represents an ingredient with an added field for amount."""
    amount: str

    def __str__(self) -> str:
        return f"{self.amount} {self.name}"

@dataclass
class Category(ChefkochEntity):
    """Represents a recipe category with pagination and ID (mandatory)."""
    ID: int
    currentPage: int = 0
    maxPage: int = 0

@dataclass
class Recipe(ChefkochEntity):
    """Represents a recipe with ingredients and categories."""
    ingredients: List[Ingredient] = field(default_factory=list)
    categories: List[Category] = field(default_factory=list)

    def __str__(self) -> str:
        return self.name
