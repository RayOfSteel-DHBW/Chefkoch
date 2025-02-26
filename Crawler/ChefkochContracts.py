from dataclasses import dataclass, field, asdict
from typing import List

# Import the model classes from your new models.py file.
from ChefkochModels import IngredientModel, CategoryModel, RecipeModel

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

    def to_model(self) -> IngredientModel:
        # Convert this dataclass to a dictionary and create an IngredientModel.
        data = asdict(self)
        return IngredientModel(**data)

@dataclass
class Category(ChefkochEntity):
    """Represents a recipe category with pagination and ID (mandatory)."""
    ID: int
    currentPage: int = 0
    maxPage: int = 0

    def to_model(self) -> CategoryModel:
        # Convert the dataclass to a dict and remap fields for the model.
        data = asdict(self)
        data['external_id'] = data.pop('ID')
        data['current_page'] = data.pop('currentPage')
        data['max_page'] = data.pop('maxPage')
        return CategoryModel(**data)

@dataclass
class Recipe(ChefkochEntity):
    """Represents a recipe with ingredients and categories."""
    ingredients: List[Ingredient] = field(default_factory=list)
    categories: List[Category] = field(default_factory=list)

    def __str__(self) -> str:
        return self.name

    def to_model(self) -> RecipeModel:
        # Create the base recipe without the relationships.
        data = asdict(self)
        data.pop('ingredients', None)
        data.pop('categories', None)
        recipe_model = RecipeModel(**data)
        recipe_model.save()  # Save to assign an ID for m2m relationships.

        # Process ingredients and add them to the recipe.
        for ing in self.ingredients:
            ing_model = ing.to_model()
            ing_model.save()  # Save the ingredient model.
            recipe_model.ingredients.add(ing_model)

        # Process categories and add them to the recipe.
        for cat in self.categories:
            cat_model = cat.to_model()
            cat_model.save()
            recipe_model.categories.add(cat_model)

        return recipe_model
