from pathlib import Path
from peewee import (
    Model, CharField, IntegerField, ManyToManyField, SqliteDatabase,
    DoesNotExist, ForeignKeyField
)
from fileinput import filename
from typing import Union

# from Crawler import ParsingResult  # Adjust import as needed

db_path = Path(r'Data\crawled_data.db').resolve()
db = SqliteDatabase(str(db_path), pragmas={'journal_mode': 'wal'})


class ChefkochObjectModel(Model):
    name = CharField()
    class Meta:
        database = db
        abstract = True


class ChefkochEntityModel(ChefkochObjectModel):
    file = CharField()

    @property
    def url(self):
        raise NotImplementedError("Subclasses must implement url property")

    class Meta:
        abstract = True


class IngredientModel(ChefkochObjectModel):
    # Use a separate field for the amount. If an ingredient can appear multiple times
    # with different amounts, consider storing that in the through-table only.
    pass


class CategoryModel(ChefkochEntityModel):
    category_id = IntegerField()
    current_page = IntegerField(default=0)
    max_page = IntegerField(default=1)

    @property
    def url(self):
        return f"https://www.chefkoch.de/rs/s{self.current_page}t{self.category_id}/{self.file}"

    @property
    def next_page_url(self):
        if self.current_page < self.max_page:
            return f"https://www.chefkoch.de/rs/s{self.current_page + 1}t{self.category_id}/{self.file}"
        else:
            return f"https://www.chefkoch.de/rs/s{self.max_page}t{self.category_id}/{self.file}"


class RecipeModel(ChefkochEntityModel):
    categories = ManyToManyField(CategoryModel, backref='recipes')
    recipe_id = CharField()

    def __init__(self, name, file, recipe_id):
        super().__init__(name, file)
        self.recipe_id = recipe_id

    @property
    def url(self):
        return f"https://www.chefkoch.de/rezepte/{self.recipe_id}/{self.file}"
    
class RecipeIngredientThroughModel(Model):
    recipe = ForeignKeyField(RecipeModel, backref='recipe_ingredients')
    ingredient = ForeignKeyField(IngredientModel, backref='ingredient_recipes')
    amount = CharField()

    class Meta:
        database = db
RecipeCategoryThrough = RecipeModel.categories.get_through_model()




class ChefkochDataService:
    def __init__(self):
        db.connect(reuse_if_open=True)
        db.create_tables([
            IngredientModel,
            CategoryModel,
            RecipeModel,
            RecipeIngredientThroughModel,
            RecipeCategoryThrough
        ], safe=True)

    def create_or_update_category(self, category_data: CategoryModel) -> CategoryModel:
        """
        Check if a category already exists by (name, category_id).
        If it does, update current_page and max_page.
        If not, create a new one.
        """
        with db.atomic():
            category, created = CategoryModel.get_or_create(
                name=category_data.name,
                category_id=category_data.category_id,
                file=category_data.file,
                current_page = category_data.current_page,
                max_page = category_data.max_page
            )
            if not created:
                category.current_page = category_data.current_page
                category.max_page = category_data.max_page
                category.file = category_data.file
                category.save()
            return category

    def create_or_update_recipe(self, recipe_data: RecipeModel, ingredients: list[dict], category_ids: list[int]) -> RecipeModel:
        # Wrap the whole operation in a transaction to ensure atomicity.
        with db.atomic():
            # Either fetch an existing recipe or create a new one
            recipe, created = RecipeModel.get_or_create(
                name=recipe_data.name,
                recipe_id=recipe_data.recipe_id,
                file=recipe_data.file)
            if not created:
                # If the recipe already exists, update fields as needed
                recipe.file = recipe_data.file
                recipe.save()

            # Process and link ingredients with the custom through model.
            for ingredient_data in ingredients:
                # Ensure the Ingredient exists in the database.
                # This will create a new IngredientModel entry if it doesn't exist.
                ingredient, _ = IngredientModel.get_or_create(name=ingredient_data['name'])
                
                # Create or update the link in the through model.
                # Using get_or_create avoids creating duplicate links.
                recipe_ing, created = RecipeIngredientThroughModel.get_or_create(
                    recipe=recipe,
                    ingredient=ingredient,
                    defaults={'amount': ingredient_data['amount']}
                )
                if not created:
                    # Update the amount if the link already exists.
                    recipe_ing.amount = ingredient_data['amount']
                    recipe_ing.save()

            # Process and link categories. You could similarly check if you want to update categories.
            for cat_id in category_ids:
                try:
                    cat = CategoryModel.get_by_id(cat_id)
                    # The ManyToManyField helper lets you add links without dealing with the through model directly.
                    recipe.categories.add(cat)
                except DoesNotExist:
                    # Optionally handle the case where the category isn't found
                    pass

            return recipe

    def process_entity(self, entity: ChefkochEntityModel,
                       ingredient_amounts=None,
                       category_ids=None) -> None:
        """
        General method to process an entity.
        If it's a CategoryModel, create or update it.
        If it's a RecipeModel, create or update it with its related data.
        """
        if isinstance(entity, CategoryModel):
            self.create_or_update_category(entity)
        elif isinstance(entity, RecipeModel):
            if ingredient_amounts is None:
                ingredient_amounts = {}
            if category_ids is None:
                category_ids = []
            self.create_or_update_recipe(entity, ingredient_amounts, category_ids)
        else:
            raise ValueError("Unsupported entity type")

    def get_categories_for_update(self):
        """
        Returns categories that can still be updated (i.e., current_page < max_page).
        """
        return CategoryModel.select().where(CategoryModel.current_page < CategoryModel.max_page)
    
