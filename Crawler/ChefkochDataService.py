from typing import Type, TypeVar, List, Optional
from peewee import (
    SqliteDatabase, Model, AutoField, CharField, FloatField,
    ManyToManyField, DoesNotExist
)

from Crawler.ChefkochContracts import Category

# Define a generic type for models
T = TypeVar("T", bound=Model)

class ChefkochDataService:
    def __init__(self, db_path: str):
        self.db = SqliteDatabase(db_path)
        self.db.connect(reuse_if_open=True)
        self.db.create_tables([])  # Tables are managed externally
        self._initialize_categories()

    def _initialize_categories(self):
        """Add default categories if they don't exist."""
        DEFAULT_CATEGORIES = [
            {"name": "Auflauf", "url": "https://www.chefkoch.de/rs/s0t30/Auflauf-Rezepte.html"},
            {"name": "Pizza", "url": "https://www.chefkoch.de/rs/s0t82/Pizza-Rezepte.html"},
        ]  # Add more if needed
        for cat in DEFAULT_CATEGORIES:
            Category.get_or_create(name=cat["name"], defaults={"url": cat["url"]})

    def create_or_update_entity(self, entity: T) -> bool:
        """Creates or updates an entity, returns True if a new entity was created."""
        obj, created = entity.__class__.get_or_create(name=entity.name, defaults={"url": getattr(entity, 'url', None)})
        if not created:
            if hasattr(entity, 'url'):
                obj.url = entity.url
                obj.save()
        return created
    
    def getCategories(self) -> List[T]:
        """Returns all categories."""
        return list(Category.select())
    
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
    
    def exists(self, entity_type: Type[T], entity_id: int) -> bool:
        """Generic exists method."""
        return entity_type.select().where(entity_type.id == entity_id).exists()

# Example usage
if __name__ == "__main__":
    service = ChefkochDataService("chefkoch.db")
    
    # Example: Create a new category
    new_category = Category(name="TestCategory", url="https://example.com")
    service.create(new_category)
    
    # Verify category exists
    print("Category exists:", service.exists(Category, new_category.id))
    
    # Read and print category
    retrieved_category = service.read(Category, new_category.id)
    print("Retrieved Category:", retrieved_category.name if retrieved_category else "Not found")
    
    # Delete the category
    service.delete(Category, new_category.id)
    print("Category deleted.")
