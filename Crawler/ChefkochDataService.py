from typing import List
from peewee import (
    SqliteDatabase, Model, AutoField, CharField, FloatField,
    ManyToManyField, DoesNotExist
)

# ---------------------------------------------------------------------
# Initialize the SQLite database
# ---------------------------------------------------------------------
db = SqliteDatabase("chefkoch.db")

# ---------------------------------------------------------------------
# Base entity: ChefkochEntity (name + url), used by Category, Tag, etc.
# ---------------------------------------------------------------------
class ChefkochEntity(Model):
    id = AutoField()
    name = CharField()
    url = CharField(null=True)

    class Meta:
        database = db
        abstract = True  # Not directly mapped to a table itself


# ---------------------------------------------------------------------
# Concrete entities
# ---------------------------------------------------------------------
class Category(ChefkochEntity):
    """Categories (e.g., 'Pizza', 'Auflauf', etc.)"""
    pass


class Tag(ChefkochEntity):
    """Tags (e.g., 'Vegan', 'Low-Carb', etc.)"""
    pass


class Ingredient(ChefkochEntity):
    """Ingredient with amount, optionally ignoring URL if not needed."""
    amount = FloatField(default=1.0)


class Recipe(ChefkochEntity):
    """Recipes with potential Many-to-Many relationships to categories, tags, ingredients."""
    categories = ManyToManyField(Category, backref="recipes")
    tags = ManyToManyField(Tag, backref="recipes")
    ingredients = ManyToManyField(Ingredient, backref="recipes")


# ---------------------------------------------------------------------
# Through (join) tables for Many-to-Many relationships
# ---------------------------------------------------------------------
RecipeCategory = Recipe.categories.get_through_model()
RecipeTag = Recipe.tags.get_through_model()
RecipeIngredient = Recipe.ingredients.get_through_model()

# ---------------------------------------------------------------------
# Default categories to seed
# ---------------------------------------------------------------------
DEFAULT_CATEGORIES: List[Category] = [
    Category(name="Auflauf",           url="https://www.chefkoch.de/rs/s0t30/Auflauf-Rezepte.html"),
    Category(name="Pizza",             url="https://www.chefkoch.de/rs/s0t82/Pizza-Rezepte.html"),
    Category(name="Reis- oder Nudelsalat", url="https://www.chefkoch.de/rs/s0t94/Reis-oder-Nudelsalat-Rezepte.html"),
    Category(name="Salat",             url="https://www.chefkoch.de/rs/s0t15/Salat-Rezepte.html"),
    Category(name="Salatdressing",     url="https://www.chefkoch.de/rs/s0t3669/Salatdressing-Rezepte.html"),
    Category(name="Tarte",             url="https://www.chefkoch.de/rs/s0t122/Tarte-Rezepte.html"),
    Category(name="Fingerfood",        url="https://www.chefkoch.de/rs/s0t52/Fingerfood-Rezepte.html"),
    Category(name="Dips",              url="https://www.chefkoch.de/rs/s0t35/Dips-Rezepte.html"),
    Category(name="Saucen",            url="https://www.chefkoch.de/rs/s0t34/Saucen-Rezepte.html"),
    Category(name="Suppe",             url="https://www.chefkoch.de/rs/s0t40/Suppe-Rezepte.html"),
    Category(name="Klöße",             url="https://www.chefkoch.de/rs/s0t166/Kloesse-Rezepte.html"),
    Category(name="Brot und Brötchen", url="https://www.chefkoch.de/rs/s0t108/Brot-und-Broetchen-Rezepte.html"),
    Category(name="Brotspeise",        url="https://www.chefkoch.de/rs/s0t46/Brotspeise-Rezepte.html"),
    Category(name="Aufstrich",         url="https://www.chefkoch.de/rs/s0t51/Aufstrich-Rezepte.html"),
    Category(name="Süßspeise",         url="https://www.chefkoch.de/rs/s0t89/Suessspeise-Rezepte.html"),
    Category(name="Eis",               url="https://www.chefkoch.de/rs/s0t127/Eis-Rezepte.html"),
    Category(name="Kuchen",            url="https://www.chefkoch.de/rs/s0t92/Kuchen-Rezepte.html"),
    Category(name="Kekse",             url="https://www.chefkoch.de/rs/s0t147/Kekse-Rezepte.html"),
    Category(name="Torte",             url="https://www.chefkoch.de/rs/s0t93/Torte-Rezepte.html"),
    Category(name="Confiserie",        url="https://www.chefkoch.de/rs/s0t157/Confiserie-Rezepte.html"),
    Category(name="Getränke",          url="https://www.chefkoch.de/rs/s0t11/Getraenke-Rezepte.html"),
    Category(name="Shake",             url="https://www.chefkoch.de/rs/s0t113/Shake-Rezepte.html"),
    Category(name="Gewürzmischung",    url="https://www.chefkoch.de/rs/s0t313/Gewuermischung-Rezepte.html"),
    Category(name="Pasten",            url="https://www.chefkoch.de/rs/s0t243/Pasten-Rezepte.html"),
    Category(name="Studentenküche",    url="https://www.chefkoch.de/rs/s0t211/Studentenkueche-Rezepte.html"),
]

