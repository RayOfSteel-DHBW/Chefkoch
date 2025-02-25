from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ChefkochEntity:
    """Base class for Chefkoch entities that have a name and URL."""
    name: str
    url: str
    def __str__(self) -> str:
        return self.name

@dataclass
class Category(ChefkochEntity):
    """Represents a recipe category on Chefkoch."""
    pass

@dataclass
class Ingredient:
    """Represents a single ingredient with name and amount."""
    name: str
    amount: str

    def __str__(self) -> str:
        return f"{self.amount} {self.name}"


@dataclass
class Recipe:
    """
    Represents a full recipe, including:
    - name
    - detailed page URL
    - list of ingredients
    - List of categories/tags
    """
    name: str
    url: str
    ingredients: List[Ingredient]
    categories: List[Category]

    def __str__(self) -> str:
        return self.name
