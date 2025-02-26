from typing import Type, TypeVar, List, Optional
from peewee import SqliteDatabase, Model, DoesNotExist

# Import models from ChefkochModels.py
from ChefkochModels import (
    CategoryModel, RecipeModel, IngredientModel,
    RecipeIngredient, RecipeCategory
)

# Define a generic type for models
T = TypeVar("T", bound=Model)

class ChefkochDataService:
    def __init__(self, db_path: str):
        self.db = SqliteDatabase(db_path)
        
        # Set database for models
        models = [CategoryModel, RecipeModel, IngredientModel, RecipeIngredient, RecipeCategory]
        for model in models:
            model._meta.database = self.db
        
        self.db.connect(reuse_if_open=True)
        self.db.create_tables(models)
        self._initialize_categories()

    def _initialize_categories(self):
        """Add default categories if they don't exist."""
        DEFAULT_CATEGORIES = [
            {"name": "Auflauf", "url": "https://www.chefkoch.de/rs/s0t30/Auflauf-Rezepte.html", "external_id": 30, "current_page": 0, "max_page": 1},
            {"name": "Pizza", "url": "https://www.chefkoch.de/rs/s0t82/Pizza-Rezepte.html", "external_id": 82, "current_page": 0, "max_page": 1},
            {"name": "Kuchen", "url": "https://www.chefkoch.de/rs/s0t78/Kuchen-Rezepte.html", "external_id": 78, "current_page": 0, "max_page": 1},
        ]  # Add more if needed
        
        for cat_data in DEFAULT_CATEGORIES:
            CategoryModel.get_or_create(name=cat_data['name'], defaults=cat_data)

    def create_or_update_entity(self, entity: T) -> bool:
        """Creates or updates an entity, returns True if a new entity was created."""
        obj, created = entity.__class__.get_or_create(name=entity.name, defaults={"url": getattr(entity, 'url', None)})
        if not created and hasattr(entity, 'url'):
            obj.url = entity.url
            obj.save()
        return created
    
    def getCategories(self) -> List[CategoryModel]:
        """Returns all categories."""
        return list(CategoryModel.select())
    
    def create(self, entity: T) -> None:
        """Generic create method."""
        entity.save()
    
    def read(self, entity_type: Type[T], entity_id: int) -> Optional[T]:
        """Generic read method."""
        try:
            return entity_type.get_by_id(entity_id)
        except DoesNotExist:
            return None
    
    def update(self, entity: T) -> None:
        """Generic update method."""
        entity.save()
    
    def delete(self, entity_type: Type[T], entity_id: int) -> None:
        """Generic delete method."""
        try:
            entity = entity_type.get_by_id(entity_id)
            entity.delete_instance()
        except DoesNotExist:
            pass

    def create_recipe_with_relations(self, recipe_data: dict, ingredients: List[IngredientModel], categories: List[CategoryModel]) -> RecipeModel:
        """Create a recipe with its ingredients and categories relationships"""
        recipe = RecipeModel.create(**recipe_data)
        
        # Add ingredient relationships
        for ingredient in ingredients:
            recipe.ingredients.add(ingredient)
            
        # Add category relationships
        for category in categories:
            recipe.categories.add(category)
            
        return recipe
            
    def exists(self, entity_type: Type[T], entity_id: int) -> bool:
        """Check if an entity with the given ID exists."""
        return entity_type.select().where(entity_type.id == entity_id).exists()

if __name__ == "__main__":
    service = ChefkochDataService("chefkoch.db")
    
    # Example: Create a new category
    new_category = CategoryModel(name="TestCategory", url="https://example.com", external_id=999)
    service.create(new_category)
    
    # Verify category exists
    print("Category exists:", service.exists(CategoryModel, new_category.id))
    
    # Read and print category
    retrieved_category = service.read(CategoryModel, new_category.id)
    print("Retrieved Category:", retrieved_category.name if retrieved_category else "Not found")
    
    # Delete the category
    service.delete(CategoryModel, new_category.id)
    print("Category deleted.")