# ---------------------------------------------------------------------
# The ChefkochDataService with all CRUD methods
# ---------------------------------------------------------------------
class ChefkochDataService:
    def __init__(self):
        # Ensure DB and tables are set up
        db.connect(reuse_if_open=True)
        db.create_tables([
            Category, Tag, Ingredient, Recipe, 
            RecipeCategory, RecipeTag, RecipeIngredient
        ])
        # Seed default categories (only if they're missing)
        self._initialize_categories()

    def _initialize_categories(self):
        """Add default categories if they don't exist."""
        for cat in DEFAULT_CATEGORIES:
            # get_or_create ensures duplicates aren't made
            Category.get_or_create(name=cat.name, defaults={"url": cat.url})

    # ---------------- CATEGORY CRUD ----------------

    def create_category(self, category: Category) -> None:
        """Create a category."""
        category.save()

    def read_category(self, category_id: int) -> Category:
        """Read a category by ID."""
        return Category.get_by_id(category_id)

    def update_category(self, category: Category) -> None:
        """Update a category."""
        category.save()

        def delete_category(self, category_id: int) -> None:
        """Delete a category by ID."""
        Category.get_by_id(category_id).delete_instance()

    def category_exists(self, category_id: int) -> bool:
        """Check if a category exists."""
        return Category.select().where(Category.id == category_id).exists()

    # ---------------- INGREDIENT CRUD ----------------
    
    def create_ingredient(self, ingredient: Ingredient) -> None:
        ingredient.save()

    def read_ingredient(self, ingredient_id: int) -> Ingredient:
        return Ingredient.get_by_id(ingredient_id)

    def update_ingredient(self, ingredient: Ingredient) -> None:
        ingredient.save()

    def delete_ingredient(self, ingredient_id: int) -> None:
        Ingredient.get_by_id(ingredient_id).delete_instance()

    def ingredient_exists(self, ingredient_id: int) -> bool:
        return Ingredient.select().where(Ingredient.id == ingredient_id).exists()

    # ---------------- TAG CRUD ----------------
    
    def create_tag(self, tag: Tag) -> None:
        tag.save()

    def read_tag(self, tag_id: int) -> Tag:
        return Tag.get_by_id(tag_id)

    def update_tag(self, tag: Tag) -> None:
        tag.save()

    def delete_tag(self, tag_id: int) -> None:
        Tag.get_by_id(tag_id).delete_instance()

    def tag_exists(self, tag_id: int) -> bool:
        return Tag.select().where(Tag.id == tag_id).exists()

    # ---------------- RECIPE CRUD ----------------
    
    def create_recipe(self, recipe: Recipe) -> None:
        recipe.save()

    def read_recipe(self, recipe_id: int) -> Recipe:
        return Recipe.get_by_id(recipe_id)

    def update_recipe(self, recipe: Recipe) -> None:
        recipe.save()

    def delete_recipe(self, recipe_id: int) -> None:
        Recipe.get_by_id(recipe_id).delete_instance()

    def recipe_exists(self, recipe_id: int) -> bool:
        return Recipe.select().where(Recipe.id == recipe_id).exists()

# Example usage
if __name__ == "__main__":
    service = ChefkochDataService()
    
    # Example: Create a new category
    new_category = Category(name="TestCategory", url="https://example.com")
    service.create_category(new_category)
    
    # Verify category exists
    print("Category exists:", service.category_exists(new_category.id))
    
    # Read and print category
    retrieved_category = service.read_category(new_category.id)
    print("Retrieved Category:", retrieved_category.name, retrieved_category.url)
    
    # Delete the category
    service.delete_category(new_category.id)
    print("Category deleted.")

