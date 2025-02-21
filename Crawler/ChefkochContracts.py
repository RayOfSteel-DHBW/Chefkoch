from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Category:
    """Represents a recipe category on Chefkoch."""
    name: str
    url: str

    def __str__(self) -> str:
        return self.name


@dataclass
class Ingredient:
    """Represents a single ingredient with name and amount."""
    name: str
    amount: str

    def __str__(self) -> str:
        return f"{self.amount} {self.name}"


@dataclass
class Tag:
    """Represents a 'tag' for a Chefkoch recipe (e.g., 'vegetarisch', 'asiatisch', etc.)."""
    name: str
    url: str

    def __str__(self) -> str:
        return self.name


@dataclass
class Recipe:
    """
    Represents a full recipe, including:
    - name
    - detailed page URL
    - list of ingredients
    - category (Category object)
    - tags
    """
    name: str
    url: str
    ingredients: List[Ingredient]
    category: Optional[Category] = None
    tags: List[Tag] = field(default_factory=list)

    def __str__(self) -> str:
        return self.name
