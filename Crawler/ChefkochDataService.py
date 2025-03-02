from pathlib import Path
from peewee import (
    Model, CharField, IntegerField, ManyToManyField, SqliteDatabase,
    DoesNotExist, ForeignKeyField
)
from fileinput import filename
from typing import Union

# from Crawler import ParsingResult  # Adjust import as needed

db_path = Path(Path(r'..\Data\crawled_data.db').resolve())
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
                defaults={
                    'file': category_data.file,
                    'current_page': category_data.current_page,
                    'max_page': category_data.max_page
                }
            )
            if not created:
                category.current_page = category_data.current_page
                category.max_page = category_data.max_page
                category.file = category_data.file
                category.save()
            return category

    def create_or_update_recipe(self, recipe_data: RecipeModel,
                                ingredient_amounts: dict,
                                category_ids: list) -> RecipeModel:
        """
        Check if a recipe already exists by (name, recipe_id).
        If it does, update relevant fields.
        Then link to ingredients and categories, creating them if needed.
        
        :param recipe_data: A RecipeModel instance with the basic fields set.
        :param ingredient_amounts: A dict containing ingredient_name -> amount
        :param category_ids: A list of CategoryModel primary keys or unique identifiers
        """
        with db.atomic():
            recipe, created = RecipeModel.get_or_create(
                name=recipe_data.name,
                recipe_id=recipe_data.recipe_id,
                defaults={
                    'file': recipe_data.file
                }
            )
            if not created:
                recipe.file = recipe_data.file
                recipe.save()

            # Link ingredients
            for ingredient_name, amount in ingredient_amounts.items():
                ingredient, _ = IngredientModel.get_or_create(name=ingredient_name)
                recipe.ingredients.add(ingredient, through_defaults={'amount': amount})

            # Link categories
            # If you have the entire CategoryModel object instead of IDs, adapt accordingly
            for cat_id in category_ids:
                try:
                    cat = CategoryModel.get_by_id(cat_id)
                    recipe.categories.add(cat)
                except DoesNotExist:
                    pass  # Or create a new category if needed

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
    
